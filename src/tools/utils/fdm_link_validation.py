"""Contract loader for Forward Dynamics Matching ``link_validation.json``."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.core.contracts.definitions import PreconditionError, require

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
UPSTREAM_EVIDENCE_COMMIT = "d7c7d07add0d7407a5a3376d5fe4a97aee9112a0"
_BLOB_SNAPSHOT = frozenset({"vendored", "digest_only"})
_TREE_SNAPSHOT = frozenset({"directory_not_digestible"})


class LinkValidationError(ValueError):
    """``link_validation.json`` is missing required fields or has invalid values."""


def load_link_validation(path: Path) -> dict[str, Any]:
    """Parse and validate ``link_validation.json``; raise ``LinkValidationError`` on failure."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LinkValidationError(f"{path}: invalid JSON: {exc}") from exc
    try:
        validate_link_validation_document(data, source=str(path))
    except PreconditionError as exc:
        raise LinkValidationError(str(exc)) from exc
    return data


def upstream_artifact_entries(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Return UpstreamDrift artifact rows (entries that include a ``path`` field)."""
    links = data.get("links")
    if not isinstance(links, list):
        return []
    return [entry for entry in links if isinstance(entry, dict) and "path" in entry]


def validate_link_validation_document(
    data: object, *, source: str = "link_validation.json"
) -> None:
    require(isinstance(data, dict), f"{source}: root must be a JSON object", data)
    links = data.get("links")
    require(isinstance(links, list), f"{source}: links must be an array", links)
    gaps = data.get("network_only_gaps")
    require(
        isinstance(gaps, str) and gaps.strip(),
        f"{source}: network_only_gaps must be a non-empty string",
        gaps,
    )
    require("digest_only" in gaps, f"{source}: network_only_gaps must mention digest_only", gaps)
    require(
        "pending_network_stop" in gaps,
        f"{source}: network_only_gaps must mention pending_network_stop",
        gaps,
    )

    for index, entry in enumerate(links):
        prefix = f"{source}: links[{index}]"
        require(isinstance(entry, dict), f"{prefix} must be an object", entry)
        if "path" not in entry:
            continue
        _validate_upstream_artifact_entry(entry, prefix=prefix)


def _validate_upstream_artifact_entry(entry: dict[str, Any], *, prefix: str) -> None:
    require(
        entry.get("evidence_commit") == UPSTREAM_EVIDENCE_COMMIT,
        f"{prefix}: evidence_commit mismatch",
        entry,
    )
    kind = entry.get("kind")
    require(kind in {"blob", "tree"}, f"{prefix}: kind must be blob or tree", kind)
    status = entry.get("snapshot_status")
    if kind == "blob":
        digest = entry.get("content_sha256")
        require(
            isinstance(digest, str) and SHA256_RE.match(digest),
            f"{prefix}: content_sha256 required for blob",
            digest,
        )
        require(status in _BLOB_SNAPSHOT, f"{prefix}: invalid snapshot_status for blob", status)
        if status == "vendored":
            snap = entry.get("snapshot_path")
            require(
                isinstance(snap, str) and snap.strip(),
                f"{prefix}: snapshot_path required when vendored",
                snap,
            )
    else:
        require(
            entry.get("content_sha256") is None,
            f"{prefix}: tree entries must not have content_sha256",
            entry,
        )
        require(status in _TREE_SNAPSHOT, f"{prefix}: invalid snapshot_status for tree", status)
