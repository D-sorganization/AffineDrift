"""Affine Control Swing Optimization Pipeline.

This module provides a reusable optimization pipeline for golf swing
trajectory optimization.  It wraps the existing DDP (Differential Dynamic
Programming) solver from ``src.affine_control.ddp`` and exposes a clean,
configuration-driven API for finding optimal joint torque trajectories
that maximize clubhead velocity while minimizing control effort.

The pipeline follows a quadratic cost structure::

    J = sum_t [ (x_t - x_target)^T Q (x_t - x_target) + u_t^T R u_t ]
      + (x_T - x_target)^T Q_f (x_T - x_target)

where Q penalizes state deviations from the target velocity, R penalizes
control effort, and Q_f is the terminal cost weight.

Design by Contract
------------------
All public methods enforce preconditions on their inputs (positive dt,
valid array dimensions, etc.) using the ``src.core.contracts`` primitives.

Usage
-----
::

    from src.affine_control.swing_optimizer import (
        SwingOptimizationConfig,
        SwingOptimizer,
    )

    config = SwingOptimizationConfig(n_joints=3, horizon_steps=50)
    optimizer = SwingOptimizer(config)
    result = optimizer.optimize(initial_state, dynamics_fn)
    logger.debug(f"Achieved velocity: {result.final_velocity:.2f} m/s")
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

import numpy as np

from src.affine_control.ddp import MockDDPSolver
from src.affine_control.swing_types import (
    DEFAULT_CONTROL_WEIGHT,
    DEFAULT_CONVERGENCE_TOL,
    DEFAULT_DT,
    DEFAULT_HORIZON_STEPS,
    DEFAULT_MAX_ITERATIONS,
    DEFAULT_TARGET_VELOCITY,
    DEFAULT_TERMINAL_WEIGHT,
    SwingOptimizationConfig,
    SwingOptimizationResult,
)
from src.core.constants import EPSILON
from src.core.contracts import (
    check_finite_array,
    check_shape,
    ensure,
    require,
)

logger = logging.getLogger(__name__)


class SwingOptimizer:
    """Swing optimization pipeline wrapping the DDP solver.

    This class orchestrates the full optimization loop: it builds the
    cost matrices, constructs the initial control guess, calls the DDP
    solver, and packages the result.

    Example
    -------
    ::

        config = SwingOptimizationConfig(n_joints=3, horizon_steps=50)
        optimizer = SwingOptimizer(config)

        def dynamics(x, u):
            # Simple double-integrator per joint
            n = len(x) // 2
            dq = x[n:]
            ddq = u
            return np.concatenate([dq, ddq])

        x0 = np.zeros(config.state_dim)
        result = optimizer.optimize(x0, dynamics)
    """

    def __init__(
        self,
        config: SwingOptimizationConfig,
        ddp_solver: (
            Callable[..., tuple[np.ndarray[Any, Any], np.ndarray[Any, Any], np.ndarray[Any, Any]]]
            | None
        ) = None,
    ) -> None:
        """Initialize the optimizer with given configuration.

        Args:
            config: Optimization configuration dataclass.

        Raises:
            PreconditionError: If config is not a SwingOptimizationConfig.
        """
        require(
            isinstance(config, SwingOptimizationConfig),
            "config must be a SwingOptimizationConfig instance",
            type(config).__name__,
        )
        self._config = config
        self._ddp_solver = ddp_solver if ddp_solver is not None else MockDDPSolver()
        self._R = config.control_weight * np.eye(config.control_dim)
        self._Q = np.zeros((config.state_dim, config.state_dim))
        # Penalize velocity deviations (second half of state vector)
        for i in range(config.n_joints, config.state_dim):
            self._Q[i, i] = 1.0
        self._Q_f = config.terminal_weight * self._Q

    @property
    def config(self) -> SwingOptimizationConfig:
        """Return the optimizer's configuration (read-only)."""
        return self._config

    @property
    def R(self) -> np.ndarray[Any, Any]:
        """Control cost weight matrix (read-only copy)."""
        return self._R.copy()

    @property
    def Q(self) -> np.ndarray[Any, Any]:
        """State cost weight matrix (read-only copy)."""
        return self._Q.copy()

    @property
    def Q_f(self) -> np.ndarray[Any, Any]:
        """Terminal state cost weight matrix (read-only copy)."""
        return self._Q_f.copy()

    def compute_cost(
        self,
        state: np.ndarray[Any, Any],
        control: np.ndarray[Any, Any],
    ) -> float:
        """Compute the instantaneous quadratic cost for a state-control pair.

        The cost is::

            c(x, u) = (x_vel - v_target)^T Q_vel (x_vel - v_target) + u^T R u

        where ``x_vel`` is the velocity portion of the state and ``v_target``
        is the target velocity vector.

        Args:
            state: State vector of dimension ``state_dim``.
            control: Control vector of dimension ``control_dim``.

        Returns:
            Scalar cost value (non-negative).

        Raises:
            PreconditionError: On dimension mismatch or non-finite values.
        """
        check_finite_array(state, "state")
        check_finite_array(control, "control")
        check_shape(
            state,
            (self._config.state_dim,),
            "state",
        )
        check_shape(
            control,
            (self._config.control_dim,),
            "control",
        )

        # Build the target state (zeros for positions, target_velocity for velocities)
        x_target = np.zeros(self._config.state_dim)
        x_target[self._config.n_joints :] = self._config.target_velocity

        dx = state - x_target
        state_cost = float(dx @ self._Q @ dx)
        control_cost = float(control @ self._R @ control)
        total = state_cost + control_cost

        ensure(total >= -EPSILON, "cost must be non-negative", total)
        return max(total, 0.0)

    def compute_terminal_cost(
        self,
        state: np.ndarray[Any, Any],
    ) -> float:
        """Compute the terminal cost for a final state.

        Args:
            state: Terminal state vector.

        Returns:
            Scalar terminal cost (non-negative).
        """
        check_finite_array(state, "state")
        check_shape(state, (self._config.state_dim,), "state")

        x_target = np.zeros(self._config.state_dim)
        x_target[self._config.n_joints :] = self._config.target_velocity

        dx = state - x_target
        cost = float(dx @ self._Q_f @ dx)
        ensure(cost >= -EPSILON, "terminal cost must be non-negative", cost)
        return max(cost, 0.0)

    def compute_trajectory_cost(
        self,
        trajectory: list[np.ndarray[Any, Any]],
        controls: list[np.ndarray[Any, Any]],
    ) -> float:
        """Compute the total cost across an entire trajectory.

        Args:
            trajectory: List of state vectors (length N+1).
            controls: List of control vectors (length N).

        Returns:
            Total cost (running + terminal).
        """
        require(
            len(trajectory) == len(controls) + 1,
            "trajectory must have one more element than controls",
            (len(trajectory), len(controls)),
        )
        require(len(controls) > 0, "controls must not be empty")

        running_cost = 0.0
        for t in range(len(controls)):
            running_cost += self.compute_cost(trajectory[t], controls[t]) * self._config.dt

        terminal = self.compute_terminal_cost(trajectory[-1])
        total = running_cost + terminal

        ensure(total >= -EPSILON, "trajectory cost must be non-negative", total)
        return max(total, 0.0)

    def _validate_optimize_inputs(
        self,
        initial_state: np.ndarray[Any, Any],
        dynamics_fn: object,
    ) -> None:
        """Validate inputs to :meth:`optimize`.

        Args:
            initial_state: Initial state vector to validate.
            dynamics_fn: Must be callable.

        Raises:
            PreconditionError: On invalid inputs (wrong dimensions, non-finite, etc.).
        """
        check_finite_array(initial_state, "initial_state")
        check_shape(initial_state, (self._config.state_dim,), "initial_state")
        require(callable(dynamics_fn), "dynamics_fn must be callable")
        require(
            self._config.allow_mock_solver or not isinstance(self._ddp_solver, MockDDPSolver),
            "mock DDP solver is disabled; set allow_mock_solver=True or pass a real solver",
        )

    def _call_ddp_solver(
        self,
        dynamics_fn: Callable[
            [np.ndarray[Any, Any], np.ndarray[Any, Any]],
            np.ndarray[Any, Any],
        ],
        initial_state: np.ndarray[Any, Any],
        x_target: np.ndarray[Any, Any],
        u_init: np.ndarray[Any, Any],
    ) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
        """Invoke the DDP solver for one outer iteration and return (x_traj, u_traj)."""
        cfg = self._config
        x_traj, u_traj, _t_traj = self._ddp_solver(
            f=dynamics_fn,
            x0=initial_state,
            xf=x_target,
            u_init=u_init,
            eps_residual=cfg.convergence_tol,
            max_iters=min(5, cfg.max_iterations),
        )
        return x_traj, u_traj

    def _update_best_and_check_convergence(
        self,
        iteration: int,
        x_traj: np.ndarray[Any, Any],
        u_traj: np.ndarray[Any, Any],
        current_cost: float,
        best_cost: float,
        best_x_traj: np.ndarray[Any, Any] | None,
        best_u_traj: np.ndarray[Any, Any] | None,
    ) -> tuple[float, np.ndarray[Any, Any], np.ndarray[Any, Any], bool]:
        """Track best trajectory and test for convergence.

        Returns:
            Tuple of (new_best_cost, new_best_x_traj, new_best_u_traj, converged).
        """
        cost_improvement = best_cost - current_cost
        logger.debug(
            "Iteration %d: cost=%.6f, improvement=%.6e", iteration, current_cost, cost_improvement
        )
        if current_cost < best_cost:
            best_cost, best_x_traj, best_u_traj = current_cost, x_traj, u_traj
        converged = abs(cost_improvement) < self._config.convergence_tol and iteration > 1
        if converged:
            logger.info("Converged at iteration %d (cost=%.6f)", iteration, best_cost)
        return best_cost, best_x_traj, best_u_traj, converged  # type: ignore[return-value]

    def _run_optimization_loop(
        self,
        initial_state: np.ndarray[Any, Any],
        dynamics_fn: Callable[
            [np.ndarray[Any, Any], np.ndarray[Any, Any]],
            np.ndarray[Any, Any],
        ],
        x_target: np.ndarray[Any, Any],
        u_init: np.ndarray[Any, Any],
    ) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any], float, bool, int]:
        """Iterative DDP loop with convergence tracking.

        Returns:
            Tuple of (best_x_traj, best_u_traj, best_cost, converged, iteration).
        """
        cfg = self._config
        best_cost = float("inf")
        converged = False
        iteration = 0
        best_x_traj: np.ndarray[Any, Any] | None = None
        best_u_traj: np.ndarray[Any, Any] | None = None

        for iteration in range(1, cfg.max_iterations + 1):
            x_traj, u_traj = self._call_ddp_solver(dynamics_fn, initial_state, x_target, u_init)
            current_cost = self.compute_trajectory_cost(
                [x_traj[i] for i in range(len(x_traj))],
                [u_traj[i] for i in range(len(u_traj))],
            )
            best_cost, best_x_traj, best_u_traj, converged = (
                self._update_best_and_check_convergence(
                    iteration, x_traj, u_traj, current_cost, best_cost, best_x_traj, best_u_traj
                )
            )
            if converged:
                break
            u_init = u_traj

        if best_x_traj is None or best_u_traj is None:
            best_x_traj, best_u_traj = x_traj, u_traj

        return best_x_traj, best_u_traj, best_cost, converged, iteration

    def _build_result(
        self,
        best_x_traj: np.ndarray[Any, Any],
        best_u_traj: np.ndarray[Any, Any],
        best_cost: float,
        converged: bool,
        iteration: int,
    ) -> SwingOptimizationResult:
        """Package raw trajectory arrays into a :class:`SwingOptimizationResult`.

        Args:
            best_x_traj: Optimal state trajectory array.
            best_u_traj: Optimal control trajectory array.
            best_cost: Total trajectory cost achieved.
            converged: Whether the loop converged.
            iteration: Final iteration count.

        Returns:
            Populated :class:`SwingOptimizationResult`.
        """
        cfg = self._config
        final_state = best_x_traj[-1]
        final_velocity = float(np.linalg.norm(final_state[cfg.n_joints :]))
        result = SwingOptimizationResult(
            optimal_controls=[best_u_traj[i] for i in range(len(best_u_traj))],
            optimal_trajectory=[best_x_traj[i] for i in range(len(best_x_traj))],
            final_velocity=final_velocity,
            cost=best_cost,
            converged=converged,
            iterations=iteration,
        )
        logger.info(
            "Optimization complete: velocity=%.2f m/s, cost=%.4f, converged=%s, iterations=%d",
            result.final_velocity,
            result.cost,
            result.converged,
            result.iterations,
        )
        return result

    def optimize(
        self,
        initial_state: np.ndarray[Any, Any],
        dynamics_fn: Callable[
            [np.ndarray[Any, Any], np.ndarray[Any, Any]],
            np.ndarray[Any, Any],
        ],
    ) -> SwingOptimizationResult:
        """Run the swing optimization pipeline.

        This method:
        1. Validates the initial state dimensions.
        2. Constructs a zero initial control guess.
        3. Builds the target state from ``config.target_velocity``.
        4. Calls the DDP solver (:class:`~src.affine_control.ddp.MockDDPSolver`).
        5. Evaluates convergence by comparing successive cost values.
        6. Packages and returns a ``SwingOptimizationResult``.

        Args:
            initial_state: Initial state vector of dimension ``state_dim``.
            dynamics_fn: Dynamics function ``f(x, u) -> dx/dt``.

        Returns:
            SwingOptimizationResult with optimal trajectory and metadata.

        Raises:
            PreconditionError: On invalid inputs (wrong dimensions, non-finite, etc.).
        """
        self._validate_optimize_inputs(initial_state, dynamics_fn)

        cfg = self._config
        x_target = np.zeros(cfg.state_dim)
        x_target[cfg.n_joints :] = cfg.target_velocity
        u_init = np.zeros((cfg.horizon_steps, cfg.control_dim))

        logger.info(
            "Starting swing optimization: n_joints=%d, horizon=%d, dt=%.4f",
            cfg.n_joints,
            cfg.horizon_steps,
            cfg.dt,
        )

        # NOTE: MockDDPSolver is a non-functional placeholder (issue #1659).
        # It does not implement a real backward pass or Riccati solve.
        # Replace with a proper DDP implementation before production use.
        best_x_traj, best_u_traj, best_cost, converged, iteration = self._run_optimization_loop(
            initial_state, dynamics_fn, x_target, u_init
        )
        return self._build_result(best_x_traj, best_u_traj, best_cost, converged, iteration)


__all__ = [
    "DEFAULT_CONTROL_WEIGHT",
    "DEFAULT_CONVERGENCE_TOL",
    "DEFAULT_DT",
    "DEFAULT_HORIZON_STEPS",
    "DEFAULT_MAX_ITERATIONS",
    "DEFAULT_TARGET_VELOCITY",
    "DEFAULT_TERMINAL_WEIGHT",
    "SwingOptimizationConfig",
    "SwingOptimizationResult",
    "SwingOptimizer",
]
