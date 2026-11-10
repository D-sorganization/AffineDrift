"""Manuscript naming contract for tangent review #5185."""

from __future__ import annotations

from pathlib import Path

THESIS = (
    Path(__file__).resolve().parent.parent
    / "articles/tangent-hyperplane-articles/Tangent_Hyperplanes_Unified_Thesis.qmd"
)


def test_integral_accumulation_principle_name_retired() -> None:
    """The fixed-trajectory identity must not be branded a general 'Principle' (#5185)."""
    text = THESIS.read_text(encoding="utf-8")
    assert "Integral Accumulation Principle" not in text
    assert "General Principle: Integral Accumulation" not in text
    assert "Fundamentals of Integral Accumulation" not in text
    assert "## Linearity of Integrals Along a Fixed Trajectory" in text
    assert "## Fixed-Trajectory Integral Identity" in text
    assert "Variation vs. Causation" in text
