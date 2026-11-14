"""Contracts for installing the provider-published companion artifact (#4123 Phase 1).

UpstreamDrift ships ``upstreamdrift-companion-<sha>`` as an attested GitHub
Actions artifact rather than a raw ``dist/companion`` path. These tests build a
bundle from the pinned schema and the fixture manifest and drive the same
install path the CLI uses.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts import install_programming_companion as cli
from src.affine_control.programming_companion import (
    AcquisitionError,
    ConsumerPolicy,
    DirectoryTransport,
    SnapshotStore,
)

PINNED_SCHEMA = Path("schemas/upstreamdrift-companion-v1.schema.json")
POLICY = ConsumerPolicy.upstreamdrift_actions_artifact()
REPO_ROOT = Path(__file__).resolve().parents[1]


def _active_manifest_bytes() -> bytes:
    """Use the committed active pin manifest so artifact-install tests track the live schema."""
    lock = json.loads((REPO_ROOT / "data/companion/active-lock.json").read_text(encoding="utf-8"))
    snap = REPO_ROOT / "data/companion/snapshots" / str(lock["snapshot"]["id"]) / "manifest.json"
    return snap.read_bytes()


def _write_bundle(root: Path, manifest_bytes: bytes | None = None) -> tuple[Path, str]:
    """Write a bundle shaped like the published artifact and return (dir, commit)."""
    payload = manifest_bytes or _active_manifest_bytes()
    manifest = json.loads(payload)
    commit = str(manifest["source"]["commit"])
    bundle = root / "bundle"
    bundle.mkdir(parents=True)
    files = {POLICY.manifest_path: payload, POLICY.schema_path: PINNED_SCHEMA.read_bytes()}
    for name, data in files.items():
        (bundle / name).write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        (bundle / f"{name}.sha256").write_text(f"{digest}  {name}\n", encoding="utf-8")
    return bundle, commit


def _args(bundle: Path, commit: str, store: Path, *extra: str) -> cli.argparse.Namespace:
    return cli.parse_args(
        [
            "--source",
            str(bundle),
            "--commit",
            commit,
            "--store",
            str(store),
            "--skip-attestation",
            "--fetched-on",
            "2026-09-03",
            *extra,
        ]
    )


@pytest.mark.unit
def test_artifact_policy_addresses_the_named_artifact_by_exact_commit() -> None:
    commit = "a" * 40
    url = POLICY.object_url(commit, POLICY.manifest_path)
    assert url == (
        "https://github.com/D-sorganization/UpstreamDrift/actions/artifacts/"
        f"upstreamdrift-companion-{commit}/upstreamdrift-companion.v1.json"
    )
    POLICY.validate_url(url, commit, POLICY.manifest_path)
    with pytest.raises(AcquisitionError):
        POLICY.validate_url(url.replace(commit, "b" * 40), commit, POLICY.manifest_path)
    with pytest.raises(AcquisitionError):
        POLICY.object_url(commit, "../escape.json")
    # The raw-object policy is unchanged.
    raw = ConsumerPolicy.upstreamdrift()
    assert raw.object_url(commit, raw.manifest_path) == (
        f"https://raw.githubusercontent.com/D-sorganization/UpstreamDrift/{commit}/"
        "dist/companion/manifest.json"
    )


@pytest.mark.unit
def test_directory_transport_serves_only_flat_bounded_regular_files(tmp_path: Path) -> None:
    bundle, commit = _write_bundle(tmp_path)
    prefix = POLICY.object_url(commit, POLICY.manifest_path)[: -len(POLICY.manifest_path)]
    transport = DirectoryTransport(bundle, prefix)
    result = transport.fetch(prefix + POLICY.schema_path, 5_000_000)
    assert result.payload == PINNED_SCHEMA.read_bytes()
    assert result.redirects == ()
    with pytest.raises(AcquisitionError, match="byte limit"):
        transport.fetch(prefix + POLICY.schema_path, 10)
    with pytest.raises(AcquisitionError, match="prefix"):
        transport.fetch("https://example.com/" + POLICY.schema_path, 5_000_000)
    with pytest.raises(AcquisitionError, match="single file"):
        transport.fetch(prefix + "nested/" + POLICY.schema_path, 5_000_000)
    with pytest.raises(AcquisitionError, match="missing"):
        transport.fetch(prefix + "absent.json", 5_000_000)
    with pytest.raises(AcquisitionError):
        DirectoryTransport(tmp_path / "nope", prefix)


@pytest.mark.unit
def test_sidecar_digests_must_describe_their_file(tmp_path: Path) -> None:
    bundle, _ = _write_bundle(tmp_path)
    name = POLICY.manifest_path
    expected = hashlib.sha256((bundle / name).read_bytes()).hexdigest()
    assert cli.read_sidecar_digest(bundle, name) == expected
    (bundle / f"{name}.sha256").write_text(f"{expected}  other.json\n", encoding="utf-8")
    with pytest.raises(AcquisitionError, match="does not describe"):
        cli.read_sidecar_digest(bundle, name)
    (bundle / f"{name}.sha256").unlink()
    with pytest.raises(AcquisitionError, match="sidecar"):
        cli.read_sidecar_digest(bundle, name)


@pytest.mark.unit
def test_install_writes_lock_snapshot_and_acquisition_receipt(tmp_path: Path) -> None:
    bundle, commit = _write_bundle(tmp_path)
    store = tmp_path / "store"
    assert (
        cli.main(
            [
                "--source",
                str(bundle),
                "--commit",
                commit,
                "--store",
                str(store),
                "--skip-attestation",
                "--fetched-on",
                "2026-09-03",
                "--artifact-id",
                "42",
                "--run-id",
                "7",
            ]
        )
        == 0
    )
    lock = SnapshotStore(store).active_lock()
    assert lock is not None
    assert lock.source_commit == commit
    active_manifest = _active_manifest_bytes()
    assert lock.manifest_sha256 == hashlib.sha256(active_manifest).hexdigest()
    assert lock.manifest_url == POLICY.object_url(commit, POLICY.manifest_path)
    payloads = SnapshotStore(store).snapshot_bytes(lock)
    assert payloads["manifest.json"] == active_manifest
    receipt = json.loads((store / "acquisition.json").read_text(encoding="utf-8"))
    assert receipt["schema_version"] == cli.ACQUISITION_SCHEMA
    assert receipt["artifact_name"] == f"upstreamdrift-companion-{commit}"
    assert receipt["artifact_id"] == 42 and receipt["workflow_run_id"] == 7
    assert receipt["attestation"] == "skipped"
    assert receipt["fetched_on"] == "2026-09-03"
    assert receipt["bundle_files_sha256"][POLICY.manifest_path] == lock.manifest_sha256
    # Re-installing the identical pin is idempotent.
    assert cli.install(_args(bundle, commit, store), bundle, commit) == 0


@pytest.mark.unit
def test_install_fails_closed_on_tampered_bytes_and_wrong_commit(tmp_path: Path) -> None:
    bundle, commit = _write_bundle(tmp_path)
    store = tmp_path / "store"
    assert (
        cli.main(
            [
                "--source",
                str(bundle),
                "--commit",
                "f" * 40,
                "--store",
                str(store),
                "--skip-attestation",
            ]
        )
        == 1
    )
    assert not store.exists()
    (bundle / POLICY.manifest_path).write_bytes(b"{}")
    assert (
        cli.main(
            [
                "--source",
                str(bundle),
                "--commit",
                commit,
                "--store",
                str(store),
                "--skip-attestation",
            ]
        )
        == 1
    )
    assert not store.exists()


@pytest.mark.unit
def test_replacing_a_pin_requires_the_active_lock_digest(tmp_path: Path) -> None:
    bundle, commit = _write_bundle(tmp_path)
    store = tmp_path / "store"
    assert cli.install(_args(bundle, commit, store), bundle, commit) == 0
    other = json.loads(_active_manifest_bytes())
    other["source"]["commit"] = "c" * 40
    other_bundle, _ = _write_bundle(tmp_path / "second", json.dumps(other, indent=2).encode())
    # A different pin without --replace conflicts and leaves the store intact.
    with pytest.raises(AcquisitionError):
        cli.install(_args(other_bundle, "c" * 40, store), other_bundle, "c" * 40)
    active_digest = hashlib.sha256((store / "active-lock.json").read_bytes()).hexdigest()
    assert (
        cli.install(
            _args(
                other_bundle,
                "c" * 40,
                store,
                "--replace",
                "--expected-active-lock-sha256",
                active_digest,
            ),
            other_bundle,
            "c" * 40,
        )
        == 0
    )
    lock = SnapshotStore(store).active_lock()
    assert lock is not None and lock.source_commit == "c" * 40


@pytest.mark.unit
def test_committed_acquisition_receipt_requires_verified_provenance() -> None:
    """The repo pin must cite a verified Actions artifact, not a skipped local install."""
    receipt_path = REPO_ROOT / "data/companion/acquisition.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt.get("artifact_id") is not None, "committed artifact_id must not be null"
    assert receipt.get("workflow_run_id") is not None, "committed workflow_run_id must not be null"
    attestation = str(receipt.get("attestation", ""))
    assert attestation != "skipped", "committed acquisition must not use skip-attestation"
    assert attestation.startswith("verified"), attestation


@pytest.mark.unit
def test_artifact_names_are_validated_before_any_download() -> None:
    assert cli.main(["--fetch", "upstreamdrift-companion-notasha"]) == 1
