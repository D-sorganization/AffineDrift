"""Regression contracts for sensorimotor latency and feedback claims."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.content_lint

ROOT_DIR = Path(__file__).resolve().parent.parent
QMD_CHAPTER = ROOT_DIR / "articles/The_Physics_of_Golf/quarto/ch24_motor_control_brain.qmd"
TEX_CHAPTER = ROOT_DIR / "articles/The_Physics_of_Golf/chapters/ch24_motor_control_brain.tex"
MUSCLE_CHAPTER = ROOT_DIR / "articles/The_Physics_of_Golf/quarto/ch17_muscle_force_generation.qmd"


@pytest.mark.parametrize("chapter", (QMD_CHAPTER, TEX_CHAPTER), ids=("quarto", "latex"))
def test_motor_control_chapter_does_not_use_a_serial_or_binary_feedback_story(
    chapter: Path,
) -> None:
    source = chapter.read_text(encoding="utf-8").casefold()

    forbidden_claims = (
        "Total round-trip delay: approximately 250--330",
        "The Feedback Fantasy",
        "No error correction is possible during execution",
        "The elite golfer does not rely on this",
        "The elite golfer likely does not rely heavily on this",
        "only the fastest spinal loops can close at all",
        "Sensory feedback is too slow to correct the swing trajectory in real time",
        "leave no room for a visually driven correction",
        "most corrections cannot happen mid-swing",
        "ballistic execution is the only option",
    )
    for claim in forbidden_claims:
        assert claim.casefold() not in source, f"{chapter.name} retains overclaim: {claim}"


@pytest.mark.parametrize("chapter", (QMD_CHAPTER, TEX_CHAPTER), ids=("quarto", "latex"))
def test_motor_control_chapter_states_pathway_phase_and_evidence_boundaries(
    chapter: Path,
) -> None:
    source = chapter.read_text(encoding="utf-8").casefold()

    required_claims = (
        "parallel pathways",
        "20--45 ms",
        "50--100 ms",
        "greater than 100 ms",
        "task-dependent",
        "response authority",
        "late visually guided",
        "golf-specific perturbation evidence",
        "kurtzer2014longlatency",
        "pruszynski2012longlatency",
    )
    for claim in required_claims:
        assert claim.casefold() in source, f"{chapter.name} lacks governed boundary: {claim}"


@pytest.mark.parametrize(
    "chapter",
    (
        MUSCLE_CHAPTER,
        ROOT_DIR / "articles/The_Physics_of_Golf/chapters/ch17_muscle_force_generation.tex",
    ),
    ids=("quarto", "latex"),
)
def test_muscle_chapter_keeps_the_latency_example_model_bounded(chapter: Path) -> None:
    source = chapter.read_text(encoding="utf-8")

    # The revised example specifies a delay and activation response separately,
    # without equating either to a universal serial sensory-feedback budget.
    assert "a separately specified pure transmission delay" in source
    assert "not a measured sequence of events in every downswing" in source
    assert (
        "Preparation and a new response must be compared from their actual initial states" in source
    )
    assert "double-count processes" in source
    assert "no response time remains" in source
    assert "all within-swing feedback is ineffective" not in source
