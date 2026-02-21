"""Tests for the Affine Control Swing Optimization Pipeline.

This module provides 25+ tests covering:
- SwingOptimizationConfig validation (positive dt, valid n_joints, etc.)
- SwingOptimizationResult dataclass validation
- Cost computation (zero control, known values, symmetry)
- Optimization with simple dynamics (double integrator)
- Convergence behavior and edge cases
"""

from __future__ import annotations

import unittest
from typing import Any

import numpy as np

from src.affine_control.swing_optimizer import (
    DEFAULT_CONTROL_WEIGHT,
    DEFAULT_CONVERGENCE_TOL,
    DEFAULT_DT,
    DEFAULT_HORIZON_STEPS,
    DEFAULT_MAX_ITERATIONS,
    DEFAULT_TARGET_VELOCITY,
    DEFAULT_TERMINAL_WEIGHT,
    SwingOptimizationConfig,
    SwingOptimizationResult,
    SwingOptimizer,
)
from src.core.contracts import ContractViolationError

# ── Helper dynamics functions ───────────────────────────────────────────────


def double_integrator_1dof(
    x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]
) -> np.ndarray[Any, Any]:
    """Single-DOF double integrator: x = [q, dq], u = [ddq]."""
    return np.array([x[1], u[0]])


def double_integrator_2dof(
    x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]
) -> np.ndarray[Any, Any]:
    """Two-DOF double integrator: x = [q1, q2, dq1, dq2], u = [ddq1, ddq2]."""
    n = 2
    dq = x[n:]
    ddq = u
    return np.concatenate([dq, ddq])


def double_integrator_3dof(
    x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]
) -> np.ndarray[Any, Any]:
    """Three-DOF double integrator: x = [q1..q3, dq1..dq3], u = [ddq1..ddq3]."""
    n = 3
    dq = x[n:]
    ddq = u
    return np.concatenate([dq, ddq])


# ── Config validation tests ─────────────────────────────────────────────────


class TestSwingOptimizationConfig(unittest.TestCase):
    """Tests for SwingOptimizationConfig dataclass validation."""

    def test_valid_config_defaults(self) -> None:
        """Config with n_joints and all defaults should be valid."""
        config = SwingOptimizationConfig(n_joints=3)
        self.assertEqual(config.n_joints, 3)
        self.assertEqual(config.horizon_steps, DEFAULT_HORIZON_STEPS)
        self.assertEqual(config.dt, DEFAULT_DT)
        self.assertEqual(config.max_iterations, DEFAULT_MAX_ITERATIONS)
        self.assertEqual(config.convergence_tol, DEFAULT_CONVERGENCE_TOL)
        self.assertEqual(config.control_weight, DEFAULT_CONTROL_WEIGHT)
        self.assertEqual(config.target_velocity, DEFAULT_TARGET_VELOCITY)
        self.assertEqual(config.terminal_weight, DEFAULT_TERMINAL_WEIGHT)

    def test_valid_config_custom(self) -> None:
        """Config with all custom values should be valid."""
        config = SwingOptimizationConfig(
            n_joints=5,
            horizon_steps=100,
            dt=0.005,
            max_iterations=200,
            convergence_tol=1e-8,
            control_weight=0.1,
            target_velocity=40.0,
            terminal_weight=50.0,
        )
        self.assertEqual(config.n_joints, 5)
        self.assertEqual(config.horizon_steps, 100)
        self.assertAlmostEqual(config.dt, 0.005)

    def test_state_dim_property(self) -> None:
        """state_dim should be 2 * n_joints."""
        config = SwingOptimizationConfig(n_joints=4)
        self.assertEqual(config.state_dim, 8)

    def test_control_dim_property(self) -> None:
        """control_dim should equal n_joints."""
        config = SwingOptimizationConfig(n_joints=4)
        self.assertEqual(config.control_dim, 4)

    def test_invalid_n_joints_zero(self) -> None:
        """n_joints=0 should raise ContractViolationError."""
        with self.assertRaises(ContractViolationError):
            SwingOptimizationConfig(n_joints=0)

    def test_invalid_n_joints_negative(self) -> None:
        """Negative n_joints should raise ContractViolationError."""
        with self.assertRaises(ContractViolationError):
            SwingOptimizationConfig(n_joints=-1)

    def test_invalid_dt_zero(self) -> None:
        """dt=0 should raise ContractViolationError."""
        with self.assertRaises(ContractViolationError):
            SwingOptimizationConfig(n_joints=3, dt=0.0)

    def test_invalid_dt_negative(self) -> None:
        """Negative dt should raise ContractViolationError."""
        with self.assertRaises(ContractViolationError):
            SwingOptimizationConfig(n_joints=3, dt=-0.01)

    def test_invalid_horizon_steps_zero(self) -> None:
        """horizon_steps=0 should raise ContractViolationError."""
        with self.assertRaises(ContractViolationError):
            SwingOptimizationConfig(n_joints=3, horizon_steps=0)

    def test_invalid_max_iterations_zero(self) -> None:
        """max_iterations=0 should raise ContractViolationError."""
        with self.assertRaises(ContractViolationError):
            SwingOptimizationConfig(n_joints=3, max_iterations=0)

    def test_invalid_convergence_tol_negative(self) -> None:
        """Negative convergence_tol should raise ContractViolationError."""
        with self.assertRaises(ContractViolationError):
            SwingOptimizationConfig(n_joints=3, convergence_tol=-1e-6)

    def test_invalid_control_weight_negative(self) -> None:
        """Negative control_weight should raise ContractViolationError."""
        with self.assertRaises(ContractViolationError):
            SwingOptimizationConfig(n_joints=3, control_weight=-0.01)

    def test_invalid_target_velocity_zero(self) -> None:
        """target_velocity=0 should raise ContractViolationError (must be positive)."""
        with self.assertRaises(ContractViolationError):
            SwingOptimizationConfig(n_joints=3, target_velocity=0.0)

    def test_config_is_frozen(self) -> None:
        """Config should be immutable (frozen dataclass)."""
        config = SwingOptimizationConfig(n_joints=3)
        with self.assertRaises(AttributeError):
            config.n_joints = 5  # type: ignore[misc]


# ── Result validation tests ─────────────────────────────────────────────────


class TestSwingOptimizationResult(unittest.TestCase):
    """Tests for SwingOptimizationResult dataclass validation."""

    def test_valid_result(self) -> None:
        """A well-formed result should pass validation."""
        result = SwingOptimizationResult(
            optimal_controls=[np.zeros(3) for _ in range(10)],
            optimal_trajectory=[np.zeros(6) for _ in range(11)],
            final_velocity=45.0,
            cost=1.23,
            converged=True,
            iterations=42,
        )
        self.assertTrue(result.converged)
        self.assertEqual(result.iterations, 42)
        self.assertAlmostEqual(result.final_velocity, 45.0)

    def test_result_not_converged(self) -> None:
        """Result with converged=False should be valid."""
        result = SwingOptimizationResult(
            optimal_controls=[],
            optimal_trajectory=[],
            final_velocity=0.0,
            cost=999.0,
            converged=False,
            iterations=100,
        )
        self.assertFalse(result.converged)

    def test_result_negative_cost_rejected(self) -> None:
        """Negative cost should raise ContractViolationError."""
        with self.assertRaises(ContractViolationError):
            SwingOptimizationResult(
                optimal_controls=[],
                optimal_trajectory=[],
                final_velocity=0.0,
                cost=-1.0,
                converged=False,
                iterations=0,
            )

    def test_result_negative_velocity_rejected(self) -> None:
        """Negative final_velocity should raise ContractViolationError."""
        with self.assertRaises(ContractViolationError):
            SwingOptimizationResult(
                optimal_controls=[],
                optimal_trajectory=[],
                final_velocity=-5.0,
                cost=0.0,
                converged=False,
                iterations=0,
            )

    def test_result_negative_iterations_rejected(self) -> None:
        """Negative iterations should raise ContractViolationError."""
        with self.assertRaises(ContractViolationError):
            SwingOptimizationResult(
                optimal_controls=[],
                optimal_trajectory=[],
                final_velocity=0.0,
                cost=0.0,
                converged=False,
                iterations=-1,
            )


# ── Cost computation tests ──────────────────────────────────────────────────


class TestSwingOptimizerCost(unittest.TestCase):
    """Tests for SwingOptimizer.compute_cost and related methods."""

    def setUp(self) -> None:
        """Create a standard 2-joint optimizer for cost tests."""
        self.config = SwingOptimizationConfig(
            n_joints=2,
            control_weight=1.0,
            target_velocity=10.0,
            terminal_weight=100.0,
        )
        self.optimizer = SwingOptimizer(self.config)

    def test_zero_control_zero_control_cost(self) -> None:
        """Zero control at target velocity should give zero cost."""
        # State at target: positions=0, velocities=target_velocity
        state = np.array([0.0, 0.0, 10.0, 10.0])
        control = np.zeros(2)
        cost = self.optimizer.compute_cost(state, control)
        self.assertAlmostEqual(cost, 0.0, places=10)

    def test_nonzero_control_adds_cost(self) -> None:
        """Non-zero control should add control cost u^T R u."""
        state = np.array([0.0, 0.0, 10.0, 10.0])  # at target velocity
        control = np.array([1.0, 0.0])
        cost = self.optimizer.compute_cost(state, control)
        # R = 1.0 * I, so cost = 1^2 = 1.0
        self.assertAlmostEqual(cost, 1.0, places=10)

    def test_velocity_deviation_adds_cost(self) -> None:
        """Velocity deviation from target should add state cost."""
        state = np.array([0.0, 0.0, 0.0, 0.0])  # zero velocity
        control = np.zeros(2)
        cost = self.optimizer.compute_cost(state, control)
        # dx_vel = [0 - 10, 0 - 10] = [-10, -10]
        # Q has 1.0 on velocity diag entries
        # cost = (-10)^2 + (-10)^2 = 200
        self.assertAlmostEqual(cost, 200.0, places=10)

    def test_position_does_not_affect_cost(self) -> None:
        """Position deviations should not affect cost (Q is zero for positions)."""
        state1 = np.array([0.0, 0.0, 10.0, 10.0])
        state2 = np.array([100.0, -50.0, 10.0, 10.0])
        control = np.zeros(2)
        cost1 = self.optimizer.compute_cost(state1, control)
        cost2 = self.optimizer.compute_cost(state2, control)
        self.assertAlmostEqual(cost1, cost2, places=10)

    def test_cost_is_non_negative(self) -> None:
        """Cost should always be non-negative for any state and control."""
        rng = np.random.default_rng(42)
        for _ in range(50):
            state = rng.standard_normal(4) * 100
            control = rng.standard_normal(2) * 10
            cost = self.optimizer.compute_cost(state, control)
            self.assertGreaterEqual(cost, 0.0)

    def test_cost_symmetry_in_control(self) -> None:
        """Cost should be the same for u and -u (quadratic form)."""
        state = np.array([0.0, 0.0, 5.0, 5.0])
        control = np.array([3.0, -2.0])
        cost_pos = self.optimizer.compute_cost(state, control)
        cost_neg = self.optimizer.compute_cost(state, -control)
        self.assertAlmostEqual(cost_pos, cost_neg, places=10)

    def test_terminal_cost_at_target_is_zero(self) -> None:
        """Terminal cost at target velocity should be zero."""
        state = np.array([0.0, 0.0, 10.0, 10.0])
        cost = self.optimizer.compute_terminal_cost(state)
        self.assertAlmostEqual(cost, 0.0, places=10)

    def test_terminal_cost_scales_with_terminal_weight(self) -> None:
        """Terminal cost should scale with terminal_weight."""
        config_low = SwingOptimizationConfig(n_joints=2, target_velocity=10.0, terminal_weight=1.0)
        config_high = SwingOptimizationConfig(
            n_joints=2, target_velocity=10.0, terminal_weight=100.0
        )
        opt_low = SwingOptimizer(config_low)
        opt_high = SwingOptimizer(config_high)

        state = np.array([0.0, 0.0, 0.0, 0.0])  # far from target
        cost_low = opt_low.compute_terminal_cost(state)
        cost_high = opt_high.compute_terminal_cost(state)
        self.assertAlmostEqual(cost_high / cost_low, 100.0, places=5)

    def test_compute_cost_wrong_state_dim_rejected(self) -> None:
        """State with wrong dimension should raise ContractViolationError."""
        with self.assertRaises(ContractViolationError):
            self.optimizer.compute_cost(np.zeros(3), np.zeros(2))

    def test_compute_cost_wrong_control_dim_rejected(self) -> None:
        """Control with wrong dimension should raise ContractViolationError."""
        with self.assertRaises(ContractViolationError):
            self.optimizer.compute_cost(np.zeros(4), np.zeros(5))

    def test_compute_cost_nan_state_rejected(self) -> None:
        """State with NaN should raise ContractViolationError."""
        with self.assertRaises(ContractViolationError):
            self.optimizer.compute_cost(
                np.array([0.0, float("nan"), 0.0, 0.0]),
                np.zeros(2),
            )

    def test_trajectory_cost_consistency(self) -> None:
        """Trajectory cost should equal sum of running costs plus terminal."""
        traj = [np.array([0.0, 0.0, 5.0, 5.0]) for _ in range(6)]
        ctrls = [np.array([1.0, 1.0]) for _ in range(5)]

        total = self.optimizer.compute_trajectory_cost(traj, ctrls)

        # Manual calculation
        running = sum(
            self.optimizer.compute_cost(traj[t], ctrls[t]) * self.config.dt for t in range(5)
        )
        terminal = self.optimizer.compute_terminal_cost(traj[-1])
        expected = running + terminal

        self.assertAlmostEqual(total, expected, places=10)


# ── Optimizer integration tests ─────────────────────────────────────────────


class TestSwingOptimizerOptimize(unittest.TestCase):
    """Integration tests for SwingOptimizer.optimize."""

    def test_optimize_1dof_runs_without_error(self) -> None:
        """Optimization on a 1-DOF double integrator should complete."""
        config = SwingOptimizationConfig(
            n_joints=1,
            horizon_steps=10,
            max_iterations=3,
            target_velocity=5.0,
        )
        optimizer = SwingOptimizer(config)
        x0 = np.zeros(2)
        result = optimizer.optimize(x0, double_integrator_1dof)

        self.assertIsInstance(result, SwingOptimizationResult)
        self.assertGreater(len(result.optimal_controls), 0)
        self.assertGreater(len(result.optimal_trajectory), 0)
        self.assertGreaterEqual(result.final_velocity, 0.0)
        self.assertGreaterEqual(result.cost, 0.0)
        self.assertGreater(result.iterations, 0)

    def test_optimize_2dof_runs_without_error(self) -> None:
        """Optimization on a 2-DOF double integrator should complete."""
        config = SwingOptimizationConfig(
            n_joints=2,
            horizon_steps=10,
            max_iterations=3,
            target_velocity=10.0,
        )
        optimizer = SwingOptimizer(config)
        x0 = np.zeros(4)
        result = optimizer.optimize(x0, double_integrator_2dof)

        self.assertIsInstance(result, SwingOptimizationResult)
        self.assertEqual(len(result.optimal_trajectory), len(result.optimal_controls) + 1)

    def test_optimize_3dof_runs_without_error(self) -> None:
        """Optimization on a 3-DOF double integrator should complete."""
        config = SwingOptimizationConfig(
            n_joints=3,
            horizon_steps=10,
            max_iterations=2,
            target_velocity=15.0,
        )
        optimizer = SwingOptimizer(config)
        x0 = np.zeros(6)
        result = optimizer.optimize(x0, double_integrator_3dof)

        self.assertIsInstance(result, SwingOptimizationResult)

    def test_optimize_wrong_initial_state_dim(self) -> None:
        """Wrong initial_state dimension should raise ContractViolationError."""
        config = SwingOptimizationConfig(n_joints=2, horizon_steps=5, max_iterations=1)
        optimizer = SwingOptimizer(config)
        with self.assertRaises(ContractViolationError):
            optimizer.optimize(np.zeros(3), double_integrator_2dof)  # need dim 4

    def test_optimize_nan_initial_state_rejected(self) -> None:
        """NaN in initial_state should raise ContractViolationError."""
        config = SwingOptimizationConfig(n_joints=1, horizon_steps=5, max_iterations=1)
        optimizer = SwingOptimizer(config)
        with self.assertRaises(ContractViolationError):
            optimizer.optimize(
                np.array([0.0, float("nan")]),
                double_integrator_1dof,
            )

    def test_optimize_result_trajectory_length(self) -> None:
        """Trajectory should be one longer than controls."""
        config = SwingOptimizationConfig(
            n_joints=1,
            horizon_steps=10,
            max_iterations=2,
        )
        optimizer = SwingOptimizer(config)
        x0 = np.zeros(2)
        result = optimizer.optimize(x0, double_integrator_1dof)
        self.assertEqual(
            len(result.optimal_trajectory),
            len(result.optimal_controls) + 1,
        )

    def test_optimize_cost_is_finite(self) -> None:
        """Optimization cost should be a finite positive number."""
        config = SwingOptimizationConfig(
            n_joints=1,
            horizon_steps=10,
            max_iterations=3,
        )
        optimizer = SwingOptimizer(config)
        x0 = np.zeros(2)
        result = optimizer.optimize(x0, double_integrator_1dof)
        self.assertTrue(np.isfinite(result.cost))
        self.assertGreaterEqual(result.cost, 0.0)


# ── Property and accessor tests ─────────────────────────────────────────────


class TestSwingOptimizerProperties(unittest.TestCase):
    """Tests for SwingOptimizer properties and accessors."""

    def test_config_property(self) -> None:
        """Config should be accessible via property."""
        config = SwingOptimizationConfig(n_joints=3)
        optimizer = SwingOptimizer(config)
        self.assertIs(optimizer.config, config)

    def test_R_matrix_shape(self) -> None:
        """R matrix should be (control_dim x control_dim)."""
        config = SwingOptimizationConfig(n_joints=3, control_weight=0.5)
        optimizer = SwingOptimizer(config)
        R = optimizer.R
        self.assertEqual(R.shape, (3, 3))
        # Should be 0.5 * I
        np.testing.assert_array_almost_equal(R, 0.5 * np.eye(3))

    def test_Q_matrix_shape(self) -> None:
        """Q matrix should be (state_dim x state_dim)."""
        config = SwingOptimizationConfig(n_joints=2)
        optimizer = SwingOptimizer(config)
        Q = optimizer.Q
        self.assertEqual(Q.shape, (4, 4))
        # Position block should be zero
        np.testing.assert_array_almost_equal(Q[:2, :2], np.zeros((2, 2)))
        # Velocity block should be identity
        np.testing.assert_array_almost_equal(Q[2:, 2:], np.eye(2))

    def test_Q_f_matrix_is_scaled_Q(self) -> None:
        """Q_f should be terminal_weight * Q."""
        config = SwingOptimizationConfig(
            n_joints=2,
            terminal_weight=50.0,
        )
        optimizer = SwingOptimizer(config)
        Q = optimizer.Q
        Q_f = optimizer.Q_f
        np.testing.assert_array_almost_equal(Q_f, 50.0 * Q)

    def test_R_is_copy(self) -> None:
        """R property should return a copy (not a reference)."""
        config = SwingOptimizationConfig(n_joints=2)
        optimizer = SwingOptimizer(config)
        R1 = optimizer.R
        R1[0, 0] = 999.0
        R2 = optimizer.R
        self.assertNotAlmostEqual(R2[0, 0], 999.0)

    def test_zero_control_weight_gives_zero_R(self) -> None:
        """control_weight=0 should produce a zero R matrix."""
        config = SwingOptimizationConfig(n_joints=2, control_weight=0.0)
        optimizer = SwingOptimizer(config)
        R = optimizer.R
        np.testing.assert_array_almost_equal(R, np.zeros((2, 2)))


if __name__ == "__main__":
    unittest.main()
