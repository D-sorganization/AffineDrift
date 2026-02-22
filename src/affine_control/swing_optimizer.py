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
    print(f"Achieved velocity: {result.final_velocity:.2f} m/s")
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np

from src.affine_control.ddp import adaptive_timestep_ddp_mock
from src.core.constants import EPSILON
from src.core.contracts import (
    check_finite_array,
    check_non_negative,
    check_positive,
    check_shape,
    ensure,
    require,
)

logger = logging.getLogger(__name__)

# ── Default configuration values ────────────────────────────────────────────

DEFAULT_HORIZON_STEPS: int = 50
"""Default number of time steps in the optimization horizon."""

DEFAULT_DT: float = 0.01
"""Default time step size in seconds."""

DEFAULT_MAX_ITERATIONS: int = 100
"""Default maximum DDP iterations."""

DEFAULT_CONVERGENCE_TOL: float = 1e-6
"""Default convergence tolerance for the cost function."""

DEFAULT_CONTROL_WEIGHT: float = 0.01
"""Default weight on control effort (R matrix scaling)."""

DEFAULT_TARGET_VELOCITY: float = 50.0
"""Default target clubhead velocity in m/s (~112 mph, tour average)."""

DEFAULT_TERMINAL_WEIGHT: float = 100.0
"""Default terminal cost weight scaling."""


# ── Data classes ────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SwingOptimizationConfig:
    """Configuration for the swing optimization pipeline.

    All fields have sensible defaults.  The ``n_joints`` field must be
    provided explicitly since it depends on the robot model.

    Attributes:
        n_joints: Number of joints (actuated DOFs) in the model.
        horizon_steps: Number of time steps in the optimization horizon.
        dt: Integration time step size in seconds.
        max_iterations: Maximum number of DDP iterations.
        convergence_tol: Cost convergence tolerance.
        control_weight: Scalar weight on control effort (R = control_weight * I).
        target_velocity: Target clubhead velocity in m/s.
        terminal_weight: Scalar weight on terminal cost (Q_f scaling).
    """

    n_joints: int
    horizon_steps: int = DEFAULT_HORIZON_STEPS
    dt: float = DEFAULT_DT
    max_iterations: int = DEFAULT_MAX_ITERATIONS
    convergence_tol: float = DEFAULT_CONVERGENCE_TOL
    control_weight: float = DEFAULT_CONTROL_WEIGHT
    target_velocity: float = DEFAULT_TARGET_VELOCITY
    terminal_weight: float = DEFAULT_TERMINAL_WEIGHT

    def __post_init__(self) -> None:
        """Validate configuration invariants (Design by Contract)."""
        require(
            isinstance(self.n_joints, int),
            "n_joints must be an integer",
            self.n_joints,
        )
        require(self.n_joints >= 1, "n_joints must be >= 1", self.n_joints)
        require(
            isinstance(self.horizon_steps, int),
            "horizon_steps must be an integer",
            self.horizon_steps,
        )
        require(
            self.horizon_steps >= 1,
            "horizon_steps must be >= 1",
            self.horizon_steps,
        )
        check_positive(self.dt, "dt")
        require(
            isinstance(self.max_iterations, int),
            "max_iterations must be an integer",
            self.max_iterations,
        )
        require(
            self.max_iterations >= 1,
            "max_iterations must be >= 1",
            self.max_iterations,
        )
        check_positive(self.convergence_tol, "convergence_tol")
        check_non_negative(self.control_weight, "control_weight")
        check_positive(self.target_velocity, "target_velocity")
        check_non_negative(self.terminal_weight, "terminal_weight")

    @property
    def state_dim(self) -> int:
        """State dimension: positions + velocities for each joint."""
        return 2 * self.n_joints

    @property
    def control_dim(self) -> int:
        """Control dimension: one torque per joint."""
        return self.n_joints


@dataclass
class SwingOptimizationResult:
    """Result container for a swing optimization run.

    Attributes:
        optimal_controls: Optimal control (torque) sequence, one array per step.
        optimal_trajectory: Optimal state trajectory, one array per step.
        final_velocity: Achieved clubhead velocity at the terminal state [m/s].
        cost: Final cost function value.
        converged: Whether the optimizer reached convergence tolerance.
        iterations: Number of iterations actually performed.
    """

    optimal_controls: list[np.ndarray[Any, Any]]
    optimal_trajectory: list[np.ndarray[Any, Any]]
    final_velocity: float
    cost: float
    converged: bool
    iterations: int

    def __post_init__(self) -> None:
        """Validate result consistency."""
        require(
            len(self.optimal_controls) >= 0,
            "optimal_controls must be a list",
        )
        require(
            len(self.optimal_trajectory) >= 0,
            "optimal_trajectory must be a list",
        )
        check_non_negative(self.final_velocity, "final_velocity")
        check_non_negative(self.cost, "cost")
        require(
            isinstance(self.converged, bool),
            "converged must be a boolean",
            self.converged,
        )
        require(self.iterations >= 0, "iterations must be >= 0", self.iterations)


# ── Optimizer ───────────────────────────────────────────────────────────────


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

    def __init__(self, config: SwingOptimizationConfig) -> None:
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
        4. Calls the DDP solver (``adaptive_timestep_ddp_mock``).
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
        check_finite_array(initial_state, "initial_state")
        check_shape(
            initial_state,
            (self._config.state_dim,),
            "initial_state",
        )
        require(callable(dynamics_fn), "dynamics_fn must be callable")

        cfg = self._config
        n = cfg.state_dim

        # Build target state
        x_target = np.zeros(n)
        x_target[cfg.n_joints :] = cfg.target_velocity

        # Initial control guess: zero torques
        u_init = np.zeros((cfg.horizon_steps, cfg.control_dim))

        logger.info(
            "Starting swing optimization: n_joints=%d, horizon=%d, dt=%.4f",
            cfg.n_joints,
            cfg.horizon_steps,
            cfg.dt,
        )

        # Iterative DDP with convergence check
        best_cost = float("inf")
        converged = False
        iteration = 0
        best_x_traj: np.ndarray[Any, Any] | None = None
        best_u_traj: np.ndarray[Any, Any] | None = None

        for iteration in range(1, cfg.max_iterations + 1):
            # Call the DDP solver
            x_traj, u_traj, t_traj = adaptive_timestep_ddp_mock(
                f=dynamics_fn,
                x0=initial_state,
                xf=x_target,
                u_init=u_init,
                eps_residual=cfg.convergence_tol,
                max_iters=min(5, cfg.max_iterations),  # inner DDP iters
            )

            # Evaluate cost on the returned trajectory
            traj_list = [x_traj[i] for i in range(len(x_traj))]
            ctrl_list = [u_traj[i] for i in range(len(u_traj))]
            current_cost = self.compute_trajectory_cost(traj_list, ctrl_list)

            cost_improvement = best_cost - current_cost
            logger.debug(
                "Iteration %d: cost=%.6f, improvement=%.6e",
                iteration,
                current_cost,
                cost_improvement,
            )

            if current_cost < best_cost:
                best_cost = current_cost
                best_x_traj = x_traj
                best_u_traj = u_traj

            # Convergence check
            if abs(cost_improvement) < cfg.convergence_tol and iteration > 1:
                converged = True
                logger.info(
                    "Converged at iteration %d (cost=%.6f)",
                    iteration,
                    best_cost,
                )
                break

            # Warm-start next iteration with current best controls
            u_init = u_traj

        # If no improvement was ever made, use initial trajectory
        if best_x_traj is None or best_u_traj is None:
            best_x_traj = x_traj  # type: ignore[possibly-undefined]
            best_u_traj = u_traj  # type: ignore[possibly-undefined]

        # Extract final velocity (norm of velocity portion of terminal state)
        final_state = best_x_traj[-1]
        velocity_portion = final_state[cfg.n_joints :]
        final_velocity = float(np.linalg.norm(velocity_portion))

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
