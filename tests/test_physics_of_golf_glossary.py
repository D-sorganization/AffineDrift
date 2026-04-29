"""Regression tests for the Physics of Golf glossary definitions."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.content_lint

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY_QMD = ROOT / "articles" / "The_Physics_of_Golf" / "quarto" / "glossary.qmd"
GLOSSARY_TEX = ROOT / "articles" / "The_Physics_of_Golf" / "chapters" / "glossary.tex"
ZERO_TORQUE_CHAPTER = (
    ROOT / "articles" / "The_Physics_of_Golf" / "quarto" / "ch06_zero_torque_counterfactual.qmd"
)


def test_glossary_distinguishes_raw_dcr_from_normalized_fraction() -> None:
    """The glossary should keep the textbook DCR convention separate from normalization."""
    glossary_text = GLOSSARY_QMD.read_text(encoding="utf-8")
    assert "drift-to-control ratio" in glossary_text
    assert "passive to active torques" in glossary_text
    assert "drift / (drift + control)" in glossary_text
    assert "ranging from 0 (pure control) to 1 (pure drift)" in glossary_text
    assert "much greater than 1" in glossary_text


def test_committed_glossary_matches_textbook_usage() -> None:
    """The rendered glossary should agree with the chapter's raw ratio framing."""
    glossary_text = GLOSSARY_TEX.read_text(encoding="utf-8")
    chapter_text = ZERO_TORQUE_CHAPTER.read_text(encoding="utf-8")

    assert "drift-to-control ratio" in glossary_text
    assert "passive to active torques" in glossary_text
    assert "drift / (drift + control)" in glossary_text
    assert "ratio of passive to active torques" in chapter_text
