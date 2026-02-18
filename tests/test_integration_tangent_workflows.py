"""Integration tests for tangent model workflows.

Tests that tangent models, affine control DDP, residual monitoring,
and cross-module data flows work correctly end-to-end.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest

# ---- Affine control imports ----
from src.affine_control.ddp import (
    adaptive_timestep_ddp_mock,
    estimate_perturbation_size,
)
from src.affine_control.residuals import (
    ResidualMonitor,
    compute_hessian_bound,
    predict_residual_bound,
)

# ---- Tangent model imports ----
from src.tangent_models.examples import (
    PlanarQuadrotor,
    RobotArm,
    SimplePendulum,
    SpacecraftRendezvous,
)

# ---------------------------------------------------------------------------
# Tangent Model Examples -- Valid Outputs
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestTangentModelOutputs:
    """Verify that every tangent model example produces valid outputs."""

    # -- SimplePendulum --

    def test_pendulum_dynamics_returns_finite_array(self) -> None:
        """SimplePendulum.dynamics must return a finite 2-element array."""
        pend = SimplePendulum(m=1.0, L=1.0)
        x = np.array([0.1, 0.0])
        u = np.array([0.0])
        dx = pend.dynamics(x, u)
        assert dx.shape == (2,)
        assert np.all(np.isfinite(dx))

    def test_pendulum_linearize_returns_correct_shapes(self) -> None:
        """SimplePendulum.linearize must return A(2x2) and B(2x1)."""
        pend = SimplePendulum(m=1.0, L=1.0)
        x = np.array([0.1, 0.0])
        u = np.array([0.0])
        A, B = pend.linearize(x, u)
        assert A.shape == (2, 2)
        assert B.shape == (2, 1)
        assert np.all(np.isfinite(A))
        assert np.all(np.isfinite(B))

    # -- PlanarQuadrotor --

    def test_quadrotor_dynamics_returns_finite_array(self) -> None:
        """PlanarQuadrotor.dynamics must return a finite 6-element array."""
        quad = PlanarQuadrotor(m=1.0, L=0.25, moment_inertia=0.01)
        x = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        u = np.array([4.905, 4.905])  # hover thrust
        dx = quad.dynamics(x, u)
        assert dx.shape == (6,)
        assert np.all(np.isfinite(dx))

    def test_quadrotor_linearize_returns_correct_shapes(self) -> None:
        """PlanarQuadrotor.linearize must return A(6x6) and B(6x2)."""
        quad = PlanarQuadrotor()
        x = np.zeros(6)
        u = np.array([4.905, 4.905])
        A, B = quad.linearize(x, u)
        assert A.shape == (6, 6)
        assert B.shape == (6, 2)
        assert np.all(np.isfinite(A))
        assert np.all(np.isfinite(B))

    # -- SpacecraftRendezvous --

    def test_spacecraft_dynamics_returns_finite_array(self) -> None:
        """SpacecraftRendezvous.dynamics must return a finite 6-element array."""
        sc = SpacecraftRendezvous()
        x = np.array([0.0, 0.0, 0.0, 0.1, 0.0, 0.0])
        u = np.array([0.0, 0.0, 0.0])
        dx = sc.dynamics(x, u)
        assert dx.shape == (6,)
        assert np.all(np.isfinite(dx))

    def test_spacecraft_linearize_returns_correct_shapes(self) -> None:
        """SpacecraftRendezvous.linearize must return A(6x6) and B(6x3)."""
        sc = SpacecraftRendezvous()
        x = np.zeros(6)
        u = np.zeros(3)
        A, B = sc.linearize(x, u)
        assert A.shape == (6, 6)
        assert B.shape == (6, 3)
        assert np.all(np.isfinite(A))
        assert np.all(np.isfinite(B))

    # -- RobotArm --

    def test_robot_arm_dynamics_returns_finite_array(self) -> None:
        """RobotArm.dynamics must return a finite 4-element array."""
        arm = RobotArm()
        x = np.array([0.1, 0.2, 0.0, 0.0])
        u = np.array([0.0, 0.0])
        dx = arm.dynamics(x, u)
        assert dx.shape == (4,)
        assert np.all(np.isfinite(dx))

    def test_robot_arm_linearize_returns_correct_shapes(self) -> None:
        """RobotArm.linearize must return A(4x4) and B(4x2)."""
        arm = RobotArm()
        x = np.array([0.1, 0.2, 0.0, 0.0])
        u = np.array([0.0, 0.0])
        A, B = arm.linearize(x, u)
        assert A.shape == (4, 4)
        assert B.shape == (4, 2)
        assert np.all(np.isfinite(A))
        assert np.all(np.isfinite(B))


# ---------------------------------------------------------------------------
# Affine Control DDP -- End-to-End Workflow
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestDDPWorkflowEndToEnd:
    """Integration tests for the adaptive timestep DDP workflow."""

    @staticmethod
    def _double_integrator(
        x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]
    ) -> np.ndarray[Any, Any]:
        """Minimal double-integrator dynamics: x=[pos, vel], u=[accel]."""
        return np.array([x[1], u[0]])

    def test_ddp_returns_consistent_trajectory_lengths(self) -> None:
        """DDP output trajectories must satisfy len(x) == len(t) and len(u) == len(t)-1."""
        x0 = np.array([0.0, 0.0])
        xf = np.array([1.0, 0.0])
        u_init = np.zeros((10, 1))

        x_traj, u_traj, t_traj = adaptive_timestep_ddp_mock(
            self._double_integrator,
            x0,
            xf,
            u_init,
            eps_residual=0.01,
            max_iters=3,
        )
        assert len(t_traj) == len(x_traj)
        assert len(u_traj) == len(t_traj) - 1

    def test_ddp_time_is_monotonically_increasing(self) -> None:
        """DDP time grid must be strictly monotonically increasing."""
        x0 = np.array([0.0, 0.0])
        xf = np.array([1.0, 0.0])
        u_init = np.zeros((10, 1))

        _, _, t_traj = adaptive_timestep_ddp_mock(
            self._double_integrator,
            x0,
            xf,
            u_init,
            eps_residual=0.01,
            max_iters=3,
        )
        dts = np.diff(t_traj)
        assert np.all(dts > 0), "Time grid must be strictly increasing"

    def test_ddp_with_pendulum_dynamics(self) -> None:
        """DDP must run without error when using SimplePendulum dynamics."""
        pend = SimplePendulum(m=1.0, L=1.0)
        x0 = np.array([0.5, 0.0])
        xf = np.array([0.0, 0.0])
        u_init = np.zeros((10, 1))

        x_traj, u_traj, t_traj = adaptive_timestep_ddp_mock(
            pend.dynamics,
            x0,
            xf,
            u_init,
            eps_residual=0.01,
            max_iters=3,
        )
        assert x_traj.shape[1] == 2, "Pendulum state is 2-dimensional"
        assert np.all(np.isfinite(x_traj))

    def test_ddp_timesteps_within_clip_bounds(self) -> None:
        """DDP adaptive timesteps must be clipped within [DT_CLIP_MIN, DT_CLIP_MAX]."""
        from src.core.constants import DT_CLIP_MAX, DT_CLIP_MIN

        x0 = np.array([0.0, 0.0])
        xf = np.array([1.0, 0.0])
        u_init = np.zeros((10, 1))

        _, _, t_traj = adaptive_timestep_ddp_mock(
            self._double_integrator,
            x0,
            xf,
            u_init,
            eps_residual=0.01,
            max_iters=5,
        )
        dts = np.diff(t_traj)
        assert np.all(dts >= DT_CLIP_MIN - 1e-12)
        assert np.all(dts <= DT_CLIP_MAX + 1e-12)


# ---------------------------------------------------------------------------
# Residual Monitoring -- Integration Workflow
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestResidualMonitoringWorkflow:
    """Integration tests for the residual monitoring pipeline."""

    def test_monitor_full_lifecycle(self) -> None:
        """ResidualMonitor must handle a realistic sequence of measurements.

        Invariant: mode transitions follow LQR -> MPC_FULL -> LQR cycle
        when residuals rise above eps_critical then fall below eps_warning.
        """
        monitor = ResidualMonitor(
            eps_warning=0.05,
            eps_critical=0.2,
            n_hysteresis=2,
        )
        x_nom = np.array([0.0, 0.0])

        # Start in LQR
        assert monitor.mode == "LQR"

        # Ramp up: residual above critical for n_hysteresis steps
        for _ in range(2):
            mode, r = monitor.update(np.array([0.3, 0.0]), x_nom)
            assert r >= 0

        # Should have switched to MPC_FULL
        assert monitor.mode == "MPC_FULL"

        # Ramp down: residual below warning for n_hysteresis steps
        for _ in range(2):
            mode, r = monitor.update(np.array([0.01, 0.0]), x_nom)
            assert r >= 0

        # Should have switched back to LQR
        assert monitor.mode == "LQR"

    def test_hessian_bound_with_real_dynamics(self) -> None:
        """compute_hessian_bound must return a finite positive number for real dynamics."""
        pend = SimplePendulum()
        x = np.array([0.5, 0.1])
        u = np.array([0.0])

        M = compute_hessian_bound(pend.dynamics, x, u)
        assert np.isfinite(M)
        assert M >= 0

    def test_predict_residual_bound_positive(self) -> None:
        """predict_residual_bound must return a non-negative value for valid inputs."""
        M_traj = np.array([1.0, 2.0, 1.5])
        dx_traj = np.array([0.01, 0.02, 0.015])
        dt_traj = np.array([0.01, 0.01, 0.01])

        r_bound = predict_residual_bound(M_traj, dx_traj, dt_traj)
        assert r_bound >= 0
        assert np.isfinite(r_bound)

    def test_perturbation_estimation_with_real_state(self) -> None:
        """estimate_perturbation_size must return a positive float for valid state."""
        x = np.array([1.0, 2.0, 3.0])
        u = np.array([0.0])

        pert = estimate_perturbation_size(x, u)
        assert pert > 0
        assert np.isfinite(pert)


# ---------------------------------------------------------------------------
# Cross-Module Data Flow: tangent_models -> affine_control
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestCrossModuleDataFlow:
    """Test that data produced by tangent models flows correctly into
    the affine control pipeline.
    """

    def test_pendulum_dynamics_into_ddp(self) -> None:
        """SimplePendulum dynamics must be accepted by DDP without shape errors.

        Invariant: tangent model dynamics signature matches DDP f(x, u) contract.
        """
        pend = SimplePendulum(m=2.0, L=0.5)
        x0 = np.array([1.0, 0.0])
        xf = np.array([0.0, 0.0])
        u_init = np.zeros((15, 1))

        x_traj, u_traj, t_traj = adaptive_timestep_ddp_mock(
            pend.dynamics,
            x0,
            xf,
            u_init,
            eps_residual=0.02,
            max_iters=3,
        )
        # Verify data shapes are consistent
        assert x_traj.shape[0] == len(t_traj)
        assert u_traj.shape[0] == len(t_traj) - 1
        assert x_traj.shape[1] == x0.shape[0]

    def test_pendulum_linearize_into_hessian_bound(self) -> None:
        """Hessian bound computation must work with tangent model dynamics.

        Invariant: the dynamics function from tangent_models satisfies the
        signature required by compute_hessian_bound.
        """
        pend = SimplePendulum()
        x = np.array([0.3, 0.1])
        u = np.array([0.5])

        M = compute_hessian_bound(pend.dynamics, x, u)
        assert np.isfinite(M)
        assert M >= 0

    def test_ddp_trajectory_into_residual_monitor(self) -> None:
        """DDP trajectory output must be consumable by ResidualMonitor.

        Invariant: each state pair (x_traj[i], x_traj[i+1]) can be fed to
        monitor.update as (x_meas, x_nom).
        """

        def double_integrator(
            x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]
        ) -> np.ndarray[Any, Any]:
            return np.array([x[1], u[0]])

        x0 = np.array([0.0, 0.0])
        xf = np.array([1.0, 0.0])
        u_init = np.zeros((10, 1))

        x_traj, _, _ = adaptive_timestep_ddp_mock(
            double_integrator,
            x0,
            xf,
            u_init,
            eps_residual=0.01,
            max_iters=3,
        )

        monitor = ResidualMonitor(
            eps_warning=0.01,
            eps_critical=0.1,
            n_hysteresis=2,
        )

        # Feed consecutive state pairs into the monitor
        for i in range(len(x_traj) - 1):
            mode, residual = monitor.update(x_traj[i + 1], x_traj[i])
            assert isinstance(mode, str)
            assert mode in ("LQR", "MPC_WARN", "MPC_FULL")
            assert residual >= 0

    def test_hessian_bounds_along_trajectory(self) -> None:
        """Hessian bounds computed along a DDP trajectory must all be finite.

        Invariant: for every point on the trajectory, M(x, u) is finite and
        non-negative.
        """
        pend = SimplePendulum()
        x0 = np.array([0.5, 0.0])
        xf = np.array([0.0, 0.0])
        u_init = np.zeros((8, 1))

        x_traj, u_traj, _ = adaptive_timestep_ddp_mock(
            pend.dynamics,
            x0,
            xf,
            u_init,
            eps_residual=0.01,
            max_iters=3,
        )

        for i in range(len(u_traj)):
            M = compute_hessian_bound(pend.dynamics, x_traj[i], u_traj[i])
            assert np.isfinite(M), f"Non-finite Hessian bound at step {i}"
            assert M >= 0

    def test_full_pipeline_tangent_to_residual_bound(self) -> None:
        """Full pipeline: tangent model -> DDP -> Hessian bounds -> residual bound.

        Invariant: the predicted residual bound for the entire trajectory is
        a finite non-negative number.
        """
        pend = SimplePendulum(m=1.0, L=1.0)
        x0 = np.array([0.3, 0.0])
        xf = np.array([0.0, 0.0])
        u_init = np.zeros((8, 1))

        x_traj, u_traj, t_traj = adaptive_timestep_ddp_mock(
            pend.dynamics,
            x0,
            xf,
            u_init,
            eps_residual=0.01,
            max_iters=3,
        )

        N = len(u_traj)
        M_traj = np.array(
            [compute_hessian_bound(pend.dynamics, x_traj[i], u_traj[i]) for i in range(N)]
        )
        dx_traj = np.array([estimate_perturbation_size(x_traj[i], u_traj[i]) for i in range(N)])
        dt_traj = np.diff(t_traj)[:N]

        r_bound = predict_residual_bound(M_traj, dx_traj, dt_traj)
        assert np.isfinite(r_bound)
        assert r_bound >= 0
