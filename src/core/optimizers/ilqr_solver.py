from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

import numpy as np
import numpy.typing as npt

from src.core.contracts import check_finite_array, check_positive, require

type NDArray = npt.NDArray[np.float64]


class TrajectoryOptimizer(Protocol):
    def optimize(
        self,
        dynamics_fn: Callable[[NDArray, NDArray], NDArray],
        x0: NDArray,
        xf: NDArray,
        u_init: NDArray,
        dt: float = 0.01,
        max_iters: int = 20,
        tol: float = 1e-4,
    ) -> tuple[NDArray, NDArray, NDArray]: ...


class ILQRSolver:
    """Functional Iterative Linear Quadratic Regulator (iLQR) implementation."""

    def __init__(self) -> None:
        """Initialize the iLQR solver with default cost weights."""
        self.state_weight = 1.0
        self.terminal_weight = 100.0
        self.control_weight = 0.01

    def _validate_inputs(
        self,
        dynamics_fn: Callable[[NDArray, NDArray], NDArray],
        x0: NDArray,
        xf: NDArray,
        u_init: NDArray,
        dt: float,
        max_iters: int,
        tol: float,
    ) -> None:
        """Validate inputs before starting optimization."""
        require(callable(dynamics_fn), "dynamics_fn must be callable")
        check_finite_array(x0, "x0")
        check_finite_array(xf, "xf")
        require(x0.shape == xf.shape, "x0 and xf must have same shape")
        require(len(u_init) > 0, "u_init must not be empty")
        check_positive(dt, "dt")
        require(max_iters >= 1, "max_iters must be >= 1", max_iters)
        check_positive(tol, "tol")

    def _linearize_dynamics(
        self,
        dynamics_fn: Callable[[NDArray, NDArray], NDArray],
        x: NDArray,
        u: NDArray,
        n_x: int,
        n_u: int,
        dt: float,
    ) -> tuple[NDArray, NDArray]:
        """Compute linearized dynamics A, B matrices via finite differences."""
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

    def _backward_pass(
        self,
        x_traj: NDArray,
        u_traj: NDArray,
        xf: NDArray,
        dt: float,
        n_x: int,
        n_u: int,
        Q: NDArray,
        R: NDArray,
        Q_f: NDArray,
        dynamics_fn: Callable[[NDArray, NDArray], NDArray],
    ) -> tuple[NDArray, NDArray, float]:
        """Perform iLQR backward pass to compute optimal gains."""
        N = len(u_traj)
        V_x = Q_f @ (x_traj[-1] - xf)
        V_xx = Q_f

        k_traj = np.zeros((N, n_u))
        K_traj = np.zeros((N, n_u, n_x))
        max_k = 0.0

        for k_idx in range(N - 1, -1, -1):
            x_k = x_traj[k_idx]
            u_k = u_traj[k_idx]

            A, B = self._linearize_dynamics(dynamics_fn, x_k, u_k, n_x, n_u, dt)

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

            max_k = max(max_k, np.max(np.abs(k_gain)))

        return k_traj, K_traj, float(max_k)

    def optimize(
        self,
        dynamics_fn: Callable[[NDArray, NDArray], NDArray],
        x0: NDArray,
        xf: NDArray,
        u_init: NDArray,
        dt: float = 0.01,
        max_iters: int = 50,
        tol: float = 1e-3,
    ) -> tuple[NDArray, NDArray, NDArray]:
        """Runs the iLQR algorithm."""
        self._validate_inputs(dynamics_fn, x0, xf, u_init, dt, max_iters, tol)
        N = len(u_init)
        n_x = len(x0)
        n_u = u_init.shape[1] if len(u_init.shape) > 1 else 1

        u_traj = np.array(u_init, dtype=np.float64)
        if len(u_traj.shape) == 1:
            u_traj = u_traj.reshape(-1, 1)

        x_traj = self._rollout(dynamics_fn, x0, u_traj, dt)

        Q = np.eye(n_x) * self.state_weight
        R = np.eye(n_u) * self.control_weight
        Q_f = np.eye(n_x) * self.terminal_weight

        for _iteration in range(max_iters):
            k_traj, K_traj, max_k = self._backward_pass(
                x_traj, u_traj, xf, dt, n_x, n_u, Q, R, Q_f, dynamics_fn
            )

            alpha = 1.0
            x_new = np.zeros_like(x_traj)
            u_new = np.zeros_like(u_traj)

            for _ in range(5):
                x_new[0] = x0
                for k_idx in range(N):
                    u_new[k_idx] = (
                        u_traj[k_idx]
                        + alpha * k_traj[k_idx]
                        + K_traj[k_idx] @ (x_new[k_idx] - x_traj[k_idx])
                    )
                    x_new[k_idx + 1] = x_new[k_idx] + dynamics_fn(x_new[k_idx], u_new[k_idx]) * dt
                break

            x_traj = x_new
            u_traj = u_new

            if max_k < tol:
                break

        t_traj: NDArray = np.asarray(np.linspace(0, N * dt, N + 1))
        return x_traj, u_traj, t_traj

    def _rollout(
        self,
        dynamics_fn: Callable[[NDArray, NDArray], NDArray],
        x0: NDArray,
        u_traj: NDArray,
        dt: float,
    ) -> NDArray:
        """Simulate the system forward using Euler integration."""
        check_finite_array(x0, "x0")
        require(len(u_traj) > 0, "u_traj must not be empty")
        check_positive(dt, "dt")
        N = len(u_traj)
        x_traj = np.zeros((N + 1, len(x0)))
        x_traj[0] = x0
        for i in range(N):
            x_traj[i + 1] = x_traj[i] + dynamics_fn(x_traj[i], u_traj[i]) * dt
        return x_traj
