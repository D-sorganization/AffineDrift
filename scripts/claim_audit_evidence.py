"""Self-contained byte evidence for reviewed claim-audit records."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path, PurePosixPath
from typing import cast

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
QUARTO_INCLUDE_PATTERN = re.compile(r"\{\{<\s*include\s+([^\s>]+)\s*>\}\}")


class ReviewEvidenceError(ValueError):
    """Raised when review evidence cannot be reproduced from protected bytes."""


def _relative_path(raw_path: object) -> PurePosixPath:
    """Return one normalized repository-relative POSIX path."""
    if not isinstance(raw_path, str) or not raw_path:
        raise ReviewEvidenceError("review evidence path must be a nonempty string")
    path = PurePosixPath(raw_path)
    if (
        path.is_absolute()
        or path.as_posix() != raw_path
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise ReviewEvidenceError(f"review evidence path is not normalized: {raw_path}")
    return path


def _regular_file(root: Path, raw_path: object) -> tuple[str, Path]:
    """Resolve a declared path without accepting symlinks or directory escape."""
    relative = _relative_path(raw_path)
    root_resolved = root.resolve(strict=True)
    candidate = root.joinpath(*relative.parts)
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root_resolved)
    except (OSError, ValueError) as exc:
        raise ReviewEvidenceError(
            f"review evidence path is missing or outside root: {relative}"
        ) from exc
    cursor = root_resolved
    for part in relative.parts:
        cursor /= part
        if cursor.is_symlink():
            raise ReviewEvidenceError(f"review evidence path cannot be a symlink: {relative}")
    if not resolved.is_file():
        raise ReviewEvidenceError(f"review evidence path is not a regular file: {relative}")
    return relative.as_posix(), resolved


def file_sha256(path: Path) -> str:
    """Return the lowercase SHA-256 digest of one regular file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def evidence_digests(root: Path, paths: list[str]) -> dict[str, str]:
    """Return deterministic digests for a declared evidence-path collection."""
    records = (_regular_file(root, path) for path in paths)
    return {relative: file_sha256(resolved) for relative, resolved in sorted(records)}


def canonical_source_path(route: str) -> str:
    """Map one public HTML route to its canonical Quarto source path."""
    if route == "/":
        return "index.qmd"
    if not route.startswith("/") or not route.endswith(".html"):
        raise ReviewEvidenceError(f"reviewed route has no canonical Quarto mapping: {route}")
    return f"{route[1:-5]}.qmd"


def included_sources(root: Path, source_path: str) -> set[str]:
    """Return all recursively included canonical files for one Quarto source."""
    pending = [source_path]
    visited: set[str] = set()
    included: set[str] = set()
    while pending:
        current = pending.pop()
        if current in visited:
            continue
        visited.add(current)
        current_relative, current_file = _regular_file(root, current)
        try:
            text = current_file.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ReviewEvidenceError(
                f"included source is not UTF-8 text: {current_relative}"
            ) from exc
        for match in QUARTO_INCLUDE_PATTERN.finditer(text):
            raw_target = match.group(1)
            if "\\" in raw_target or PurePosixPath(raw_target).is_absolute():
                raise ReviewEvidenceError(f"included source path is invalid: {raw_target}")
            try:
                resolved_target = (current_file.parent / raw_target).resolve(strict=True)
                relative_target = resolved_target.relative_to(root.resolve(strict=True)).as_posix()
            except (OSError, ValueError) as exc:
                raise ReviewEvidenceError(
                    f"included source is missing or outside root: {raw_target}"
                ) from exc
            normalized, _ = _regular_file(root, relative_target)
            if normalized not in included:
                included.add(normalized)
                pending.append(normalized)
    return included


def validate_digest_map(
    root: Path,
    paths: object,
    digests: object,
    *,
    label: str,
) -> list[str]:
    """Require an exact path-to-current-byte digest mapping."""
    if not isinstance(paths, list) or not all(isinstance(path, str) for path in paths):
        raise ReviewEvidenceError(f"{label} paths must be strings")
    if not isinstance(digests, dict) or not all(
        isinstance(path, str) and isinstance(digest, str) for path, digest in digests.items()
    ):
        raise ReviewEvidenceError(f"{label} digest map must contain string pairs")
    path_list = cast(list[str], paths)
    digest_map = cast(dict[str, str], digests)
    if set(path_list) != set(digest_map) or len(path_list) != len(digest_map):
        raise ReviewEvidenceError(f"{label} digest keys must exactly match its evidence paths")
    actual = evidence_digests(root, path_list)
    for path in path_list:
        expected = digest_map[path]
        if not SHA256_PATTERN.fullmatch(expected) or actual[path] != expected:
            raise ReviewEvidenceError(f"{label} digest mismatch: {path}")
    return path_list


def validate_review_evidence(record: dict[str, object], root: Path) -> None:
    """Validate canonical source, recursive includes, and exact reviewed bytes."""
    route = str(record.get("route", ""))
    review = record.get("review")
    if not isinstance(review, dict):
        raise ReviewEvidenceError(f"{route} reviewed route lacks review evidence")
    source_path = review.get("source_path")
    if source_path != canonical_source_path(route):
        raise ReviewEvidenceError(f"{route} review source path does not match its public route")
    evidence_paths = validate_digest_map(
        root,
        review.get("evidence_paths"),
        review.get("evidence_sha256"),
        label=f"{route} review evidence",
    )
    if source_path not in evidence_paths:
        raise ReviewEvidenceError(f"{route} review evidence omits its canonical source")
    missing_includes = included_sources(root, str(source_path)) - set(evidence_paths)
    if missing_includes:
        raise ReviewEvidenceError(
            f"{route} review evidence omits included source(s): {sorted(missing_includes)}"
        )
