"""Executable regression coverage for core optimization and RL funnel algorithms."""

from __future__ import annotations

import numpy as np
import pytest

from src.core.contracts.definitions import ContractViolationError
from src.core.optimizers.ilqr_solver import ILQRSolver
from src.tools.rl_funnel_controllers import (
    setpoint_lqr_controller,
    trajectory_tracking_lqr,
    validate_weight_matrix,
)


def test_ilqr_solver_optimizes_scalar_integrator_toward_target() -> None:
    solver = ILQRSolver()

    def dynamics(_x: np.ndarray, u: np.ndarray) -> np.ndarray:
        return np.array([u[0]], dtype=np.float64)

    x_traj, u_traj, t_traj = solver.optimize(
        dynamics,
        np.array([0.0], dtype=np.float64),
        np.array([1.0], dtype=np.float64),
        np.zeros((5, 1), dtype=np.float64),
        dt=0.2,
        max_iters=10,
    )

    assert x_traj.shape == (6, 1)
    assert u_traj.shape == (5, 1)
    assert t_traj.tolist() == pytest.approx([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    assert abs(x_traj[-1, 0] - 1.0) < abs(x_traj[0, 0] - 1.0)
    assert np.all(np.isfinite(x_traj))
    assert np.all(np.isfinite(u_traj))


def test_ilqr_solver_rejects_invalid_input_shapes() -> None:
    solver = ILQRSolver()

    def dynamics(x: np.ndarray, _u: np.ndarray) -> np.ndarray:
        return x

    with pytest.raises(ContractViolationError, match="x0 and xf must have same shape"):
        solver.optimize(
            dynamics,
            np.array([0.0], dtype=np.float64),
            np.array([0.0, 1.0], dtype=np.float64),
            np.zeros((2, 1), dtype=np.float64),
        )


def test_rl_funnel_setpoint_controller_returns_finite_control() -> None:
    controller = setpoint_lqr_controller(np.zeros(4, dtype=np.float64))

    control = controller(0.0, np.array([0.1, -0.1, 0.05, -0.05], dtype=np.float64))

    assert control.shape == (2,)
    assert np.all(np.isfinite(control))


def test_rl_funnel_trajectory_tracking_controller_returns_finite_control() -> None:
    t_ref = np.array([0.0, 0.5, 1.0], dtype=np.float64)
    x_ref = np.zeros((4, len(t_ref)), dtype=np.float64)
    controller = trajectory_tracking_lqr(t_ref, x_ref)

    control = controller(0.25, np.array([0.1, 0.0, 0.0, -0.1], dtype=np.float64))

    assert control.shape == (2,)
    assert np.all(np.isfinite(control))


def test_rl_funnel_weight_validation_rejects_shape_mismatch() -> None:
    with pytest.raises(ContractViolationError, match="Q_sp must have shape"):
        validate_weight_matrix(np.eye(3), (4, 4), "Q_sp")
