"""Atomic immutable snapshot storage for the programming companion."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, cast

from .errors import AcquisitionError, ExistingPinConflict
from .models import ImportRequest, LockRecord, ValidatedSnapshot

ACTIVE_LOCK_NAME = "active-lock.json"
SNAPSHOTS_NAME = "snapshots"
SNAPSHOT_FILES = frozenset({"manifest.json", "schema.json"})


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Build a lock mapping while rejecting ambiguous duplicate keys."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise AcquisitionError(f"duplicate JSON key in active lock: {key}")
        result[key] = value
    return result


def _load_lock(payload: bytes) -> LockRecord:
    """Parse and validate canonical active-lock bytes."""
    try:
        record = json.loads(payload.decode(), object_pairs_hook=_reject_duplicate_keys)
        if not isinstance(record, dict):
            raise AcquisitionError("active lock must be a JSON object")
        if set(record) != {
            "lock_version",
            "provider",
            "manifest",
            "schema",
            "snapshot",
            "publication_state",
        }:
            raise AcquisitionError("active lock has missing or extra fields")
        provider = _strict_mapping(record["provider"], {"repository", "commit"}, "provider")
        manifest = _strict_mapping(record["manifest"], {"url", "sha256", "bytes"}, "manifest")
        schema = _strict_mapping(record["schema"], {"url", "sha256", "bytes"}, "schema")
        snapshot = _strict_mapping(record["snapshot"], {"id", "tree_sha256"}, "snapshot")
        lock = LockRecord(
            repository=str(provider["repository"]),
            source_commit=str(provider["commit"]),
            manifest_url=str(manifest["url"]),
            manifest_sha256=str(manifest["sha256"]),
            manifest_bytes=int(manifest["bytes"]),
            schema_url=str(schema["url"]),
            schema_sha256=str(schema["sha256"]),
            schema_bytes=int(schema["bytes"]),
            snapshot_id=str(snapshot["id"]),
            snapshot_tree_sha256=str(snapshot["tree_sha256"]),
            publication_state=record["publication_state"],
            lock_version=str(record["lock_version"]),
        )
        lock.validate()
        if lock.to_bytes() != payload:
            raise AcquisitionError("active lock bytes are not canonical")
        return lock
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise AcquisitionError(f"invalid active lock: {exc}") from exc


def _strict_mapping(value: object, keys: set[str], label: str) -> dict[str, Any]:
    """Require one lock mapping to contain exactly its declared keys."""
    if not isinstance(value, dict) or set(value) != keys:
        raise AcquisitionError(f"active lock {label} has missing or extra fields")
    return cast(dict[str, Any], value)


class SnapshotStore:
    """Store one active lock and content-addressed immutable snapshots."""

    def __init__(self, root: Path) -> None:
        """Configure a store rooted at an explicit filesystem path."""
        if not isinstance(root, Path):
            raise TypeError("root must be a pathlib.Path")
        self._root = root

    def active_lock(self) -> LockRecord | None:
        """Load the active lock without mutating storage."""
        lock_path = self._root / ACTIVE_LOCK_NAME
        if not lock_path.exists():
            return None
        if lock_path.is_symlink() or not lock_path.is_file():
            raise AcquisitionError("active lock must be a regular non-symlink file")
        lock = _load_lock(lock_path.read_bytes())
        return lock

    def require_active_digest(self, expected_sha256: str) -> LockRecord:
        """Require an exact active-lock byte digest for explicit replacement."""
        active = self.active_lock()
        if active is None:
            raise ExistingPinConflict("no active immutable pin exists to replace")
        actual = hashlib.sha256(active.to_bytes()).hexdigest()
        if actual != expected_sha256:
            raise ExistingPinConflict("active lock SHA-256 does not match replacement precondition")
        return active

    def reject_conflicting_request(self, request: ImportRequest) -> None:
        """Reject a candidate that would silently replace the active pin."""
        active = self.active_lock()
        if active is not None and not active.matches(request):
            raise ExistingPinConflict(
                "active immutable pin differs; explicit replacement is required"
            )

    def install(self, snapshot: ValidatedSnapshot) -> LockRecord:
        """Atomically install validated bytes, or return an exact existing pin."""
        active = self.active_lock()
        if active is not None:
            if active.to_bytes() != snapshot.lock.to_bytes():
                raise ExistingPinConflict("active immutable pin differs")
            self._verify_snapshot(snapshot)
            return active
        return self._install_new(snapshot)

    def replace(self, snapshot: ValidatedSnapshot, expected_sha256: str) -> LockRecord:
        """Atomically move the active pointer after an optimistic digest check."""
        active = self.require_active_digest(expected_sha256)
        if active.to_bytes() == snapshot.lock.to_bytes():
            self._verify_snapshot(snapshot)
            return active
        installed_target = self._prepare_snapshot(snapshot)
        try:
            self._replace_lock(snapshot.lock.to_bytes())
        except Exception:
            if installed_target:
                shutil.rmtree(self._snapshot_path(snapshot.lock.snapshot_id))
            raise
        return snapshot.lock

    def snapshot_bytes(self, lock: LockRecord) -> dict[str, bytes]:
        """Read and verify the two regular files addressed by a lock."""
        target = self._snapshot_path(lock.snapshot_id)
        if target.is_symlink() or not target.is_dir():
            raise AcquisitionError("active snapshot directory is missing or unsafe")
        files = {path.name for path in target.iterdir() if path.is_file()}
        if files != SNAPSHOT_FILES or any(path.is_symlink() for path in target.iterdir()):
            raise AcquisitionError("active snapshot has missing, extra, or symlinked entries")
        payloads = {name: (target / name).read_bytes() for name in sorted(SNAPSHOT_FILES)}
        manifest = payloads["manifest.json"]
        schema = payloads["schema.json"]
        if len(manifest) != lock.manifest_bytes or len(schema) != lock.schema_bytes:
            raise AcquisitionError("active snapshot bytes count does not match its lock")
        if hashlib.sha256(manifest).hexdigest() != lock.manifest_sha256:
            raise AcquisitionError("active snapshot manifest digest does not match its lock")
        if hashlib.sha256(schema).hexdigest() != lock.schema_sha256:
            raise AcquisitionError("active snapshot schema digest does not match its lock")
        return payloads

    def _verify_snapshot(self, snapshot: ValidatedSnapshot) -> None:
        """Require stored bytes to equal a validated candidate exactly."""
        actual = self.snapshot_bytes(snapshot.lock)
        expected = {"manifest.json": snapshot.manifest, "schema.json": snapshot.schema}
        if actual != expected:
            raise ExistingPinConflict("active snapshot bytes conflict with the requested pin")

    def _snapshot_path(self, snapshot_id: str) -> Path:
        """Resolve one safe content-addressed snapshot directory."""
        if not snapshot_id or any(char not in "0123456789abcdef-" for char in snapshot_id):
            raise AcquisitionError("snapshot ID is unsafe")
        return self._root / SNAPSHOTS_NAME / snapshot_id

    def _install_new(self, snapshot: ValidatedSnapshot) -> LockRecord:
        """Install the first active lock with rollback on pointer failure."""
        self._root.mkdir(parents=True, exist_ok=True)
        snapshots_root = self._root / SNAPSHOTS_NAME
        snapshots_root.mkdir(exist_ok=True)
        installed_target = self._prepare_snapshot(snapshot)
        try:
            self._replace_lock(snapshot.lock.to_bytes())
        except Exception:
            if installed_target:
                shutil.rmtree(self._snapshot_path(snapshot.lock.snapshot_id))
            self._remove_empty_directories(snapshots_root)
            raise
        return snapshot.lock

    def _prepare_snapshot(self, snapshot: ValidatedSnapshot) -> bool:
        """Verify an existing snapshot or stage a new immutable directory."""
        target = self._snapshot_path(snapshot.lock.snapshot_id)
        if target.exists():
            self._verify_snapshot(snapshot)
            return False
        return self._stage_snapshot(snapshot, target)

    def _stage_snapshot(self, snapshot: ValidatedSnapshot, target: Path) -> bool:
        """Write both payloads to staging before one directory rename."""
        staging = Path(tempfile.mkdtemp(prefix=".snapshot-", dir=self._root))
        try:
            (staging / "manifest.json").write_bytes(snapshot.manifest)
            (staging / "schema.json").write_bytes(snapshot.schema)
            os.replace(staging, target)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
        return True

    def _replace_lock(self, lock_bytes: bytes) -> None:
        """Durably write canonical lock bytes before replacing the pointer."""
        descriptor, raw_path = tempfile.mkstemp(prefix=".lock-", dir=self._root)
        temporary = Path(raw_path)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(lock_bytes)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self._root / ACTIVE_LOCK_NAME)
        finally:
            temporary.unlink(missing_ok=True)

    def _remove_empty_directories(self, snapshots_root: Path) -> None:
        """Remove only empty directories created by a failed first install."""
        if snapshots_root.exists() and not any(snapshots_root.iterdir()):
            snapshots_root.rmdir()
        if self._root.exists() and not any(self._root.iterdir()):
            self._root.rmdir()
