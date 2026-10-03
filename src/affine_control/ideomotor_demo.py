"""Nominal output-control example; no neural learning or human validation.

A constant bounded torque is selected for a fixed future horizon. The cost is
dimensionless and is not metabolic energy. The model has no observation noise,
feedback, actuator dynamics or joint limits. Angles are unwrapped radians.
"""

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar

MASS_KG = 1.0
LENGTH_M = 1.0
GRAVITY_M_S2 = 9.81
DAMPING_RATE_PER_S = 0.5
MIN_TORQUE_NM = -6.0
MAX_TORQUE_NM = 6.0
TRACKING_WEIGHT_PER_RAD2 = 10.0
CONTROL_WEIGHT_PER_NM2 = 0.01
DEFAULT_HORIZON_S = 0.2
DEFAULT_STEPS = 100
RELATIVE_TOLERANCE = 1e-10
ABSOLUTE_TOLERANCE = 1e-12


@dataclass(frozen=True)
class TorqueChoice:
    """Selected torque and nominal same-horizon outcomes."""

    torque_nm: float
    final_state: NDArray[np.float64]
    cost: float
    zero_input_cost: float


def _finite(value: float, name: str) -> float:
    """Validate a real finite scalar at the public boundary."""
    if isinstance(value, (bool, np.bool_)) or not isinstance(
        value, (int, float, np.integer, np.floating)
    ):
        raise ValueError(f"{name} must be a finite real scalar")
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a finite real scalar") from error
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _state(state: ArrayLike) -> NDArray[np.float64]:
    """Copy a finite angle/velocity state without changing the caller's data."""
    result = np.array(state, dtype=np.float64, copy=True)
    if result.shape != (2,) or not np.all(np.isfinite(result)):
        raise ValueError("state must have two finite entries: angle and angular velocity")
    return result


def predict_pendulum(
    state: ArrayLike,
    torque_nm: float,
    horizon_s: float = DEFAULT_HORIZON_S,
    steps: int = DEFAULT_STEPS,
) -> NDArray[np.float64]:
    """Predict a constant-torque future with adaptive DOP853 integration.

    ``steps`` bounds the maximum solver step by horizon/steps; it is not the
    number of accepted adaptive steps. Positive finite horizon and integer
    subdivisions are required. This numerical solution is not an exact flow.
    """
    initial = _state(state)
    torque = _finite(torque_nm, "torque_nm")
    horizon = _finite(horizon_s, "horizon_s")
    if horizon <= 0 or isinstance(steps, bool) or not isinstance(steps, (int, np.integer)):
        raise ValueError("horizon and integer steps must be positive")
    if steps <= 0:
        raise ValueError("steps must be positive")

    def derivative(_time: float, value: NDArray[np.float64]) -> NDArray[np.float64]:
        """Evaluate angular dynamics with the declared constant torque."""
        angle, speed = value
        acceleration = (
            -GRAVITY_M_S2 / LENGTH_M * np.sin(angle)
            - DAMPING_RATE_PER_S * speed
            + torque / (MASS_KG * LENGTH_M**2)
        )
        return np.array([speed, acceleration], dtype=np.float64)

    solution = solve_ivp(
        derivative,
        (0.0, horizon),
        initial,
        method="DOP853",
        t_eval=[horizon],
        max_step=horizon / steps,
        rtol=RELATIVE_TOLERANCE,
        atol=ABSOLUTE_TOLERANCE,
    )
    if not solution.success:
        raise RuntimeError(f"Pendulum integration failed: {solution.message}")
    return _state(solution.y[:, -1])


def action_cost(final_angle_rad: float, torque_nm: float, target_angle_rad: float = 0.0) -> float:
    """Return dimensionless angle-error and constant-torque penalties."""
    angle = _finite(final_angle_rad, "final_angle_rad")
    torque = _finite(torque_nm, "torque_nm")
    target = _finite(target_angle_rad, "target_angle_rad")
    cost = TRACKING_WEIGHT_PER_RAD2 * (angle - target) ** 2 + CONTROL_WEIGHT_PER_NM2 * torque**2
    return _finite(cost, "cost")


def choose_torque(
    initial_state: ArrayLike,
    target_angle_rad: float = 0.0,
    horizon_s: float = DEFAULT_HORIZON_S,
    steps: int = DEFAULT_STEPS,
) -> TorqueChoice:
    """Compare a bounded solver candidate with both bounds and zero input.

    This is one constant-input search, not a globally optimal time-varying
    policy. Solver failure is reported; the zero candidate is not a fallback
    that conceals failure. Predictions use the same state, horizon and model.
    """
    initial = _state(initial_state)
    target = _finite(target_angle_rad, "target_angle_rad")

    def outcome(torque: float) -> tuple[float, float, NDArray[np.float64]]:
        """Keep every candidate on the same model, horizon and objective."""
        final = predict_pendulum(initial, torque, horizon_s, steps)
        return action_cost(float(final[0]), torque, target), torque, final

    zero = outcome(0.0)
    result = minimize_scalar(
        lambda torque: outcome(float(torque))[0],
        method="bounded",
        bounds=(MIN_TORQUE_NM, MAX_TORQUE_NM),
    )
    candidate = _finite(result.x, "solver candidate")
    if not result.success or not MIN_TORQUE_NM <= candidate <= MAX_TORQUE_NM:
        raise RuntimeError(f"Bounded torque search failed: {result.message}")
    choices = [zero, outcome(candidate), outcome(MIN_TORQUE_NM), outcome(MAX_TORQUE_NM)]
    cost, torque, final = min(choices, key=lambda item: item[0])
    return TorqueChoice(torque, final, cost, zero[0])
