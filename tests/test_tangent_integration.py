"""Integration and property-based tests for tangent model workflows.

Tests the full pipeline from dynamical system -> linearization -> residual monitoring,
verifying that the affine control modules work together correctly.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.affine_control.residuals import (
    ResidualMonitor,
    compute_hessian_norm,
    predict_residual_bound,
)
from src.core.contracts import ContractViolationError
from src.tangent_models.examples import (
    PlanarQuadrotor,
    SimplePendulum,
)

# ─── Strategies ───────────────────────────────────────────────

small_positive = st.floats(min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False)
small_angles = st.floats(
    min_value=-np.pi / 4, max_value=np.pi / 4, allow_nan=False, allow_infinity=False
)


# ─── Integration Tests: Linearization Consistency ─────────────


class TestLinearizationConsistency:
    """Verify linearization is consistent with dynamics across all systems."""

    def test_pendulum_linearization_at_equilibrium(self) -> None:
        """At the hanging equilibrium, linearization should match expected structure."""
        sys = SimplePendulum(m=1.0, L=1.0, g=9.81)
        x_eq = np.array([0.0, 0.0])  # Hanging down
        u_eq = np.array([0.0])

        A, B = sys.linearize(x_eq, u_eq)

        # A[0, 1] = 1 (dtheta_dot/domega = 1)
        assert A[0, 1] == pytest.approx(1.0, abs=1e-10)
        # A[1, 0] = -g/L * cos(0) = -g/L
        assert A[1, 0] == pytest.approx(-9.81, rel=1e-6)
        # B[1, 0] = 1/(m*L^2) = 1.0
        assert B[1, 0] == pytest.approx(1.0, rel=1e-6)

    def test_quadrotor_hover_linearization(self) -> None:
        """At hover, quadrotor should have standard linearized structure."""
        sys = PlanarQuadrotor(m=1.0, L=0.25, moment_inertia=0.01, g=9.81)
        x_hover = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        # Hover thrust: each motor produces mg/2
        u_hover = np.array([9.81 / 2, 9.81 / 2])

        A, B = sys.linearize(x_hover, u_hover)

        # Position to velocity coupling
        assert A[0, 3] == pytest.approx(1.0, abs=1e-10)
        assert A[1, 4] == pytest.approx(1.0, abs=1e-10)
        assert A[2, 5] == pytest.approx(1.0, abs=1e-10)

    @given(
        theta=small_angles,
        omega=st.floats(min_value=-1.0, max_value=1.0),
    )
    def test_pendulum_dynamics_linearization_approx(self, theta: float, omega: float) -> None:
        """Linearized dynamics should approximate nonlinear dynamics near the operating point."""
        sys = SimplePendulum()
        x0 = np.array([theta, omega])
        u0 = np.array([0.0])

        # Nonlinear dynamics at x0
        f0 = sys.dynamics(x0, u0)
        A, B = sys.linearize(x0, u0)

        # Small perturbation
        dx = np.array([0.01, 0.01])
        x_pert = x0 + dx

        # Nonlinear at perturbed point
        f_pert = sys.dynamics(x_pert, u0)
        # Linear prediction
        f_linear = f0 + A @ dx

        # Should be close for small perturbations
        np.testing.assert_allclose(f_pert, f_linear, atol=0.01)


# ─── Integration Tests: Residual Monitor Pipeline ────────────


class TestResidualMonitorPipeline:
    """Test the full residual monitoring workflow."""

    def test_monitor_transitions_on_large_residuals(self) -> None:
        """Monitor should transition to MPC_FULL when residuals exceed threshold."""
        monitor = ResidualMonitor(eps_warning=0.1, eps_critical=0.5, n_hysteresis=3)

        # Feed large residuals
        for _ in range(5):
            mode, r_est = monitor.update(
                x_meas=np.array([1.0, 0.0]),
                x_nom=np.array([0.0, 0.0]),
            )

        assert mode == "MPC_FULL"
        assert r_est > 0.5

    def test_monitor_returns_to_lqr_on_small_residuals(self) -> None:
        """Monitor should return to LQR when residuals drop below warning threshold."""
        monitor = ResidualMonitor(eps_warning=0.1, eps_critical=0.5, n_hysteresis=2)

        # First drive to MPC_FULL
        for _ in range(3):
            monitor.update(
                x_meas=np.array([1.0, 0.0]),
                x_nom=np.array([0.0, 0.0]),
            )
        assert monitor.mode == "MPC_FULL"

        # Now feed small residuals
        for _ in range(3):
            mode, r_est = monitor.update(
                x_meas=np.array([0.01, 0.0]),
                x_nom=np.array([0.0, 0.0]),
            )

        assert mode == "LQR"
        assert r_est < 0.1

    def test_hysteresis_prevents_oscillation(self) -> None:
        """Monitor should not oscillate between modes with borderline residuals."""
        monitor = ResidualMonitor(eps_warning=0.1, eps_critical=0.5, n_hysteresis=3)

        # Feed values in the hysteresis band (between warning and critical)
        modes = []
        for _ in range(10):
            mode, _ = monitor.update(
                x_meas=np.array([0.3, 0.0]),
                x_nom=np.array([0.0, 0.0]),
            )
            modes.append(mode)

        # Should stay in LQR since values are in hysteresis band, not above critical
        assert all(m == "LQR" for m in modes)


# ─── Integration Tests: Hessian and Residual Bound ───────────


class TestHessianResidualBound:
    """Test the Hessian computation and residual bound prediction pipeline."""

    def test_linear_system_has_zero_hessian(self) -> None:
        """A linear system should have approximately zero Hessian norm."""

        def linear_dynamics(
            x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]
        ) -> np.ndarray[Any, Any]:
            A = np.array([[0.0, 1.0], [-1.0, -0.1]])
            B = np.array([[0.0], [1.0]])
            return A @ x + B @ u

        x = np.array([1.0, 0.0])
        u = np.array([0.0])

        M = compute_hessian_norm(linear_dynamics, x, u)
        # Linear system has zero second derivatives
        assert M < 1e-3

    def test_residual_bound_accumulates(self) -> None:
        """Residual bound should accumulate over timesteps."""
        M_traj = np.array([1.0, 1.0, 1.0])
        delta_x = np.array([0.1, 0.1, 0.1])
        dt = np.array([0.01, 0.01, 0.01])

        bound = predict_residual_bound(M_traj, delta_x, dt)

        # Expected: sum(M_i/2 * delta_x_i^2 * dt_i) = 3 * (1/2 * 0.01 * 0.01) = 0.00015
        expected = 3 * (0.5 * 1.0 * 0.1**2 * 0.01)
        assert bound == pytest.approx(expected, rel=1e-6)
        assert bound >= 0

    def test_residual_bound_increases_with_perturbation(self) -> None:
        """Larger perturbations should yield larger residual bounds."""
        M_traj = np.array([1.0, 1.0])
        dt = np.array([0.01, 0.01])

        small_delta = np.array([0.01, 0.01])
        large_delta = np.array([0.1, 0.1])

        bound_small = predict_residual_bound(M_traj, small_delta, dt)
        bound_large = predict_residual_bound(M_traj, large_delta, dt)

        assert bound_large > bound_small


# ─── Property Tests: Dynamical Systems ───────────────────────


class TestDynamicalSystemProperties:
    """Property-based tests for dynamical systems."""

    @given(
        m=st.floats(min_value=0.1, max_value=10.0),
        L=st.floats(min_value=0.1, max_value=5.0),
    )
    def test_pendulum_constructor_accepts_positive_params(self, m: float, L: float) -> None:
        """Pendulum constructor should accept any positive parameters."""
        sys = SimplePendulum(m=m, L=L)
        assert sys.m == m
        assert sys.L == L

    @given(
        m=st.floats(max_value=0.0, allow_nan=False, allow_infinity=False),
    )
    def test_pendulum_rejects_non_positive_mass(self, m: float) -> None:
        """Pendulum constructor should reject non-positive mass."""
        with pytest.raises(ContractViolationError):
            SimplePendulum(m=m)

    @given(
        theta=small_angles,
        omega=st.floats(min_value=-2.0, max_value=2.0),
    )
    def test_pendulum_dynamics_finite(self, theta: float, omega: float) -> None:
        """Pendulum dynamics should always produce finite output for finite input."""
        sys = SimplePendulum()
        x = np.array([theta, omega])
        u = np.array([0.0])
        dx = sys.dynamics(x, u)
        assert np.all(np.isfinite(dx))

    @given(
        theta=small_angles,
        omega=st.floats(min_value=-2.0, max_value=2.0),
    )
    def test_pendulum_jacobian_shapes(self, theta: float, omega: float) -> None:
        """Linearization always produces correctly shaped matrices."""
        sys = SimplePendulum()
        x = np.array([theta, omega])
        u = np.array([0.0])
        A, B = sys.linearize(x, u)
        assert A.shape == (2, 2)
        assert B.shape == (2, 1)


# ─── Property Tests: Residual Monitor ────────────────────────


class TestResidualMonitorProperties:
    """Property-based tests for the ResidualMonitor."""

    @given(
        eps_w=st.floats(min_value=0.01, max_value=1.0),
        factor=st.floats(min_value=1.1, max_value=10.0),
    )
    def test_constructor_accepts_valid_thresholds(self, eps_w: float, factor: float) -> None:
        """Monitor constructor accepts any eps_warning < eps_critical."""
        eps_c = eps_w * factor
        monitor = ResidualMonitor(eps_warning=eps_w, eps_critical=eps_c)
        assert monitor.eps_warning == eps_w
        assert monitor.eps_critical == eps_c
        assert monitor.mode == "LQR"

    @given(
        eps=st.floats(min_value=0.01, max_value=1.0),
    )
    def test_constructor_rejects_invalid_ordering(self, eps: float) -> None:
        """Monitor constructor rejects eps_critical <= eps_warning."""
        with pytest.raises(ContractViolationError):
            ResidualMonitor(eps_warning=eps, eps_critical=eps)

    @given(
        residual_scale=st.floats(min_value=0.001, max_value=0.05),
    )
    def test_small_residuals_stay_lqr(self, residual_scale: float) -> None:
        """Small residuals should keep the monitor in LQR mode."""
        monitor = ResidualMonitor(eps_warning=0.1, eps_critical=0.5, n_hysteresis=2)

        for _ in range(5):
            mode, _ = monitor.update(
                x_meas=np.array([residual_scale, 0.0]),
                x_nom=np.array([0.0, 0.0]),
            )

        assert mode == "LQR"
