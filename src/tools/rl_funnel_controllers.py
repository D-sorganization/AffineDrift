"""Controllers for RL funnel benchmarking."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

import numpy as np
import numpy.typing as npt
from scipy.linalg import solve_continuous_are

from src.core.contracts.definitions import require
from src.core.contracts.validators import check_finite_array
from src.tools.rl_funnel_dynamics import (
    double_pendulum_B,
    double_pendulum_drift,
    validate_state_vector,
)


def validate_weight_matrix(Q: npt.NDArray[Any], shape: tuple[int, int], name: str) -> None:
    """Validate that the weight matrix is finite and has the expected shape."""
    check_finite_array(Q, name)
    require(Q.shape == shape, f"{name} must have shape {shape}", Q.shape)


def setpoint_lqr_controller(
    x_target: npt.NDArray[Any],
    Q_sp: npt.NDArray[Any] | None = None,
    R_sp: npt.NDArray[Any] | None = None,
) -> Callable[[float, npt.NDArray[Any]], npt.NDArray[Any]]:
    """Classical setpoint LQR controller.

    Minimizes integral (x - x_target)' Q (x - x_target) + u' R u.
    Linearizes around x_target.
    """
    require(
        isinstance(x_target, np.ndarray) and x_target.shape == (4,),
        "x_target must be a numpy array of shape (4,)",
        x_target,
    )
    check_finite_array(x_target, "x_target")

    n = 4
    m = 2
    validate_state_vector(x_target, "x_target")
    if Q_sp is None:
        Q_sp = np.diag([10.0, 10.0, 1.0, 1.0])
    if R_sp is None:
        R_sp = 0.1 * np.eye(m)
    validate_weight_matrix(Q_sp, (n, n), "Q_sp")
    validate_weight_matrix(R_sp, (m, m), "R_sp")

    # Linearize at target
    eps = 1e-6
    A = np.zeros((n, n))
    f0 = double_pendulum_drift(0.0, x_target)
    for j in range(n):
        ej = np.zeros(n)
        ej[j] = eps
        A[:, j] = (double_pendulum_drift(0.0, x_target + ej) - f0) / eps

    B0 = double_pendulum_B(x_target)

    P = solve_continuous_are(A, B0, Q_sp, R_sp)
    K = np.linalg.solve(R_sp, B0.T @ P)

    def controller(t: float, x: npt.NDArray[Any]) -> npt.NDArray[Any]:
        """Apply setpoint LQR control law u = -K(x - x_target)."""
        return cast(npt.NDArray[Any], -K @ (x - x_target))

    return controller


def _precompute_lqr_gains(
    t_ref: np.ndarray,
    x_ref: np.ndarray,
    n: int,
    m: int,
    Q_tt: np.ndarray,
    R_tt: np.ndarray,
) -> np.ndarray:
    """Precompute time-varying LQR gains at each reference time step.

    For each step, linearises the double-pendulum dynamics via finite differences,
    then solves the continuous algebraic Riccati equation (CARE) to obtain the
    feedback gain matrix.  Falls back to a zero-gain matrix when the CARE is
    infeasible.

    Args:
        t_ref: Reference time array of shape (T,).
        x_ref: Reference state trajectory of shape (n, T).
        n: State dimension.
        m: Input dimension.
        Q_tt: State cost matrix of shape (n, n).
        R_tt: Input cost matrix of shape (m, m).

    Returns:
        Gains array of shape (T, m, n).
    """
    eps = 1e-6

    def _compute_gain(idx: int) -> np.ndarray:
        """Compute LQR gain at a single reference time step."""
        x_ref_i = x_ref[:, idx]
        A = np.zeros((n, n))
        f0 = double_pendulum_drift(t_ref[idx], x_ref_i)
        for j in range(n):
            ej = np.zeros(n)
            ej[j] = eps
            A[:, j] = (double_pendulum_drift(t_ref[idx], x_ref_i + ej) - f0) / eps
        B0 = double_pendulum_B(x_ref_i)
        try:
            P = solve_continuous_are(A, B0, Q_tt, R_tt)
            return np.linalg.solve(R_tt, B0.T @ P)
        except (np.linalg.LinAlgError, ValueError):
            return np.zeros((m, n))

    gains = [_compute_gain(i) for i in range(len(t_ref))]
    return np.array(gains)


def _validate_ttcf_inputs(t_ref: np.ndarray, x_ref: np.ndarray) -> None:
    """Validate reference trajectory inputs for the TTCF controller."""
    require(
        isinstance(t_ref, np.ndarray) and t_ref.ndim == 1 and len(t_ref) >= 2,
        "t_ref must be a 1D numpy array with at least 2 elements",
        t_ref,
    )
    require(
        isinstance(x_ref, np.ndarray)
        and x_ref.ndim == 2
        and x_ref.shape[0] == 4
        and x_ref.shape[1] == len(t_ref),
        "x_ref must be a numpy array of shape (4, len(t_ref))",
        x_ref,
    )
    check_finite_array(t_ref, "t_ref")
    check_finite_array(x_ref, "x_ref")


def trajectory_tracking_lqr(
    t_ref: np.ndarray,
    x_ref: np.ndarray,
    Q_tt: np.ndarray | None = None,
    R_tt: np.ndarray | None = None,
) -> Callable[[float, np.ndarray], np.ndarray]:
    """Trajectory Tracking Cost Functional (TTCF) controller.

    Time-varying LQR that tracks x*(t) with time-varying linearization.
    Uses frozen-time LQR at each point (approximation; exact requires Riccati ODE).

    Gain precomputation is delegated to ``_precompute_lqr_gains``.
    Validation is delegated to ``_validate_ttcf_inputs``.
    """
    from scipy.interpolate import interp1d

    _validate_ttcf_inputs(t_ref, x_ref)

    n, m = 4, 2
    Q_tt = Q_tt if Q_tt is not None else np.diag([10.0, 10.0, 1.0, 1.0])
    R_tt = R_tt if R_tt is not None else 0.1 * np.eye(m)
    gains_array = _precompute_lqr_gains(t_ref, x_ref, n, m, Q_tt, R_tt)
    x_ref_interp = interp1d(t_ref, x_ref, kind="linear", fill_value="extrapolate")

    def get_K(t: float) -> np.ndarray:
        """Look up precomputed LQR gain at time t via nearest-index interpolation."""
        idx = np.clip(np.searchsorted(t_ref, t) - 1, 0, len(t_ref) - 2)
        return cast(npt.NDArray[Any], gains_array[idx])

    def controller(t: float, x: np.ndarray) -> np.ndarray:
        """Apply time-varying TTCF control law u = -K(t)(x - x*(t))."""
        return cast(npt.NDArray[Any], -get_K(t) @ (x - x_ref_interp(t)))

    return controller
