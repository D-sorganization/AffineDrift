from __future__ import annotations

from collections.abc import Callable
from typing import Any

from src.core.contracts import check_finite_array, check_positive, require

from .ilqr_solver import ILQRSolver, NDArray, TrajectoryOptimizer  # noqa: F401


def get_default_optimizer() -> TrajectoryOptimizer:
    """Returns the default TrajectoryOptimizer implementation."""
    return ILQRSolver()


def ilqr_solver_wrapper(
    f: Callable[[NDArray, NDArray], NDArray],
    x0: NDArray,
    xf: NDArray,
    u_init: NDArray,
    eps_residual: float = 1e-3,
    max_iters: int = 50,
    compute_hessian_bound_func: Any = None,
) -> tuple[NDArray, NDArray, NDArray]:
    """
    Wrapper around ILQRSolver to match the DDP mock signature.
    """
    require(callable(f), "dynamics function f must be callable")
    check_finite_array(x0, "x0")
    check_finite_array(xf, "xf")
    require(x0.shape == xf.shape, "x0 and xf must have same shape")
    require(len(u_init) > 0, "u_init must not be empty")
    check_positive(eps_residual, "eps_residual")
    require(max_iters >= 1, "max_iters must be >= 1", max_iters)
    solver = ILQRSolver()
    dt = 0.01  # default dt, adaptive timestep might be needed but simple fixed is fine
    x_traj, u_traj, t_traj = solver.optimize(
        dynamics_fn=f, x0=x0, xf=xf, u_init=u_init, dt=dt, max_iters=max_iters, tol=eps_residual
    )
    return x_traj, u_traj, t_traj
