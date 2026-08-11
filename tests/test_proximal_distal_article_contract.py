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


def test_article_exposes_fail_closed_evidence_status() -> None:
    text = ARTICLE.read_text(encoding="utf-8")

    assert "Evidence Pin Pending" in text
    assert "hand_path_attribution_snapshot.json" in text
    assert "D-sorganization/UpstreamDrift#8470" in text


def test_article_cites_primary_hand_path_study() -> None:
    text = ARTICLE.read_text(encoding="utf-8")

    assert "@mackenzie2020energy" in text
    assert "average force along the hand path" in text
