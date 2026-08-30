"""High-level immutable companion acquisition and provenance API."""

from __future__ import annotations

from typing import Literal

from .errors import AcquisitionError
from .models import (
    ImportRequest,
    LockRecord,
    ProvenanceRecord,
    UpdateReport,
    ValidatedSnapshot,
)
from .policy import ConsumerPolicy
from .store import SnapshotStore
from .transport import Transport
from .validation import validate_downloads


class CompanionConsumer:
    """Coordinate transport, validation, storage, and read-only inspection."""

    def __init__(self, policy: ConsumerPolicy, transport: Transport, store: SnapshotStore) -> None:
        self._policy = policy
        self._transport = transport
        self._store = store

    def inspect(self, request: ImportRequest) -> ValidatedSnapshot:
        """Download and fully validate a candidate without writing any bytes."""
        self._policy.validate_request(request)
        manifest = self._transport.fetch(request.manifest_url, self._policy.max_payload_bytes)
        schema = self._transport.fetch(request.schema_url, self._policy.max_payload_bytes)
        return validate_downloads(request, self._policy, manifest, schema)

    def install(self, request: ImportRequest) -> LockRecord:
        """Validate and atomically install an exact pin without implicit replacement."""
        self._policy.validate_request(request)
        self._store.reject_conflicting_request(request)
        return self._store.install(self.inspect(request))

    def check_update(self, request: ImportRequest) -> UpdateReport:
        """Validate a candidate and compare it without mutating the active pin."""
        candidate = self.inspect(request)
        active = self._store.active_lock()
        if active is None:
            status: Literal["uninitialized", "same", "different"] = "uninitialized"
            active_digest = None
        else:
            status = "same" if active.to_bytes() == candidate.lock.to_bytes() else "different"
            active_digest = active.manifest_sha256
        return UpdateReport(
            status=status,
            active_manifest_sha256=active_digest,
            candidate_manifest_sha256=candidate.lock.manifest_sha256,
            candidate_commit=candidate.lock.source_commit,
        )

    def replace_pin(self, request: ImportRequest, expected_active_lock_sha256: str) -> LockRecord:
        """Explicitly replace a pin guarded by the exact active-lock digest."""
        self._policy.validate_request(request)
        self._store.require_active_digest(expected_active_lock_sha256)
        candidate = self.inspect(request)
        return self._store.replace(candidate, expected_active_lock_sha256)

    def provenance(self) -> ProvenanceRecord:
        """Return verified provenance for the active snapshot."""
        active = self._store.active_lock()
        if active is None:
            raise AcquisitionError("no active programming-companion pin exists")
        self._store.snapshot_bytes(active)
        return ProvenanceRecord(
            repository=active.repository,
            source_commit=active.source_commit,
            manifest_sha256=active.manifest_sha256,
            schema_sha256=active.schema_sha256,
            publication_state=active.publication_state,
            snapshot_id=active.snapshot_id,
        )
