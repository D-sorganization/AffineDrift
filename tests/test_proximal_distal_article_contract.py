"""Publication-boundary checks for the hand-path attribution article."""

from pathlib import Path

ARTICLE = Path("articles/proximal-distal-energy-transfer.qmd")
GLOSSARY = Path("articles/zero-torque-counterfactual.qmd")


def test_article_distinguishes_force_from_biological_effort() -> None:
    text = ARTICLE.read_text(encoding="utf-8")

    assert "does not identify biological effort" in text
    assert "co-contraction" in text
    assert "muscle activation" in text


def test_article_uses_canonical_pointwise_terminology() -> None:
    text = ARTICLE.read_text(encoding="utf-8")

    assert "pointwise ZTCF sample" in text
    assert "stitched pointwise ZTCF trace" in text
    assert "must not be used to infer persistence" in text
    assert "forward or branched ZTCF trajectory" in text
    assert "ZVCF is not the control contribution" in text
    assert "pointwise drift vector" in text


def test_glossary_requires_qualified_ztcf_and_rejects_muscle_inference() -> None:
    text = GLOSSARY.read_text(encoding="utf-8")

    for term in (
        "Pointwise ZTCF sample",
        "Stitched pointwise ZTCF trace",
        "Forward ZTCF trajectory",
        "Branched ZTCF trajectory",
        "drift vector field",
    ):
        assert term in text
    assert "qualifier is required on first use" in text
    assert "cannot establish persistence" in text
    assert "This is not a no-muscle simulation" in text


def test_article_exposes_exact_pinned_evidence_status() -> None:
    text = ARTICLE.read_text(encoding="utf-8")

    assert "Pinned Open Evidence" in text
    assert "hand_path_attribution_snapshot.json" in text
    assert "69eb7e9db32ccd17e45824619315b1d04b400c27" in text
    assert "--require-pinned" in text


def test_article_reports_three_model_results_and_bounded_preview() -> None:
    text = ARTICLE.read_text(encoding="utf-8")

    for term in (
        "Exact double pendulum",
        "One-arm, three-link point-mass",
        "Two-arm floating-club closed loop",
        "Every-Joint Drift Shares Across Normalized-Time Quartiles",
        "Two-Hand Common and Differential Contact-Force Modes",
        "57.6%",
    ):
        assert term in text
    assert "not evidence that golfers use muscle" in text


def test_article_cites_primary_hand_path_study() -> None:
    text = ARTICLE.read_text(encoding="utf-8")

    assert "@mackenzie2020energy" in text
    assert "average force along the hand path" in text


def test_article_exposes_matched_allocation_and_preload_falsifiers() -> None:
    text = ARTICLE.read_text(encoding="utf-8")

    for term in (
        "Arm--Wrist Allocation and Transmission Preload",
        "same 8 N m control moment",
        "modeled RMS hand force spans 7.58--91.51",
        "11 of 12 dead-zone/time-constant sensitivity cases",
        "applies the preparation commands for 180 ms",
        "without resetting state",
        "not a model of an anatomical",
        "not be relabeled as scapular retraction",
        "participant-level holdout",
        "UpstreamDrift/issues/8497",
        "e96a585a41f2d7659864e478db3de829e710e622",
    ):
        assert term in text
    assert "does not establish a universal" in text


def test_article_exposes_ground_reaction_drift_boundaries() -> None:
    text = ARTICLE.read_text(encoding="utf-8")

    for term in (
        "Ground-Reaction Drift Attribution",
        "configuration + velocity + control + other external load",
        "cannot identify bilateral foot forces",
        "not a human force-plate validation",
        "held-out participant",
        "ZTCF and ZVCF overlap",
    ):
        assert term in text


def test_article_connects_frames_biology_and_engines_without_overclaiming() -> None:
    text = ARTICLE.read_text(encoding="utf-8")

    for term in (
        "Reference Frames, Biological Redundancy, and Engine Roles",
        "fig_frame_power_invariance.svg",
        "fig_biological_redundancy.svg",
        "fig_biological_role_reversal.svg",
        "fig_cross_engine_question_ladder.svg",
        "MuJoCo",
        "Pinocchio",
        "Drake",
        "OpenSim",
        "MyoSuite",
        "1.14\\times10^{-13}",
        "cannot determine whether a golfer used one unique",
        "they are not completed human",
        "UpstreamDrift/issues/8505",
    ):
        assert term in text


def test_advanced_site_figures_are_local_and_nonempty() -> None:
    figure_dir = Path("articles/figures/proximal_distal_energy_transfer")
    for stem in (
        "fig_frame_power_invariance",
        "fig_biological_redundancy",
        "fig_biological_role_reversal",
        "fig_cross_engine_question_ladder",
        "fig_advanced_model_motion_plate",
    ):
        path = figure_dir / f"{stem}.svg"
        assert path.is_file()
        assert path.stat().st_size > 1000


def test_advanced_bridge_has_article_local_mobile_containment() -> None:
    css = Path("articles/proximal-distal-energy-transfer.css").read_text(encoding="utf-8")
    assert "#sec-advanced-bridge" in css
    assert "overflow-x: auto" in css
    assert "max-width: 100%" in css


def test_article_exposes_transmission_robustness_without_human_overclaim() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    for term in (
        "Transmission Pathways, Robust Speed, and Task Stability",
        "fig_transmission_pathway_framework.svg",
        "fig_robust_speed_variability_pareto.svg",
        "fig_clock_vs_state_perturbation_response.svg",
        "fig_task_null_variability_map.svg",
        "Every\nregistered program remains Pareto-nondominated",
        "not evidence of a neural synergy",
        "participant-held-out",
        "UpstreamDrift/issues/8507",
    ):
        assert term in text
    assert "not evidence of human self-stabilization" in text


def test_transmission_robustness_figures_are_local_and_nonempty() -> None:
    figure_dir = Path("articles/figures/proximal_distal_energy_transfer")
    for stem in (
        "fig_transmission_pathway_framework",
        "fig_robust_speed_variability_pareto",
        "fig_clock_vs_state_perturbation_response",
        "fig_task_null_variability_map",
    ):
        path = figure_dir / f"{stem}.svg"
        assert path.is_file()
        assert path.stat().st_size > 1000


def test_transmission_section_has_mobile_containment() -> None:
    css = Path("articles/proximal-distal-energy-transfer.css").read_text(encoding="utf-8")
    assert "#sec-transmission-robustness" in css
    assert "overflow-x: auto" in css
