"""Independent flow comparisons for the residual-aware control article."""

import math

import numpy as np
import pytest
from scipy.integrate import quad, solve_ivp

from src.affine_control.residuals import predict_residual_bound
from src.core.contracts import ContractViolationError


@pytest.mark.parametrize("growth", [-2.0, 0.0, 1e-12, 1.0])
def test_constant_forcing_matches_independent_quadrature(growth: float) -> None:
    """The comparison equation propagates forcing through a nontrivial flow."""
    horizon = 0.7
    forcing = 0.03
    expected = quad(lambda time: forcing * math.exp(growth * (horizon - time)), 0, horizon)[0]
    actual = predict_residual_bound(
        np.array([2 * forcing]), np.ones(1), np.array([horizon]), np.array([growth])
    )
    assert actual == pytest.approx(expected, rel=1e-13)


def test_piecewise_bound_propagates_earlier_errors() -> None:
    """A quiet second interval can still amplify the first interval's remainder."""
    actual = predict_residual_bound(
        np.array([2.0, 0.0]), np.ones(2), np.array([0.2, 0.3]), np.array([0.0, 2.0])
    )
    assert actual == pytest.approx(0.2 * math.exp(0.6))


def test_subdivision_does_not_reset_accumulated_error() -> None:
    """Partitioning the same comparison ODE must not change its terminal bound."""
    whole = predict_residual_bound(np.ones(1), np.ones(1), np.ones(1), np.ones(1))
    split = predict_residual_bound(np.ones(10), np.ones(10), np.full(10, 0.1), np.ones(10))
    assert split == pytest.approx(whole, rel=1e-13)


def test_riccati_counterexample_and_conditional_bound() -> None:
    """Exact nonlinear flow refutes the old theorem and satisfies the corrected one."""
    initial = 0.01
    horizon = 1.0
    exact = initial * math.exp(horizon) / (1 - initial * math.expm1(horizon))
    linear = initial * math.exp(horizon)
    residual = exact - linear
    numerical = solve_ivp(
        lambda time, state: state + state**2,
        (0.0, horizon),
        [initial],
        rtol=1e-11,
        atol=1e-13,
    )
    assert numerical.success
    assert numerical.y[0, -1] == pytest.approx(exact, rel=1e-10)
    old_bound = initial**2 * math.expm1(2 * horizon) / 2
    assert residual > old_bound
    # Positive, increasing exact solution: its terminal value bounds the whole interval.
    corrected = predict_residual_bound(
        np.array([2.0]), np.array([exact]), np.array([horizon]), np.array([1.0])
    )
    assert residual < corrected


@pytest.mark.parametrize("index", [0, 1, 2])
def test_negative_interval_data_rejected(index: int) -> None:
    """Signed values cannot serve as Hessian, deviation, or time bounds."""
    arrays = [np.ones(2), np.ones(2), np.ones(2)]
    arrays[index][0] = -0.1
    with pytest.raises(ContractViolationError, match="non-negative"):
        predict_residual_bound(*arrays)


@pytest.mark.parametrize("index", [0, 1, 2, 3])
def test_only_one_dimensional_interval_arrays_accepted(index: int) -> None:
    """Reject accidental broadcasting and ambiguous vector-valued deviations."""
    arrays = [np.ones(2), np.ones(2), np.ones(2), np.ones(2)]
    arrays[index] = np.ones((2, 1))
    with pytest.raises(ContractViolationError, match="one-dimensional"):
        predict_residual_bound(*arrays)


@pytest.mark.parametrize("growth", [np.array([1.0]), np.array([1.0, np.nan])])
def test_invalid_growth_array_rejected(growth: np.ndarray) -> None:
    """Growth information must cover exactly the same finite intervals."""
    with pytest.raises(ContractViolationError):
        predict_residual_bound(np.ones(2), np.ones(2), np.ones(2), growth)


def test_zero_duration_and_zero_forcing() -> None:
    """Zero-length intervals add no error; an affine flow has no Taylor forcing."""
    assert (
        predict_residual_bound(np.array([2.0, 0.0]), np.ones(2), np.array([0.0, 1.0]), np.ones(2))
        == 0.0
    )


def test_unrepresentable_bound_fails_explicitly() -> None:
    """Do not silently report an infinite number as a useful error certificate."""
    with pytest.raises(ValueError, match="representable"):
        predict_residual_bound(np.ones(1), np.ones(1), np.ones(1), np.array([1000.0]))
