"""Tests for residual monitoring."""

import numpy as np

from src.affine_control.residuals import ResidualMonitor, compute_hessian_norm


def test_compute_hessian_norm():
    """Test Hessian norm computation."""

    def f(x, u):
        """Simple quadratic function."""
        return np.array([x[0] ** 2 + x[1] ** 2])

    x = np.array([1.0, 1.0])
    u = np.array([0.0])

    # Hessian of x^2 + y^2 is diag(2, 2)
    # Norm should be 2.0
    norm = compute_hessian_norm(f, x, u)
    assert np.isclose(norm, 2.0, atol=1e-2)


def test_residual_monitor():
    """Test residual monitor updates."""
    monitor = ResidualMonitor(eps_warning=0.1, eps_critical=0.5, n_hysteresis=2)

    # Start LQR
    assert monitor.mode == "LQR"

    # Good tracking
    monitor.update(np.array([0.0]), np.array([0.0]))
    assert monitor.mode == "LQR"

    # Critical error
    monitor.update(np.array([1.0]), np.array([0.0]))  # 1
    assert monitor.mode == "LQR"  # n=2

    monitor.update(np.array([1.0]), np.array([0.0]))  # 2
    assert monitor.mode == "MPC_FULL"

    # Recover
    monitor.update(np.array([0.0]), np.array([0.0]))
    assert monitor.mode == "MPC_FULL"

    monitor.update(np.array([0.0]), np.array([0.0]))
    assert monitor.mode == "LQR"
