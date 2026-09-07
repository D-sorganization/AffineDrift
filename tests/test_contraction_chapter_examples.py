"""Independent matrix, flow and noise checks for the contraction chapter."""

import importlib
from typing import Any

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.linalg import expm, solve_continuous_lyapunov


@pytest.fixture(scope="module")
def example() -> Any:
    """Keep physical contracts collectable before the example module exists."""
    return importlib.import_module("src.tools.contraction_examples")


@pytest.mark.parametrize("scale", [0.2, 1.0, 5.0])
def test_metric_rate_matches_independent_linear_flow(example: Any, scale: float) -> None:
    """Metric scaling cannot change a rate; exact flows respect its bound."""
    dynamics = np.array([[-2.0, 1.0], [0.0, -3.0]])
    metric = scale * np.eye(2)
    rate = example.local_contraction_rate(dynamics, metric, np.zeros((2, 2)))
    assert rate == pytest.approx((5 - np.sqrt(2)) / 2)
    for duration in [0.01, 0.3, 2.0]:
        transition = expm(dynamics * duration)
        residual = transition.T @ metric @ transition - np.exp(-2 * rate * duration) * metric
        assert np.linalg.eigvalsh(residual).max() <= 1e-13


def test_lyapunov_solution_and_attainable_best_rate(example: Any) -> None:
    """Solve the Lyapunov equation separately and compare its analytic entries."""
    dynamics = np.array([[-2.0, 1.0], [0.0, -3.0]])
    metric = solve_continuous_lyapunov(dynamics.T, -np.eye(2))
    np.testing.assert_allclose(metric, [[1 / 4, 1 / 20], [1 / 20, 11 / 60]])
    assert example.local_contraction_rate(dynamics, metric, np.zeros((2, 2))) == pytest.approx(
        30 / (13 + np.sqrt(13))
    )
    best_metric = np.array([[1.0, 1.0], [1.0, 2.0]])
    assert example.local_contraction_rate(dynamics, best_metric, np.zeros((2, 2))) == pytest.approx(
        2
    )


def test_metric_derivative_can_disguise_physical_growth(example: Any) -> None:
    """A shrinking ruler certifies metric decay without uniform physical bounds."""
    assert example.local_contraction_rate(
        np.ones((1, 1)), np.ones((1, 1)), -4 * np.ones((1, 1))
    ) == pytest.approx(1)
    assert np.exp(1) > 1
    assert np.exp(-4) * np.exp(1) ** 2 < 1


@pytest.mark.parametrize("weight,rate", [(1.0, -1.0), (16.0, 0.5), (25.0, 0.6)])
def test_cascade_weight_has_the_claimed_rate(example: Any, weight: float, rate: float) -> None:
    """The coupled matrix, not just its diagonal blocks, determines this rate."""
    dynamics = np.array([[-1.0, 4.0], [0.0, -1.0]])
    assert example.local_contraction_rate(
        dynamics, np.diag([1.0, weight]), np.zeros((2, 2))
    ) == pytest.approx(rate)


def test_velocity_damping_does_not_erase_position_offset() -> None:
    """An exact linear flow retains a pure initial position displacement."""
    transition = expm(np.array([[0.0, 1.0], [0.0, -2.0]]) * 3)
    np.testing.assert_allclose(transition @ [1, 0], [1, 0])


def test_dual_feedback_residual_is_a_congruence() -> None:
    """Independent primal differentiation fixes every sign in the dual LMI."""
    dynamics = np.array([[0.0, 1.0], [2.0, -1.0]])
    inputs = np.array([[0.0], [1.0]])
    metric = np.array([[2.0, 0.3], [0.3, 1.0]])
    metric_dot = np.array([[0.2, -0.1], [-0.1, 0.4]])
    gain = np.array([[4.0, 2.0]])
    rate = 0.3
    inverse = np.linalg.inv(metric)
    inverse_dot = -inverse @ metric_dot @ inverse
    weighted_gain = gain @ inverse
    closed = dynamics - inputs @ gain
    primal = metric_dot + closed.T @ metric + metric @ closed + 2 * rate * metric
    dual = -inverse_dot + dynamics @ inverse + inverse @ dynamics.T
    dual += -inputs @ weighted_gain - weighted_gain.T @ inputs.T + 2 * rate * inverse
    np.testing.assert_allclose(dual, inverse @ primal @ inverse, atol=1e-14)


@pytest.mark.parametrize("point", [[0.0, 0.0], [1.0, -2.0], [-3.0, 3.0]])
def test_vdp_residual_matches_finite_differentiation(example: Any, point: list[float]) -> None:
    """Differentiate the vector field and metric independently of the helper."""
    state = np.asarray(point)

    def field(value: np.ndarray) -> np.ndarray:
        return np.array([value[1], -value[0] + 0.5 * (1 - value[0] ** 2) * value[1]])

    def metric(value: np.ndarray) -> np.ndarray:
        return np.diag([1.0, 1.2 * (1 + 1.5 * value[0] ** 2)])

    step = 1e-6
    jacobian = np.column_stack(
        [(field(state + step * e) - field(state - step * e)) / (2 * step) for e in np.eye(2)]
    )
    derivative = (metric(state + step * field(state)) - metric(state - step * field(state))) / (
        2 * step
    )
    expected = (
        jacobian.T @ metric(state) + metric(state) @ jacobian + derivative + 0.6 * metric(state)
    )
    actual = example.vdp_candidate_residual(state)
    np.testing.assert_allclose(actual, expected, rtol=1e-8, atol=1e-8)
    assert actual[0, 0] == pytest.approx(0.6)
    assert np.linalg.eigvalsh(actual).max() > 0


def test_endpoint_quadratic_is_not_squared_geodesic_distance() -> None:
    """A bounded pullback metric contracts while its endpoint surrogate grows."""
    state = 2.0
    phi = state + 0.8 * np.sin(state)
    first, second = 1 + 0.8 * np.cos(state), -0.8 * np.sin(state)
    field = -phi / first
    jacobian = -1 + phi * second / first**2
    metric = first**2
    derivative = 2 * first * second * field
    assert derivative + 2 * metric * jacobian == pytest.approx(-2 * metric)
    length = quad(lambda value: 1 + 0.8 * np.cos(value), 0, state)[0]
    assert length**2 == pytest.approx(phi**2)
    endpoint_derivative = 2 * state * first * (first + state * second) * field
    assert endpoint_derivative > 0


def test_discrete_nonlinear_difference_is_not_one_endpoint_tangent() -> None:
    """A globally contractive tanh map still requires curve integration."""
    first, second = 0.0, 1.0
    difference = 0.5 * (np.tanh(second) - np.tanh(first))
    tangent = 0.5 / np.cosh(first) ** 2 * (second - first)
    assert difference != pytest.approx(tangent)
    assert abs(difference) <= 0.5 * abs(second - first)


def test_noise_pairing_changes_the_ou_floor() -> None:
    """The Itô isometry gives one-trial and independent-pair variances."""
    rate, sigma, duration = 2.0, 0.3, 0.8
    integral = quad(lambda time: sigma**2 * np.exp(-2 * rate * (duration - time)), 0, duration)[0]
    assert integral == pytest.approx(sigma**2 * (1 - np.exp(-2 * rate * duration)) / (2 * rate))
    assert 2 * integral == pytest.approx(sigma**2 * (1 - np.exp(-2 * rate * duration)) / rate)
    # Common additive noise cancels; multiplicative common noise need not.
    assert -2 * rate + 3.0**2 > 0


def test_disturbed_tube_respects_initial_radius_and_floor() -> None:
    """Integrate the scalar comparison equation rather than assert its formula."""
    rate, forcing, initial, duration = 0.6, 0.1, 1.0, 2.0
    integral = quad(lambda time: forcing * np.exp(-rate * (duration - time)), 0, duration)[0]
    radius = initial * np.exp(-rate * duration) + integral
    assert radius == pytest.approx(
        forcing / rate + (initial - forcing / rate) * np.exp(-rate * duration)
    )


@pytest.mark.parametrize(
    "bad",
    [
        np.zeros((2, 2)),
        np.diag([1.0, -1.0]),
        np.array([[1.0, 1.0], [0.0, 1.0]]),
        np.full((2, 2), np.nan),
    ],
)
def test_rate_rejects_invalid_metrics(example: Any, bad: np.ndarray) -> None:
    with pytest.raises(ValueError):
        example.local_contraction_rate(-np.eye(2), bad, np.zeros((2, 2)))


def test_examples_reject_invalid_shapes_and_nonfinite_parameters(example: Any) -> None:
    with pytest.raises(ValueError):
        example.local_contraction_rate(np.zeros((2, 3)), np.eye(2), np.zeros((2, 2)))
    with pytest.raises(ValueError):
        example.local_contraction_rate(np.eye(2), np.eye(2), np.zeros((3, 3)))
    for state in (np.zeros(3), np.array([np.inf, 0])):
        with pytest.raises(ValueError):
            example.vdp_candidate_residual(state)
    with pytest.raises(ValueError):
        example.vdp_candidate_residual(np.zeros(2), epsilon=-1)
