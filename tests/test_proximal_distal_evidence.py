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
            "model_tiers": [
                "exact_planar_double_pendulum",
                "one_arm_three_link_point_mass",
                "two_arm_floating_club_closed_loop",
            ],
            "quantities": [
                "force",
                "force_along_hand_path",
                "impulse",
                "power",
                "work",
                "joint_attribution",
            ],
            "results": {
                name: {
                    "model_tier": tier,
                    "trajectory_kind": "forward_simulation",
                    "integration_interpretation": "Integrated along a declared trajectory.",
                    "primary_estimand": {
                        "reference_point": "wrist",
                        "force_direction": "golfer_on_club",
                        "path_length_m": 1.0,
                        "force_work_j": {
                            "total": 10.0,
                            "drift": 8.0,
                            "control": 2.0,
                            "zvcf": 1.0,
                        },
                        "mean_force_n": {
                            "total": 10.0,
                            "drift": 8.0,
                            "control": 2.0,
                            "zvcf": 1.0,
                        },
                    },
                    "closure": {
                        "force_max_abs": 0.0,
                        "couple_max_abs": 0.0,
                        "power_max_abs": 0.0,
                        "work_max_abs": 0.0,
                    },
                    "common_differential_convention": (
                        "common=right+left; differential=(right-left)/2"
                        if name == "two_arm"
                        else None
                    ),
                }
                for name, tier in (
                    ("double_pendulum", "exact_planar_double_pendulum"),
                    ("one_arm", "one_arm_three_link_point_mass"),
                    ("two_arm", "two_arm_floating_club_closed_loop"),
                )
            },
            "bounded_preview_hypothesis": {
                "study_type": "model_only_delayed_actuator_preview_hypothesis",
                "time_constant_s": 0.03,
                "best_preview_s": 0.024,
                "reactive_rmse_nm": 1.25,
                "preview_rmse_nm": 0.53,
                "improvement_percent": 57.6,
                "pointwise_ztcf_minimum_nm": -19.6,
                "base_at_ztcf_minimum_nm": -22.8,
                "control_residual_at_ztcf_minimum_nm": -3.2,
                "human_preactivation": "not_established",
                "clubhead_speed_outcome": "not_evaluated",
                "muscle_activation": "not_modeled",
            },
        },
        "release_blockers": [],
        "pin_procedure": ["Replace the placeholder from a merged upstream commit."],
    }


def test_repository_snapshot_is_valid_and_publishable() -> None:
    path = Path("data/proximal_distal_energy_transfer/hand_path_attribution_snapshot.json")
    manifest = load_manifest(path)

    assert validate_manifest(manifest, Path(".")) == []
    assert publication_ready(manifest) is True


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


def test_pinned_state_rejects_artifact_path_escape(tmp_path: Path) -> None:
    artifact = tmp_path / "figure.svg"
    artifact.write_text("<svg/>", encoding="utf-8")
    manifest = _pinned_manifest(artifact)
    artifacts = manifest["artifacts"]
    assert isinstance(artifacts, list)
    record = artifacts[0]
    assert isinstance(record, dict)
    record["path"] = "../figure.svg"

    errors = validate_manifest(manifest, tmp_path / "evidence")

    assert any("escapes the declared root" in error for error in errors)


def test_pinned_state_requires_declared_evidence_quantities(tmp_path: Path) -> None:
    artifact = tmp_path / "figure.svg"
    artifact.write_text("<svg/>", encoding="utf-8")
    manifest = _pinned_manifest(artifact)
    evidence = manifest["evidence"]
    assert isinstance(evidence, dict)
    evidence["quantities"] = ["force"]

    errors = validate_manifest(manifest, tmp_path)

    assert any("missing required quantities" in error for error in errors)


def test_pinned_state_requires_every_declared_model_result(tmp_path: Path) -> None:
    artifact = tmp_path / "figure.svg"
    artifact.write_text("<svg/>", encoding="utf-8")
    manifest = _pinned_manifest(artifact)
    evidence = manifest["evidence"]
    assert isinstance(evidence, dict)
    results = evidence["results"]
    assert isinstance(results, dict)
    results.pop("two_arm")

    errors = validate_manifest(manifest, tmp_path)

    assert any("missing model results: two_arm" in error for error in errors)


def test_pinned_state_rejects_nonclosing_or_nonfinite_results(tmp_path: Path) -> None:
    artifact = tmp_path / "figure.svg"
    artifact.write_text("<svg/>", encoding="utf-8")
    manifest = _pinned_manifest(artifact)
    evidence = manifest["evidence"]
    assert isinstance(evidence, dict)
    results = evidence["results"]
    assert isinstance(results, dict)
    double = results["double_pendulum"]
    assert isinstance(double, dict)
    closure = double["closure"]
    estimand = double["primary_estimand"]
    assert isinstance(closure, dict)
    assert isinstance(estimand, dict)
    closure["force_max_abs"] = 1e-3
    estimand["path_length_m"] = float("nan")

    errors = validate_manifest(manifest, tmp_path)

    assert any("closure.force_max_abs" in error for error in errors)
    assert any("path_length_m" in error for error in errors)


def test_pinned_state_preserves_bounded_preview_claim_boundary(tmp_path: Path) -> None:
    artifact = tmp_path / "figure.svg"
    artifact.write_text("<svg/>", encoding="utf-8")
    manifest = _pinned_manifest(artifact)
    evidence = manifest["evidence"]
    assert isinstance(evidence, dict)
    hypothesis = evidence["bounded_preview_hypothesis"]
    assert isinstance(hypothesis, dict)
    hypothesis["human_preactivation"] = "established"
    hypothesis["preview_rmse_nm"] = float("inf")

    errors = validate_manifest(manifest, tmp_path)

    assert any("human_preactivation must equal not_established" in error for error in errors)
    assert any("preview_rmse_nm must be finite" in error for error in errors)


def test_load_manifest_rejects_non_object(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps([]), encoding="utf-8")

    try:
        load_manifest(path)
    except ValueError as exc:
        assert "JSON object" in str(exc)
    else:
        raise AssertionError("non-object manifest must fail")
