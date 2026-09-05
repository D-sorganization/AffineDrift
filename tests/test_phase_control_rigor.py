"""Independent checks for phase control, zero dynamics, and impact claims."""

from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad, solve_ivp

ROOT = Path(__file__).resolve().parents[1]


def test_curved_configuration_lift_retains_speed_and_acceleration() -> None:
    time = 0.7
    phase, speed, acceleration = time**2, 2 * time, 2.0
    tangent = np.array([1.0, 2 * phase])
    curvature = np.array([0.0, 2.0])
    lifted = curvature * speed**2 + tangent * acceleration
    assert lifted == pytest.approx([2.0, 12 * time**2])
    assert not np.allclose(lifted, tangent * acceleration)


def test_single_valued_periodic_phase_has_zero_net_change() -> None:
    integrated = quad(lambda time: np.cos(time), 0, 2 * np.pi)[0]
    assert integrated == pytest.approx(0, abs=1e-12)
    assert np.cos(np.pi) < 0


def test_positive_nominal_phase_rate_does_not_prevent_stalling() -> None:
    # s'=v, v'=u. Nominal u=0 has progress; admissible u=-1 stops it.
    solution = solve_ivp(lambda _t, x: [x[1], -1], (0, 1), [0, 1])
    assert solution.success
    assert solution.y[:, -1] == pytest.approx([0.5, 0], abs=1e-12)


def test_position_constraint_without_tangent_velocity_is_not_invariant() -> None:
    solution = solve_ivp(lambda _t, x: [x[1], 0], (0, 0.1), [0, 1])
    assert solution.success
    assert solution.y[0, -1] == pytest.approx(0.1)


def test_regular_output_can_have_singular_actuation_decoupling() -> None:
    derivative = np.array([[0.0, 1.0]])
    input_map = np.array([[1.0], [0.0]])
    assert np.linalg.matrix_rank(derivative) == 1
    assert (derivative @ input_map).item() == 0


def test_output_regulation_does_not_stabilize_internal_dynamics() -> None:
    def dynamics(_time: float, state: np.ndarray) -> list[float]:
        q1, q2, v1, v2 = state
        control = q2 - 2 * (v1 - v2) - (q1 - q2)
        return [v1, v2, control, q2]

    solution = solve_ivp(dynamics, (0, 2), [1.3, 1, 0.8, 1], rtol=1e-10, atol=1e-12)
    assert solution.success
    time = solution.t
    error = solution.y[0] - solution.y[1]
    assert error == pytest.approx((0.3 + 0.1 * time) * np.exp(-time), abs=2e-10)
    assert solution.y[1] == pytest.approx(np.exp(time), rel=1e-9)
    assert abs(error[-1]) < abs(error[0])
    assert solution.y[1, -1] > 7


def test_parabolic_virtual_constraint_requires_active_power() -> None:
    solution = solve_ivp(lambda _t, x: [x[2], x[3], 2 * x[3] ** 2, 0], (0, 2), [0, 0, 0, 1])
    assert solution.success
    q1, q2, v1, v2 = solution.y
    assert q1 == pytest.approx(q2**2, abs=1e-12)
    assert v1 == pytest.approx(2 * q2 * v2)
    power = v1 * (2 * v2**2)
    work = quad(lambda time: 4 * time, 0, 2)[0]
    energy_change = (v1[-1] ** 2 + v2[-1] ** 2 - 1) / 2
    assert power[-1] == pytest.approx(8)
    assert work == pytest.approx(energy_change)


def test_ideal_stationary_constraint_reaction_has_zero_power() -> None:
    position, speed, multiplier = 0.7, 1.2, 4.0
    gradient = np.array([1.0, -2 * position])
    velocity = np.array([2 * position * speed, speed])
    assert (multiplier * gradient) @ velocity == pytest.approx(0, abs=1e-12)
    assert np.linalg.norm(multiplier * gradient) > 0


def test_plastic_reset_can_break_virtual_velocity_constraint() -> None:
    mass = np.eye(2)
    contact = np.array([[0.0, 1.0]])
    before = np.array([1.0, 1.0])
    inverse_contact = np.linalg.solve(mass, contact.T)
    impulse = -np.linalg.solve(contact @ inverse_contact, contact @ before)
    after = before + inverse_contact @ impulse
    assert after == pytest.approx([1, 0])
    assert contact @ after == pytest.approx([0])
    assert mass @ (after - before) == pytest.approx(contact.T @ impulse)
    assert before[0] - before[1] == 0
    assert after[0] - after[1] == 1


def test_same_configuration_path_different_speed_changes_impact_energy() -> None:
    tangent = np.array([1.0, 2.0])
    mass = np.diag([2.0, 3.0])

    def energy(speed: float) -> float:
        return float(0.5 * speed**2 * (tangent @ mass @ tangent))

    assert energy(2) == pytest.approx(4 * energy(1))


@pytest.mark.parametrize(
    "source",
    [
        "articles/The_Geometry_of_Motion/Volume_II/chapters/ch08_phase_variable_control.tex",
        "articles/motion-control/chapter8.tex",
        "articles/motion-control/Control_Is_Motion_Complete.tex",
        "articles/The_Geometry_of_Motion/quarto/volume2_content.qmd",
    ],
)
def test_all_editions_separate_coordination_progress_and_impact(source: str) -> None:
    text = (ROOT / source).read_text(encoding="utf-8")
    if source.endswith(".qmd"):
        text = text.split("## Phase-Variable Control", 1)[1].split("## Stochastic Trajectories", 1)[
            0
        ]
    else:
        text = text.split(r"\chapter{Phase-Variable Control}", 1)[1].split(
            r"\chapter{Stochastic Trajectories", 1
        )[0]
    for required in [
        r"Dh(q)v=0",
        "2(n-k)",
        "Near rank loss",
        "internal dynamics",
        "external impulse",
        "quadruples",
        "held-out impact outcomes",
        "https://grizzle.robotics.umich.edu/files/HZD_HandbookApril2015.pdf",
        "q_d''(s)",
    ]:
        assert required in text
    for incorrect in [
        "astonishingly robust",
        "dictated by conservation of momentum",
        "entire complexity",
        "publication-safe",
    ]:
        assert incorrect not in text
