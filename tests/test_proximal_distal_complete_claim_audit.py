"""Contracts for the complete canonical proximal-distal claim audit pin."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/proximal_distal_energy_transfer/complete_claim_audit_snapshot.json"
ARTICLE = ROOT / "articles/proximal-distal-energy-transfer.qmd"
SPATIAL_COMPANION = ROOT / "articles/proximal_distal_companion/chapters/ch20_plane_to_space.qmd"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def test_complete_claim_audit_snapshot_is_exact_and_fail_closed() -> None:
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    source = payload["source"]
    audit = payload["audit"]
    release = payload["release"]
    boundaries = payload["principal_boundaries"]

    assert source["repository"] == "D-sorganization/UpstreamDrift"
    assert SHA40.fullmatch(source["commit"])
    assert source["commit"] in source["registry_url"]
    assert source["commit"] in source["pdf_url"]
    assert source["commit"] in source["readiness_url"]
    assert source["commit"] in source["timing_viability_url"]
    assert source["commit"] in source["typed_slack_url"]
    assert source["commit"] in source["bilateral_wrench_identifiability_url"]
    assert source["commit"] in source["bilateral_wrench_sensor_qualification_url"]
    assert source["commit"] in source["subject_scaled_spatial_geometry_url"]
    assert audit == {
        "completion_status": "complete",
        "candidate_count": 982,
        "reviewed_candidate_count": 982,
        "unadjudicated_candidate_count": 0,
        "registered_claim_count": 261,
        "release_claim_count": 29,
    }
    assert release["pdf_pages"] == 216
    assert release["qualified_artifact_count"] == 448
    assert SHA256.fullmatch(release["claim_registry_sha256"])
    assert SHA256.fullmatch(release["pdf_sha256"])
    assert boundaries["universal_human_or_coaching_strategy"] == "not_supported"
    assert boundaries["bilateral_human_grip_wrench_validation"].startswith("unexecuted")
    assert payload["source_agenda_readiness"] == {
        "critical_point_count": 9,
        "answered_or_partly_answered": 8,
        "unresolved_or_definition_gated": 1,
        "model_plan_registered_for_all": True,
        "human_plan_registered_for_all": True,
        "human_execution_blocked": True,
    }
    timing = payload["timing_viability"]
    assert timing["paired_case_count"] == 60
    assert timing["trajectory_count"] == 120
    assert timing["primary_clock_viable_fraction"] == 0.8
    assert timing["primary_state_triggered_viable_fraction"] == 0.2
    assert timing["sustained_recovery_case_count"] == 0
    assert timing["human_timing_or_coaching_inference"] == "unsupported"
    assert SHA256.fullmatch(timing["json_sha256"])
    assert SHA256.fullmatch(timing["npz_sha256"])
    typed_slack = payload["typed_slack"]
    assert typed_slack["class_count"] == 5
    assert typed_slack["global_slack_benefit"] == "unsupported"
    assert typed_slack["single_channel_class_identification"] == "not_established"
    assert typed_slack["human_intentionality"] == "untested"
    assert SHA256.fullmatch(typed_slack["json_sha256"])
    assert SHA256.fullmatch(typed_slack["npz_sha256"])
    assert SHA256.fullmatch(typed_slack["figure_sha256"])
    bilateral = payload["bilateral_wrench_identifiability"]
    assert bilateral["point_force_map_rank"] == 5
    assert bilateral["point_force_map_nullity"] == 1
    assert bilateral["augmented_point_force_map_rank"] == 6
    assert bilateral["full_bilateral_wrench_map_rank"] == 6
    assert bilateral["full_bilateral_wrench_map_nullity"] == 6
    assert bilateral["invisible_point_force_mode"] == "equal_and_opposite_axial"
    assert bilateral["human_validation"] == "untested"
    assert bilateral["noise_robust_practical_identifiability"] == "not_established"
    assert SHA256.fullmatch(bilateral["json_sha256"])
    assert SHA256.fullmatch(bilateral["figure_sha256"])
    qualification = payload["bilateral_wrench_sensor_qualification"]
    assert qualification["analysis_type"] == "synthetic_point_force_sensor_qualification"
    assert qualification["sample_count"] == 301
    assert qualification["trial_count"] == 32
    assert qualification["net_wrench_only_allocation_rmse_n"] > 10.0
    assert qualification["net_wrench_only_axial_mode_rmse_n"] > 25.0
    assert qualification["combined_registered_allocation_rmse_n"] < 1.1
    assert qualification["sensor_values"] == "synthetic_not_device_calibration"
    assert qualification["human_validation"] == "untested"
    assert SHA256.fullmatch(qualification["json_sha256"])
    assert SHA256.fullmatch(qualification["figure_sha256"])
    geometry = payload["subject_scaled_spatial_geometry"]
    assert geometry["profile_count"] == 6
    assert geometry["case_count"] == 18
    assert geometry["all_samples_close_contact"] is False
    assert geometry["minimum_hand_to_grip_distance_m"] > 0.17
    assert geometry["contact_closure_tolerance_m"] == 0.005
    assert geometry["constraint_jacobian_rank_values"] == [6]
    assert geometry["point_force_map_rank_values"] == [5]
    assert geometry["augmented_map_rank_values"] == [6]
    assert geometry["human_or_coaching_inference"] == "unsupported"
    assert SHA256.fullmatch(geometry["json_sha256"])
    assert SHA256.fullmatch(geometry["npz_sha256"])
    assert SHA256.fullmatch(geometry["figure_svg_sha256"])


def test_article_exposes_the_complete_audit_without_promoting_it() -> None:
    article = ARTICLE.read_text(encoding="utf-8")
    normalized_article = " ".join(article.split())
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert "Complete Claim Audit" in article
    assert payload["source"]["commit"] in article
    assert "982 of 982" in article
    assert "zero unadjudicated" in article
    assert "does not validate a universal human or coaching strategy" in article
    assert "manual NotebookLM reauthentication" in article
    assert "nine independently tracked points" in article
    assert "Casting remains unresolved as one universal construct" in normalized_article
    assert "One transmitted-output channel therefore does not identify" in article
    assert "equal-and-opposite axial force mode" in article
    assert "does not identify muscle or scapular strategy" in normalized_article
    assert "larger state-triggered timing region" in normalized_article
    assert "no sustained half-error recovery" in normalized_article
    assert "11.86 N" in article
    assert "29.05 N" in article
    assert "synthetic point-force sensor qualification" in normalized_article
    assert "not a device calibration or human validation result" in normalized_article
    assert "local rank does not prove contact closure" in normalized_article
    assert "0.171--0.616 m" in article
    assert "closed-contact inverse kinematics" in normalized_article


def test_spatial_companion_exposes_contact_closure_before_contact_dynamics() -> None:
    companion = " ".join(SPATIAL_COMPANION.read_text(encoding="utf-8").split())
    assert "Contact Closure Comes Before Contact Dynamics" in companion
    assert "0.171--0.616 m" in companion
    assert "rank-six bilateral contact Jacobian" in companion
    assert "respecting joint limits and collisions" in companion
    assert "cannot answer whether a passive mechanism reduces timing demand" in companion
