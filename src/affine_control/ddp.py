"""Differential Dynamic Programming (DDP) solver for affine control.

This module provides the mock DDP solver infrastructure used during early
prototyping, along with helpers for adaptive timestep selection and trajectory
simulation.  See GitHub issue #1659 for the full implementation roadmap.

Public API: ``MockDDPSolver``, ``adaptive_timestep_ddp_mock``,
``estimate_perturbation_size``.
"""

import logging
import os
import warnings
from collections.abc import Callable
from typing import Any, cast

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


def _is_running_under_pytest() -> bool:
    """Return True if the current call occurs inside a pytest session."""
    return "PYTEST_CURRENT_TEST" in os.environ or "pytest" in os.environ.get("PYTHONPATH", "")


def estimate_perturbation_size(
    x: np.ndarray[Any, Any],
    _u: np.ndarray[Any, Any],
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
        _u: Control vector (unused, reserved for control-dependent noise models)
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


class MockDDPSolver:
    """Non-functional placeholder for a full DDP (Differential Dynamic Programming) solver.

    .. warning::
        This is a **mock implementation** intended for use in tests and early
        prototyping only.  It does **not** implement a correct DDP backward
        pass or Riccati equation solve.  The forward simulation uses simple
        Euler integration and the iteration loop exits after at most 3 steps.
        Trajectories produced by this solver are **mathematically incorrect**
        and must not be used to drive physical hardware or generate production
        decisions.

        See GitHub issue #1659 for the tracking item to replace this with a
        real DDP implementation.

    When instantiated outside a pytest session this class emits a
    :class:`UserWarning` to make the limitation visible at runtime.
    """

    def __init__(
        self,
        compute_hessian_bound_func: Callable[
            [Callable[..., np.ndarray[Any, Any]], np.ndarray[Any, Any], np.ndarray[Any, Any]],
            float,
        ] = compute_hessian_bound,
    ) -> None:
        """Initialise the mock solver and warn if used outside a pytest session.

        Args:
            compute_hessian_bound_func: Function ``M(f, x, u) -> float`` returning a
                local upper bound on the dynamics Hessian.  Defaults to
                :func:`src.affine_control.residuals.compute_hessian_bound`.
        """
        if not _is_running_under_pytest():
            warnings.warn(
                "MockDDPSolver is a non-functional prototype.  "
                "The backward pass and Riccati solve are NOT implemented.  "
                "Trajectories produced here are mathematically incorrect.  "
                "See issue #1659 to track the full DDP implementation.",
                UserWarning,
                stacklevel=2,
            )
        self._compute_hessian_bound_func = compute_hessian_bound_func

    def _initialize_ddp_trajectory(
        self,
        f: Callable[[np.ndarray[Any, Any], np.ndarray[Any, Any]], np.ndarray[Any, Any]],
        x0: np.ndarray[Any, Any],
        u_init: np.ndarray[Any, Any],
    ) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any], np.ndarray[Any, Any]]:
        """Initialize trajectory with a uniform timestep grid and initial forward pass.

        Returns:
            (u_traj, x_traj, t) on the initial uniform grid.
        """
        u_traj = np.array(u_init)
        n_steps = len(u_traj)
        t = np.linspace(0, n_steps * DEFAULT_DT_INIT, n_steps + 1)
        x_traj = _simulate_trajectory(f, x0, u_traj, t)
        return u_traj, x_traj, t

    def _run_ddp_iteration(
        self,
        f: Callable[[np.ndarray[Any, Any], np.ndarray[Any, Any]], np.ndarray[Any, Any]],
        x0: np.ndarray[Any, Any],
        x_traj: np.ndarray[Any, Any],
        u_traj: np.ndarray[Any, Any],
        t: np.ndarray[Any, Any],
        eps_residual: float,
    ) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any], np.ndarray[Any, Any]]:
        """Adapt timesteps, resample controls, and simulate one DDP iteration.

        Returns:
            Updated (u_traj, x_traj, t_new).
        """
        dt_adaptive = _compute_adaptive_timesteps(
            f, x_traj, u_traj, eps_residual, self._compute_hessian_bound_func
        )
        t_new = np.concatenate([[0], np.cumsum(dt_adaptive)])
        u_traj = _resample_controls(u_traj, t, t_new[:-1])
        x_traj = _simulate_trajectory(f, x0, u_traj, t_new)
        return u_traj, x_traj, t_new

    def solve(
        self,
        f: Callable[[np.ndarray[Any, Any], np.ndarray[Any, Any]], np.ndarray[Any, Any]],
        x0: np.ndarray[Any, Any],
        xf: np.ndarray[Any, Any],
        u_init: np.ndarray[Any, Any],
        eps_residual: float = DEFAULT_EPS_RESIDUAL,
        max_iters: int = DEFAULT_MAX_ITERS,
    ) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any], np.ndarray[Any, Any]]:
        """Run the mock DDP solve (prototype only — does not converge optimally).

        Returns:
            x_traj: State trajectory of shape (N+1, state_dim)
            u_traj: Control trajectory of shape (N, control_dim)
            t_traj: Adaptive time grid of shape (N+1,)
        """
        check_finite_array(x0, "x0")
        check_finite_array(xf, "xf")
        require(x0.shape == xf.shape, "x0 and xf must have same shape")
        check_positive(eps_residual, "eps_residual")
        require(max_iters >= 1, "max_iters must be >= 1", max_iters)
        require(len(u_init) > 0, "u_init must not be empty")

        u_traj, x_traj, t = self._initialize_ddp_trajectory(f, x0, u_init)
        for iteration in range(max_iters):
            u_traj, x_traj, t = self._run_ddp_iteration(f, x0, x_traj, u_traj, t, eps_residual)
            if iteration > 2:  # exit early — mock does not converge
                break
        return x_traj, u_traj, t

    def __call__(
        self,
        f: Callable[[np.ndarray[Any, Any], np.ndarray[Any, Any]], np.ndarray[Any, Any]],
        x0: np.ndarray[Any, Any],
        xf: np.ndarray[Any, Any],
        u_init: np.ndarray[Any, Any],
        eps_residual: float = DEFAULT_EPS_RESIDUAL,
        max_iters: int = DEFAULT_MAX_ITERS,
    ) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any], np.ndarray[Any, Any]]:
        """Call through to :meth:`solve` for backend interchangeability."""
        return self.solve(
            f=f,
            x0=x0,
            xf=xf,
            u_init=u_init,
            eps_residual=eps_residual,
            max_iters=max_iters,
        )


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
    """Thin wrapper around :class:`MockDDPSolver` kept for test compatibility.

    .. deprecated::
        Use :class:`MockDDPSolver` directly.  This function exists only so
        that existing test code continues to import without modification while
        the mock is properly gated behind its class.

    See :meth:`MockDDPSolver.solve` for full documentation.
    """
    solver = MockDDPSolver(compute_hessian_bound_func=compute_hessian_bound_func)
    return solver.solve(
        f=f,
        x0=x0,
        xf=xf,
        u_init=u_init,
        eps_residual=eps_residual,
        max_iters=max_iters,
    )


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
    m_traj = np.array(
        [compute_hessian_bound_func(f, x_traj[i], u_traj[i]) for i in range(len(u_traj))]
    )
    delta_x_max = np.array(
        [estimate_perturbation_size(x_traj[i], u_traj[i]) for i in range(len(u_traj))]
    )

    # Avoid division by zero
    delta_x_max = np.maximum(delta_x_max, EPSILON)
    m_traj = np.maximum(m_traj, EPSILON)

    # Adaptive timestep: dt = sqrt( 2 * eps / (M * delta_x^2) )
    dt_adaptive = np.sqrt(2 * eps_residual / (m_traj * delta_x_max**2))
    return cast(np.ndarray[Any, Any], np.clip(dt_adaptive, DT_CLIP_MIN, DT_CLIP_MAX))


def _simulate_trajectory(
    f: Callable[..., np.ndarray[Any, Any]],
    x0: np.ndarray[Any, Any],
    u_traj: np.ndarray[Any, Any],
    t_grid: np.ndarray[Any, Any],
) -> np.ndarray[Any, Any]:
    """Forward simulation using simple Euler integration (prototype quality only)."""
    require(
        len(u_traj) == len(t_grid) - 1,
        "u_traj length must equal t_grid length - 1",
    )
    check_finite_array(x0, "x0")
    x = [x0]
    curr_x = x0
    for i in range(len(u_traj)):
        dt = t_grid[i + 1] - t_grid[i]
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

    for t in t_new:
        idx = np.searchsorted(t_old, t)
        idx = min(idx, len(u_old) - 1)
        u_resampled.append(u_old[idx])

    return np.array(u_resampled)
