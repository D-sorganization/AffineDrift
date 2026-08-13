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


def test_glossary_uses_canonical_capacity_based_dcr() -> None:
    """DCR must compare drift with bounded control in a declared common space."""
    glossary_text = GLOSSARY_QMD.read_text(encoding="utf-8")
    assert "same acceleration or task-projected space" in glossary_text
    assert "weighting matrix" in glossary_text
    assert "admissible control set" in glossary_text
    assert "regularizer" in glossary_text
    assert "passive to active torques" not in glossary_text
    assert "drift / (drift + control)" in glossary_text
    assert "ranging from 0 (pure control) to 1 (pure drift)" in glossary_text


def test_committed_glossary_matches_canonical_usage() -> None:
    """The LaTeX glossary and chapter must use the capacity-based definition."""
    glossary_text = GLOSSARY_TEX.read_text(encoding="utf-8")
    chapter_text = ZERO_TORQUE_CHAPTER.read_text(encoding="utf-8")

    assert "same acceleration or task-projected space" in glossary_text
    assert "admissible control set" in glossary_text
    assert "drift / (drift + control)" in glossary_text
    assert "admissible torque bound" in chapter_text
    assert "ratio of passive to active torques" not in chapter_text


def test_counterfactuals_do_not_claim_zero_control_means_zero_muscle() -> None:
    """The chapter must not infer physiology from a declared control channel."""
    chapter_text = ZERO_TORQUE_CHAPTER.read_text(encoding="utf-8")
    forbidden = (
        "all muscle torques are set to zero",
        "muscles produce no torque whatsoever",
        "every muscle in your body freezes",
        "No muscles. Physics takes over.",
    )
    for phrase in forbidden:
        assert phrase not in chapter_text
    assert "does not imply zero muscle activation" in chapter_text


def test_zvcf_is_an_instantaneous_zero_control_acceleration() -> None:
    """ZVCF is an evaluation, not a released or control-preserving trajectory."""
    chapter_text = ZERO_TORQUE_CHAPTER.read_text(encoding="utf-8")
    assert "instantaneous acceleration" in chapter_text
    assert "with both velocity and declared control set to zero" in chapter_text
    assert "then release" not in chapter_text
