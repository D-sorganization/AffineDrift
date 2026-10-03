"""Local research adapter over existing public transport and atomic snapshot storage."""

import hashlib
from pathlib import Path

from src.affine_control.programming_companion import (
    ConsumerPolicy,
    ImportRequest,
    SnapshotStore,
    Transport,
)
from src.affine_control.programming_companion.models import (
    LockRecord,
    ValidatedSnapshot,
    snapshot_tree_digest,
)

from .admission import SCHEMA_ID, admit_package, validate_research_schema
from .models import MAX_BYTES, HistoricalResearchPackage, ResearchImportPins

NAMESPACE = "historical-player-research-v1"
PROVIDER = "https://github.com/D-sorganization/UpstreamDrift"


class HistoricalResearchConsumer:
    """Acquire JSON only in a distinct local namespace; never attest a public release."""

    def __init__(self, policy: ConsumerPolicy, transport: Transport, storage_root: Path) -> None:
        """Bind reviewed pins and reject mutable/unsafe storage before any acquisition."""
        if policy.repository_url != PROVIDER or policy.schema_id != SCHEMA_ID:
            raise ValueError("Historical research requires its own provider/schema boundary")
        if not isinstance(storage_root, Path):
            raise TypeError("Research storage root must be a pathlib.Path")
        self._safe_root(storage_root)
        self._policy, self._transport = policy, transport
        self._root = storage_root / NAMESPACE
        self._store = SnapshotStore(self._root)

    @staticmethod
    def _safe_root(root: Path) -> None:
        """Reject symlink and junction ancestors before accessing local storage."""
        for item in (root, *root.parents):
            if item.is_symlink() or item.is_junction():
                raise ValueError("Research storage cannot contain symlinks or junctions")

    def _fetch(self, pins: ResearchImportPins) -> tuple[HistoricalResearchPackage, bytes]:
        """Fetch exact pinned JSON bytes and admit the independent schema and package."""
        request = pins.request
        self._policy.validate_request(request)
        values: list[bytes] = []
        for url, digest, size in [
            (request.manifest_url, request.manifest_sha256, pins.manifest_bytes),
            (request.schema_url, request.schema_sha256, pins.schema_bytes),
        ]:
            result = self._transport.fetch(url, min(MAX_BYTES, self._policy.max_payload_bytes))
            if result.requested_url != url or result.final_url != url or result.redirects:
                raise ValueError("Historical research transport redirected its immutable pin")
            if not 0 < len(result.payload) <= min(MAX_BYTES, self._policy.max_payload_bytes):
                raise ValueError("Historical research transport exceeded its byte bound")
            if len(result.payload) != size:
                raise ValueError("Research payload differs from its reviewed byte-size pin")
            if hashlib.sha256(result.payload).hexdigest() != digest:
                raise ValueError("Historical research payload differs from its reviewed hash")
            values.append(result.payload)
        manifest, schema = values
        validate_research_schema(schema)
        package = admit_package(
            manifest,
            request.manifest_sha256,
            len(manifest),
            request.source_commit,
        )
        return package, schema

    def inspect(self, pins: ResearchImportPins) -> HistoricalResearchPackage:
        """Validate hash-bound candidate bytes without writing the store."""
        package, _ = self._fetch(pins)
        return package

    def install(self, pins: ResearchImportPins) -> LockRecord:
        """Use shared atomic storage with draft envelope; no implicit pin replacement."""
        request = pins.request
        snapshot_id = f"{request.source_commit}-{request.manifest_sha256[:16]}"
        self._safe_root(self._root / "snapshots" / snapshot_id)
        self._store.reject_conflicting_request(request)
        package, schema = self._fetch(pins)
        tree = snapshot_tree_digest(request.manifest_sha256, request.schema_sha256)
        lock = LockRecord(
            "D-sorganization/UpstreamDrift",
            request.source_commit,
            request.manifest_url,
            request.manifest_sha256,
            len(package.manifest_bytes),
            request.schema_url,
            request.schema_sha256,
            len(schema),
            snapshot_id,
            tree,
            "draft",
        )
        lock.validate()
        return self._store.install(ValidatedSnapshot(package.manifest_bytes, schema, lock))

    def recall(self) -> HistoricalResearchPackage:
        """Recheck stored bytes and current supported schema before local presentation."""
        self._safe_root(self._root)
        lock = self._store.active_lock()
        if lock is None or lock.publication_state != "draft":
            raise ValueError("No local draft historical research pin is available")
        if lock.repository != "D-sorganization/UpstreamDrift":
            raise ValueError("Stored research provider differs from the supported provider")
        self._policy.validate_request(
            ImportRequest(
                lock.source_commit,
                lock.manifest_url,
                lock.manifest_sha256,
                lock.schema_url,
                lock.schema_sha256,
            )
        )
        self._safe_root(self._root / "snapshots" / lock.snapshot_id)
        payloads = self._store.snapshot_bytes(lock)
        validate_research_schema(payloads["schema.json"])
        return admit_package(
            payloads["manifest.json"],
            lock.manifest_sha256,
            lock.manifest_bytes,
            lock.source_commit,
        )
