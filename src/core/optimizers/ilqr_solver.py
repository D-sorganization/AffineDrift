from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

import numpy as np
import numpy.typing as npt

from src.core.contracts import check_finite_array, check_positive, require

type NDArray = npt.NDArray[np.float64]

ILQR_STATUS_NOT_STARTED = "not_started"
ILQR_STATUS_CONVERGED = "converged"
ILQR_STATUS_LINE_SEARCH_FAILED = "line_search_failed"
ILQR_STATUS_MAX_ITERATIONS = "max_iterations"


@dataclass(frozen=True)
class ILQRDiagnostics:
    """Structured status from the most recent iLQR run."""

    status: str
    converged: bool
    iterations: int
    final_cost: float | None
    reason: str


@dataclass(frozen=True)
class ILQROptimizationRequest:
    """Validated inputs and solver knobs for an iLQR optimization run."""

    dynamics_fn: Callable[[NDArray, NDArray], NDArray]
    x0: NDArray
    xf: NDArray
    u_init: NDArray
    dt: float = 0.01
    max_iters: int = 50
    tol: float = 1e-3

    @classmethod
    def from_inputs(
        cls,
        dynamics_fn: Callable[[NDArray, NDArray], NDArray],
        x0: NDArray,
        xf: NDArray,
        u_init: NDArray,
        dt: float = 0.01,
        max_iters: int = 50,
        tol: float = 1e-3,
    ) -> ILQROptimizationRequest:
        """Build a request after enforcing public optimizer preconditions."""
        require(callable(dynamics_fn), "dynamics_fn must be callable")
        check_finite_array(x0, "x0")
        check_finite_array(xf, "xf")
        require(x0.shape == xf.shape, "x0 and xf must have same shape")
        require(len(u_init) > 0, "u_init must not be empty")
        check_finite_array(u_init, "u_init")
        check_positive(dt, "dt")
        require(max_iters >= 1, "max_iters must be >= 1", max_iters)
        check_positive(tol, "tol")
        return cls(
            dynamics_fn=dynamics_fn,
            x0=x0,
            xf=xf,
            u_init=u_init,
            dt=dt,
            max_iters=max_iters,
            tol=tol,
        )


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
        self._last_diagnostics = ILQRDiagnostics(
            status=ILQR_STATUS_NOT_STARTED,
            converged=False,
            iterations=0,
            final_cost=None,
            reason="optimize has not been called",
        )

    @property
    def last_diagnostics(self) -> ILQRDiagnostics:
        """Return diagnostics from the most recent optimize call."""
        return self._last_diagnostics

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
        ILQROptimizationRequest.from_inputs(dynamics_fn, x0, xf, u_init, dt, max_iters, tol)

    @staticmethod
    def _validated_dynamics_output(
        dynamics_fn: Callable[[NDArray, NDArray], NDArray],
        x: NDArray,
        u: NDArray,
        expected_shape: tuple[int, ...],
    ) -> NDArray:
        """Evaluate dynamics and require a finite derivative matching state shape."""
        raw_dx = dynamics_fn(x, u)
        dx = np.asarray(raw_dx, dtype=np.float64)
        require(
            dx.shape == expected_shape,
            "dynamics_fn output must match state shape",
            {"expected": expected_shape, "actual": dx.shape},
        )
        check_finite_array(dx, "dynamics_fn output")
        return dx

    def _linearize_dynamics(
        self,
        dynamics_fn: Callable[[NDArray, NDArray], NDArray],
        x: NDArray,
        u: NDArray,
        n_x: int,
        n_u: int,
        dt: float,
    ) -> tuple[NDArray, NDArray]:
        """Compute linearized dynamics A, B matrices via central finite differences."""
        A = np.zeros((n_x, n_x))
        B = np.zeros((n_x, n_u))
        eps = 1e-5
        expected_shape = x.shape
        for i in range(n_x):
            x_plus = x.copy()
            x_plus[i] += eps
            x_minus = x.copy()
            x_minus[i] -= eps
            dx_plus = self._validated_dynamics_output(dynamics_fn, x_plus, u, expected_shape)
            dx_minus = self._validated_dynamics_output(dynamics_fn, x_minus, u, expected_shape)
            A[:, i] = (dx_plus - dx_minus) / (2.0 * eps)
        for j in range(n_u):
            u_plus = u.copy()
            u_plus[j] += eps
            u_minus = u.copy()
            u_minus[j] -= eps
            dx_plus = self._validated_dynamics_output(dynamics_fn, x, u_plus, expected_shape)
            dx_minus = self._validated_dynamics_output(dynamics_fn, x, u_minus, expected_shape)
            B[:, j] = (dx_plus - dx_minus) / (2.0 * eps)

        Ad = np.eye(n_x) + A * dt
        Bd = B * dt
        return Ad, Bd

    @staticmethod
    def _compute_q_terms(
        x_k: NDArray,
        u_k: NDArray,
        xf: NDArray,
        A: NDArray,
        B: NDArray,
        Q: NDArray,
        R: NDArray,
        V_x: NDArray,
        V_xx: NDArray,
        n_u: int,
        n_x: int,
    ) -> tuple[NDArray, NDArray, NDArray, NDArray, NDArray]:
        """Assemble Q_x, Q_u, Q_xx, Q_uu, Q_ux for one backward-pass step."""
        lx = Q @ (x_k - xf)
        lu = R @ u_k
        lux = np.zeros((n_u, n_x))

        Q_x = lx + A.T @ V_x
        Q_u = lu + B.T @ V_x
        Q_xx = Q + A.T @ V_xx @ A
        Q_uu = R + B.T @ V_xx @ B
        Q_ux = lux + B.T @ V_xx @ A
        return Q_x, Q_u, Q_xx, Q_uu, Q_ux

    @staticmethod
    def _solve_feedback_gains(
        Q_u: NDArray, Q_uu: NDArray, Q_ux: NDArray, n_u: int
    ) -> tuple[NDArray, NDArray, NDArray]:
        """Regularize Q_uu if needed and solve for feedforward/feedback gains."""
        eigvals = np.linalg.eigvalsh(Q_uu)
        if eigvals[0] <= 0:
            Q_uu = Q_uu + np.eye(n_u) * (-eigvals[0] + 1e-3)

        Q_uu_inv = np.linalg.inv(Q_uu)
        k_gain = -Q_uu_inv @ Q_u
        K_gain = -Q_uu_inv @ Q_ux
        return k_gain, K_gain, Q_uu

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
            Q_x, Q_u, Q_xx, Q_uu, Q_ux = self._compute_q_terms(
                x_k, u_k, xf, A, B, Q, R, V_x, V_xx, n_u, n_x
            )
            k_gain, K_gain, Q_uu = self._solve_feedback_gains(Q_u, Q_uu, Q_ux, n_u)

            k_traj[k_idx] = k_gain
            K_traj[k_idx] = K_gain

            V_x = Q_x + K_gain.T @ Q_uu @ k_gain + K_gain.T @ Q_u + Q_ux.T @ k_gain
            V_xx = Q_xx + K_gain.T @ Q_uu @ K_gain + K_gain.T @ Q_ux + Q_ux.T @ K_gain

            max_k = max(max_k, np.max(np.abs(k_gain)))

        return k_traj, K_traj, float(max_k)

    def _prepare_optimization_state(
        self,
        dynamics_fn: Callable[[NDArray, NDArray], NDArray],
        x0: NDArray,
        u_init: NDArray,
        dt: float,
    ) -> tuple[NDArray, NDArray, int, int, int, NDArray, NDArray, NDArray]:
        """Normalize initial trajectories and build cost-weight matrices."""
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
        return x_traj, u_traj, N, n_x, n_u, Q, R, Q_f

    def _line_search(
        self,
        x_traj: NDArray,
        u_traj: NDArray,
        x0: NDArray,
        xf: NDArray,
        k_traj: NDArray,
        K_traj: NDArray,
        current_cost: float,
        N: int,
        dt: float,
        Q: NDArray,
        R: NDArray,
        Q_f: NDArray,
        dynamics_fn: Callable[[NDArray, NDArray], NDArray],
    ) -> tuple[NDArray, NDArray, float, bool]:
        """Backtracking line search along the iLQR update direction."""
        alpha = 1.0
        best_x_traj = x_traj
        best_u_traj = u_traj
        best_cost = current_cost
        accepted = False

        for _ in range(5):
            x_new = np.zeros_like(x_traj)
            u_new = np.zeros_like(u_traj)
            x_new[0] = x0
            for k_idx in range(N):
                u_new[k_idx] = (
                    u_traj[k_idx]
                    + alpha * k_traj[k_idx]
                    + K_traj[k_idx] @ (x_new[k_idx] - x_traj[k_idx])
                )
                dx = self._validated_dynamics_output(
                    dynamics_fn, x_new[k_idx], u_new[k_idx], x0.shape
                )
                x_new[k_idx + 1] = x_new[k_idx] + dx * dt
            candidate_cost = self._trajectory_cost(x_new, u_new, xf, Q, R, Q_f)
            if np.isfinite(candidate_cost) and candidate_cost < current_cost:
                best_x_traj = x_new
                best_u_traj = u_new
                best_cost = candidate_cost
                accepted = True
                break
            alpha *= 0.5

        return best_x_traj, best_u_traj, best_cost, accepted

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
        """Run iLQR with backward-compatible scalar arguments.

        Preconditions are the same as :meth:`ILQROptimizationRequest.from_inputs`:
        finite matching initial/target states, a non-empty finite initial control
        trajectory, positive ``dt``/``tol``, and at least one iteration.

        Returns:
            ``(x_traj, u_traj, t_traj)`` with state, control, and time samples.
        """
        request = ILQROptimizationRequest.from_inputs(
            dynamics_fn, x0, xf, u_init, dt, max_iters, tol
        )
        return self.optimize_request(request)

    def optimize_request(
        self, request: ILQROptimizationRequest
    ) -> tuple[NDArray, NDArray, NDArray]:
        """Run iLQR from a validated request object."""
        dynamics_fn = request.dynamics_fn
        x0 = request.x0
        xf = request.xf
        u_init = request.u_init
        dt = request.dt
        max_iters = request.max_iters
        tol = request.tol
        x_traj, u_traj, N, n_x, n_u, Q, R, Q_f = self._prepare_optimization_state(
            dynamics_fn, x0, u_init, dt
        )
        current_cost = self._trajectory_cost(x_traj, u_traj, xf, Q, R, Q_f)

        status = ILQR_STATUS_MAX_ITERATIONS
        reason = "maximum iterations reached"
        iterations = 0
        converged = False
        for iteration in range(1, max_iters + 1):
            iterations = iteration
            k_traj, K_traj, max_k = self._backward_pass(
                x_traj, u_traj, xf, dt, n_x, n_u, Q, R, Q_f, dynamics_fn
            )
            x_traj, u_traj, current_cost, accepted = self._line_search(
                x_traj,
                u_traj,
                x0,
                xf,
                k_traj,
                K_traj,
                current_cost,
                N,
                dt,
                Q,
                R,
                Q_f,
                dynamics_fn,
            )

            if max_k < tol:
                status = ILQR_STATUS_CONVERGED
                reason = "feedforward gain below tolerance"
                converged = True
                break
            if not accepted:
                status = ILQR_STATUS_LINE_SEARCH_FAILED
                reason = "line search failed to reduce cost"
                break

        t_traj: NDArray = np.asarray(np.linspace(0, N * dt, N + 1))
        self._last_diagnostics = ILQRDiagnostics(
            status=status,
            converged=converged,
            iterations=iterations,
            final_cost=float(current_cost),
            reason=reason,
        )
        return x_traj, u_traj, t_traj

    def _trajectory_cost(
        self,
        x_traj: NDArray,
        u_traj: NDArray,
        xf: NDArray,
        Q: NDArray,
        R: NDArray,
        Q_f: NDArray,
    ) -> float:
        """Return the finite-horizon quadratic tracking cost."""
        total = 0.0
        for x_k, u_k in zip(x_traj[:-1], u_traj, strict=True):
            state_error = x_k - xf
            total += 0.5 * float(state_error.T @ Q @ state_error)
            total += 0.5 * float(u_k.T @ R @ u_k)
        terminal_error = x_traj[-1] - xf
        total += 0.5 * float(terminal_error.T @ Q_f @ terminal_error)
        return total

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
            dx = self._validated_dynamics_output(dynamics_fn, x_traj[i], u_traj[i], x0.shape)
            x_traj[i + 1] = x_traj[i] + dx * dt
        return x_traj
