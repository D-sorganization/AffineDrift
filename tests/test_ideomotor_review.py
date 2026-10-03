"""Tests for ideomotor pendulum prediction and bounded torque selection."""

import math

import numpy as np
import pytest
from numpy.testing import assert_allclose

GRAVITY_M_S2 = 9.81


def test_constant_equilibrium_preserves_state() -> None:
    """Constant equilibrium torque u = g*sin(theta) must preserve rest state."""
    from src.affine_control.ideomotor_demo import predict_pendulum

    theta_0 = 0.5
    torque_eq = GRAVITY_M_S2 * math.sin(theta_0)
    initial_state = np.array([theta_0, 0.0], dtype=float)

    final_state = predict_pendulum(initial_state, torque_nm=torque_eq, horizon_s=0.2, steps=100)

    assert_allclose(final_state, initial_state, rtol=0.0, atol=1e-12)


def test_torque_changes_final_angle() -> None:
    """Torque must affect position through acceleration over a finite horizon."""
    from src.affine_control.ideomotor_demo import predict_pendulum

    initial_state = np.array([0.0, 0.0], dtype=float)
    free_state = predict_pendulum(initial_state, torque_nm=0.0, horizon_s=0.2, steps=100)
    forced_state = predict_pendulum(initial_state, torque_nm=2.0, horizon_s=0.2, steps=100)

    assert forced_state[0] > free_state[0]
    assert abs(forced_state[0] - free_state[0]) > 1e-3


def test_choose_torque_optimizes_over_zero_and_matches_cost() -> None:
    """Torque choice must be bounded, outperform zero-input, and match independent cost."""
    from src.affine_control.ideomotor_demo import action_cost, choose_torque, predict_pendulum

    initial_state = np.array([0.3, 0.0], dtype=float)
    target_angle = 0.0
    horizon = 0.2
    steps = 100

    result = choose_torque(
        initial_state, target_angle_rad=target_angle, horizon_s=horizon, steps=steps
    )

    assert -6.0 <= result.torque_nm <= 6.0
    assert abs(result.torque_nm) > 1e-3
    assert result.cost < result.zero_input_cost
    zero_state = predict_pendulum(initial_state, 0.0, horizon, steps)
    assert_allclose(result.zero_input_cost, 10.0 * zero_state[0] ** 2, rtol=1e-12)
    assert_allclose(
        result.final_state,
        predict_pendulum(initial_state, result.torque_nm, horizon, steps),
        rtol=1e-12,
    )
    assert_allclose(initial_state, [0.3, 0.0], rtol=0.0, atol=0.0)

    expected_cost = 10.0 * (result.final_state[0] - target_angle) ** 2 + 0.01 * (
        result.torque_nm**2
    )
    api_cost = action_cost(result.final_state[0], result.torque_nm, target_angle_rad=target_angle)
    assert_allclose(result.cost, expected_cost, rtol=1e-6)
    assert_allclose(api_cost, expected_cost, rtol=1e-6)


def test_small_horizon_torque_sensitivity() -> None:
    """Verify analytical sensitivity dtheta/du ≈ T^2 / 2 for small horizon."""
    from src.affine_control.ideomotor_demo import predict_pendulum

    horizon = 0.001
    delta_u = 0.001
    initial_state = np.array([0.0, 0.0], dtype=float)

    pos_state = predict_pendulum(initial_state, torque_nm=delta_u, horizon_s=horizon, steps=50)
    neg_state = predict_pendulum(initial_state, torque_nm=-delta_u, horizon_s=horizon, steps=50)

    dtheta_du = (pos_state[0] - neg_state[0]) / (2.0 * delta_u)
    expected_sensitivity = 0.5 * (horizon**2)
    assert_allclose(dtheta_du, expected_sensitivity, rtol=1e-3)


def test_halving_timestep_refines_prediction() -> None:
    """Halving the timestep agrees for this declared smooth trajectory."""
    from src.affine_control.ideomotor_demo import predict_pendulum

    initial_state = np.array([0.4, -0.2], dtype=float)
    torque = 1.5
    horizon = 0.2

    state_full = predict_pendulum(initial_state, torque, horizon_s=horizon, steps=100)
    state_half = predict_pendulum(initial_state, torque, horizon_s=horizon, steps=50)

    assert_allclose(state_half, state_full, rtol=1e-4, atol=1e-5)


@pytest.mark.parametrize(
    ("state", "torque", "horizon", "steps"),
    [
        ([0.0], 0.0, 0.2, 100),
        ([0.0, 0.0, 0.0], 0.0, 0.2, 100),
        ([np.nan, 0.0], 0.0, 0.2, 100),
        ([0.0, np.inf], 0.0, 0.2, 100),
        ([0.0, 0.0], np.nan, 0.2, 100),
        ([0.0, 0.0], np.inf, 0.2, 100),
        ([0.0, 0.0], 0.0, 0.0, 100),
        ([0.0, 0.0], 0.0, -0.2, 100),
        ([0.0, 0.0], 0.0, np.nan, 100),
        ([0.0, 0.0], 0.0, np.inf, 100),
        ([0.0, 0.0], 0.0, 0.2, 0),
        ([0.0, 0.0], 0.0, 0.2, -10),
        ([0.0, 0.0], 0.0, 0.2, 10.5),
        ([0.0, 0.0], 0.0, 0.2, True),
    ],
)
def test_predict_pendulum_invalid_inputs_raise_value_error(
    state: object, torque: float, horizon: float, steps: object
) -> None:
    """Invalid dimensions, non-finite values, or illegal horizons/steps must raise ValueError."""
    from src.affine_control.ideomotor_demo import predict_pendulum

    with pytest.raises(ValueError):
        predict_pendulum(state, torque_nm=torque, horizon_s=horizon, steps=steps)  # type: ignore[arg-type]
