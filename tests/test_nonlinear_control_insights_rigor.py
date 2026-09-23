"""Independent counterexamples supporting the nonlinear-control article."""

from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import solve_ivp

from tests.test_zero_torque_chapter_rigor import _bias, _mass, _potential

ROOT = Path(__file__).resolve().parents[1]


def test_braking_changes_relative_and_absolute_acceleration_differently() -> None:
    """Reuse the independently qualified Cartesian rod model from Chapter 6."""
    angles, rates = np.deg2rad([45, 70]), np.array([8.0, 12.0])
    mass = _mass(angles)
    velocity, gravity = _bias(angles, rates)
    baseline = np.linalg.solve(mass, -velocity - gravity)
    increment = np.linalg.solve(mass, [-2.0, 0.0])
    assert increment == pytest.approx([-14.721123, 24.790964], abs=1e-6)
    assert baseline + increment == pytest.approx([-3.021639, -94.462667], abs=1e-6)
    assert increment.sum() == pytest.approx(10.069841, abs=1e-6)
    assert increment[1] > 0 > (baseline + increment)[1]


@pytest.mark.parametrize("torque", [-2.0, 0.0, 2.0])
def test_total_energy_rate_matches_work_despite_coupled_acceleration(torque: float) -> None:
    """Differentiate Cartesian kinetic plus gravitational energy along the flow."""
    angles, rates = np.deg2rad([45, 70]), np.array([8.0, 12.0])
    velocity, gravity = _bias(angles, rates)
    applied = np.array([torque, 0.0])
    acceleration = np.linalg.solve(_mass(angles), applied - velocity - gravity)
    step = 1e-6
    plus_angles, minus_angles = angles + step * rates, angles - step * rates
    plus_rates, minus_rates = rates + step * acceleration, rates - step * acceleration
    plus_energy = 0.5 * plus_rates @ _mass(plus_angles) @ plus_rates + _potential(plus_angles)
    minus_energy = 0.5 * minus_rates @ _mass(minus_angles) @ minus_rates + _potential(minus_angles)
    assert (plus_energy - minus_energy) / (2 * step) == pytest.approx(rates @ applied, abs=1e-7)


def test_underactuation_does_not_require_nonzero_drift() -> None:
    """A horizontal two-coordinate inertial plant at rest has zero drift."""
    mass, input_map = np.eye(2), np.array([[1.0], [0.0]])
    assert np.linalg.matrix_rank(np.linalg.solve(mass, input_map)) == 1
    drift = np.concatenate((np.zeros(2), np.linalg.solve(mass, np.zeros(2))))
    assert drift == pytest.approx(np.zeros(4))


@pytest.mark.parametrize("control", [-0.5, 0.0, 0.5])
def test_full_field_span_does_not_allow_reversal_of_bounded_drift(control: float) -> None:
    """xdot=1+u, |u|<=1/2 is accessible but cannot move left from its start."""
    assert np.linalg.matrix_rank(np.array([[1.0, 1.0]])) == 1
    solution = solve_ivp(lambda _time, _state: [1 + control], (0, 0.1), [0])
    assert solution.y[0, -1] == pytest.approx(0.1 * (1 + control))
    assert solution.y[0, -1] > 0


@pytest.mark.parametrize("duration", [0.01, 0.1, 0.2])
def test_position_authority_of_double_integrator_scales_with_time_squared(duration: float) -> None:
    """Integrate a saturating input and a smaller sinusoid from equal initial states."""
    acceleration_bound = 2.0
    for fraction in [lambda _time: 1.0, lambda time: np.sin(time / duration)]:
        solution = solve_ivp(
            lambda time, state, profile=fraction: [state[1], acceleration_bound * profile(time)],
            (0, duration),
            [0, 0],
            rtol=1e-10,
            atol=1e-12,
        )
        assert abs(solution.y[0, -1]) <= acceleration_bound * duration**2 / 2 + 1e-10


@pytest.mark.parametrize("duration", [0.01, 0.05])
def test_reversible_driftless_commutator_has_quadratic_displacement(duration: float) -> None:
    """Integrate four feasible flows, independently of the bracket derivative formula."""
    state = np.zeros(2)
    for first, second in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
        solution = solve_ivp(
            lambda _time, point, inputs=(first, second): [inputs[0], point[0] * inputs[1]],
            (0, duration),
            state,
            rtol=1e-10,
            atol=1e-12,
        )
        state = solution.y[:, -1]
    assert state == pytest.approx([0, duration**2], abs=1e-12)


def test_nonlinear_coordinate_change_needs_velocity_squared_term() -> None:
    """For y=q² and qddot=-q, yddot=2v²-2q² on the chart q>0."""
    position, velocity = 2.0, 3.0
    direct = solve_ivp(
        lambda _time, state: [state[1], -state[0]],
        (0, 0.02),
        [position, velocity],
        rtol=1e-11,
        atol=1e-13,
    )
    transformed = solve_ivp(
        lambda _time, state: [state[1], state[1] ** 2 / (2 * state[0]) - 2 * state[0]],
        (0, 0.02),
        [position**2, 2 * position * velocity],
        rtol=1e-11,
        atol=1e-13,
    )
    final_position, final_velocity = direct.y[:, -1]
    assert transformed.y[:, -1] == pytest.approx(
        [final_position**2, 2 * final_position * final_velocity], rel=1e-9
    )


def test_feedback_input_origin_changes_the_zero_input_baseline() -> None:
    """Invertible input reparameterization preserves the family, not its zero slice."""
    drift, gain, offset, scale = 3.0, 2.0, -1.0, 4.0
    zero_new_input_rate = drift + gain * offset
    assert zero_new_input_rate != drift
    for new_input in [-0.2, 0, 0.4]:
        assert drift + gain * (offset + scale * new_input) == pytest.approx(
            zero_new_input_rate + gain * scale * new_input
        )


def test_article_uses_verified_example_and_removes_known_false_claims() -> None:
    """Keep the published arithmetic synchronized with independently checked values."""
    source = (ROOT / "articles/nonlinear-control-insights.qmd").read_text(encoding="utf-8")
    for value in ["14.721123", "24.790964", "94.462667", "10.069841"]:
        assert value in source, f"Missing checked acceleration {value}"
    for obsolete in [
        "Drift is not instantaneous",
        "no muscular torque of any kind",
        "proximal braking amplifies distal speed",
        "at high speed, this local geometric picture is irrelevant",
        "Seek Timestamps",
    ]:
        assert obsolete not in source
    assert "_generated/trust/critique-annotations/nonlinear-control-insights.qmd" in source
