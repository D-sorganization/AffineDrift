from typing import Any, Callable, Tuple

import numpy as np

from .ilqr_solver import ILQRSolver, TrajectoryOptimizer


def get_default_optimizer() -> TrajectoryOptimizer:
    """Returns the default TrajectoryOptimizer implementation."""
    return ILQRSolver()


def ilqr_solver_wrapper(
    f: Callable[[np.ndarray, np.ndarray], np.ndarray],
    x0: np.ndarray,
    xf: np.ndarray,
    u_init: np.ndarray,
    eps_residual: float = 1e-3,
    max_iters: int = 50,
    compute_hessian_bound_func: Any = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Wrapper around ILQRSolver to match the DDP mock signature.
    """
    solver = ILQRSolver()
    dt = 0.01  # default dt, adaptive timestep might be needed but simple fixed is fine
    x_traj, u_traj, t_traj = solver.optimize(
        dynamics_fn=f, x0=x0, xf=xf, u_init=u_init, dt=dt, max_iters=max_iters, tol=eps_residual
    )
    return x_traj, u_traj, t_traj
