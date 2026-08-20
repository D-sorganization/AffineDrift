#!/usr/bin/env python3
"""Verify the AffineDrift projection of the immutable UpstreamDrift release."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import cast

MAX_MANIFEST_BYTES = 5_000_000
MAX_PDF_BYTES = 10_000_000
USER_AGENT = "AffineDrift-publication-verifier/1"


class ProjectionError(RuntimeError):
    """Raised when publication evidence diverges from its declared authority."""


@dataclass(frozen=True)
class ProjectionResult:
    """Counts from a successful source-projection verification."""

    source_identical: int
    flattened: int
    rewritten: int
    adapted: int


def sha256_bytes(data: bytes) -> str:
    """Return a lowercase SHA-256 digest."""
    return hashlib.sha256(data).hexdigest()


def _mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ProjectionError(f"{label} must be an object with string keys")
    return cast(dict[str, object], value)


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ProjectionError(f"{label} must be a non-empty string")
    return value


def _integer(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ProjectionError(f"{label} must be a non-negative integer")
    return value


def _artifact_entry(artifacts: dict[str, object], path: str) -> dict[str, object]:
    if path not in artifacts:
        raise ProjectionError(f"upstream artifact is missing: {path}")
    return _mapping(artifacts[path], f"artifact {path}")


def _verify_artifact(path: str, data: bytes, entry: dict[str, object]) -> None:
    expected_hash = _text(entry.get("sha256"), f"{path} sha256")
    expected_bytes = _integer(entry.get("bytes"), f"{path} bytes")
    if len(data) != expected_bytes or sha256_bytes(data) != expected_hash:
        raise ProjectionError(f"artifact mismatch: {path}")


def projection_tree(publication_root: Path, pdf_name: str) -> tuple[int, str]:
    """Hash every projected source file except the recursive manifest and PDF."""
    digest = hashlib.sha256()
    files = [
        path
        for path in publication_root.rglob("*")
        if path.is_file() and path.name != "source_manifest.json" and path.name != pdf_name
    ]
    for path in sorted(files, key=lambda item: item.relative_to(publication_root).as_posix()):
        relative = path.relative_to(publication_root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_bytes(path.read_bytes()).encode("ascii"))
        digest.update(b"\n")
    return len(files), digest.hexdigest()


def verify_projection_lock(publication_root: Path, publisher: dict[str, object]) -> None:
    """Fail closed when any copied or adapted publication source changes."""
    publication = _mapping(publisher.get("publication"), "publication")
    projection = _mapping(publisher.get("projection"), "projection")
    pdf_name = _text(publication.get("pdf"), "publication pdf")
    actual_count, actual_hash = projection_tree(publication_root, pdf_name)
    expected_count = _integer(projection.get("file_count"), "projection file_count")
    expected_hash = _text(projection.get("tree_sha256"), "projection tree_sha256")
    if (actual_count, actual_hash) != (expected_count, expected_hash):
        raise ProjectionError("local publication source projection is stale")


def _resolve_upstream_path(
    relative: str, source_root: str, artifacts: dict[str, object]
) -> tuple[str, bool]:
    direct = f"{source_root}/{relative}"
    if direct in artifacts:
        return direct, False
    candidates = [
        path
        for path in artifacts
        if path.startswith(f"{source_root}/") and path.endswith(f"/{Path(relative).name}")
    ]
    if len(candidates) != 1:
        state = "missing" if not candidates else "ambiguous"
        raise ProjectionError(f"{state} upstream source for {relative}")
    return candidates[0], True


def _verify_claim_registry(source: dict[str, object], artifacts: dict[str, object]) -> None:
    claimed = _mapping(source.get("claim_registry"), "claim registry")
    path = _text(claimed.get("path"), "claim registry path")
    upstream = _artifact_entry(artifacts, path)
    for key in ("sha256", "bytes"):
        if claimed.get(key) != upstream.get(key):
            raise ProjectionError(f"claim registry {key} does not match the release manifest")


def _normalize_source_links(data: bytes, repository: str, commit: str) -> tuple[bytes, bool]:
    """Reverse the declared immutable-link rewrite before source comparison."""
    prefix = f"https://github.com/{repository}/".encode()
    normalized = data.replace(prefix + f"blob/{commit}/".encode(), prefix + b"blob/main/")
    normalized = normalized.replace(prefix + f"tree/{commit}/".encode(), prefix + b"tree/main/")
    return normalized, normalized != data


def _verify_source_files(
    publication_root: Path,
    pdf_name: str,
    source: dict[str, object],
    projection: dict[str, object],
    artifacts: dict[str, object],
    source_root: str,
) -> ProjectionResult:
    adapted = _mapping(projection.get("adapted_files"), "adapted files")
    repository = _text(source.get("repository"), "source repository")
    commit = _text(source.get("commit"), "source commit")
    seen_adapted: set[str] = set()
    direct_count = flattened_count = rewritten_count = 0
    for path in sorted(item for item in publication_root.rglob("*") if item.is_file()):
        relative = path.relative_to(publication_root).as_posix()
        if relative in {"source_manifest.json", pdf_name}:
            continue
        data = path.read_bytes()
        if relative in adapted:
            spec = _mapping(adapted[relative], f"adaptation {relative}")
            _text(spec.get("reason"), f"adaptation reason {relative}")
            expected = _text(spec.get("sha256"), f"adaptation sha256 {relative}")
            if sha256_bytes(data) != expected:
                raise ProjectionError(f"adapted publication file is stale: {relative}")
            seen_adapted.add(relative)
            continue
        upstream_path, flattened = _resolve_upstream_path(relative, source_root, artifacts)
        normalized, rewritten = _normalize_source_links(data, repository, commit)
        _verify_artifact(upstream_path, normalized, _artifact_entry(artifacts, upstream_path))
        flattened_count += int(flattened)
        rewritten_count += int(rewritten)
        direct_count += int(not flattened and not rewritten)
    undeclared = set(adapted) - seen_adapted
    if undeclared:
        raise ProjectionError(f"declared adaptations are missing: {sorted(undeclared)}")
    return ProjectionResult(direct_count, flattened_count, rewritten_count, len(seen_adapted))


def verify_projection(
    publication_root: Path,
    publisher: dict[str, object],
    upstream: dict[str, object],
    upstream_pdf: bytes,
) -> ProjectionResult:
    """Verify local source, adaptations, claim registry, and PDF as one bundle."""
    source = _mapping(publisher.get("source"), "source")
    publication = _mapping(publisher.get("publication"), "publication")
    projection = _mapping(publisher.get("projection"), "projection")
    artifacts = _mapping(upstream.get("artifacts"), "upstream artifacts")
    source_root = _text(source.get("root"), "source root").strip("/")
    pdf_name = _text(publication.get("pdf"), "publication pdf")
    pdf_path = f"{source_root}/{pdf_name}"
    _verify_artifact(pdf_path, upstream_pdf, _artifact_entry(artifacts, pdf_path))
    local_pdf = (publication_root / pdf_name).read_bytes()
    expected_pdf = _text(source.get("pdf_sha256"), "source pdf sha256")
    if sha256_bytes(upstream_pdf) != expected_pdf or local_pdf != upstream_pdf:
        raise ProjectionError("publication PDF does not match the protected source PDF")
    if publication.get("pdf_sha256") != expected_pdf:
        raise ProjectionError("publication PDF authority does not match the source authority")
    _verify_claim_registry(source, artifacts)

    result = _verify_source_files(
        publication_root, pdf_name, source, projection, artifacts, source_root
    )
    verify_projection_lock(publication_root, publisher)
    return result


def _read_bounded(location: str, limit: int) -> bytes:
    path = Path(location)
    if path.exists():
        data = path.read_bytes()
    else:
        if not location.startswith("https://"):
            raise ProjectionError(f"remote resource must use HTTPS: {location}")
        request = urllib.request.Request(location, headers={"User-Agent": USER_AGENT})
        # HTTPS-only source is pinned by digest before its JSON is trusted.
        with urllib.request.urlopen(
            request, timeout=30
        ) as response:  # noqa: S310 -- HTTPS only  # nosec B310
            data = response.read(limit + 1)
    if len(data) > limit:
        raise ProjectionError(f"resource exceeds {limit} bytes: {location}")
    return data


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--publication-root", type=Path, default=Path("articles/proximal_distal_energy_transfer")
    )
    parser.add_argument("--source-manifest", help="Exact release_manifest.json path or URL")
    parser.add_argument("--source-pdf", help="Exact protected PDF path or URL")
    return parser.parse_args()


def main() -> int:
    """Download or read the pinned authority and verify the complete projection."""
    args = _arguments()
    publisher_path = args.publication_root / "source_manifest.json"
    publisher = _mapping(
        json.loads(publisher_path.read_text(encoding="utf-8")), "publisher manifest"
    )
    source = _mapping(publisher.get("source"), "source")
    repository = _text(source.get("repository"), "source repository")
    commit = _text(source.get("commit"), "source commit")
    source_root = _text(source.get("root"), "source root").strip("/")
    pdf_name = _text(
        _mapping(publisher.get("publication"), "publication").get("pdf"), "publication pdf"
    )
    raw_root = f"https://raw.githubusercontent.com/{repository}/{commit}/{source_root}"
    manifest_bytes = _read_bounded(
        args.source_manifest or f"{raw_root}/release_manifest.json", MAX_MANIFEST_BYTES
    )
    expected_manifest = _text(source.get("release_manifest_sha256"), "release manifest sha256")
    if sha256_bytes(manifest_bytes) != expected_manifest:
        raise ProjectionError("release manifest digest does not match the protected authority")
    upstream = _mapping(json.loads(manifest_bytes), "upstream release manifest")
    upstream_pdf = _read_bounded(args.source_pdf or f"{raw_root}/{pdf_name}", MAX_PDF_BYTES)
    result = verify_projection(args.publication_root, publisher, upstream, upstream_pdf)
    print(
        "Projection verified: "
        f"{result.source_identical} source-identical, {result.flattened} flattened, "
        f"{result.rewritten} immutable-link rewrites, {result.adapted} declared adaptations."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ProjectionError, OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
