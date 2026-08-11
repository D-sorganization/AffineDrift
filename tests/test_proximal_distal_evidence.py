"""Contract tests for the pinned proximal-distal evidence snapshot."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.check_proximal_distal_evidence import (
    load_manifest,
    publication_ready,
    validate_manifest,
)


def _pinned_manifest(artifact_path: Path) -> dict[str, object]:
    digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    return {
        "schema_version": "1.0.0",
        "publication_state": "pinned",
        "source": {
            "repository": "D-sorganization/UpstreamDrift",
            "commit": "a" * 40,
            "issue_url": "https://github.com/D-sorganization/UpstreamDrift/issues/8470",
        },
        "regeneration_commands": ["python -m scripts.research.example"],
        "artifacts": [{"path": artifact_path.name, "sha256": digest, "role": "figure"}],
        "evidence": {
            "status": "published",
            "model_tiers": ["exact_planar_double_pendulum"],
            "quantities": [
                "force",
                "force_along_hand_path",
                "impulse",
                "power",
                "work",
                "joint_attribution",
            ],
        },
        "release_blockers": [],
        "pin_procedure": ["Replace the placeholder from a merged upstream commit."],
    }


def test_repository_placeholder_is_valid_but_not_publishable() -> None:
    path = Path("data/proximal_distal_energy_transfer/hand_path_attribution_snapshot.json")
    manifest = load_manifest(path)

    assert validate_manifest(manifest, path.parent) == []
    assert publication_ready(manifest) is False


def test_pending_state_fails_closed_if_it_contains_claim_artifacts(tmp_path: Path) -> None:
    artifact = tmp_path / "figure.svg"
    artifact.write_text("<svg/>", encoding="utf-8")
    manifest = _pinned_manifest(artifact)
    manifest["publication_state"] = "awaiting_upstream_merge"

    errors = validate_manifest(manifest, tmp_path)

    assert any("must not contain" in error for error in errors)


def test_pinned_state_requires_full_source_commit(tmp_path: Path) -> None:
    artifact = tmp_path / "figure.svg"
    artifact.write_text("<svg/>", encoding="utf-8")
    manifest = _pinned_manifest(artifact)
    source = manifest["source"]
    assert isinstance(source, dict)
    source["commit"] = "branch-name"

    errors = validate_manifest(manifest, tmp_path)

    assert any("40-character" in error for error in errors)


def test_pinned_state_verifies_artifact_hashes(tmp_path: Path) -> None:
    artifact = tmp_path / "figure.svg"
    artifact.write_text("<svg/>", encoding="utf-8")
    manifest = _pinned_manifest(artifact)
    artifact.write_text("changed", encoding="utf-8")

    errors = validate_manifest(manifest, tmp_path)

    assert any("SHA-256 mismatch" in error for error in errors)


def test_pinned_state_requires_declared_evidence_quantities(tmp_path: Path) -> None:
    artifact = tmp_path / "figure.svg"
    artifact.write_text("<svg/>", encoding="utf-8")
    manifest = _pinned_manifest(artifact)
    evidence = manifest["evidence"]
    assert isinstance(evidence, dict)
    evidence["quantities"] = ["force"]

    errors = validate_manifest(manifest, tmp_path)

    assert any("missing required quantities" in error for error in errors)


def test_load_manifest_rejects_non_object(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps([]), encoding="utf-8")

    try:
        load_manifest(path)
    except ValueError as exc:
        assert "JSON object" in str(exc)
    else:
        raise AssertionError("non-object manifest must fail")
