"""Bosch integration instructions must match rewritten chapters (issue #5615)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "articles/bosch_integration/instructions/INTEGRATION_GUIDE.md"
WORKFLOW = ROOT / "articles/bosch_integration/instructions/PR_WORKFLOW.md"


def test_integration_guide_uses_cite_not_citep_and_scopes_bosch_promises() -> None:
    text = GUIDE.read_text(encoding="utf-8")
    assert "\\citep" not in text
    assert "All content is backed by peer-reviewed research" not in text
    assert "856 lines" not in text
    assert "1,130 lines" not in text
    assert "assembly line hierarchy" not in text.lower()
    assert "Practitioner vocabulary" in text or "practitioner vocabulary" in text


def test_integration_guide_website_blurb_labels_bosch_topics_as_hypothesis() -> None:
    text = GUIDE.read_text(encoding="utf-8")
    assert "attractor-fluctuation landscapes" in text
    assert "labeled practitioner vocabulary" in text.lower() or "hypothesis" in text.lower()


def test_pr_workflow_line_counts_match_current_chapter_sizes() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "~388 lines" in text or "388 lines" in text
    assert "~835 lines" in text or "835 lines" in text
    assert "856 lines" not in text
    assert "1,130 lines" not in text
