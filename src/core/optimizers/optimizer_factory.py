from __future__ import annotations

from typing import Any, Callable, Tuple

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
) -> Tuple[NDArray, NDArray, NDArray]:
    """Wrapper around ILQRSolver to match the DDP mock signature."""
    solver = ILQRSolver()
    dt = 0.01
    x_traj, u_traj, t_traj = solver.optimize(
        dynamics_fn=f, x0=x0, xf=xf, u_init=u_init, dt=dt, max_iters=max_iters, tol=eps_residual
    )
    return x_traj, u_traj, t_traj
