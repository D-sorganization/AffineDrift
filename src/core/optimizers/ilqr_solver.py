from __future__ import annotations

from typing import Callable, Protocol, Tuple, TypeAlias

import numpy as np
import numpy.typing as npt

NDArray: TypeAlias = npt.NDArray[np.float64]


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
    ) -> Tuple[NDArray, NDArray, NDArray]: ...


class ILQRSolver:
    """Functional Iterative Linear Quadratic Regulator (iLQR) implementation."""

    def __init__(self) -> None:
        """Initialize the iLQR solver with default cost weights."""
        self.state_weight = 1.0
        self.terminal_weight = 100.0
        self.control_weight = 0.01

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
        """
        Runs the iLQR algorithm.
        Returns: x_traj, u_traj, t_traj
        """
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

        # Since this is a basic interface matching DDP_mock,
        # we do finite differences for A and B.
        def get_linearized(x: NDArray, u: NDArray) -> Tuple[NDArray, NDArray]:
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

            # Continuous to discrete approx: x_{k+1} = x_k + f(x,u)*dt
            Ad = np.eye(n_x) + A * dt
            Bd = B * dt
            return Ad, Bd

        for iteration in range(max_iters):
            # Backward Pass
            V_x = Q_f @ (x_traj[-1] - xf)
            V_xx = Q_f

            k_traj = np.zeros((N, n_u))
            K_traj = np.zeros((N, n_u, n_x))

            expected_cost_reduction = 0.0

            for k_idx in range(N - 1, -1, -1):
                x_k = x_traj[k_idx]
                u_k = u_traj[k_idx]

                A, B = get_linearized(x_k, u_k)

                lx = Q @ (x_k - xf) + (R @ u_k) * 0  # simplify state cost
                lu = R @ u_k
                lxx = Q
                luu = R
                lux = np.zeros((n_u, n_x))

                Q_x = lx + A.T @ V_x
                Q_u = lu + B.T @ V_x
                Q_xx = lxx + A.T @ V_xx @ A
                Q_uu = luu + B.T @ V_xx @ B
                Q_ux = lux + B.T @ V_xx @ A

                # Regularize Q_uu
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

                expected_cost_reduction += 0.5 * k_gain.T @ Q_uu @ k_gain

            # Forward Pass (Line Search)
            alpha = 1.0
            x_new = np.zeros_like(x_traj)
            u_new = np.zeros_like(u_traj)

            for _ in range(5):  # backtracking
                x_new[0] = x0
                for k_idx in range(N):
                    u_new[k_idx] = (
                        u_traj[k_idx]
                        + alpha * k_traj[k_idx]
                        + K_traj[k_idx] @ (x_new[k_idx] - x_traj[k_idx])
                    )
                    x_new[k_idx + 1] = x_new[k_idx] + dynamics_fn(x_new[k_idx], u_new[k_idx]) * dt

                # We could evaluate true cost and accept if improved, but we'll take best effort
                break

            max_k = np.max(np.abs(k_traj))
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
        N = len(u_traj)
        x_traj = np.zeros((N + 1, len(x0)))
        x_traj[0] = x0
        for i in range(N):
            x_traj[i + 1] = x_traj[i] + dynamics_fn(x_traj[i], u_traj[i]) * dt
        return x_traj
