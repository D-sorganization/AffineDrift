"""Shared configuration and result types for swing optimization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from src.core.contracts import check_non_negative, check_positive, require

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


@dataclass(frozen=True)
class SwingOptimizationConfig:
    """Configuration for the swing optimization pipeline."""

    n_joints: int
    horizon_steps: int = DEFAULT_HORIZON_STEPS
    dt: float = DEFAULT_DT
    max_iterations: int = DEFAULT_MAX_ITERATIONS
    convergence_tol: float = DEFAULT_CONVERGENCE_TOL
    control_weight: float = DEFAULT_CONTROL_WEIGHT
    target_velocity: float = DEFAULT_TARGET_VELOCITY
    terminal_weight: float = DEFAULT_TERMINAL_WEIGHT
    allow_mock_solver: bool = True

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
        require(
            isinstance(self.allow_mock_solver, bool),
            "allow_mock_solver must be a boolean",
            self.allow_mock_solver,
        )

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
    """Result container for a swing optimization run."""

    optimal_controls: list[np.ndarray[Any, Any]]
    optimal_trajectory: list[np.ndarray[Any, Any]]
    final_velocity: float
    cost: float
    converged: bool
    iterations: int

    def __post_init__(self) -> None:
        """Validate result consistency."""
        require(
            isinstance(self.optimal_controls, list),
            "optimal_controls must be a list",
            type(self.optimal_controls).__name__,
        )
        require(
            isinstance(self.optimal_trajectory, list),
            "optimal_trajectory must be a list",
            type(self.optimal_trajectory).__name__,
        )
        check_non_negative(self.final_velocity, "final_velocity")
        check_non_negative(self.cost, "cost")
        require(
            isinstance(self.converged, bool),
            "converged must be a boolean",
            self.converged,
        )
        require(self.iterations >= 0, "iterations must be >= 0", self.iterations)


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
]
