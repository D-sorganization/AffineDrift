"""Regression tests for Geometry of Motion notation harmonisation (#5602)."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


def test_control_is_motion_transverse_uses_et_not_projector_as_coordinates() -> None:
    text = _read("books/control-is-motion.qmd")
    assert "z = E(t)^T" in text
    assert "z = P(t)" not in text


def test_ch03b_uses_hm_not_p_for_constrained_acceleration_operator() -> None:
    text = _read(
        "articles/The_Geometry_of_Motion/quarto/ch03b_induced_acceleration_biomechanics.qmd"
    )
    assert r"\mathcal{H}_M" in text
    assert r"P&=M^{-1}-M^{-1}A^{\mathsf T}W^{-1}AM^{-1}" not in text
    assert r"\mathcal{H}_M Q_0" in text


def test_ch03b_singular_operational_inertia_uses_kc_not_w() -> None:
    text = _read(
        "articles/The_Geometry_of_Motion/quarto/ch03b_induced_acceleration_biomechanics.qmd"
    )
    assert "inverting singular $K_c$" in text
    assert "inverting singular $W$" not in text


def test_ch03b_gamma_sign_matches_notation_registry() -> None:
    text = _read(
        "articles/The_Geometry_of_Motion/quarto/ch03b_induced_acceleration_biomechanics.qmd"
    )
    assert r"J_c\dot v=-\gamma" in text
    assert r"\gamma=\dot J_c v" in text
    assert r"\gamma=-\dot J_c v" not in text
    assert r"J_c\ddot q=\gamma" not in text
    assert r"a_c&=-M^{-1}J_c^{\mathsf T}K_c^{-1}\gamma" in text


def test_ch07_constrained_symbols_match_ch09_registry() -> None:
    text = _read("articles/The_Geometry_of_Motion/quarto/ch07_counterfactuals.qmd")
    assert r"J_c\dot v=-\gamma" in text
    assert r"P_v=I-M^{-1}J_c^T" in text
    assert r"A\dot v=-b" not in text


def test_notation_md_documents_gom_constrained_projector_split() -> None:
    text = _read("NOTATION.md")
    assert "Geometry of Motion Notation" in text
    assert r"\mathcal{H}_M" in text
    assert r"\Pi_M" in text


@pytest.mark.parametrize(
    "rel",
    [
        "articles/The_Geometry_of_Motion/quarto/vol0_ch04_rotations_se3.qmd",
        "articles/The_Geometry_of_Motion/quarto/vol0_ch05_screw_axes.qmd",
        "articles/The_Geometry_of_Motion/quarto/vol0_ch06_exponential_coordinates.qmd",
    ],
)
def test_volume0_rotation_chapters_include_notation_note(rel: str) -> None:
    assert "gom_rotation_notation_note.qmd" in _read(rel)


@pytest.mark.parametrize(
    "rel",
    [
        "articles/The_Geometry_of_Motion/quarto/ch03_superposition.qmd",
        "articles/The_Geometry_of_Motion/Volume_I/chapters/ch03_superposition.tex",
    ],
)
def test_ch03_lie_bracket_uses_one_input_column(rel: str) -> None:
    """A bracket of vector fields cannot differentiate a multi-input matrix."""
    text = _read(rel)
    assert r"G_j(x)=G(x)e_j" in text
    assert r"[f,G_j](x)=DG_j(x)f(x)-Df(x)G_j(x)" in text
    assert r"[f,g](x)=DG(x)f(x)-Df(x)G(x)" not in text
    assert r"G_j=(0,h_j(q))" in text
    assert r"[f,G_j]=\begin{bmatrix}-h_j" in text
    assert r"G_1=(0,1)" in text
    assert r"[f,G_1]=(-1,0)" in text


@pytest.mark.parametrize(
    "rel",
    [
        "articles/The_Geometry_of_Motion/quarto/ch03_superposition.qmd",
        "articles/The_Geometry_of_Motion/Volume_I/chapters/ch03_superposition.tex",
    ],
)
def test_ch03_relative_degree_uses_declared_single_input_field(rel: str) -> None:
    """Lie derivatives must use the declared single column of the input map."""
    text = _read(rel)
    assert r"G_1(x)=G(x)" in text
    assert r"L_{G_1}L_f^kh=0" in text
    assert r"b(x)=L_{G_1}L_f^{r-1}h" in text
    assert r"L_gL_f" not in text


def test_print_chapters_keep_the_corrected_web_notation() -> None:
    """Print readers need the same tangent space, impulse interval and time endpoints."""
    foundations = _read("articles/The_Geometry_of_Motion/Volume_I/chapters/ch01_foundations.tex")
    assert r"T_T SE(3)=\{T\hat\xi:\hat\xi\in\mathfrak{se}(3)\}" in foundations
    variation = _read("articles/The_Geometry_of_Motion/Volume_I/chapters/ch02_variational.tex")
    assert r"\Phi(0.5,0.25)BJ_\tau=\Phi(0.25,0)BJ_\tau" in variation
    assert "by time invariance" in variation
    adjoint = _read("articles/The_Geometry_of_Motion/Volume_0/chapters/ch12_machine_learning.tex")
    assert "with fixed integration times $0$ and $T$" in adjoint
    assert "with fixed endpoints, define a column adjoint" not in adjoint


@pytest.mark.parametrize(
    "suffix", ["quarto/ch03_superposition.qmd", "Volume_I/chapters/ch03_superposition.tex"]
)
def test_pendulum_damping_has_a_declared_torque_coefficient(suffix: str) -> None:
    """Avoid reusing the rod-arm inertia constant d as undefined damping."""
    text = _read(f"articles/The_Geometry_of_Motion/{suffix}")
    assert r"-c_\tau/I" in text
    assert r"-d/I" not in text
    assert "N m s/rad" in text
    assert "Chapter 1" in text and "Chapter 2" in text


@pytest.mark.parametrize(
    "suffix", ["quarto/ch04_contraction.qmd", "Volume_I/chapters/ch04_contraction.tex"]
)
def test_contraction_chapter_declares_local_metric_and_multiplier_aliases(suffix: str) -> None:
    text = _read(f"articles/The_Geometry_of_Motion/{suffix}")
    for phrase in (
        "not the mechanical mass matrix",
        "CCM multiplier",
        "discrete contraction factor",
        "nonlinear discrete map",
        "disturbance bound",
        "generalized eigenvalue",
    ):
        assert phrase in text


@pytest.mark.parametrize(
    "rel",
    [
        "articles/The_Geometry_of_Motion/quarto/vol0_ch08_spatial_algebra.qmd",
        "articles/The_Geometry_of_Motion/quarto/vol0_ch09_product_of_exponentials.qmd",
        "articles/The_Geometry_of_Motion/quarto/vol0_ch10_articulated_body_algorithm.qmd",
        "articles/The_Geometry_of_Motion/quarto/vol0_ch11_lagrangian_mechanics.qmd",
        "articles/The_Geometry_of_Motion/quarto/vol0_ch12_machine_learning.qmd",
    ],
)
def test_volume0_spatial_chapters_include_notation_note(rel: str) -> None:
    assert "gom_spatial_algebra_notation_note.qmd" in _read(rel)


def test_volume2_entry_includes_control_affine_notation_note() -> None:
    assert "gom_volume2_control_affine_notation_note.qmd" in _read(
        "articles/The_Geometry_of_Motion/quarto/volume2.qmd"
    )


def test_volume2_content_uses_uppercase_input_map_notation() -> None:
    text = _read("articles/The_Geometry_of_Motion/quarto/volume2_content.qmd")
    assert r"\dot x=Ax+Gu" in text
    assert r"\dot x=Ax+gu" not in text
    assert r"\sum_i G_i(x)u_i" in text
    assert r"\sum_i g_i(x)u_i" not in text
    assert r"[G_i,G_j]=DG_j\,G_i-DG_i\,G_j" in text
    assert r"\sum_j(\sigma_j+N_je)\,dW_j" in text
    assert r"(g_j+N_je)" not in text


def test_notation_md_documents_volume2_sigma_diffusion() -> None:
    text = _read("NOTATION.md")
    assert "stochastic diffusion" in text.lower() or "diffusion direction" in text.lower()
    assert r"\sigma_j" in text
