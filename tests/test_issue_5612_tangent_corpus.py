"""Regression contracts for tangent-hyperplane corpus notation (#5612)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

THESIS = ROOT / "articles/tangent-hyperplane-articles/Tangent_Hyperplanes_Unified_Thesis.qmd"
PART_1 = ROOT / "articles/tangent-hyperplanes-series/part-1-geometry.qmd"
PART_4 = ROOT / "articles/tangent-hyperplanes-series/part-4-residuals-curvature.qmd"
PART_6 = ROOT / "articles/tangent-hyperplanes-series/part-6-hybrid.qmd"
PART_7 = ROOT / "articles/tangent-hyperplanes-series/part-7-residual-aware.qmd"
HYBRID = ROOT / "articles/tangent-hyperplane-articles/Advanced/Hybrid_Tangent_Spaces.qmd"
RESIDUAL = ROOT / "articles/tangent-hyperplane-articles/Advanced/Residual-Aware_Control.qmd"
TOC = ROOT / "articles/tangent-hyperplane-articles/TABLE_OF_CONTENTS.qmd"
LAYMANS = ROOT / "articles/tangent-hyperplane-articles/LAYMANS_TERMS_SUMMARY.qmd"
NOTATION = ROOT / "NOTATION.md"

TANGENT_QMD_ROOTS = (
    ROOT / "articles/tangent-hyperplane-articles",
    ROOT / "articles/tangent-hyperplanes-series",
)

BANNED_IN_TANGENT_CORPUS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"M\\ddot\s*q[^=]*\+G\(q\)"), "uppercase G(q) for gravity in robot EOM"),
    (re.compile(r"Switching in Systems and Control"), "wrong Liberzon (2003) bibliography entry"),
    (
        re.compile(r"Synthesis and stabilization of complex behaviors through online trajectory"),
        "wrong Tassa IROS 2012 bibliography entry",
    ),
    (re.compile(r"\\boxed\{S="), "saltation matrix labeled S (collides with Riccati S)"),
    (re.compile(r"g_j\(z\)"), "lowercase g_j for input vector fields"),
    (re.compile(r"\\dot\s*z\s*=\s*g\("), "lowercase g for whole hybrid dynamics RHS"),
    (re.compile(r"guard\s*\$g\("), "lowercase g for hybrid guard"),
    (re.compile(r"\\partial_tg\+"), "guard time derivative subscript g (use h)"),
)


def _iter_tangent_qmd() -> list[Path]:
    paths: list[Path] = []
    for base in TANGENT_QMD_ROOTS:
        paths.extend(sorted(base.rglob("*.qmd")))
    return paths


@pytest.mark.content_lint
@pytest.mark.parametrize("path", _iter_tangent_qmd(), ids=lambda p: p.relative_to(ROOT).as_posix())
def test_tangent_corpus_has_no_banned_notation(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    hits: list[str] = []
    for pattern, rule in BANNED_IN_TANGENT_CORPUS:
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            hits.append(f"{path.relative_to(ROOT).as_posix()}:{line}: {rule}")
    assert not hits, "\n".join(hits)


def test_unified_thesis_gravity_uses_lowercase_g_q() -> None:
    text = THESIS.read_text(encoding="utf-8")
    assert "M(q)\\ddot q+C(q,\\dot q)\\dot q+g(q)=\\tau" in text
    assert "g(q)=g_0" in text
    assert re.search(r"M\(q\)\\ddot q[^=]*\+G\(q\)", text) is None


def test_unified_thesis_reference_list_matches_in_text_citations() -> None:
    text = THESIS.read_text(encoding="utf-8")
    assert "Liberzon, D. (2012). *Calculus of Variations and Optimal Control Theory" in text
    assert "Switching in Systems and Control" not in text
    assert "Tassa, Y., Mansard, N., and Todorov, E. (2014)" in text
    assert "Synthesis and stabilization of complex behaviors" not in text


def test_unified_thesis_four_trajectory_residual_scopes_bar_u_zero() -> None:
    text = THESIS.read_text(encoding="utf-8")
    assert "With $\\bar u=0$, replacing its last term by $x_0$" in text


def test_part_1_defines_instantaneous_rate_set_and_dimension() -> None:
    text = PART_1.read_text(encoding="utf-8")
    assert "Instantaneous Rate Sets" in text
    assert "\\mathcal A(x)=f_0(x,t)+\\operatorname{im}G(x,t)" in text
    assert "\\dim\\mathcal A(x)=\\operatorname{rank}G(x,t)" in text
    assert "hyperplane in $T_x\\mathcal M$" in text


def test_laymans_points_to_part_1_rate_set_definition() -> None:
    text = LAYMANS.read_text(encoding="utf-8")
    assert "part-1-geometry.html#instantaneous-rate-sets-title-hyperplane" in text
    assert "instantaneous rate set" in text.lower()


def test_hybrid_articles_standardize_xi_and_guard_h() -> None:
    for path in (PART_6, HYBRID, TOC):
        text = path.read_text(encoding="utf-8")
        assert "\\Xi" in text
        assert "h(x,t)=0" in text or "h(t,x^-)=0" in text or "guard $h" in text


def test_residual_aware_uses_canonical_input_columns_and_guard() -> None:
    text = RESIDUAL.read_text(encoding="utf-8")
    assert "G_j(z)" in text
    assert re.search(r"guard \$g\(", text) is None
    assert "\\Xi=D_zR" in text


def test_part_7_disambiguates_tube_radius_from_linearized_eta() -> None:
    text = PART_7.read_text(encoding="utf-8")
    assert "\\rho_{\\mathrm{tube}}" in text
    assert "first-order comparison $\\eta$" in text


def test_part_4_input_push_uses_c_b_not_scalar_g() -> None:
    text = PART_4.read_text(encoding="utf-8")
    assert "c_B\\epsilon" in text
    assert "input part has norm at most $G\\epsilon$" not in text


def test_part_4_names_standard_sensitivity_background() -> None:
    text = PART_4.read_text(encoding="utf-8")
    assert "Khalil" in text and "sensitivity" in text.lower()


def test_part_7_names_robust_positively_invariant_condition() -> None:
    text = PART_7.read_text(encoding="utf-8")
    assert "robust positively invariant" in text.lower()
    assert "RPI" in text


def test_advanced_residual_article_names_matrix_measure() -> None:
    text = RESIDUAL.read_text(encoding="utf-8")
    assert "matrix measure" in text
    assert "logarithmic norm" in text


def test_notation_documents_hybrid_guard_saltation_and_reset() -> None:
    text = NOTATION.read_text(encoding="utf-8")
    assert "h, R, and Ξ" in text
    assert "Instantaneous Rate Set" in text
    assert "\\mathcal A(x)" in text
    assert "Saltation matrix at hybrid events" in text


def test_notation_saltation_symbol_is_valid_inline_math() -> None:
    text = NOTATION.read_text(encoding="utf-8")
    saltation_row = next(line for line in text.splitlines() if "| Saltation matrix:" in line)
    assert r"**$\Xi$**" in saltation_row
    assert r"\\Xi" not in saltation_row
