"""Publication and arithmetic checks for Physics of Golf issue #5599 worked slices."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
POG = REPO / "articles" / "The_Physics_of_Golf"
CH28 = (
    POG / "quarto/ch28_impact_collision.qmd",
    POG / "chapters/ch28_impact_collision.tex",
)

M_HEAD = 0.200
M_BALL = 0.04593
E_COR = 0.83
R_OFFSET = 0.020
I_ZZ = 4.5e-4


def _read_pair() -> tuple[str, str]:
    return CH28[0].read_text(encoding="utf-8"), CH28[1].read_text(encoding="utf-8")


def effective_mass(mass: float, offset: float, inertia_zz: float) -> float:
    inverse = 1 / mass + offset**2 / inertia_zz
    return 1 / inverse


def ball_speed_ratio(e: float, m_ball: float, m_eff: float) -> float:
    return (1 + e) / (1 + m_ball / m_eff)


def test_ch28_off_centre_worked_numbers_match_rigid_impulse_model() -> None:
    m_eff = effective_mass(M_HEAD, R_OFFSET, I_ZZ)
    assert m_eff == pytest.approx(0.1698, rel=1e-3)
    centred = ball_speed_ratio(E_COR, M_BALL, M_HEAD)
    offset = ball_speed_ratio(E_COR, M_BALL, m_eff)
    assert centred == pytest.approx(1.488, rel=1e-3)
    assert offset == pytest.approx(1.440, rel=1e-3)
    assert (offset - centred) / centred == pytest.approx(-0.0322, rel=0.02)


@pytest.mark.parametrize("edition", CH28, ids=("web", "print"))
def test_ch28_carries_effective_mass_derivation_and_gear_closure(edition: Path) -> None:
    text = edition.read_text(encoding="utf-8")
    assert "effective_mass_derivation" in text
    assert "gear_effect_spin_closure" in text
    for token in (
        r"\Delta\mathbf v_P",
        r"\Delta\boldsymbol\omega",
        "friction",
        "Jorgensen",
    ):
        assert token.replace("\\", "") in text.replace("\\", "") or token in text
    assert "5.889" in text
    assert "gear_effect_impact" in text


@pytest.mark.parametrize("edition", CH28, ids=("web", "print"))
def test_ch28_normal_projection_and_gear_geometry(edition: Path) -> None:
    """The normal-only offset cannot generate tangential contact motion."""
    text = edition.read_text(encoding="utf-8")
    assert r"\hat n\cdot\Delta\mathbf v_P" in text
    assert "normal velocity" in text
    assert "front-to-back" in text
    assert "laboratory frame" in text
    assert "2.7" not in text
    assert "@ex-gear_effect" not in text
    assert r"\ref{ex:gear_effect}" not in text


def test_centrifugal_stiffening_ratio_in_ch11() -> None:
    chapter = (POG / "quarto/ch11_flexible_shaft.qmd").read_text(encoding="utf-8")
    tension = 0.20 * 45**2 / 1.5
    euler_scale = 40 * np.pi**2 / 4
    ratio = tension * 1.0**2 / 40
    assert "6.8" in chapter
    assert tension == pytest.approx(270, rel=0.02)
    assert euler_scale == pytest.approx(99.0, rel=0.02)
    assert ratio == pytest.approx(6.75, rel=0.02)


def test_isb_jcs_subsection_present_in_ch22() -> None:
    text = (POG / "quarto/ch22_anatomy_joint_modeling.qmd").read_text(encoding="utf-8")
    assert "sec-isb_jcs" in text
    assert "Grood1983" in text
    assert "Y–X–Y" in text or "Y-X-Y" in text


def test_urdf_format_table_and_mjcf_snippet_in_ch23() -> None:
    text = (POG / "quarto/ch23_dof_urdf_models.qmd").read_text(encoding="utf-8")
    assert "revolute" in text and "planar" in text
    assert "SDF" in text
    assert "<weld" in text or "weld name" in text


def test_putting_worked_answers_and_capture_figure() -> None:
    text = (POG / "quarto/ch32_putting.qmd").read_text(encoding="utf-8")
    assert "sec-putting_worked_answers" in text
    assert "2.2857" in text
    assert "putting_break_capture" in text
    assert "Holmes1991" in text


def test_reported_range_tables_in_ch30_and_ch31() -> None:
    ch30 = (POG / "quarto/ch30_kinetic_chain.qmd").read_text(encoding="utf-8")
    ch31 = (POG / "quarto/ch31_swing_plane_launch.qmd").read_text(encoding="utf-8")
    assert "tbl-kinetic-chain-ranges" in ch30
    assert "tbl-launch-ranges" in ch31
