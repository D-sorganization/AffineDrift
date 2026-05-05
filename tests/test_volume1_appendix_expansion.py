"""Coverage guardrails for Volume I appendix expansions (issue #1286)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOLUME_I_MAIN = ROOT / "articles" / "The_Geometry_of_Motion" / "Volume_I" / "main.tex"


def test_differential_geometry_appendix_contains_required_topics() -> None:
    """Differential geometry appendix should cover all required expansion topics."""
    text = VOLUME_I_MAIN.read_text(encoding="utf-8")
    assert r"\chapter{Differential Geometry Primer}" in text
    assert "Lie Groups and Lie Algebras" in text
    assert "Exponential and Logarithmic Maps" in text
    assert "Adjoint Representation" in text
    assert "Fiber Bundles" in text
    assert "Connections and Parallel Transport" in text
    assert "Curvature and Trajectory Sensitivity" in text
    assert "Python Example" in text


def test_linear_algebra_appendix_contains_required_topics() -> None:
    """Linear algebra appendix should cover all required expansion topics."""
    text = VOLUME_I_MAIN.read_text(encoding="utf-8")
    assert r"\chapter{Linear Algebra for Control}" in text
    assert "Kronecker Products" in text
    assert "Matrix Calculus" in text
    assert "Generalized Eigenvalue Problems" in text
    assert "Perturbation Theory and Pseudospectra" in text
    assert "Sparse Matrix Methods" in text
    assert "LMI Fundamentals" in text
    assert "SciPy" in text
    assert "cvxpy" in text
