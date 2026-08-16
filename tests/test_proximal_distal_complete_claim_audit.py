"""Contracts for the complete canonical proximal-distal claim audit pin."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/proximal_distal_energy_transfer/complete_claim_audit_snapshot.json"
ARTICLE = ROOT / "articles/proximal-distal-energy-transfer.qmd"
COMPANION = ROOT / "articles/proximal_distal_companion/chapters"
SPATIAL_COMPANION = COMPANION / "ch20_plane_to_space.qmd"
GRIP_COMPANION = COMPANION / "ch12_two_hands_one_wrench.qmd"
SHAFT_COMPANION = COMPANION / "ch15_shaft_memory.qmd"
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
    assert source["commit"] in source["subject_scaled_closed_contact_url"]
    assert source["commit"] in source["scapulothoracic_contact_screen_url"]
    assert source["commit"] in source["release_claim_review_url"]
    assert source["commit"] in source["articulated_inertia_cross_engine_url"]
    assert source["commit"] in source["articulated_contact_projection_url"]
    assert source["commit"] in source["articulated_forward_contact_url"]
    assert source["commit"] in source["articulated_slack_atlas_url"]
    assert source["commit"] in source["articulated_distributed_grip_atlas_url"]
    assert source["commit"] in source["articulated_shaft_atlas_url"]
    assert audit["completion_status"] == "complete"
    assert audit["completion_layer"] == "narrative_candidate_census"
    assert audit["candidate_count"] == 1047
    assert audit["reviewed_candidate_count"] == 1047
    assert audit["unadjudicated_candidate_count"] == 0
    assert audit["registered_claim_count"] == 291
    # Release review is complete, but completion is traceability, not validation:
    # every release claim must still carry a scientifically open gate.
    assert audit["release_review_completion_status"] == "complete"
    assert audit["release_claim_count"] == 39
    assert audit["open_release_claim_count"] == 0
    assert audit["open_release_claim_keys"] == []
    assert audit["scientifically_open_gate_count"] == audit["release_claim_count"]
    assert (
        "does not mean any claim is scientifically validated" in audit["review_completion_meaning"]
    )
    assert release["pdf_pages"] == 229
    assert release["pdf_bytes"] == 1733358
    assert release["pdf_uri_links"] == 189
    assert release["pdf_outline_entries"] == 246
    assert release["qualified_artifact_count"] == 546
    assert SHA256.fullmatch(release["claim_registry_sha256"])
    assert SHA256.fullmatch(release["pdf_sha256"])
    assert boundaries["universal_human_or_coaching_strategy"] == "not_supported"
    assert boundaries["bilateral_human_grip_wrench_validation"].startswith("unexecuted")
    assert payload["source_agenda_readiness"] == {
        "critical_point_count": 9,
        "answered_or_partly_answered": 8,
        "unresolved_or_definition_gated": 1,
        "unresolved_point_ids": ["MTQ-06"],
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
    closed_contact = payload["subject_scaled_closed_contact"]
    assert closed_contact["total_sample_count"] == 234
    assert closed_contact["feasible_sample_count"] == 234
    assert closed_contact["maximum_contact_error_m"] < 1e-9
    assert closed_contact["constraint_jacobian_rank_values"] == [6]
    assert closed_contact["minimum_joint_limit_margin_rad"] > 0.1
    assert closed_contact["minimum_collision_clearance_m"] > 0.03
    assert closed_contact["anatomical_feasibility"] == "not_established"
    assert closed_contact["human_or_coaching_inference"] == "unsupported"
    assert SHA256.fullmatch(closed_contact["json_sha256"])
    assert SHA256.fullmatch(closed_contact["npz_sha256"])
    assert SHA256.fullmatch(closed_contact["figure_svg_sha256"])
    scapular = payload["scapulothoracic_contact_screen"]
    assert scapular["paired_state_count"] == 54
    assert scapular["fixed_contact_closed_count"] == 0
    assert scapular["scapular_contact_closed_count"] == 31
    assert scapular["scapular_qualified_contact_count"] == 16
    assert scapular["scapular_bound_active_count"] == 28
    assert scapular["fixed_coordinate_nullity"] == 2
    assert scapular["scapular_coordinate_nullity"] == 10
    assert scapular["adverse_contact_closed"] is False
    assert scapular["human_or_coaching_inference"] == "unsupported"
    assert SHA256.fullmatch(scapular["json_sha256"])
    assert SHA256.fullmatch(scapular["npz_sha256"])
    assert SHA256.fullmatch(scapular["figure_svg_sha256"])


def test_articulated_tier_blocks_are_exact_and_retain_their_boundaries() -> None:
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    for key in (
        "articulated_inertia_cross_engine",
        "articulated_contact_projection",
        "articulated_forward_contact",
        "articulated_slack_atlas",
        "articulated_distributed_grip_atlas",
        "articulated_shaft_atlas",
    ):
        block = payload[key]
        assert SHA256.fullmatch(block["json_sha256"])
        assert SHA256.fullmatch(block["npz_sha256"])
        assert SHA256.fullmatch(block["figure_svg_sha256"])
        assert block["human_or_coaching_inference"] == "unsupported"

    inertia = payload["articulated_inertia_cross_engine"]
    assert inertia["state_count"] == 234
    assert inertia["coordinate_count"] == 20
    assert inertia["engine_names"] == ["mujoco", "pinocchio"]
    assert inertia["maximum_mass_matrix_relative_error"] < 1e-11
    assert inertia["maximum_inverse_dynamics_relative_error"] < 1e-11
    assert inertia["maximum_symmetry_residual"] == 0.0
    assert inertia["minimum_mass_matrix_eigenvalue"] > 0.0
    assert inertia["failed_state_count"] == 0
    assert inertia["common_state_not_forward_trajectory"] is True
    assert inertia["forward_contact"] == "not_established"

    projection = payload["articulated_contact_projection"]
    assert projection["state_count"] == 234
    assert projection["forward_steps"] == 0
    assert projection["maximum_action_reaction_residual_n"] == 0.0
    # the declared contact law must dissipate, never inject, energy
    assert projection["maximum_contact_dissipation_power_w"] < 0.0
    assert projection["minimum_contact_dissipation_power_w"] < 0.0
    assert projection["forward_trajectory"] == "not_executed"

    forward = payload["articulated_forward_contact"]
    assert forward["bounded_horizon_s"] == 0.005
    assert forward["trajectory_count"] == 756
    assert forward["unilateral_collision_contact"] is False
    assert forward["failed_retention_cell_count"] == 0
    assert forward["maximum_attachment_separation_m"] < forward["retention_threshold_m"]
    residuals = forward["refinement_worst_normalized_residual"]
    assert residuals == sorted(residuals, reverse=True)
    assert "right_censored" in forward["right_censoring"].replace("-", "_") or (
        "does not establish persistence" in forward["right_censoring"]
    )
    assert forward["late_downswing_or_impact"] == "not_established_by_5_ms_horizon"

    slack = payload["articulated_slack_atlas"]
    assert slack["trajectory_count"] == 1944
    assert slack["opening_cell_count"] == 108
    assert slack["reattachment_cell_count"] == 216
    assert slack["active_set_parity_failures"] == 0
    slack_residuals = slack["refinement_worst_normalized_residual"]
    assert slack_residuals == sorted(slack_residuals, reverse=True)
    assert slack["biological_slack_or_intent"] == "not_identified"

    grip = payload["articulated_distributed_grip_atlas"]
    assert grip["station_counts_per_hand"] == [1, 3, 5]
    assert grip["trajectory_count"] == 288
    # total stiffness/damping are the control that makes station counts comparable
    assert grip["total_stiffness_n_m"] == 1800.0
    assert grip["total_damping_n_s_m"] == 18.0
    assert grip["maximum_transition_count"] == 0
    assert grip["station_refinement_passed"] is True
    grip_residuals = grip["time_refinement_worst_normalized_residual"]
    assert grip_residuals == sorted(grip_residuals, reverse=True)
    assert grip["measured_pressure_or_finger_anatomy"] == "not_identified"

    shaft = payload["articulated_shaft_atlas"]
    assert shaft["trajectory_count"] == 384
    assert shaft["activations"] == ["rigid", "bending", "torsion", "coupled"]
    assert shaft["fe_bending_frequency_relative_error"] == 0.0
    assert shaft["excluded_coarse_step_probe_count"] == 2
    assert shaft["failed_small_deflection_cell_count"] == 0
    shaft_residuals = shaft["time_refinement_worst_normalized_residual"]
    assert shaft_residuals == sorted(shaft_residuals, reverse=True)
    # the adverse result: only a minority of cells match, and both signs appear
    assert shaft["matched_load_work_cell_count"] == 126
    assert shaft["matched_load_work_total_cell_count"] == 384
    low, high = shaft["matched_final_speed_difference_range_m_s"]
    assert low < 0.0 < high
    assert shaft["universal_passive_shaft_speed_benefit"] == "rejected"
    assert shaft["calibration_status"] == "synthetic_reference_not_equipment_calibrated"
    assert shaft["support_boundary"] == "ground reaction and free moment are absent"

    boundaries = payload["principal_boundaries"]
    assert boundaries["universal_passive_shaft_speed_benefit"].startswith("rejected")
    assert boundaries["distributed_grip_pressure_or_finger_anatomy"] == "not_identified"
    assert boundaries["articulated_forward_contact"].startswith("right_censored")
    # the ground pathway is still an open upstream child and must not be pinned here
    assert boundaries["finite_ground_reaction_and_free_moment"].startswith("not_yet_pinned")


def test_article_exposes_the_complete_audit_without_promoting_it() -> None:
    article = ARTICLE.read_text(encoding="utf-8")
    normalized_article = " ".join(article.split())
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert "Complete Claim Audit" in article
    assert payload["source"]["commit"] in article
    assert "1,047 of 1,047" in article
    assert "zero unadjudicated" in article
    assert "does not validate a universal human or coaching strategy" in article
    assert "manual NotebookLM reauthentication" in article
    assert "nine independently tracked points" in article
    assert "MTQ-06, timing precision, remains unresolved" in normalized_article
    # review completion must never be presented as scientific validation
    assert "all 39 of 39 release claims have been" in normalized_article
    assert "all 39 still carry a scientifically open gate" in normalized_article
    assert "Review completion is a traceability property, not a scientific verdict" in (
        normalized_article
    )
    assert "No claim here is validated by having been reviewed" in normalized_article
    assert "Casting has a bounded answer" in normalized_article
    for label in (
        "Drift Contribution",
        "Geometry Dependencies",
        "Casting",
        "Early Proximal Acceleration",
        "Segment Release",
        "Timing Precision",
        "Self-Correction and Noise",
        "Proximal-Velocity Maximization",
        "Slack",
    ):
        assert label in article
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
    assert "234 of 234" in normalized_article
    assert "necessary-condition screen" in normalized_article
    assert "does not establish anatomical feasibility" in normalized_article
    assert "Paired Scapulothoracic Geometry Screen" in article
    assert "31 of 54" in normalized_article
    assert "16 of 54" in normalized_article
    assert "nullity rises from two to ten" in normalized_article
    # the articulated forward-contact rung, with its horizon stated as a limit
    assert "bounded 5 ms horizon" in normalized_article
    assert "right-censored" in normalized_article
    assert "not late downswing and not impact" in normalized_article
    # distributed grip: a convergence result, not a pressure measurement
    assert "77.0% of the load" in normalized_article
    assert "does not identify measured grip pressure" in normalized_article
    # shaft: the adverse headline must survive verbatim
    assert "126 match" in normalized_article
    assert "universal passive-shaft speed benefit is therefore rejected" in normalized_article
    assert "Both signs" in normalized_article or "negative and positive" in normalized_article
    # the unmerged ground pathway must be declared absent, not implied
    assert "not pinned here" in normalized_article


def test_grip_and_shaft_companions_state_the_limits_with_the_results() -> None:
    grip = " ".join(GRIP_COMPANION.read_text(encoding="utf-8").split())
    assert "One Point per Hand Is Itself a Modeling Choice" in grip
    assert "77% of the load" in grip
    assert "held fixed at 1800 N/m" in grip
    assert "A number of stations is not a set of fingers" in grip
    assert "does not measure grip pressure" in grip

    shaft = " ".join(SHAFT_COMPANION.read_text(encoding="utf-8").split())
    assert "The Registered Test Says the Benefit Is Not Universal" in shaft
    assert "126 of 384" in shaft
    assert "Both signs appear" in shaft
    assert "Sometimes the flexible shaft is slower" in shaft
    assert "rejected as a universal rule" in shaft
    assert "excluded and reported" in shaft


def test_spatial_companion_exposes_contact_closure_before_contact_dynamics() -> None:
    companion = " ".join(SPATIAL_COMPANION.read_text(encoding="utf-8").split())
    assert "Contact Closure Comes Before Contact Dynamics" in companion
    assert "0.171--0.616 m" in companion
    assert "rank-six bilateral contact Jacobian" in companion
    assert "respecting joint limits and collisions" in companion
    assert "234 of 234" in companion
    assert "reduced-tree necessary condition" in companion
    assert "cannot answer whether a passive mechanism reduces timing demand" in companion
    assert "Scapular Mobility Changes Reachability Without Identifying Strategy" in companion
    assert "31 of 54" in companion
    assert "nullity rises from two to ten" in companion
