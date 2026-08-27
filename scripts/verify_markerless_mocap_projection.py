#!/usr/bin/env python3
"""Verify a qualified markerless-mocap publication projection."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import cast

SCHEMA_ID = "affinedrift/mocap-publication-projection/v1"
ALLOWED_REPOSITORIES = frozenset({"D-sorganization/Tools", "D-sorganization/UpstreamDrift"})
ALLOWED_LICENSES = frozenset(
    "Apache-2.0 BSD-2-Clause BSD-3-Clause CC-BY-4.0 CC0-1.0 ISC MIT".split()
)
ALLOWED_ARTIFACT_KINDS = frozenset(
    "aggregate_statistics calibration_summary compatibility_report derived_kinematics "
    "sanitized_c3d schema validation_report visualization".split()
)
ALLOWED_CLASSIFICATIONS = frozenset(
    "public_aggregate qualified_model_scenario sanitized_derived".split()
)
ALLOWED_EVIDENCE_CLASSES = {"derived", "model_scenario", "observed", "unavailable"}
MUTABLE_LINK = re.compile(
    r"https://(?:github\.com/[^/]+/[^/]+/(?:blob|tree)|raw\.githubusercontent\.com/[^/]+/[^/]+)"
    r"/(?:main|master)(?:/|$)",
    re.IGNORECASE,
)
REVISION = re.compile(r"[0-9a-f]{40}")
DIGEST = re.compile(r"[0-9a-f]{64}")
SENSITIVE_SUFFIXES = frozenset(".avi .env .key .mkv .mov .mp4 .pem .raw .webm".split())


class MocapProjectionError(RuntimeError):
    """Raised when public markerless-mocap evidence violates its contract."""


@dataclass(frozen=True)
class MocapProjectionSummary:
    """Deterministic counts for one accepted projection."""

    artifact_count: int
    claim_count: int
    total_bytes: int


def _object(value: object, label: str, keys: set[str]) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise MocapProjectionError(f"{label} must be an object")
    result = cast(dict[str, object], value)
    actual = set(result)
    if actual != keys:
        raise MocapProjectionError(
            f"{label} fields differ: missing={sorted(keys - actual)}, extra={sorted(actual - keys)}"
        )
    return result


def _array(value: object, label: str) -> list[object]:
    if not isinstance(value, list) or not value:
        raise MocapProjectionError(f"{label} must be a non-empty array")
    return cast(list[object], value)


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MocapProjectionError(f"{label} must be a non-empty string")
    return value


def _boolean(value: object, label: str) -> bool:
    if type(value) is not bool:
        raise MocapProjectionError(f"{label} must be boolean")
    return value


def _integer(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise MocapProjectionError(f"{label} must be a non-negative integer")
    return value


def _matches(value: object, label: str, pattern: re.Pattern[str]) -> str:
    text = _text(value, label)
    if pattern.fullmatch(text) is None:
        raise MocapProjectionError(f"{label} is invalid")
    return text


def _reject_mutable_links(value: object) -> None:
    if isinstance(value, str) and MUTABLE_LINK.search(value):
        raise MocapProjectionError(f"mutable branch link is forbidden: {value}")
    if isinstance(value, dict):
        for child in value.values():
            _reject_mutable_links(child)
    if isinstance(value, list):
        for child in value:
            _reject_mutable_links(child)


def _verify_source(value: object) -> tuple[str, str]:
    source = _object(
        value,
        "source",
        {"repository", "revision", "release_manifest_sha256", "source_url"},
    )
    repository = _text(source["repository"], "source repository")
    if repository not in ALLOWED_REPOSITORIES:
        raise MocapProjectionError("source repository is not an approved computational authority")
    revision = _matches(source["revision"], "source revision", REVISION)
    _matches(source["release_manifest_sha256"], "release manifest sha256", DIGEST)
    expected_url = f"https://github.com/{repository}/tree/{revision}"
    if _text(source["source_url"], "source URL") != expected_url:
        raise MocapProjectionError("source URL must be revision-pinned to the declared authority")
    return repository, revision


def _verify_license(value: object) -> None:
    policy = _object(value, "license", {"publication_spdx", "components"})
    if _text(policy["publication_spdx"], "publication license") != "MIT":
        raise MocapProjectionError("publication license must remain MIT")
    for index, value in enumerate(_array(policy["components"], "license components")):
        component = _object(value, f"license component {index}", {"name", "spdx", "distribution"})
        _text(component["name"], f"license component {index} name")
        spdx = _text(component["spdx"], f"license component {index} SPDX")
        if spdx not in ALLOWED_LICENSES:
            raise MocapProjectionError(f"component license is not approved for publication: {spdx}")
        distribution = _text(component["distribution"], f"license component {index} distribution")
        if distribution not in {"embedded", "linked"}:
            raise MocapProjectionError("component distribution must be embedded or linked")


def _verify_privacy(value: object) -> str:
    privacy = _object(
        value,
        "privacy",
        {
            "review",
            "consent",
            "retention",
            "contains_raw_video",
            "contains_pii",
            "contains_secrets",
        },
    )
    if _text(privacy["review"], "privacy review") != "approved":
        raise MocapProjectionError("privacy review must be approved")
    if _text(privacy["retention"], "privacy retention") != "sanitized_artifacts_only":
        raise MocapProjectionError("privacy retention must allow sanitized artifacts only")
    flags = {
        "raw video": _boolean(privacy["contains_raw_video"], "contains_raw_video"),
        "PII": _boolean(privacy["contains_pii"], "contains_pii"),
        "secrets": _boolean(privacy["contains_secrets"], "contains_secrets"),
    }
    for label, present in flags.items():
        if present:
            raise MocapProjectionError(f"projection declares forbidden {label}")
    return _text(privacy["consent"], "privacy consent")


def _verify_security(value: object) -> None:
    security = _object(value, "security", {"review", "malware_scan"})
    if _text(security["review"], "security review") != "approved":
        raise MocapProjectionError("security review must be approved")
    if _text(security["malware_scan"], "malware scan") != "passed":
        raise MocapProjectionError("malware scan must pass")


def _verify_qualification(value: object, repository: str, consent: str) -> str:
    qualification = _object(
        value,
        "qualification",
        {"origin", "status", "authority_repository", "protocol_version"},
    )
    if _text(qualification["status"], "qualification status") != "qualified":
        raise MocapProjectionError("projection must be qualified")
    if _text(qualification["authority_repository"], "qualification authority") != repository:
        raise MocapProjectionError("qualification authority must match the source repository")
    _text(qualification["protocol_version"], "qualification protocol version")
    origin = _text(qualification["origin"], "qualification origin")
    if origin not in {"live_lab", "protected_release", "synthetic"}:
        raise MocapProjectionError("qualification origin is unsupported")
    if origin == "live_lab" and consent != "public_release_approved":
        raise MocapProjectionError("live-lab evidence requires public-release consent")
    return origin


def _verify_claim(value: object, index: int, origin: str) -> tuple[str, set[str]]:
    claim = _object(
        value,
        f"claim {index}",
        {"id", "evidence_class", "status", "artifact_ids"},
    )
    claim_id = _text(claim["id"], f"claim {index} id")
    evidence_class = _text(claim["evidence_class"], f"claim {claim_id} evidence class")
    if evidence_class not in ALLOWED_EVIDENCE_CLASSES:
        raise MocapProjectionError(f"claim {claim_id} evidence class is unsupported")
    status = _text(claim["status"], f"claim {claim_id} status")
    artifact_values = claim["artifact_ids"]
    if not isinstance(artifact_values, list):
        raise MocapProjectionError(f"claim {claim_id} artifact_ids must be an array")
    reference_list = [_text(item, f"claim {claim_id} artifact id") for item in artifact_values]
    references = set(reference_list)
    if len(references) != len(reference_list):
        raise MocapProjectionError(f"claim {claim_id} repeats an artifact id")
    if status == "unavailable" and (evidence_class != "unavailable" or references):
        raise MocapProjectionError(f"unavailable claim {claim_id} must not cite artifacts")
    if status != "unavailable" and status != "qualified":
        raise MocapProjectionError(f"claim {claim_id} must be qualified or unavailable")
    if status == "qualified" and (evidence_class == "unavailable" or not references):
        raise MocapProjectionError(f"qualified claim {claim_id} requires evidence artifacts")
    if origin == "synthetic" and evidence_class not in {"model_scenario", "unavailable"}:
        raise MocapProjectionError("synthetic claims must use the model_scenario evidence class")
    return claim_id, references


def _verify_claims(value: object, origin: str) -> tuple[set[str], set[str]]:
    claim_ids: set[str] = set()
    references: set[str] = set()
    for index, item in enumerate(_array(value, "claims")):
        claim_id, claim_references = _verify_claim(item, index, origin)
        if claim_id in claim_ids:
            raise MocapProjectionError(f"duplicate claim id: {claim_id}")
        claim_ids.add(claim_id)
        references.update(claim_references)
    return claim_ids, references


def _safe_artifact_path(value: object, label: str) -> PurePosixPath:
    text = _text(value, label)
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts or "\\" in text or text != path.as_posix():
        raise MocapProjectionError(f"{label} must be a normalized relative path")
    if path.suffix.lower() in SENSITIVE_SUFFIXES:
        kind = (
            "raw video"
            if path.suffix.lower() in {".avi", ".mkv", ".mov", ".mp4", ".raw", ".webm"}
            else "secret material"
        )
        raise MocapProjectionError(f"artifact path contains forbidden {kind}: {text}")
    return path


def _verify_artifact_file(root: Path, path: PurePosixPath, digest: str, size: int) -> None:
    root_resolved = root.resolve()
    local_path = root_resolved.joinpath(*path.parts).resolve()
    try:
        local_path.relative_to(root_resolved)
    except ValueError as error:
        raise MocapProjectionError(f"artifact escapes projection root: {path}") from error
    if not local_path.is_file():
        raise MocapProjectionError(f"artifact is missing: {path}")
    data = local_path.read_bytes()
    actual_digest = hashlib.sha256(data).hexdigest()
    if len(data) != size or actual_digest != digest:
        raise MocapProjectionError(f"artifact mismatch: {path}")


def _verify_artifact(
    value: object, index: int, source: tuple[str, str], root: Path | None
) -> tuple[str, int]:
    artifact = _object(
        value,
        f"artifact {index}",
        {
            "id",
            "path",
            "kind",
            "classification",
            "media_type",
            "sha256",
            "bytes",
            "source_license",
            "source_url",
        },
    )
    artifact_id = _text(artifact["id"], f"artifact {index} id")
    path = _safe_artifact_path(artifact["path"], f"artifact {artifact_id} path")
    kind = _text(artifact["kind"], f"artifact {artifact_id} kind")
    media_type = _text(artifact["media_type"], f"artifact {artifact_id} media type")
    if kind == "raw_video" or media_type.startswith("video/"):
        raise MocapProjectionError(f"artifact {artifact_id} contains forbidden raw video")
    if kind not in ALLOWED_ARTIFACT_KINDS:
        raise MocapProjectionError(f"artifact {artifact_id} kind is unsupported")
    classification = _text(artifact["classification"], f"artifact {artifact_id} classification")
    if classification not in ALLOWED_CLASSIFICATIONS:
        raise MocapProjectionError(f"artifact {artifact_id} classification is not publishable")
    license_id = _text(artifact["source_license"], f"artifact {artifact_id} source license")
    if license_id not in ALLOWED_LICENSES:
        raise MocapProjectionError(f"artifact {artifact_id} license is not approved")
    repository, revision = source
    source_url = _text(artifact["source_url"], f"artifact {artifact_id} source URL")
    source_prefix = f"https://github.com/{repository}/blob/{revision}/"
    if not source_url.startswith(source_prefix):
        raise MocapProjectionError(f"artifact {artifact_id} source URL must be revision-pinned")
    _safe_artifact_path(source_url.removeprefix(source_prefix), f"artifact {artifact_id} URL path")
    digest = _matches(artifact["sha256"], f"artifact {artifact_id} sha256", DIGEST)
    size = _integer(artifact["bytes"], f"artifact {artifact_id} bytes")
    if root is not None:
        _verify_artifact_file(root, path, digest, size)
    return artifact_id, size


def _verify_artifacts(
    value: object, source: tuple[str, str], root: Path | None
) -> tuple[set[str], int]:
    artifact_ids: set[str] = set()
    total_bytes = 0
    for index, item in enumerate(_array(value, "artifacts")):
        artifact_id, size = _verify_artifact(item, index, source, root)
        if artifact_id in artifact_ids:
            raise MocapProjectionError(f"duplicate artifact id: {artifact_id}")
        artifact_ids.add(artifact_id)
        total_bytes += size
    return artifact_ids, total_bytes


def verify_projection_manifest(
    manifest: object, projection_root: Path | None = None
) -> MocapProjectionSummary:
    """Validate one sanitized, immutable projection and its local artifact digests.

    Preconditions:
        ``manifest`` follows the versioned public schema. ``projection_root`` is
        the directory containing declared artifacts when supplied.
    Postconditions:
        The return value is deterministic and all qualified claim references
        resolve to approved, revision-pinned artifacts.
    """
    _reject_mutable_links(manifest)
    document = _object(
        manifest,
        "manifest",
        {
            "schema",
            "source",
            "license",
            "privacy",
            "security",
            "qualification",
            "claims",
            "artifacts",
        },
    )
    if _text(document["schema"], "schema") != SCHEMA_ID:
        raise MocapProjectionError(f"schema must be {SCHEMA_ID}")
    source = _verify_source(document["source"])
    _verify_license(document["license"])
    consent = _verify_privacy(document["privacy"])
    _verify_security(document["security"])
    origin = _verify_qualification(document["qualification"], source[0], consent)
    claim_ids, references = _verify_claims(document["claims"], origin)
    artifact_ids, total_bytes = _verify_artifacts(document["artifacts"], source, projection_root)
    missing = references - artifact_ids
    if missing:
        raise MocapProjectionError(f"claims reference missing artifacts: {sorted(missing)}")
    return MocapProjectionSummary(len(artifact_ids), len(claim_ids), total_bytes)


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--projection-root", type=Path)
    return parser.parse_args()


def main() -> int:
    """Validate a manifest from disk and report deterministic counts."""
    args = _arguments()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    root = args.projection_root or args.manifest.parent
    result = verify_projection_manifest(manifest, root)
    print(
        "Markerless-mocap projection verified: "
        f"{result.artifact_count} artifacts, {result.claim_count} claims, "
        f"{result.total_bytes} bytes."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (MocapProjectionError, OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
