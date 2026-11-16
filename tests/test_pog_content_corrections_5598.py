"""Regression checks for Physics of Golf content corrections (Fixes #5598)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[1]
POG = ROOT / "articles" / "The_Physics_of_Golf"
QUARTO = POG / "quarto"
CHAPTERS = POG / "chapters"

CH08 = (QUARTO / "ch08_triple_pendulum.qmd", CHAPTERS / "ch08_triple_pendulum.tex")
CH13 = (QUARTO / "ch13_interdisciplinary.qmd", CHAPTERS / "ch13_interdisciplinary.tex")
CH18 = (
    QUARTO / "ch18_inverse_dynamics_parallel.qmd",
    CHAPTERS / "ch18_inverse_dynamics_parallel.tex",
)
CH19 = (QUARTO / "ch19_aerodynamic_drag.qmd", CHAPTERS / "ch19_aerodynamic_drag.tex")
CH23 = (QUARTO / "ch23_dof_urdf_models.qmd", CHAPTERS / "ch23_dof_urdf_models.tex")
CH06 = QUARTO / "ch06_zero_torque_counterfactual.qmd"
CH09B = (QUARTO / "ch09b_passive_stabilization.qmd", CHAPTERS / "ch09b_passive_stabilization.tex")
CH24 = QUARTO / "ch24_motor_control_brain.qmd"
CH12 = (QUARTO / "ch12_fascia.qmd", CHAPTERS / "ch12_fascia.tex")

CH13_PERCENT_IN_MATH = re.compile(r"\$43\.33%")
WITHDRAWN_REBUTTAL = re.compile(
    r"\bwithdrawn\b|earlier chapter asserted|previous(?:ly)? unsourced|"
    r"The previous shoulder|fixes the reversed limits in the previous",
    re.IGNORECASE,
)


@pytest.mark.parametrize("path", CH13)
def test_ch13_collision_percent_is_escaped_in_math(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert r"43.33\%" in text
    assert "$43.33%" not in text


@pytest.mark.parametrize("path", CH18)
def test_ch18_piezo_relation_is_strain_charge_form(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert "strain-charge form" in text
    assert "stress-charge form" not in text
    assert "permittivity at" in text
    assert "constant stress" in text


def test_ch19_shaft_crossflow_coefficient_matches_subcritical_re() -> None:
    text = (CH19[0]).read_text(encoding="utf-8")
    assert "C_n\\approx1.1" in text or "C_n\\approx 1.1" in text
    assert "1.54131 N m" in text
    assert "C_n=0.5" not in text
    density, coefficient, diameter, omega, length = 1.225, 1.1, 0.01, 25.0, 1.1
    prefactor = 0.5 * density * coefficient * diameter * omega**2
    moment = quad(lambda s: prefactor * s**3, 0, length)[0]
    assert moment == pytest.approx(1.54131, rel=1e-4)


@pytest.mark.parametrize("path", CH23)
def test_ch23_serial_shoulder_rank_loss_is_mechanism_singularity(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert "mechanism singularity of the modelled joint" in text
    assert "chart's gimbal-lock" not in text


def test_pog_quarto_has_no_reader_facing_withdrawn_rebuttal_residue() -> None:
    """F13: editorial 'withdrawn' sentences should not appear in published chapters."""
    offenders: list[str] = []
    for path in sorted(QUARTO.glob("ch*.qmd")):
        if WITHDRAWN_REBUTTAL.search(path.read_text(encoding="utf-8")):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


@pytest.mark.parametrize("path", CH09B)
def test_ch09b_stiffness_pulse_hypotheses_are_forward_stated(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert "Three hypotheses are sometimes proposed" in text
    assert "The earlier chapter asserted" not in text


def test_ch06_angle_datum_differs_from_part_i_vertical_convention() -> None:
    text = CH06.read_text(encoding="utf-8")
    assert "measures $q_1$ from the horizontal $x$-axis" in text
    assert "Chapters 3--5 and 8" in text


@pytest.mark.parametrize("path", CH08)
def test_ch08_mass_matrix_matches_worked_example_configuration(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert "At $q=(50,80,100)^\\circ$, the same configuration used in the bias" in text
    assert "At $q=(50,90,100)^\\circ$" not in text
    assert "c_1&=-2v_1v_2" in text
    assert "c_2&=-2\\gamma v_1v_3" in text
    assert "(-79.666,-25.210,15.127)" in text


def test_ch24_stretch_response_bands_cover_contiguous_latencies() -> None:
    text = CH24.read_text(encoding="utf-8")
    assert "20--45 ms" in text
    assert "extending to about 50 ms" in text
    assert "50--100 ms" in text


@pytest.mark.parametrize("path", CH12)
def test_ch12_fascia_does_not_withdraw_reader_facing_claim(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert "is therefore withdrawn" not in text


@pytest.mark.parametrize("path", CH13)
def test_ch13_does_not_use_unescaped_percent_in_collision_fraction_math(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert CH13_PERCENT_IN_MATH.search(text) is None
