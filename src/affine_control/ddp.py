"""Differential Dynamic Programming (DDP) with adaptive timestep for affine systems.

Implements a mock DDP trajectory optimiser that adapts the integration timestep
based on estimated perturbation size and Hessian residual bounds.  Used by the
AffineDrift benchmarks and control loop tests.
"""

import logging
from collections.abc import Callable
from typing import Any

import numpy as np

from src.affine_control.residuals import compute_hessian_bound
from src.core.constants import (
    DEFAULT_BASE_NOISE,
    DEFAULT_DT_INIT,
    DEFAULT_EPS_RESIDUAL,
    DEFAULT_MAX_ITERS,
    DEFAULT_STATE_SCALE,
    DT_CLIP_MAX,
    DT_CLIP_MIN,
    EPSILON,
)
from src.core.contracts import (
    check_finite_array,
    check_non_negative,
    check_positive,
    ensure,
    require,
)

logger = logging.getLogger(__name__)


def estimate_perturbation_size(
    x: np.ndarray[Any, Any],
    u: np.ndarray[Any, Any],
    base_noise: float = DEFAULT_BASE_NOISE,
    state_scale: float = DEFAULT_STATE_SCALE,
) -> float:
    """
    Estimates expected perturbation size based on state magnitude and noise model.

    The perturbation estimate combines a base noise floor with a state-dependent
    term that scales with the magnitude of the state vector. This models the
    common situation where larger states experience proportionally larger
    disturbances (e.g., aerodynamic drag, sensor noise proportional to signal).

    Args:
        x: State vector
        u: Control vector (unused, reserved for control-dependent noise models)
        base_noise: Minimum noise floor (default: 0.01)
        state_scale: Fraction of state magnitude to add as perturbation (default: 0.1)

    Returns:
        Estimated perturbation magnitude ||delta_x||
    """
    check_finite_array(x, "x")
    check_non_negative(base_noise, "base_noise")
    check_non_negative(state_scale, "state_scale")

    state_magnitude = float(np.linalg.norm(x))
    result = base_noise + state_scale * state_magnitude

    ensure(result >= 0, "perturbation size must be non-negative", result)
    return result


def _initialize_ddp_trajectory(
    f: Callable[[np.ndarray[Any, Any], np.ndarray[Any, Any]], np.ndarray[Any, Any]],
    x0: np.ndarray[Any, Any],
    u_init: np.ndarray[Any, Any],
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """Initialize DDP trajectory with a uniform timestep grid.

    Args:
        f: Dynamics function f(x, u).
        x0: Initial state vector.
        u_init: Initial control trajectory.

    Returns:
        Tuple of (u_traj, x_traj, t) on a uniform initial grid.
    """
    u_traj = np.array(u_init)
    N = len(u_traj)
    t = np.linspace(0, N * DEFAULT_DT_INIT, N + 1)
    x_traj = _simulate_trajectory(f, x0, u_traj, t)
    return u_traj, x_traj, t


def _run_ddp_iteration(
    f: Callable[..., np.ndarray[Any, Any]],
    x0: np.ndarray[Any, Any],
    x_traj: np.ndarray[Any, Any],
    u_traj: np.ndarray[Any, Any],
    t: np.ndarray[Any, Any],
    eps_residual: float,
    compute_hessian_bound_func: Callable[..., float],
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """Run one DDP iteration: adapt timesteps, resample controls, simulate.

    Args:
        f: Dynamics function f(x, u).
        x0: Initial state vector.
        x_traj: Current state trajectory.
        u_traj: Current control trajectory.
        t: Current time grid.
        eps_residual: Maximum acceptable residual.
        compute_hessian_bound_func: Function returning local Hessian bound.

    Returns:
        Updated (u_traj, x_traj, t_new) after one iteration.
    """
    dt_adaptive = _compute_adaptive_timesteps(
        f, x_traj, u_traj, eps_residual, compute_hessian_bound_func
    )
    t_new = np.concatenate([[0], np.cumsum(dt_adaptive)])
    u_traj = _resample_controls(u_traj, t, t_new[:-1])
    x_traj = _simulate_trajectory(f, x0, u_traj, t_new)
    return u_traj, x_traj, t_new


def adaptive_timestep_ddp_mock(
    f: Callable[[np.ndarray[Any, Any], np.ndarray[Any, Any]], np.ndarray[Any, Any]],
    x0: np.ndarray[Any, Any],
    xf: np.ndarray[Any, Any],
    u_init: np.ndarray[Any, Any],
    eps_residual: float = DEFAULT_EPS_RESIDUAL,
    max_iters: int = DEFAULT_MAX_ITERS,
    compute_hessian_bound_func: Callable[
        [Callable[..., np.ndarray[Any, Any]], np.ndarray[Any, Any], np.ndarray[Any, Any]], float
    ] = compute_hessian_bound,
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """DDP with curvature-adaptive timestep selection.

    NOTE: This is a non-functional MOCK implementation.
    The backward pass and Riccati equation solving are not implemented.
    See: docs/assessments/issues/ISSUE_Completist_Critical_DDPMock_2026-01-30.md

    Args:
        f: Dynamics function f(x, u, t)
        x0: Initial state
        xf: Target state
        u_init: Initial control trajectory (list of controls)
        eps_residual: Maximum acceptable residual
        max_iters: Maximum DDP iterations
        compute_hessian_bound_func: Function M(x, u) returning local Hessian bound

    Returns:
        Tuple of (x_traj, u_traj, t_traj).
    """
    check_finite_array(x0, "x0")
    check_finite_array(xf, "xf")
    require(x0.shape == xf.shape, "x0 and xf must have same shape")
    check_positive(eps_residual, "eps_residual")
    require(max_iters >= 1, "max_iters must be >= 1", max_iters)
    require(len(u_init) > 0, "u_init must not be empty")

    u_traj, x_traj, t = _initialize_ddp_trajectory(f, x0, u_init)

    for iteration in range(max_iters):
        u_traj, x_traj, t = _run_ddp_iteration(
            f, x0, x_traj, u_traj, t, eps_residual, compute_hessian_bound_func
        )
        if iteration > 2:  # Break early for prototype
            break

    return x_traj, u_traj, t


def _compute_adaptive_timesteps(
    f: Callable[..., np.ndarray[Any, Any]],
    x_traj: np.ndarray[Any, Any],
    u_traj: np.ndarray[Any, Any],
    eps_residual: float,
    compute_hessian_bound_func: Callable[..., float],
) -> np.ndarray[Any, Any]:
    """Compute curvature-adaptive timesteps from Hessian bounds and perturbation sizes.

    Args:
        f: Dynamics function f(x, u).
        x_traj: Current state trajectory.
        u_traj: Current control trajectory.
        eps_residual: Maximum acceptable residual.
        compute_hessian_bound_func: Function returning local Hessian bound.

    Returns:
        Array of adaptive timestep sizes, clipped to [DT_CLIP_MIN, DT_CLIP_MAX].
    """
    M_traj = np.array(
        [compute_hessian_bound_func(f, x_traj[i], u_traj[i]) for i in range(len(u_traj))]
    )
    delta_x_max = np.array(
        [estimate_perturbation_size(x_traj[i], u_traj[i]) for i in range(len(u_traj))]
    )

    # Avoid division by zero
    delta_x_max = np.maximum(delta_x_max, EPSILON)
    M_traj = np.maximum(M_traj, EPSILON)

    # dt = sqrt( 2 * eps / (M * delta_x^2) )
    dt_adaptive = np.sqrt(2 * eps_residual / (M_traj * delta_x_max**2))
    return np.clip(dt_adaptive, DT_CLIP_MIN, DT_CLIP_MAX)  # type: ignore[no-any-return]


def _simulate_trajectory(
    f: Callable[..., np.ndarray[Any, Any]],
    x0: np.ndarray[Any, Any],
    u_traj: np.ndarray[Any, Any],
    t_grid: np.ndarray[Any, Any],
) -> np.ndarray[Any, Any]:
    """Exponential integrator or RK4 simulation."""
    require(
        len(u_traj) == len(t_grid) - 1,
        "u_traj length must equal t_grid length - 1",
    )
    check_finite_array(x0, "x0")
    x = [x0]
    curr_x = x0
    for i in range(len(u_traj)):
        dt = t_grid[i + 1] - t_grid[i]
        # Simple Euler for prototype
        dx = f(curr_x, u_traj[i])
        curr_x = curr_x + dx * dt
        x.append(curr_x)
    return np.array(x)


def _resample_controls(
    u_old: np.ndarray[Any, Any], t_old: np.ndarray[Any, Any], t_new: np.ndarray[Any, Any]
) -> np.ndarray[Any, Any]:
    """Zero-order hold interpolation."""
    require(len(u_old) > 0, "u_old must not be empty")
    require(len(t_old) > 0, "t_old must not be empty")
    require(len(t_new) > 0, "t_new must not be empty")
    u_resampled = []

    # Simple interpolation
    # For robust implementation, use scipy.interpolate.interp1d
    # Here we just map indices roughly for prototype without dependencies
    for t in t_new:
        idx = np.searchsorted(t_old, t)
        idx = min(idx, len(u_old) - 1)
        u_resampled.append(u_old[idx])

    return np.array(u_resampled)
