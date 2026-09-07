"""Independent checks of the corrected contraction critique's arguments."""

from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import expm, solve_continuous_are, solve_discrete_are
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "articles/tangent-hyperplane-articles/Advanced/Contraction_Tangent_CRITIC.qmd"


def test_original_inverse_optimal_example_constructs_valid_costs() -> None:
    dynamics = np.array([[-2.0, 1.0], [0.0, -3.0]])
    for metric in (np.eye(2), np.diag([2.0, 1.0])):
        cost = -(dynamics.T @ metric + metric @ dynamics)
        assert np.linalg.eigvalsh(cost).min() > 0
        np.testing.assert_allclose(dynamics.T @ metric + metric @ dynamics + cost, 0)
    np.testing.assert_allclose(np.linalg.eigvalsh(cost), [7 - np.sqrt(5), 7 + np.sqrt(5)])


def test_prescribed_stable_feedback_can_fail_inverse_optimal_stationarity() -> None:
    plant, input_gain, feedback, metric = -1.0, 1.0, -0.5, 1.0
    closed_loop = plant - input_gain * feedback
    assert 2 * closed_loop * metric < 0
    required_input_cost = input_gain * metric / feedback
    assert required_input_cost < 0


def test_continuous_riccati_identity_requires_the_closed_loop() -> None:
    dynamics = np.array([[0.0, 1.0], [1.0, -0.2]])
    inputs = np.array([[0.0], [1.0]])
    state_cost, input_cost = np.diag([2.0, 1.0]), np.array([[0.7]])
    value = solve_continuous_are(dynamics, inputs, state_cost, input_cost)
    gain = np.linalg.solve(input_cost, inputs.T @ value)
    closed = dynamics - inputs @ gain
    dissipation = state_cost + gain.T @ input_cost @ gain
    np.testing.assert_allclose(closed.T @ value + value @ closed, -dissipation, atol=1e-13)
    assert np.linalg.eigvalsh(dynamics.T @ value + value @ dynamics).max() > 0


def test_differential_riccati_material_derivative_cancels_correctly() -> None:
    dynamics = np.array([[0.0, 1.0], [-2.0, 0.0]])
    inputs = np.array([[0.0], [1.0]])
    value = np.array([[2.0, 0.3], [0.3, 1.0]])
    state_cost = np.eye(2)
    gain = inputs.T @ value
    value_dot = -(dynamics.T @ value + value @ dynamics - value @ inputs @ gain + state_cost)
    closed = dynamics - inputs @ gain
    np.testing.assert_allclose(
        value_dot + closed.T @ value + value @ closed, -state_cost - gain.T @ gain
    )


def test_finite_horizon_value_can_degenerate_at_the_terminal_time() -> None:
    horizon = 1.0
    times = np.array([0.0, 0.5, 1.0])
    value = horizon - times
    state = np.ones(3)
    assert value[-1] == 0
    assert value[0] * state[0] ** 2 > value[-1] * state[-1] ** 2
    np.testing.assert_array_equal(state, 1)


def test_growing_scalar_metric_cancels_decay_instead_of_certifying_it() -> None:
    times = np.linspace(0.0, 2.0, 5)
    metric, state = np.exp(2 * times), np.exp(-times)
    np.testing.assert_allclose(metric * state**2, 1)
    np.testing.assert_allclose(2 * metric - 2 * metric, 0)


def test_condition_number_one_does_not_control_metric_scale() -> None:
    times = np.array([0.0, 1.0, 2.0])
    metric, state = np.exp(-4 * times), np.exp(times)
    np.testing.assert_allclose(metric * state**2, np.exp(-2 * times))
    assert state[-1] > state[0]
    for weight in metric:
        assert np.linalg.cond(weight * np.eye(2)) == 1


def test_nonlinear_coordinate_covariance_needs_the_moving_jacobian() -> None:
    position = 0.7
    jacobian = 1 + 3 * position**2
    jacobian_dot = -6 * position**2
    transformed_dynamics = -1 + jacobian_dot / jacobian
    transformed_metric = jacobian**-2
    metric_dot = -2 * jacobian_dot / jacobian**3
    assert metric_dot + 2 * transformed_dynamics * transformed_metric == pytest.approx(
        -2 / jacobian**2
    )
    assert transformed_dynamics != -1


def test_task_pullback_can_be_degenerate_on_the_full_state() -> None:
    jacobian = np.array([[1.0, 0.0, 1.0], [0.0, 1.0, 0.0]])
    pullback = jacobian.T @ jacobian
    hidden = np.array([1.0, 0.0, -1.0])
    assert hidden @ pullback @ hidden == 0
    assert np.linalg.matrix_rank(pullback) == 2


def test_discrete_riccati_decay_and_conservative_bound_are_valid() -> None:
    dynamics = np.array([[1.0, 0.1], [0.0, 1.0]])
    inputs = np.array([[0.005], [0.1]])
    state_cost, input_cost = np.eye(2), np.array([[1.0]])
    value = solve_discrete_are(dynamics, inputs, state_cost, input_cost)
    gain = np.linalg.solve(input_cost + inputs.T @ value @ inputs, inputs.T @ value @ dynamics)
    closed = dynamics - inputs @ gain
    dissipation = state_cost + gain.T @ input_cost @ gain
    np.testing.assert_allclose(closed.T @ value @ closed, value - dissipation, atol=1e-12)
    weaker = 1 - np.linalg.eigvalsh(state_cost).min() / np.linalg.eigvalsh(value).max()
    stronger = 1 - np.linalg.eigvalsh(dissipation).min() / np.linalg.eigvalsh(value).max()
    assert 0 < stronger <= weaker < 1
    assert -np.log(stronger) / 2 < -np.log(stronger)


@pytest.mark.parametrize("weight", [1.0, 10.0, 1000.0])
def test_quadratic_penalty_does_not_enforce_exact_feasibility(weight: float) -> None:
    optimum = 1 / (1 + weight)
    assert optimum > 0
    assert 2 * (optimum - 1) + 2 * weight * optimum == pytest.approx(0)


def test_mechanical_energy_has_no_strict_rate_at_zero_velocity() -> None:
    mass, stiffness, damping = 1.0, 4.0, 4.0
    error = np.array([1.0, 0.0])
    dynamics = np.array([[0.0, 1.0], [-stiffness / mass, -damping / mass]])
    energy_metric = np.diag([stiffness, mass])
    assert error @ energy_metric @ error > 0
    assert error @ (dynamics.T @ energy_metric + energy_metric @ dynamics) @ error == 0


def test_critical_damping_has_a_jordan_polynomial_at_the_spectral_rate() -> None:
    dynamics = np.array([[0.0, 1.0], [-1.0, -2.0]])
    initial = np.array([1.0, 0.0])
    for time in (1.0, 5.0, 10.0):
        state = expm(dynamics * time) @ initial
        np.testing.assert_allclose(state, np.exp(-time) * np.array([1 + time, -time]))
        assert np.linalg.norm(state) / np.exp(-time) > time


def test_ou_noise_floor_is_not_removed_by_deterministic_contraction() -> None:
    rate, diffusion = 2.0, 0.4
    stationary_variance = diffusion**2 / (2 * rate)
    assert stationary_variance == pytest.approx(0.04)
    assert -2 * rate * stationary_variance + diffusion**2 == pytest.approx(0)


def test_contracting_flows_can_be_overcome_by_periodic_resets() -> None:
    flow_rate, interval, reset_gain = 1.0, 0.1, 2.0
    factor = reset_gain * np.exp(-flow_rate * interval)
    assert factor > 1
    assert factor**10 > 1


def test_wilson_interval_for_hypothetical_successes_has_nonzero_uncertainty() -> None:
    observed = binomtest(94, 100).proportion_ci(method="wilson")
    perfect = binomtest(100, 100).proportion_ci(method="wilson")
    assert observed.low == pytest.approx(0.875, abs=0.001)
    assert observed.high == pytest.approx(0.972, abs=0.001)
    assert perfect.low == pytest.approx(0.963, abs=0.001)
    assert perfect.high == 1


@pytest.mark.parametrize(
    "phrase",
    [
        "The Critique's Proposed Data Were Not Observations",
        "A Penalty Is a Search Device",
        "A Coordinate Representation Can Express an Intrinsic Result",
    ],
)
def test_critique_explicitly_replaces_its_incorrect_repairs(phrase: str) -> None:
    assert phrase in SOURCE.read_text(encoding="utf-8")
