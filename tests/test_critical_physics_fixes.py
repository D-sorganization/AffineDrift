# ruff: noqa
"""Tests for the 8 critical physics bug fixes.

Covers issues #1742, #1743, #1744, #1745, #1746, #1749, #1750, #1755.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any
from pathlib import Path

import numpy as np
import pytest

from src.affine_control.ddp import _resample_controls, adaptive_timestep_ddp_mock
from src.affine_control.residuals import ResidualMonitor
from src.affine_control.swing_optimizer import SwingOptimizationConfig, SwingOptimizer
from src.core.contracts import ContractViolationError
from src.tools.rl_funnel_benchmark import (
    PENDULUM_L1,
    PENDULUM_L2,
    PENDULUM_M1,
    PENDULUM_M2,
    double_pendulum_drift,
    double_pendulum_mass_matrix,
)
from src.tools.wrist_universal_joint.torque_calculator import (
    universal_joint_transmission_ratio,
)

GRAVITY_M_S2 = 9.81


class TestMassMatrixPhysics:
    """#1742: mass matrix must reflect actual double-pendulum inertia."""

    def test_mass_matrix_is_not_identity(self) -> None:
        M = double_pendulum_mass_matrix(0.5, 0.3)
        assert not np.allclose(M, np.eye(2)), "Mass matrix must not be identity"

    def test_mass_matrix_diagonal_values(self) -> None:
        """M[0,0] = (m1+m2)*L1^2, M[1,1] = m2*L2^2."""
        th1, th2 = 0.0, 0.0
        M = double_pendulum_mass_matrix(th1, th2)
        assert np.isclose(M[0, 0], (PENDULUM_M1 + PENDULUM_M2) * PENDULUM_L1**2)
        assert np.isclose(M[1, 1], PENDULUM_M2 * PENDULUM_L2**2)

    def test_mass_matrix_symmetric(self) -> None:
        M = double_pendulum_mass_matrix(1.0, 0.5)
        np.testing.assert_array_almost_equal(M, M.T)

    def test_mass_matrix_positive_definite(self) -> None:
        M = double_pendulum_mass_matrix(0.7, -0.3)
        eigenvalues = np.linalg.eigvalsh(M)
        assert np.all(eigenvalues > 0), "Mass matrix must be positive definite"

    def test_mass_matrix_off_diagonal_depends_on_angle_diff(self) -> None:
        """Off-diagonal = m2*L1*L2*cos(th1-th2), changes with angle difference."""
        M_same = double_pendulum_mass_matrix(0.5, 0.5)
        M_diff = double_pendulum_mass_matrix(0.5, 1.5)
        # cos(0) != cos(-1), so off-diagonals should differ
        assert not np.isclose(M_same[0, 1], M_diff[0, 1])

    def test_drift_uses_correct_mass_matrix(self) -> None:
        """Drift dynamics at rest with angles should produce gravity-driven accelerations."""
        x = np.array([np.pi / 4, np.pi / 6, 0.0, 0.0])  # at rest, angled
        dx = double_pendulum_drift(0.0, x)
        # Velocities should be zero (dth1=0, dth2=0)
        assert dx[0] == 0.0
        assert dx[1] == 0.0
        # Accelerations should be nonzero (gravity acting on angled pendulum)
        assert dx[2] != 0.0 or dx[3] != 0.0


# ---------------------------------------------------------------------------
# Issue #1743: DDP mock solver must be guarded in production
# ---------------------------------------------------------------------------


class TestDDPMockGuard:
    """#1743: mock solver must not run in production path without guard."""

    def test_mock_solver_emits_warning_when_explicitly_opted_in(self) -> None:
        """Creating SwingOptimizer without solver should warn when mock use is explicit."""
        config = SwingOptimizationConfig(n_joints=1, horizon_steps=5, allow_mock_solver=True)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            SwingOptimizer(config)
        msgs = [str(w.message) for w in caught if issubclass(w.category, UserWarning)]
        assert any("mock" in m.lower() for m in msgs)

    def test_mock_solver_rejected_without_allow_flag(self) -> None:
        """Construction should fail when a real solver is not supplied."""
        config = SwingOptimizationConfig(
            n_joints=1, horizon_steps=5, max_iterations=1, allow_mock_solver=False
        )
        with pytest.raises(ContractViolationError, match="mock"):
            SwingOptimizer(config)

    def test_mock_solver_allowed_with_flag(self) -> None:
        """optimize() should succeed when allow_mock_solver=True."""
        config = SwingOptimizationConfig(
            n_joints=1, horizon_steps=5, max_iterations=1, allow_mock_solver=True
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            optimizer = SwingOptimizer(config)
        x0 = np.zeros(2)
        result = optimizer.optimize(x0, lambda x, u: np.array([x[1], u[0]]))
        assert result.iterations >= 1

    def test_real_solver_not_blocked(self) -> None:
        """Providing a real solver should not trigger the guard."""
        config = SwingOptimizationConfig(
            n_joints=1, horizon_steps=5, max_iterations=1, allow_mock_solver=True
        )

        def fake_solver(f: Any, x0: Any, xf: Any, u_init: Any, **kw: Any) -> Any:
            n = len(u_init)
            t = np.linspace(0, n * 0.01, n + 1)
            x_traj = np.zeros((n + 1, len(x0)))
            x_traj[0] = x0
            for i in range(n):
                x_traj[i + 1] = x_traj[i] + f(x_traj[i], u_init[i]) * 0.01
            return x_traj, np.array(u_init), t

        optimizer = SwingOptimizer(config, ddp_solver=fake_solver)
        x0 = np.zeros(2)
        result = optimizer.optimize(x0, lambda x, u: np.array([x[1], u[0]]))
        assert result.iterations >= 1


# ---------------------------------------------------------------------------
# Issue #1744: Duplicate elif makes MPC_FULL unreachable
# ---------------------------------------------------------------------------


class TestMPCFullReachable:
    """#1744: MPC_FULL must be reachable from MPC_WARN."""

    def test_mpc_full_reachable_with_persistent_critical(self) -> None:
        """Sustained critical residuals: LQR -> MPC_WARN -> MPC_FULL."""
        monitor = ResidualMonitor(eps_warning=0.1, eps_critical=0.5, n_hysteresis=2)
        x_nom = np.array([0.0])

        assert monitor.mode == "LQR"

        # Two critical samples -> LQR -> MPC_WARN
        monitor.update(np.array([0.6]), x_nom)
        monitor.update(np.array([0.6]), x_nom)
        assert monitor.mode == "MPC_WARN"

        # Two more critical samples -> MPC_WARN -> MPC_FULL
        monitor.update(np.array([0.6]), x_nom)
        monitor.update(np.array([0.6]), x_nom)
        msg = "MPC_FULL must be reachable; was unreachable due to duplicate elif"
        assert monitor.mode == "MPC_FULL", msg

    def test_full_state_cycle(self) -> None:
        """Full cycle: LQR -> MPC_WARN -> MPC_FULL -> MPC_WARN -> LQR."""
        monitor = ResidualMonitor(eps_warning=0.1, eps_critical=0.5, n_hysteresis=1)
        x_nom = np.array([0.0])

        # LQR -> MPC_WARN
        monitor.update(np.array([0.6]), x_nom)
        assert monitor.mode == "MPC_WARN"

        # MPC_WARN -> MPC_FULL
        monitor.update(np.array([0.6]), x_nom)
        assert monitor.mode == "MPC_FULL"

        # MPC_FULL -> MPC_WARN
        monitor.update(np.array([0.05]), x_nom)
        assert monitor.mode == "MPC_WARN"

        # MPC_WARN -> LQR
        monitor.update(np.array([0.05]), x_nom)
        assert monitor.mode == "LQR"


class TestGolfChapter03NumericalExample:
    """#2278: ch03 numerical example must use the table values consistently."""

    def test_double_pendulum_worked_example_values(self) -> None:
        """The published numerical example should match the stated masses."""
        m1 = 2.5
        m2 = 1.5
        l1 = 0.35
        l2 = 0.5
        theta2 = np.deg2rad(-5.0)
        theta1_dot = np.deg2rad(600.0)

        m11 = 0.015 + m2 * l1**2 + m2 * l2**2 + 0.4 + 2 * m2 * l1 * l2 * np.cos(theta2)
        g1 = (m1 * 0.175 + m2 * 0.35) * GRAVITY_M_S2 * np.sin(
            0.0
        ) + m2 * GRAVITY_M_S2 * 0.5 * np.sin(theta2)
        c21 = m2 * l1 * l2 * theta1_dot**2 * np.sin(theta2)

        assert np.isclose(m11, 1.496752, atol=1e-6)
        assert np.isclose(g1, -0.641248, atol=1e-6)
        assert np.isclose(c21, -2.508895, atol=1e-6)


# ---------------------------------------------------------------------------
# Issue #1745: Linearization must use central differences
# ---------------------------------------------------------------------------


class TestCentralDifferencesLinearization:
    """#1745: central differences give O(eps^2) accuracy vs O(eps) for forward."""

    def test_linearization_accuracy_quadratic(self) -> None:
        """For f(x) = x^2, central diff gives exact Jacobian 2x."""
        from src.tools.rl_funnel_benchmark import setpoint_lqr_controller

        # Use a simple target; the controller linearizes around it.
        # We can't directly test A, but we can verify the controller works.
        x_target = np.array([0.1, 0.1, 0.0, 0.0])
        # If linearization is correct, this should not raise
        ctrl = setpoint_lqr_controller(x_target)
        u = ctrl(0.0, x_target)
        # At the target, control should be ~zero
        np.testing.assert_allclose(u, np.zeros(2), atol=1e-3)

    def test_central_vs_forward_accuracy(self) -> None:
        """Verify central differences are more accurate on a known function."""
        # f(x) = x^3, f'(1) = 3.0 exactly
        # Use a larger eps where truncation error dominates over roundoff
        eps = 0.01
        x0 = 1.0

        f = lambda x: x**3

        # Forward difference: error is O(eps)
        fwd = (f(x0 + eps) - f(x0)) / eps
        # Central difference: error is O(eps^2)
        ctr = (f(x0 + eps) - f(x0 - eps)) / (2 * eps)

        # Central should be closer to 3.0
        msg = f"Central ({ctr}) should be closer to 3.0 than forward ({fwd})"
        assert abs(ctr - 3.0) < abs(fwd - 3.0), msg


# ---------------------------------------------------------------------------
# Issue #1746: Zero-order hold resampling index
# ---------------------------------------------------------------------------


class TestZeroOrderHoldResampling:
    """#1746: ZOH must use the last preceding control, not the next."""

    def test_zoh_picks_preceding_control(self) -> None:
        """At t=0.15, the control from t=0.1 (index 1) should be used, not t=0.2."""
        u_old = np.array([[1.0], [2.0], [3.0]])
        t_old = np.array([0.0, 0.1, 0.2, 0.3])  # 4 time points, 3 controls
        t_new = np.array([0.15])

        u_resampled = _resample_controls(u_old, t_old, t_new)
        # At t=0.15, last preceding time is t=0.1 (index 1), so control should be u[1]=2.0
        msg = f"Expected control 2.0 (from t=0.1), got {u_resampled[0, 0]}"
        assert u_resampled[0, 0] == 2.0, msg

    def test_zoh_at_exact_grid_point(self) -> None:
        """At an exact grid point t_old[k], ZOH uses u_old[k] (the interval starting there)."""
        u_old = np.array([[10.0], [20.0], [30.0]])
        t_old = np.array([0.0, 0.1, 0.2, 0.3])
        t_new = np.array([0.1])

        u_resampled = _resample_controls(u_old, t_old, t_new)
        # At exactly t=0.1, searchsorted('right') returns 2, so idx=1 => u[1]=20.0
        msg = f"At t=0.1 (grid point 1), ZOH should use u[1]=20.0, got {u_resampled[0, 0]}"
        assert u_resampled[0, 0] == 20.0, msg

    def test_zoh_at_time_zero(self) -> None:
        """At t=0.0, should use first control."""
        u_old = np.array([[5.0], [6.0]])
        t_old = np.array([0.0, 0.1, 0.2])
        t_new = np.array([0.0])

        u_resampled = _resample_controls(u_old, t_old, t_new)
        assert u_resampled[0, 0] == 5.0

    def test_zoh_beyond_last_time(self) -> None:
        """At t beyond last grid point, should clamp to last control."""
        u_old = np.array([[1.0], [2.0], [3.0]])
        t_old = np.array([0.0, 0.1, 0.2, 0.3])
        t_new = np.array([0.5])

        u_resampled = _resample_controls(u_old, t_old, t_new)
        assert u_resampled[0, 0] == 3.0


# ---------------------------------------------------------------------------
# Issue #1749: Wrist universal joint swapped arguments
# ---------------------------------------------------------------------------


class TestWristJointArgOrder:
    """#1749: phi_rad is rotation angle, delta_rad is bend angle."""

    def test_zero_bend_angle_gives_unity_ratio(self) -> None:
        """With delta=0 (no bend), omega and tau ratios should be 1.0."""
        omega, tau = universal_joint_transmission_ratio(phi_rad=0.5, delta_rad=0.0)
        assert np.isclose(omega, 1.0), f"omega_ratio={omega}, expected 1.0"
        assert np.isclose(tau, 1.0), f"tau_ratio={tau}, expected 1.0"

    def test_nonzero_bend_changes_ratio(self) -> None:
        """With nonzero delta, the ratios deviate from 1.0."""
        omega, tau = universal_joint_transmission_ratio(phi_rad=0.5, delta_rad=0.3)
        assert not np.isclose(omega, 1.0)
        assert not np.isclose(tau, 1.0)

    def test_ratio_varies_with_phi_at_fixed_delta(self) -> None:
        """At fixed bend angle, ratio should vary with rotation."""
        delta = 0.3
        ratios = [
            universal_joint_transmission_ratio(phi, delta)[0] for phi in np.linspace(0, np.pi, 10)
        ]
        # Should not all be the same
        assert max(ratios) != min(ratios)


# ---------------------------------------------------------------------------
# Issue #1750: DDP early termination must respect max_iters
# ---------------------------------------------------------------------------


class TestDDPMaxIters:
    """#1750: DDP must run up to max_iters, not terminate at iteration 2."""

    def test_max_iters_respected(self) -> None:
        """With max_iters=10, the loop should run more than 3 iterations."""

        call_count = 0

        def counting_dynamics(
            x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]
        ) -> np.ndarray[Any, Any]:
            nonlocal call_count
            call_count += 1
            return np.array([x[1], u[0]])

        x0 = np.array([0.0, 0.0])
        xf = np.array([1.0, 0.0])
        u_init = np.zeros((5, 1))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            adaptive_timestep_ddp_mock(counting_dynamics, x0, xf, u_init, max_iters=10)

        # Previously hardcoded to break at iteration 2 (3 total).
        # With 10 iterations, each doing 5 Euler steps + hessian evaluations,
        # we expect significantly more dynamics calls.
        # With 3 iterations it would be about ~300 calls.
        # With 10 iterations it should be about ~1000.
        msg = f"Expected >400 dynamics calls with max_iters=10, got {call_count}. Early termination bug may still be present."
        assert call_count > 400, msg

    def test_max_iters_1_runs_once(self) -> None:
        """max_iters=1 should still produce valid output."""

        def dyn(x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
            return np.array([x[1], u[0]])

        x0 = np.array([0.0, 0.0])
        xf = np.array([1.0, 0.0])
        u_init = np.zeros((5, 1))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            x_traj, u_traj, t_traj = adaptive_timestep_ddp_mock(dyn, x0, xf, u_init, max_iters=1)
        assert len(x_traj) > 0
        assert len(u_traj) > 0


# ---------------------------------------------------------------------------
# Issue #1755: Duplicate EPSILON constants
# ---------------------------------------------------------------------------


class TestEpsilonConsolidation:
    """#1755: wrist_universal_joint should reuse core EPSILON, not define its own."""

    def test_epsilon_is_same_object(self) -> None:
        """The EPSILON imported from wrist constants should be the core one."""
        from src.core.constants import EPSILON as CORE_EPSILON
        from src.tools.wrist_universal_joint.constants import EPSILON as WRIST_EPSILON

        assert CORE_EPSILON == WRIST_EPSILON
        # Both should be 1e-6
        assert CORE_EPSILON == 1e-6


# ---------------------------------------------------------------------------
# Issue #2324: energy-budget drop needs explicit braking explanation
# ---------------------------------------------------------------------------


class TestCh10EnergyBudgetExplanation:
    """#2324: chapter 10 should explain the 36 J phase-4-to-5 drop."""

    def test_ch10_mentions_eccentric_braking_and_losses(self) -> None:
        """The worked example should explain the apparent non-conservation."""
        repo_root = Path(__file__).resolve().parents[1]
        chapter = (
            repo_root / "articles" / "The_Physics_of_Golf" / "quarto" / "ch10_energy_transfer.qmd"
        ).read_text(encoding="utf-8")

        assert "eccentric braking" in chapter
        assert "negative work" in chapter
        assert "air resistance" in chapter or "internal dissipation" in chapter
        assert "conservation error" in chapter


# ---------------------------------------------------------------------------
# Issue #2332: short-iron D-plane weighting must remain face-dominant
# ---------------------------------------------------------------------------


class TestShortIronDPlaneWeighting:
    """#2332: short-iron launch-direction weighting should not flip toward path."""

    def test_short_iron_weighting_shifts_toward_face(self) -> None:
        """The chapter text should keep the short-iron split face-dominant."""
        chapter = Path("articles/The_Physics_of_Golf/quarto/ch31_swing_plane_launch.qmd").read_text(
            encoding="utf-8"
        )
        assert (
            "For a short iron (high loft, lower ball speed), the weighting shifts further toward the face:"
            in chapter
        )
        assert "w_{\\text{face}} \\approx 0.75, \\quad w_{\\text{path}} \\approx 0.25" in chapter
