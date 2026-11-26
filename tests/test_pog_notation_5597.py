"""Regression checks for Physics of Golf notation harmonization (Refs #5597)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
POG = ROOT / "articles" / "The_Physics_of_Golf"
NOTATION = ROOT / "NOTATION.md"

CH08 = (
    POG / "quarto" / "ch08_triple_pendulum.qmd",
    POG / "chapters" / "ch08_triple_pendulum.tex",
)
CH10 = (
    POG / "quarto" / "ch10_energy_transfer.qmd",
    POG / "chapters" / "ch10_energy_transfer.tex",
)
CH25 = (
    POG / "quarto" / "ch25_motor_learning.qmd",
    POG / "chapters" / "ch25_motor_learning.tex",
)

COM_DISTANCE_IN_CH08 = re.compile(r"m_[123]c_[123]|m_[123]L_[12]c_[23]")
GRAVITY_UPPERCASE_EOM = re.compile(r"M\\ddot\s*q\+h\+G")
DELIVERY_MAP_G = re.compile(r"\\bm\{y\}=G\(\\bm\{x\}")
AFFINE_B_INPUT = re.compile(r"\\bm\{f\}\(\\bm\{x\}\)\+B\(\\bm\{x\}\)\\bm\{u\}")


@pytest.mark.parametrize("path", CH08)
def test_ch08_com_distances_use_r_not_c(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert COM_DISTANCE_IN_CH08.search(text) is None
    assert "m_3r_3" in text
    assert re.search(r"c_3=\\beta", text) is not None


@pytest.mark.parametrize("path", CH10)
def test_ch10_gravity_vector_is_lowercase_g(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert GRAVITY_UPPERCASE_EOM.search(text) is None
    assert re.search(r"M\\ddot\s*q\+h\+g=\\tau", text) is not None


@pytest.mark.parametrize("path", CH25)
def test_ch25_reserves_uppercase_g_for_input_map(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert DELIVERY_MAP_G.search(text) is None
    assert AFFINE_B_INPUT.search(text) is None
    assert "\\mathcal{D}(\\bm{x},c)" in text
    assert "\\bm{G}(\\bm{x})\\bm{u}" in text


def test_notation_documents_pog_part_i_table() -> None:
    text = NOTATION.read_text(encoding="utf-8")
    assert "Physics of Golf Part I Multibody Symbols" in text
    rows = (
        [cell.strip() for cell in line.split("|")]
        for line in text.splitlines()
        if line.startswith("|")
    )
    row = next(cells for cells in rows if cells[1] == "**$r_i$**")
    assert row[2].startswith("COM distance")
    assert "Motor Control Delay and Activation" in text
    assert "Physics of Golf Contact Events and Launch Symbols" in text
    assert "**$Q_{\\mathrm{p}}$**" in text
    assert "**$\\sigma_L$**" in text


@pytest.mark.parametrize(
    "path",
    [POG / "quarto" / "ch32_putting.qmd", POG / "chapters" / "ch32_putting.tex"],
)
def test_ch32_ball_and_pendulum_masses_remain_distinct(path: Path) -> None:
    """The slip, normal-load, pendulum and impact laws identify their own mass."""
    text = path.read_text(encoding="utf-8")
    for expression in (
        r"I=\kappa m_bR^2",
        r"\frac{m_b\kappa}{2(1+\kappa)}",
        r"N=m_bg\cos\alpha",
        r"I_p\ddot\theta+m_agd\sin\theta",
        r"\frac{I_p}{m_ad}",
        r"v_b^+=(1+e)M U_h/(M+m_b)",
    ):
        assert expression in text
    assert "assembly mass" in text
    assert "ball mass" in text
    for ambiguous in (r"\kappa mR^2", r"+mgd\sin", "N=mg", "(M+m)"):
        assert ambiguous not in text


@pytest.mark.parametrize(
    "path",
    [POG / "quarto" / "ch32_putting.qmd", POG / "chapters" / "ch32_putting.tex"],
)
def test_ch32_declares_local_angle_and_inertia_notation(path: Path) -> None:
    """A reader crossing from launch mechanics can distinguish the local symbols."""
    text = path.read_text(encoding="utf-8")
    assert "slope angle" in text and "attack angle" in text
    assert "inertia factor" in text and "inverse effective mass" in text


@pytest.mark.parametrize(
    "path",
    [
        POG / "quarto" / "ch29_joint_damping_friction.qmd",
        POG / "chapters" / "ch29_joint_damping_friction.tex",
    ],
)
def test_ch29_gyroscopic_and_damping_symbols_are_distinct(path: Path) -> None:
    """Stability and mobility use Gamma/D; G and C retain their dynamics roles."""
    text = path.read_text(encoding="utf-8")
    assert r"\mathbf M\ddot{\boldsymbol\xi}+(\boldsymbol\Gamma+\mathbf D)" in text
    assert r"\dot E=-\dot{\boldsymbol\xi}^T\mathbf D\dot{\boldsymbol\xi}" in text
    assert r"i\omega(\boldsymbol\Gamma+\mathbf D)" in text
    assert r"\boldsymbol\Gamma=\begin{bmatrix}0&-3\\3&0\end{bmatrix}" in text
    assert r"\mathbf D=0.1\mathbf I" in text
    assert r"\mathbf G+\mathbf C" not in text
    assert r"\mathbf C=0" not in text
    assert r"-\mathbf D_{\rm cart}(\dot{\mathbf r}-\dot{\mathbf r}_d)" in text
    assert "gyroscopic matrix" in text
    assert "perturbation displacement" in text


@pytest.mark.parametrize(
    "path",
    [
        POG / "quarto" / "ch29_joint_damping_friction.qmd",
        POG / "chapters" / "ch29_joint_damping_friction.tex",
    ],
)
def test_ch29_null_basis_is_distinct_from_coordinate_rate_map(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert r"\bm N(\bm q)\bm v" in text
    assert r"\mathbf J_c\mathbf Z=0" in text
    assert r"\mathbf D_r=\mathbf Z^T\mathbf D\mathbf Z" in text
    assert "full column rank" in text
    assert r"\mathbf N\dot{\mathbf s}" not in text


@pytest.mark.parametrize(
    "path",
    [
        POG / "quarto" / "ch29_joint_damping_friction.qmd",
        POG / "chapters" / "ch29_joint_damping_friction.tex",
    ],
)
def test_ch29_full_bias_includes_declared_passive_damping(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert r"h(q,v)=C(q,v)v+D(q)v+g(q)" in text
    assert r"(f_0+f_d)_v=-M(q)^{-1}h(q,v)" in text
    assert "full-bias convention" in text


CH18 = (
    POG / "quarto" / "ch18_inverse_dynamics_parallel.qmd",
    POG / "chapters" / "ch18_inverse_dynamics_parallel.tex",
)
CH19 = (
    POG / "quarto" / "ch19_aerodynamic_drag.qmd",
    POG / "chapters" / "ch19_aerodynamic_drag.tex",
)
CH14 = (
    POG / "quarto" / "ch14_complete_swing.qmd",
    POG / "chapters" / "ch14_complete_swing.tex",
)
CH28 = (
    POG / "quarto" / "ch28_impact_collision.qmd",
    POG / "chapters" / "ch28_impact_collision.tex",
)
CH31 = (
    POG / "quarto" / "ch31_swing_plane_launch.qmd",
    POG / "chapters" / "ch31_swing_plane_launch.tex",
)
CH23 = (
    POG / "quarto" / "ch23_dof_urdf_models.qmd",
    POG / "chapters" / "ch23_dof_urdf_models.tex",
)


@pytest.mark.parametrize("path", CH18)
def test_ch18_disambiguates_input_dimension_residual_and_passive_loads(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert r"u\in\mathbb R^m" in text
    assert r"Q_{\mathrm{p}}" in text
    assert r"Az_\ell=\varrho" in text
    assert r"At constant constraint rank $\rho$" in text
    assert "r=M\\ddot q+h-p-Q_e" not in text
    assert "u\\in\\mathbb R^p" not in text


@pytest.mark.parametrize("path", CH19)
def test_ch19_passive_loads_use_q_p_not_rhs_p(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert r"M\ddot q+h=Bu+Q_{\mathrm{p}}+Q_{\rm aero}" in text
    assert "full-bias convention" in text
    assert r"M\ddot q+h=Bu+p+" not in text


@pytest.mark.parametrize("path", CH14 + CH31)
def test_contact_events_use_psi_not_gravity_g(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert r"\psi(x,t)=0" in text or r"\psi(x(T))=0" in text
    assert "g(x,t)=0" not in text
    assert "g(x(T))=0" not in text


@pytest.mark.parametrize("path", CH28 + CH31)
def test_spin_loft_uses_sigma_l_not_transition_phi(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert r"\cos\sigma_L" in text
    assert r"\Phi=\arccos(n^T\hat v)" not in text


@pytest.mark.parametrize("path", CH31)
def test_ch31_face_weight_and_wind_symbols_are_distinct(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert r"w_{\mathrm{face}}" in text
    assert "v_w(r_B,t)" in text
    assert r"C\Phi(T,s)G(x(s))" in text
    assert r"\lambda\simeq w\phi" not in text
    assert "v_B-w(r_B,t)" not in text


@pytest.mark.parametrize("path", CH31)
def test_ch31_sensitivity_example_and_exercises_use_w_face(path: Path) -> None:
    """The bare weight symbol must not survive in sensitivity, example or exercises."""
    text = path.read_text(encoding="utf-8")
    assert r"R\sec^2\lambda\,w_{\mathrm{face}}" in text
    assert r"R\sec^2\lambda\,(1-w_{\mathrm{face}})" in text
    assert text.count(r"$w_{\mathrm{face}}=0.76$") >= 3
    assert r"constant $w_{\mathrm{face}}$" in text
    for bare in (r"$w=0.76$", "constant $w$", r"\,w,", r"(1-w)"):
        assert bare not in text, bare


@pytest.mark.parametrize("path", CH23)
def test_ch23_mass_metric_projector_is_not_a_null_basis(path: Path) -> None:
    """The square projector onto ker J is P_M; N stays a null basis."""
    text = path.read_text(encoding="utf-8")
    assert r"P_M=I-\bar J J" in text
    assert r"JP_M=0" in text
    assert r"P_M^T\tau_0" in text
    assert r"JM^{-1}P_M^T=0" in text
    assert "mass-metric projector" in text
    assert "null-space basis" in text
    assert r"N=I-\bar J J" not in text
    assert r"Construct $\bar J$, $N$ and $N^T$" not in text
    assert r"Construct $\bar J$, $P_M$ and $P_M^T$" in text


def test_notation_names_the_ch23_mass_metric_projector() -> None:
    """NOTATION.md records the Chapter 23 mass-metric projector."""
    text = NOTATION.read_text(encoding="utf-8")
    assert "Physics of Golf Mass-Metric Projector" in text
    assert "**$P_M$**" in text
