"""Contracts for markerless-mocap evidence published by AffineDrift."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from scripts.verify_markerless_mocap_projection import (
    SCHEMA_ID,
    MocapProjectionError,
    verify_projection_manifest,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "markerless_mocap_publication_projection_v1.schema.json"
ADR_PATH = REPO_ROOT / "docs" / "adr" / "0001-markerless-mocap-publication-boundary.md"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _valid_manifest(tmp_path: Path) -> tuple[dict[str, Any], Path]:
    projection_root = tmp_path / "projection"
    projection_root.mkdir()
    artifact = b'{"mean_reprojection_error_px": 0.42}\n'
    (projection_root / "calibration-summary.json").write_bytes(artifact)
    revision = "1" * 40
    repository = "D-sorganization/UpstreamDrift"
    source_root = f"https://github.com/{repository}/tree/{revision}"
    manifest: dict[str, Any] = {
        "schema": SCHEMA_ID,
        "source": {
            "repository": repository,
            "revision": revision,
            "release_manifest_sha256": "2" * 64,
            "source_url": source_root,
        },
        "license": {
            "publication_spdx": "MIT",
            "components": [{"name": "mocap-contract", "spdx": "MIT", "distribution": "embedded"}],
        },
        "privacy": {
            "review": "approved",
            "consent": "public_release_approved",
            "retention": "sanitized_artifacts_only",
            "contains_raw_video": False,
            "contains_pii": False,
            "contains_secrets": False,
        },
        "security": {"review": "approved", "malware_scan": "passed"},
        "qualification": {
            "origin": "protected_release",
            "status": "qualified",
            "authority_repository": repository,
            "protocol_version": "mocap-validation/v1",
        },
        "claims": [
            {
                "id": "calibration-residual",
                "evidence_class": "derived",
                "status": "qualified",
                "artifact_ids": ["calibration-summary"],
            }
        ],
        "artifacts": [
            {
                "id": "calibration-summary",
                "path": "calibration-summary.json",
                "kind": "calibration_summary",
                "classification": "sanitized_derived",
                "media_type": "application/json",
                "sha256": _sha(artifact),
                "bytes": len(artifact),
                "source_license": "MIT",
                "source_url": (
                    f"https://github.com/{repository}/blob/{revision}/"
                    "evidence/calibration-summary.json"
                ),
            }
        ],
    }
    return manifest, projection_root


def test_qualified_sanitized_projection_is_deterministic(tmp_path: Path) -> None:
    manifest, projection_root = _valid_manifest(tmp_path)

    first = verify_projection_manifest(manifest, projection_root)
    second = verify_projection_manifest(copy.deepcopy(manifest), projection_root)

    assert first == second
    assert (first.artifact_count, first.claim_count, first.total_bytes) == (1, 1, 37)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda data: data["source"].update(revision="main"), "revision"),
        (
            lambda data: data["source"].update(
                source_url="https://github.com/D-sorganization/UpstreamDrift/tree/main"
            ),
            "mutable",
        ),
        (lambda data: data["privacy"].update(contains_raw_video=True), "raw video"),
        (lambda data: data["privacy"].update(contains_pii=True), "PII"),
        (lambda data: data["privacy"].update(contains_secrets=True), "secrets"),
        (
            lambda data: data["license"]["components"][0].update(spdx="AGPL-3.0-only"),
            "license",
        ),
        (lambda data: data["qualification"].update(status="unqualified"), "qualified"),
        (
            lambda data: data["qualification"].update(origin="synthetic", status="qualified"),
            "model_scenario",
        ),
        (
            lambda data: (
                data["qualification"].update(origin="live_lab"),
                data["privacy"].update(consent="not_applicable"),
            ),
            "live-lab",
        ),
        (
            lambda data: data["artifacts"][0].update(
                source_url=(
                    "https://github.com/D-sorganization/UpstreamDrift/blob/main/"
                    "evidence/calibration-summary.json"
                )
            ),
            "mutable",
        ),
        (
            lambda data: data["artifacts"][0].update(
                source_url=(
                    "https://github.com/D-sorganization/UpstreamDrift/blob/"
                    f"{'1' * 40}/../main/calibration-summary.json"
                )
            ),
            "normalized relative path",
        ),
        (
            lambda data: data["claims"][0].update(
                artifact_ids=["calibration-summary", "calibration-summary"]
            ),
            "repeats an artifact",
        ),
        (
            lambda data: data["artifacts"][0].update(
                kind="raw_video", path="capture.mp4", media_type="video/mp4"
            ),
            "raw video",
        ),
    ],
)
def test_projection_fails_closed_on_boundary_violation(
    tmp_path: Path, mutation: Any, message: str
) -> None:
    manifest, projection_root = _valid_manifest(tmp_path)
    mutation(manifest)

    with pytest.raises(MocapProjectionError, match=message):
        verify_projection_manifest(manifest, projection_root)


def test_projection_fails_closed_on_missing_or_changed_artifact(tmp_path: Path) -> None:
    manifest, projection_root = _valid_manifest(tmp_path)
    artifact_path = projection_root / "calibration-summary.json"
    artifact_path.write_text("changed", encoding="utf-8")

    with pytest.raises(MocapProjectionError, match="artifact mismatch"):
        verify_projection_manifest(manifest, projection_root)


def test_public_schema_and_authority_documents_are_versioned() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    adr = ADR_PATH.read_text(encoding="utf-8")
    spec = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    handoff = (REPO_ROOT / "AGENT_HANDOFF.md").read_text(encoding="utf-8")

    assert schema["$id"].endswith("markerless_mocap_publication_projection_v1.schema.json")
    assert schema["properties"]["schema"]["const"] == SCHEMA_ID
    assert "never owns capture, synchronization, calibration, or reconstruction runtime" in adr
    assert "raw video, PII, secrets, or AGPL-licensed components" in adr
    assert "revision-pinned" in adr
    assert "Markerless Mocap Publication Boundary" in spec
    assert "AffineDrift #3954" in handoff
