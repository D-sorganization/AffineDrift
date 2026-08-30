"""Security and atomicity contracts for the immutable companion consumer."""

from __future__ import annotations

import copy
import hashlib
import json
import os
from dataclasses import replace
from pathlib import Path

import pytest

from src.affine_control.programming_companion import (
    AcquisitionError,
    CompanionConsumer,
    ConsumerPolicy,
    ExistingPinConflict,
    FetchResult,
    ImportRequest,
    SnapshotStore,
)

COMMIT = "1" * 40
OTHER_COMMIT = "2" * 40
REPOSITORY = "https://github.com/D-sorganization/UpstreamDrift"
SCHEMA_ID = "https://upstreamdrift.dev/schemas/upstreamdrift-companion-v1.schema.json"
MANIFEST_PATH = "dist/companion/manifest.json"
SCHEMA_PATH = "docs/api/contracts/upstreamdrift-companion-v1.schema.json"
PINNED_SCHEMA = Path("schemas/upstreamdrift-companion-v1.schema.json")
PINNED_SCHEMA_SHA256 = "39b8e54719f75aa428f2375d804ee29c458aa23b876a094aff802c48928b6702"
SCHEMA_PROVENANCE = Path("schemas/upstreamdrift-companion-v1.provenance.json")


def _canonical(payload: object) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def _manifest(commit: str = COMMIT) -> dict[str, object]:
    return {
        "$schema": SCHEMA_ID,
        "schema_version": "1.0.0",
        "manifest_id": "upstreamdrift-companion",
        "publication": {"state": "draft", "blockers": ["manufactured fixture"]},
        "source": {
            "repository": REPOSITORY,
            "commit": commit,
            "commit_timestamp": "2026-08-30T00:00:00Z",
            "package_version": "1.0.0",
            "generator": {"path": "scripts/export_companion.py", "version": "1.0.0"},
            "inputs": [{"path": "pyproject.toml", "sha256": "a" * 64}],
        },
        "providers": [],
        "registries": [],
        "compatibility": {
            "requires_python": ">=3.11",
            "supported_python_minors": ["3.11", "3.12"],
            "verification_command": {"executable": "python", "arguments": ["-m", "pytest"]},
        },
        "engines": [],
        "programs": [],
        "features": [],
        "documentation": [],
        "workflows": [],
        "screenshots": [],
        "summary": {
            "raw_launcher_records": 0,
            "local_model_records": 0,
            "program_records": 0,
            "feature_records": 0,
            "feature_surface_paths": 0,
            "workflow_records": 0,
            "executable_workflow_records": 0,
        },
    }


class MemoryTransport:
    """Return exact in-memory responses and record requested URLs."""

    def __init__(self, responses: dict[str, FetchResult | AcquisitionError]) -> None:
        self.responses = responses
        self.requested: list[str] = []

    def fetch(self, url: str, max_bytes: int) -> FetchResult:
        self.requested.append(url)
        result = self.responses[url]
        if isinstance(result, AcquisitionError):
            raise result
        if len(result.payload) > max_bytes:
            raise AcquisitionError("payload exceeds byte limit")
        return result


def _url(commit: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/D-sorganization/UpstreamDrift/{commit}/{path}"


def _setup(
    tmp_path: Path,
    *,
    manifest: dict[str, object] | None = None,
    manifest_url: str | None = None,
    schema_bytes: bytes | None = None,
    manifest_bytes: bytes | None = None,
    redirects: tuple[str, ...] = (),
) -> tuple[CompanionConsumer, ImportRequest, MemoryTransport]:
    actual_schema = schema_bytes or PINNED_SCHEMA.read_bytes()
    actual_manifest = manifest_bytes or _canonical(manifest or _manifest())
    selected_manifest_url = manifest_url or _url(COMMIT, MANIFEST_PATH)
    schema_url = _url(COMMIT, SCHEMA_PATH)
    responses = {
        selected_manifest_url: FetchResult(
            selected_manifest_url, selected_manifest_url, redirects, actual_manifest
        ),
        schema_url: FetchResult(schema_url, schema_url, (), actual_schema),
    }
    transport = MemoryTransport(responses)
    policy = ConsumerPolicy.upstreamdrift()
    consumer = CompanionConsumer(policy, transport, SnapshotStore(tmp_path / "consumer"))
    request = ImportRequest(
        source_commit=COMMIT,
        manifest_url=selected_manifest_url,
        manifest_sha256=hashlib.sha256(actual_manifest).hexdigest(),
        schema_url=schema_url,
        schema_sha256=hashlib.sha256(actual_schema).hexdigest(),
    )
    return consumer, request, transport


def _tree_bytes(root: Path) -> dict[str, bytes]:
    if not root.exists():
        return {}
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


@pytest.mark.unit
def test_provider_schema_is_exactly_pinned() -> None:
    assert hashlib.sha256(PINNED_SCHEMA.read_bytes()).hexdigest() == PINNED_SCHEMA_SHA256
    provenance = json.loads(SCHEMA_PROVENANCE.read_text(encoding="utf-8"))
    assert provenance["schema_sha256"] == PINNED_SCHEMA_SHA256
    assert provenance["source_commit"] == "6ff956a4df928d3ef7be241e3d06289b5ea7bb89"
    assert provenance["source_repository"] == REPOSITORY


@pytest.mark.unit
def test_mutable_manifest_url_is_rejected_before_fetch(tmp_path: Path) -> None:
    mutable = _url("main", MANIFEST_PATH)
    consumer, request, transport = _setup(tmp_path, manifest_url=mutable)

    with pytest.raises(AcquisitionError, match="exact 40-hex commit"):
        consumer.inspect(request)

    assert transport.requested == []


@pytest.mark.unit
@pytest.mark.parametrize("field", ["manifest_sha256", "schema_sha256"])
def test_wrong_payload_digest_fails_without_writes(tmp_path: Path, field: str) -> None:
    consumer, request, _ = _setup(tmp_path)
    request = replace(request, **{field: "0" * 64})

    with pytest.raises(AcquisitionError, match="SHA-256"):
        consumer.install(request)

    assert _tree_bytes(tmp_path / "consumer") == {}


@pytest.mark.unit
def test_embedded_commit_must_match_requested_commit(tmp_path: Path) -> None:
    consumer, request, _ = _setup(tmp_path, manifest=_manifest(OTHER_COMMIT))

    with pytest.raises(AcquisitionError, match="embedded source commit"):
        consumer.install(request)


@pytest.mark.unit
def test_provider_repository_must_match_allowlist(tmp_path: Path) -> None:
    manifest = _manifest()
    source = manifest["source"]
    assert isinstance(source, dict)
    source["repository"] = "https://github.com/attacker/UpstreamDrift"
    consumer, request, _ = _setup(tmp_path, manifest=manifest)

    with pytest.raises(AcquisitionError, match="provider repository"):
        consumer.install(request)


@pytest.mark.unit
def test_redirect_escape_is_rejected(tmp_path: Path) -> None:
    escaped = "https://evil.example/payload.json"
    consumer, request, _ = _setup(tmp_path, redirects=(escaped,))

    with pytest.raises(AcquisitionError, match="allowlisted host"):
        consumer.install(request)


@pytest.mark.unit
@pytest.mark.parametrize("unsafe_path", ["../secrets.txt", "a/./b", "a//b", "C:/secret"])
def test_manifest_repository_path_traversal_is_rejected(tmp_path: Path, unsafe_path: str) -> None:
    manifest = _manifest()
    source = manifest["source"]
    assert isinstance(source, dict)
    generator = source["generator"]
    assert isinstance(generator, dict)
    generator["path"] = unsafe_path
    consumer, request, _ = _setup(tmp_path, manifest=manifest)

    with pytest.raises(AcquisitionError, match="repository path"):
        consumer.install(request)


@pytest.mark.unit
def test_duplicate_manifest_keys_are_rejected(tmp_path: Path) -> None:
    payload = _canonical(_manifest()).replace(
        b'{\n  "$schema"', b'{\n  "schema_version": "1.0.0",\n  "$schema"', 1
    )
    consumer, request, _ = _setup(tmp_path, manifest_bytes=payload)

    with pytest.raises(AcquisitionError, match="duplicate JSON key"):
        consumer.install(request)


@pytest.mark.unit
def test_schema_with_wrong_identity_is_rejected_even_when_digest_matches(tmp_path: Path) -> None:
    schema = json.loads(PINNED_SCHEMA.read_text(encoding="utf-8"))
    schema["$id"] = "https://evil.example/schema.json"
    consumer, request, _ = _setup(tmp_path, schema_bytes=_canonical(schema))

    with pytest.raises(AcquisitionError, match="schema ID"):
        consumer.install(request)


@pytest.mark.unit
def test_oversized_content_fails_before_store_write(tmp_path: Path) -> None:
    policy = replace(ConsumerPolicy.upstreamdrift(), max_payload_bytes=100)
    consumer, request, transport = _setup(tmp_path)
    consumer = CompanionConsumer(policy, transport, SnapshotStore(tmp_path / "consumer"))

    with pytest.raises(AcquisitionError, match="byte limit"):
        consumer.install(request)

    assert _tree_bytes(tmp_path / "consumer") == {}


@pytest.mark.unit
def test_existing_pin_conflict_preserves_all_bytes(tmp_path: Path) -> None:
    consumer, request, _ = _setup(tmp_path)
    consumer.install(request)
    before = _tree_bytes(tmp_path / "consumer")
    second_consumer, second_request, _ = _setup(tmp_path, manifest=_manifest(OTHER_COMMIT))
    second_request = replace(
        second_request,
        source_commit=OTHER_COMMIT,
        manifest_url=_url(OTHER_COMMIT, MANIFEST_PATH),
        schema_url=_url(OTHER_COMMIT, SCHEMA_PATH),
    )

    with pytest.raises(ExistingPinConflict):
        second_consumer.install(second_request)

    assert _tree_bytes(tmp_path / "consumer") == before


@pytest.mark.unit
def test_partial_atomic_install_failure_rolls_back_every_byte(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    consumer, request, _ = _setup(tmp_path)
    before = _tree_bytes(tmp_path / "consumer")
    real_replace = os.replace
    calls = 0

    def fail_lock_replace(source: str | Path, target: str | Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("manufactured lock replacement failure")
        real_replace(source, target)

    monkeypatch.setattr(
        "src.affine_control.programming_companion.store.os.replace", fail_lock_replace
    )
    with pytest.raises(OSError, match="manufactured"):
        consumer.install(request)

    assert _tree_bytes(tmp_path / "consumer") == before


@pytest.mark.unit
def test_valid_install_is_deterministic_idempotent_and_exposes_provenance(tmp_path: Path) -> None:
    consumer, request, _ = _setup(tmp_path)
    first = consumer.install(request)
    first_bytes = _tree_bytes(tmp_path / "consumer")
    second = consumer.install(request)

    assert first == second
    assert _tree_bytes(tmp_path / "consumer") == first_bytes
    provenance = consumer.provenance()
    assert provenance.source_commit == COMMIT
    assert provenance.repository == REPOSITORY
    assert provenance.manifest_sha256 == request.manifest_sha256
    assert provenance.schema_sha256 == request.schema_sha256
    assert provenance.publication_state == "draft"


@pytest.mark.unit
def test_update_check_is_read_only_and_reports_candidate_difference(tmp_path: Path) -> None:
    consumer, request, _ = _setup(tmp_path)
    consumer.install(request)
    before = _tree_bytes(tmp_path / "consumer")
    manifest = copy.deepcopy(_manifest())
    manifest["publication"] = {"state": "qualified", "blockers": []}
    candidate_consumer, candidate_request, _ = _setup(tmp_path, manifest=manifest)

    report = candidate_consumer.check_update(candidate_request)

    assert report.status == "different"
    assert report.active_manifest_sha256 == request.manifest_sha256
    assert report.candidate_manifest_sha256 == candidate_request.manifest_sha256
    assert _tree_bytes(tmp_path / "consumer") == before


@pytest.mark.unit
def test_partial_download_failure_never_creates_store_bytes(tmp_path: Path) -> None:
    consumer, request, transport = _setup(tmp_path)
    transport.responses[request.schema_url] = AcquisitionError("manufactured schema outage")

    with pytest.raises(AcquisitionError, match="schema outage"):
        consumer.install(request)

    assert transport.requested == [request.manifest_url, request.schema_url]
    assert _tree_bytes(tmp_path / "consumer") == {}


@pytest.mark.unit
def test_provenance_rejects_mutated_active_snapshot(tmp_path: Path) -> None:
    consumer, request, _ = _setup(tmp_path)
    lock = consumer.install(request)
    manifest_path = tmp_path / "consumer" / "snapshots" / lock.snapshot_id / "manifest.json"
    manifest_path.write_bytes(b"{}\n")

    with pytest.raises(AcquisitionError, match="digest|bytes"):
        consumer.provenance()


@pytest.mark.unit
def test_explicit_pin_replacement_requires_exact_active_lock_digest(tmp_path: Path) -> None:
    consumer, request, _ = _setup(tmp_path)
    consumer.install(request)
    before = _tree_bytes(tmp_path / "consumer")
    manifest = copy.deepcopy(_manifest())
    manifest["publication"] = {"state": "qualified", "blockers": []}
    candidate_consumer, candidate_request, transport = _setup(tmp_path, manifest=manifest)

    with pytest.raises(ExistingPinConflict, match="active lock SHA-256"):
        candidate_consumer.replace_pin(candidate_request, "0" * 64)

    assert transport.requested == []
    assert _tree_bytes(tmp_path / "consumer") == before


@pytest.mark.unit
def test_explicit_pin_replacement_is_atomic_and_retains_prior_snapshot(tmp_path: Path) -> None:
    consumer, request, _ = _setup(tmp_path)
    original = consumer.install(request)
    lock_path = tmp_path / "consumer" / "active-lock.json"
    expected_lock_sha256 = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    manifest = copy.deepcopy(_manifest())
    manifest["publication"] = {"state": "qualified", "blockers": []}
    candidate_consumer, candidate_request, _ = _setup(tmp_path, manifest=manifest)

    replacement = candidate_consumer.replace_pin(candidate_request, expected_lock_sha256)

    assert replacement.manifest_sha256 == candidate_request.manifest_sha256
    assert replacement.snapshot_id != original.snapshot_id
    snapshots = tmp_path / "consumer" / "snapshots"
    assert (snapshots / original.snapshot_id).is_dir()
    assert (snapshots / replacement.snapshot_id).is_dir()
    assert candidate_consumer.provenance().publication_state == "qualified"
