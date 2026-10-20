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
    if not isinstance(data, dict):
        return
    links = data.get("links")
    require(isinstance(links, list), f"{source}: links must be an array", links)
    if not isinstance(links, list):
        return
    gaps = data.get("network_only_gaps")
    gaps_text = gaps.strip() if isinstance(gaps, str) else ""
    require(
        bool(gaps_text),
        f"{source}: network_only_gaps must be a non-empty string",
        gaps,
    )
    require(
        "digest_only" in gaps_text,
        f"{source}: network_only_gaps must mention digest_only",
        gaps,
    )
    require(
        "pending_network_stop" in gaps_text,
        f"{source}: network_only_gaps must mention pending_network_stop",
        gaps,
    )

    for index, entry in enumerate(links):
        prefix = f"{source}: links[{index}]"
        require(isinstance(entry, dict), f"{prefix} must be an object", entry)
        if not isinstance(entry, dict) or "path" not in entry:
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
        digest_ok = isinstance(digest, str) and SHA256_RE.fullmatch(digest) is not None
        require(digest_ok, f"{prefix}: content_sha256 required for blob", digest)
        require(status in _BLOB_SNAPSHOT, f"{prefix}: invalid snapshot_status for blob", status)
        if status == "vendored":
            snap = entry.get("snapshot_path")
            snap_ok = isinstance(snap, str) and bool(snap.strip())
            require(snap_ok, f"{prefix}: snapshot_path required when vendored", snap)
    else:
        require(
            entry.get("content_sha256") is None,
            f"{prefix}: tree entries must not have content_sha256",
            entry,
        )
        require(status in _TREE_SNAPSHOT, f"{prefix}: invalid snapshot_status for tree", status)
