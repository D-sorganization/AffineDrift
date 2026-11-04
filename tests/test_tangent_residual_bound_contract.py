"""Contract tests for Part 4 residual bound precision (tangent review #5184)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

PART_4 = REPO_ROOT / "articles/tangent-hyperplanes-series/part-4-residuals-curvature.qmd"
PART_7 = REPO_ROOT / "articles/tangent-hyperplanes-series/part-7-residual-aware.qmd"


def test_part_4_uses_integrated_propagator_not_crude_te_lt() -> None:
    """Horizon growth uses (e^{LT}-1)/L, not T e^{LT} (#5184)."""
    text = PART_4.read_text(encoding="utf-8")
    assert r"\frac{e^{LT}-1}{L}" in text
    assert r"\|r(t)\|\le\frac12 KHC_0(T)^2\frac{e^{LT}-1}{L}\epsilon^2" in text
    assert "C_0(T)=O(e^{LT})" in text
    assert r"O\!\left(\frac{e^{3LT}}{L}\epsilon^2\right)" in text
    assert r"\|r(t)\|\le\frac12 KHC_0^2 T e^{LT}" not in text


def test_part_7_matches_part_4_residual_certificate() -> None:
    """Part 7 cites the same integrated kernel and horizon growth (#5184)."""
    text = PART_7.read_text(encoding="utf-8")
    assert r"\|r(t)\|\le\frac12 KHC_0(T)^2\frac{e^{LT}-1}{L}\epsilon^2" in text
    assert "C_0(T)=O(e^{LT})" in text
    assert r"O\!\left(\frac{e^{3LT}}{L}\epsilon^2\right)" in text
