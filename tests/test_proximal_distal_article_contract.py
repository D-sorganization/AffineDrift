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
        "not be relabeled as scapular retraction",
        "participant-level holdout",
        "UpstreamDrift/issues/8497",
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
