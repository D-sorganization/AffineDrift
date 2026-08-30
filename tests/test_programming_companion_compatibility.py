"""Provider-consumer compatibility and schema version matrix tests (ISSUE-4030).

Validates that AffineDrift's companion consumer strictly enforces schema compatibility,
supports declared current and baseline v1.0.0 versions, fails closed on future/unsupported
versions, and guarantees rollback isolation without modifying active state.
"""

from __future__ import annotations

import hashlib
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

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "companion"
CURRENT_COMMIT = "6ff956a4df928d3ef7be241e3d06289b5ea7bb89"
BASELINE_COMMIT = "1af18489e8755933a0d189aa8edafe787fa94d0f"
PINNED_SCHEMA_PATH = Path("schemas/upstreamdrift-companion-v1.schema.json")
MANIFEST_PATH = "dist/companion/manifest.json"
SCHEMA_PATH = "docs/api/contracts/upstreamdrift-companion-v1.schema.json"


class MemoryTransport:
    """Return in-memory payloads for approved raw URLs."""

    def __init__(self, responses: dict[str, FetchResult | AcquisitionError]) -> None:
        self.responses = responses
        self.requested: list[str] = []

    def fetch(self, url: str, max_bytes: int) -> FetchResult:
        self.requested.append(url)
        res = self.responses.get(url)
        if res is None:
            raise AcquisitionError(f"unmocked URL: {url}")
        if isinstance(res, AcquisitionError):
            raise res
        if len(res.payload) > max_bytes:
            raise AcquisitionError("payload exceeds byte limit")
        return res


def _make_consumer_and_request(
    tmp_path: Path,
    manifest_bytes: bytes,
    commit: str,
    schema_bytes: bytes | None = None,
) -> tuple[CompanionConsumer, ImportRequest, MemoryTransport]:
    actual_schema = schema_bytes or PINNED_SCHEMA_PATH.read_bytes()
    manifest_url = (
        f"https://raw.githubusercontent.com/D-sorganization/UpstreamDrift/{commit}/{MANIFEST_PATH}"
    )
    schema_url = (
        f"https://raw.githubusercontent.com/D-sorganization/UpstreamDrift/{commit}/{SCHEMA_PATH}"
    )

    responses = {
        manifest_url: FetchResult(manifest_url, manifest_url, (), manifest_bytes),
        schema_url: FetchResult(schema_url, schema_url, (), actual_schema),
    }
    transport = MemoryTransport(responses)
    policy = ConsumerPolicy.upstreamdrift()
    store = SnapshotStore(tmp_path / "consumer")
    consumer = CompanionConsumer(policy, transport, store)
    request = ImportRequest(
        source_commit=commit,
        manifest_url=manifest_url,
        manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
        schema_url=schema_url,
        schema_sha256=hashlib.sha256(actual_schema).hexdigest(),
    )
    return consumer, request, transport


@pytest.mark.unit
def test_current_v1_manifest_fixture_installs_successfully(tmp_path: Path) -> None:
    """Current v1.0.0 manifest with workflows validates and installs cleanly."""
    manifest_bytes = (FIXTURES_DIR / "manifest_v1_0_0_current.json").read_bytes()
    consumer, request, _ = _make_consumer_and_request(tmp_path, manifest_bytes, CURRENT_COMMIT)

    lock = consumer.install(request)
    assert lock.source_commit == CURRENT_COMMIT
    assert lock.manifest_sha256 == request.manifest_sha256
    assert lock.publication_state == "draft"

    provenance = consumer.provenance()
    assert provenance.source_commit == CURRENT_COMMIT
    assert provenance.manifest_sha256 == request.manifest_sha256


@pytest.mark.unit
def test_baseline_v1_manifest_fixture_installs_successfully(tmp_path: Path) -> None:
    """Baseline foundation v1.0.0 manifest without workflows remains backward-compatible."""
    manifest_bytes = (FIXTURES_DIR / "manifest_v1_0_0_baseline.json").read_bytes()
    consumer, request, _ = _make_consumer_and_request(tmp_path, manifest_bytes, BASELINE_COMMIT)

    lock = consumer.install(request)
    assert lock.source_commit == BASELINE_COMMIT
    assert lock.manifest_sha256 == request.manifest_sha256
    assert lock.publication_state == "draft"


@pytest.mark.unit
def test_future_incompatible_v2_manifest_is_rejected_fail_closed(tmp_path: Path) -> None:
    """Future schema v2.0.0 is rejected by the v1 schema validator."""
    manifest_bytes = (FIXTURES_DIR / "manifest_incompatible_v2.json").read_bytes()
    consumer, request, _ = _make_consumer_and_request(tmp_path, manifest_bytes, CURRENT_COMMIT)

    with pytest.raises(AcquisitionError, match="schema violation|schema_version"):
        consumer.install(request)


@pytest.mark.unit
def test_corrupt_schema_id_manifest_is_rejected_fail_closed(tmp_path: Path) -> None:
    """Manifest referencing an unapproved schema ID is rejected."""
    manifest_bytes = (FIXTURES_DIR / "manifest_corrupt_id.json").read_bytes()
    consumer, request, _ = _make_consumer_and_request(tmp_path, manifest_bytes, CURRENT_COMMIT)

    with pytest.raises(AcquisitionError, match="schema violation|schema"):
        consumer.install(request)


@pytest.mark.unit
def test_failed_candidate_import_preserves_active_snapshot_atomically(tmp_path: Path) -> None:
    """If a candidate import fails verification, the active snapshot remains untouched."""
    current_bytes = (FIXTURES_DIR / "manifest_v1_0_0_current.json").read_bytes()
    consumer, valid_request, _ = _make_consumer_and_request(tmp_path, current_bytes, CURRENT_COMMIT)

    # Initial valid install
    original_lock = consumer.install(valid_request)
    active_tree_before = {
        p.relative_to(tmp_path): p.read_bytes()
        for p in (tmp_path / "consumer").rglob("*")
        if p.is_file()
    }

    # Attempt to install incompatible fixture
    incompatible_bytes = (FIXTURES_DIR / "manifest_incompatible_v2.json").read_bytes()
    candidate_consumer, invalid_request, _ = _make_consumer_and_request(
        tmp_path, incompatible_bytes, CURRENT_COMMIT
    )

    with pytest.raises(AcquisitionError):
        candidate_consumer.install(invalid_request)

    # State must be strictly identical
    active_tree_after = {
        p.relative_to(tmp_path): p.read_bytes()
        for p in (tmp_path / "consumer").rglob("*")
        if p.is_file()
    }
    assert active_tree_before == active_tree_after
    assert consumer.provenance().manifest_sha256 == original_lock.manifest_sha256


@pytest.mark.unit
def test_conflicting_commit_pin_replacement_is_refused_without_lock_sha(tmp_path: Path) -> None:
    """Replacing an active pin with a new commit requires the exact active lock digest."""
    current_bytes = (FIXTURES_DIR / "manifest_v1_0_0_current.json").read_bytes()
    baseline_bytes = (FIXTURES_DIR / "manifest_v1_0_0_baseline.json").read_bytes()

    consumer, valid_request, _ = _make_consumer_and_request(tmp_path, current_bytes, CURRENT_COMMIT)
    consumer.install(valid_request)

    # Candidate with different commit without specifying correct expected lock SHA
    candidate_consumer, candidate_request, _ = _make_consumer_and_request(
        tmp_path, baseline_bytes, BASELINE_COMMIT
    )

    with pytest.raises(ExistingPinConflict):
        candidate_consumer.install(candidate_request)
