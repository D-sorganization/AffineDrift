from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pointwise_descriptions_do_not_claim_passive_trajectory():
    draft = (ROOT / "pages/ud-render-draft.qmd").read_text(encoding="utf-8")
    assert "The pointwise zero-torque counterfactual" in draft


def test_time_cone_draft_does_not_assert_dcr_shrinks_reachability():
    text = (ROOT / "content/drift-ratio-visualizations/time-cone-analogy.md").read_text(
        encoding="utf-8"
    )
    assert "not evidence of a shrinking reachable set" in text
    assert "reachable-set volume collapses monotonically" not in text
