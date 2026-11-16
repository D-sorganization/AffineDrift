"""Content and notation regression guards for FDM review issue #5608."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = REPO_ROOT / "articles" / "forward_dynamics_matching"
PANDOC_MATH_RESIDUE = re.compile(r"\(\\\|")


def _chapter(name: str) -> str:
    return (BOOK_DIR / name).read_text(encoding="utf-8")


def test_collocation_documents_hermite_simpson_defects() -> None:
    text = _chapter("07_collocation.qmd")
    assert "### Hermite-Simpson Defects" in text
    assert r"\frac{h_k}{6}" in text
    assert "block bidiagonal" in text


def test_index_fixes_notation_and_exercise_scope() -> None:
    text = _chapter("index.qmd")
    assert "## Book Notation Conventions" in text
    assert r"N_{\mathrm{kin}}" in text
    assert r"\mathcal{J}" in text
    assert "Each method chapter includes" in text
    assert "Survey chapters (2, 3, and 24)" in text


def test_collocation_doi_attributes_lin_and_pandy() -> None:
    text = _chapter("07_collocation.qmd")
    assert "Lin and Pandy" in text
    assert "10.1016/j.jbiomech.2017.04.038" in text
    assert not re.search(r"Dorschky[^.]{0,80}10\.1016/j/jbiomech\.2017\.04\.038", text)


def test_gradients_describes_crocoddyl_integrator_semantics() -> None:
    text = _chapter("10_gradients.qmd")
    assert "Rosenbrock" in text
    assert "node_integrator" in text


def test_named_central_objects_have_display_equations() -> None:
    control = _chapter("08_control_bases.qmd")
    assert "Cox–de Boor" in control or "Cox-de Boor" in control
    assert r"B_{i,p}(t)" in control

    muscles = _chapter("11_muscles.qmd")
    assert r"\tau_{\mathrm{act}}" in muscles
    assert r"f_L(l)" in muscles

    filtering = _chapter("12_state_estimation.qmd")
    assert r"K_k=P_k^-H_k^T" in filtering.replace(" ", "")
    assert "Scalar Kalman Update" in filtering

    bayes = _chapter("14_bayesian.qmd")
    assert "simulation-based inference" in bayes.lower()


def test_book_has_no_pandoc_inline_math_residue() -> None:
    """Broken \\( \\| ... \\) conversions leave literal '(\\|' tokens in source."""
    offenders: list[str] = []
    for qmd in sorted(BOOK_DIR.glob("*.qmd")):
        for index, line in enumerate(qmd.read_text(encoding="utf-8").splitlines(), start=1):
            if PANDOC_MATH_RESIDUE.search(line):
                offenders.append(f"{qmd.name}:{index}: {line.strip()[:120]}")
    assert not offenders, "pandoc math residue:\n" + "\n".join(offenders)
