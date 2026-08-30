"""Immutable records used by the programming-companion consumer."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Literal

from .errors import AcquisitionError

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
LOCK_VERSION = "affinedrift/upstreamdrift-companion-lock/v1"


def _canonical_json(payload: object) -> bytes:
    """Serialize a JSON record deterministically with one trailing newline."""
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def snapshot_tree_digest(manifest_sha256: str, schema_sha256: str) -> str:
    """Bind the names and SHA-256 values of both immutable snapshot files."""
    material = f"manifest.json\0{manifest_sha256}\nschema.json\0{schema_sha256}\n".encode()
    return hashlib.sha256(material).hexdigest()


@dataclass(frozen=True)
class ImportRequest:
    """Exact source and digest expectations for one acquisition attempt."""

    source_commit: str
    manifest_url: str
    manifest_sha256: str
    schema_url: str
    schema_sha256: str

    def validate_digests(self) -> None:
        """Require lowercase SHA-256 values and an exact Git commit."""
        if COMMIT_PATTERN.fullmatch(self.source_commit) is None:
            raise AcquisitionError("source commit must be an exact 40-hex commit")
        for label, value in (
            ("manifest", self.manifest_sha256),
            ("schema", self.schema_sha256),
        ):
            if SHA256_PATTERN.fullmatch(value) is None:
                raise AcquisitionError(f"{label} SHA-256 must contain 64 lowercase hex characters")


@dataclass(frozen=True)
class FetchResult:
    """One bounded transport result, including every observed redirect URL."""

    requested_url: str
    final_url: str
    redirects: tuple[str, ...]
    payload: bytes


@dataclass(frozen=True)
class LockRecord:
    """Deterministic authority pointer for an installed immutable snapshot."""

    repository: str
    source_commit: str
    manifest_url: str
    manifest_sha256: str
    manifest_bytes: int
    schema_url: str
    schema_sha256: str
    schema_bytes: int
    snapshot_id: str
    snapshot_tree_sha256: str
    publication_state: Literal["draft", "qualified"]
    lock_version: str = LOCK_VERSION

    def validate(self) -> None:
        """Reject malformed or internally inconsistent lock fields."""
        if self.lock_version != LOCK_VERSION:
            raise AcquisitionError("active lock version is unsupported")
        if COMMIT_PATTERN.fullmatch(self.source_commit) is None:
            raise AcquisitionError("active lock commit is malformed")
        for value in (self.manifest_sha256, self.schema_sha256, self.snapshot_tree_sha256):
            if SHA256_PATTERN.fullmatch(value) is None:
                raise AcquisitionError("active lock SHA-256 is malformed")
        expected_id = f"{self.source_commit}-{self.manifest_sha256[:16]}"
        if self.snapshot_id != expected_id:
            raise AcquisitionError("active lock snapshot ID is inconsistent")
        expected_tree = snapshot_tree_digest(self.manifest_sha256, self.schema_sha256)
        if self.snapshot_tree_sha256 != expected_tree:
            raise AcquisitionError("active lock snapshot tree digest is inconsistent")
        if self.manifest_bytes < 0 or self.schema_bytes < 0:
            raise AcquisitionError("active lock byte counts must be non-negative")
        if self.publication_state not in {"draft", "qualified"}:
            raise AcquisitionError("active lock publication state is unsupported")

    def as_dict(self) -> dict[str, object]:
        """Return the strict external lock representation."""
        return {
            "lock_version": self.lock_version,
            "provider": {"repository": self.repository, "commit": self.source_commit},
            "manifest": {
                "url": self.manifest_url,
                "sha256": self.manifest_sha256,
                "bytes": self.manifest_bytes,
            },
            "schema": {
                "url": self.schema_url,
                "sha256": self.schema_sha256,
                "bytes": self.schema_bytes,
            },
            "snapshot": {
                "id": self.snapshot_id,
                "tree_sha256": self.snapshot_tree_sha256,
            },
            "publication_state": self.publication_state,
        }

    def to_bytes(self) -> bytes:
        """Return canonical lock bytes."""
        return _canonical_json(self.as_dict())

    def matches(self, request: ImportRequest) -> bool:
        """Return whether a request addresses the exact active pin."""
        return (
            self.source_commit == request.source_commit
            and self.manifest_url == request.manifest_url
            and self.manifest_sha256 == request.manifest_sha256
            and self.schema_url == request.schema_url
            and self.schema_sha256 == request.schema_sha256
        )


@dataclass(frozen=True)
class ValidatedSnapshot:
    """Fully validated bytes ready for atomic installation."""

    manifest: bytes
    schema: bytes
    lock: LockRecord


@dataclass(frozen=True)
class ProvenanceRecord:
    """Read-only public view of the active provider authority."""

    repository: str
    source_commit: str
    manifest_sha256: str
    schema_sha256: str
    publication_state: Literal["draft", "qualified"]
    snapshot_id: str


@dataclass(frozen=True)
class UpdateReport:
    """Read-only comparison between an active pin and a validated candidate."""

    status: Literal["uninitialized", "same", "different"]
    active_manifest_sha256: str | None
    candidate_manifest_sha256: str
    candidate_commit: str
