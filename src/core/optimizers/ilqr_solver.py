"""Iterative Linear Quadratic Regulator (iLQR) solver.

The ``optimize`` method is decomposed into four sub-methods for clarity:

1. ``_build_cost_matrices`` -- construct Q, R, Q_f weight matrices.
2. ``_backward_pass`` -- compute feedforward and feedback gains via
   dynamic programming over the value function.
3. ``_forward_pass`` -- apply gains with a line-search step to produce
   an updated trajectory.
4. ``_rollout`` -- simulate the system forward using RK4 integration.
"""

from __future__ import annotations

import logging
from typing import Callable, Protocol, Tuple, TypeAlias

import numpy as np
import numpy.typing as npt

logger = logging.getLogger(__name__)

NDArray: TypeAlias = npt.NDArray[np.float64]


class TrajectoryOptimizer(Protocol):
    """Protocol for trajectory optimization solvers."""

    def optimize(
        self,
        dynamics_fn: Callable[[NDArray, NDArray], NDArray],
        x0: NDArray,
        xf: NDArray,
        u_init: NDArray,
        dt: float = 0.01,
        max_iters: int = 20,
        tol: float = 1e-4,
    ) -> Tuple[NDArray, NDArray, NDArray]: ...


def _get_linearized(
    dynamics_fn: Callable[[NDArray, NDArray], NDArray],
    x: NDArray,
    u: NDArray,
    n_x: int,
    n_u: int,
    dt: float,
) -> Tuple[NDArray, NDArray]:
    """Compute discretised linearisation (Ad, Bd) via forward finite differences."""
    A = np.zeros((n_x, n_x))
    B = np.zeros((n_x, n_u))
    eps = 1e-5
    f0 = dynamics_fn(x, u)
    for i in range(n_x):
        x_pert = x.copy()
        x_pert[i] += eps
        A[:, i] = (dynamics_fn(x_pert, u) - f0) / eps
    for j in range(n_u):
        u_pert = u.copy()
        u_pert[j] += eps
        B[:, j] = (dynamics_fn(x, u_pert) - f0) / eps
    Ad = np.eye(n_x) + A * dt
    Bd = B * dt
    return Ad, Bd


class ILQRSolver:
    """Functional Iterative Linear Quadratic Regulator (iLQR) implementation.

    The monolithic ``optimize`` loop has been decomposed into clearly
    separated backward and forward passes to improve readability and
    testability.
    """

    def __init__(self) -> None:
        """Initialize the iLQR solver with default cost weights."""
        self.state_weight = 1.0
        self.terminal_weight = 100.0
        self.control_weight = 0.01

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def optimize(
        self,
        dynamics_fn: Callable[[NDArray, NDArray], NDArray],
        x0: NDArray,
        xf: NDArray,
        u_init: NDArray,
        dt: float = 0.01,
        max_iters: int = 50,
        tol: float = 1e-3,
    ) -> Tuple[NDArray, NDArray, NDArray]:
        """Run the iLQR algorithm.

        Returns:
            Tuple of (x_traj, u_traj, t_traj).
        """
        N = len(u_init)
        n_x = len(x0)
        n_u = u_init.shape[1] if len(u_init.shape) > 1 else 1

        u_traj = np.array(u_init, dtype=np.float64)
        if len(u_traj.shape) == 1:
            u_traj = u_traj.reshape(-1, 1)

        x_traj = self._rollout(dynamics_fn, x0, u_traj, dt)
        Q, R, Q_f = self._build_cost_matrices(n_x, n_u)

        for _iteration in range(max_iters):
            k_traj, K_traj = self._backward_pass(
                dynamics_fn, x_traj, u_traj, xf, Q, R, Q_f, n_x, n_u, N, dt
            )
            x_traj, u_traj = self._forward_pass(
                dynamics_fn, x0, x_traj, u_traj, k_traj, K_traj, N, dt
            )
            if np.max(np.abs(k_traj)) < tol:
                logger.debug("iLQR converged at iteration %d", _iteration)
                break

        t_traj: NDArray = np.asarray(np.linspace(0, N * dt, N + 1))
        return x_traj, u_traj, t_traj

    # ------------------------------------------------------------------
    # Sub-methods
    # ------------------------------------------------------------------

    def _build_cost_matrices(self, n_x: int, n_u: int) -> Tuple[NDArray, NDArray, NDArray]:
        """Construct the quadratic cost weight matrices Q, R, Q_f."""
        Q = np.eye(n_x) * self.state_weight
        R = np.eye(n_u) * self.control_weight
        Q_f = np.eye(n_x) * self.terminal_weight
        return Q, R, Q_f

    def _backward_pass(
        self,
        dynamics_fn: Callable[[NDArray, NDArray], NDArray],
        x_traj: NDArray,
        u_traj: NDArray,
        xf: NDArray,
        Q: NDArray,
        R: NDArray,
        Q_f: NDArray,
        n_x: int,
        n_u: int,
        N: int,
        dt: float,
    ) -> Tuple[NDArray, NDArray]:
        """Compute feedforward (k) and feedback (K) gains via backward DP.

        Returns:
            Tuple of (k_traj, K_traj) gain arrays.
        """
        V_x = Q_f @ (x_traj[-1] - xf)
        V_xx = Q_f.copy()

        k_traj = np.zeros((N, n_u))
        K_traj = np.zeros((N, n_u, n_x))

        for k_idx in range(N - 1, -1, -1):
            x_k = x_traj[k_idx]
            u_k = u_traj[k_idx]

            A, B = _get_linearized(dynamics_fn, x_k, u_k, n_x, n_u, dt)

            lx = Q @ (x_k - xf)
            lu = R @ u_k
            lxx = Q
            luu = R
            lux = np.zeros((n_u, n_x))

            Q_x = lx + A.T @ V_x
            Q_u = lu + B.T @ V_x
            Q_xx = lxx + A.T @ V_xx @ A
            Q_uu = luu + B.T @ V_xx @ B
            Q_ux = lux + B.T @ V_xx @ A

            # Regularise Q_uu to ensure positive-definiteness
            eigvals = np.linalg.eigvalsh(Q_uu)
            if eigvals[0] <= 0:
                Q_uu += np.eye(n_u) * (-eigvals[0] + 1e-3)

            Q_uu_inv = np.linalg.inv(Q_uu)
            k_gain = -Q_uu_inv @ Q_u
            K_gain = -Q_uu_inv @ Q_ux

            k_traj[k_idx] = k_gain
            K_traj[k_idx] = K_gain

            V_x = Q_x + K_gain.T @ Q_uu @ k_gain + K_gain.T @ Q_u + Q_ux.T @ k_gain
            V_xx = Q_xx + K_gain.T @ Q_uu @ K_gain + K_gain.T @ Q_ux + Q_ux.T @ K_gain

        return k_traj, K_traj

    def _forward_pass(
        self,
        dynamics_fn: Callable[[NDArray, NDArray], NDArray],
        x0: NDArray,
        x_traj: NDArray,
        u_traj: NDArray,
        k_traj: NDArray,
        K_traj: NDArray,
        N: int,
        dt: float,
        alpha: float = 1.0,
    ) -> Tuple[NDArray, NDArray]:
        """Apply gains to produce an updated trajectory via RK4 rollout.

        Returns:
            Tuple of (x_new, u_new).
        """
        x_new = np.zeros_like(x_traj)
        u_new = np.zeros_like(u_traj)
        x_new[0] = x0

        for k_idx in range(N):
            u_new[k_idx] = (
                u_traj[k_idx]
                + alpha * k_traj[k_idx]
                + K_traj[k_idx] @ (x_new[k_idx] - x_traj[k_idx])
            )
            # RK4 integration step
            x_k = x_new[k_idx]
            u_k = u_new[k_idx]
            k1 = dynamics_fn(x_k, u_k)
            k2 = dynamics_fn(x_k + 0.5 * dt * k1, u_k)
            k3 = dynamics_fn(x_k + 0.5 * dt * k2, u_k)
            k4 = dynamics_fn(x_k + dt * k3, u_k)
            x_new[k_idx + 1] = x_k + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

        return x_new, u_new

    def _rollout(
        self,
        dynamics_fn: Callable[[NDArray, NDArray], NDArray],
        x0: NDArray,
        u_traj: NDArray,
        dt: float,
    ) -> NDArray:
        """Simulate the system forward using RK4 integration."""
        N = len(u_traj)
        x_traj = np.zeros((N + 1, len(x0)))
        x_traj[0] = x0
        for i in range(N):
            x_k = x_traj[i]
            u_k = u_traj[i]
            k1 = dynamics_fn(x_k, u_k)
            k2 = dynamics_fn(x_k + 0.5 * dt * k1, u_k)
            k3 = dynamics_fn(x_k + 0.5 * dt * k2, u_k)
            k4 = dynamics_fn(x_k + dt * k3, u_k)
            x_traj[i + 1] = x_k + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        return x_traj
