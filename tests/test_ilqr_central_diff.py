"""Tests to verify iLQR uses central differences for O(eps^2) accuracy."""

import numpy as np
import pytest


def _quadratic_dynamics(x: np.ndarray, u: np.ndarray) -> np.ndarray:
    """Simple quadratic dynamics for testing linearization accuracy."""
    return np.array([x[0] ** 2 + u[0], x[1] + x[0] * u[0]])


def _exact_A(x: np.ndarray, u: np.ndarray) -> np.ndarray:
    """Exact state Jacobian for the quadratic dynamics."""
    return np.array([[2 * x[0], 0.0], [u[0], 1.0]])


def _exact_B(x: np.ndarray, u: np.ndarray) -> np.ndarray:
    """Exact control Jacobian for the quadratic dynamics."""
    return np.array([[1.0], [x[0]]])


def test_linearization_is_central_difference_accurate() -> None:
    """Verify linearization matches exact Jacobians to O(eps^2) accuracy."""
    try:
        from src.core.optimizers.ilqr_solver import ILQRSolver
    except ImportError:
        pytest.skip("iLQR solver not available")

    solver = ILQRSolver()
    x0 = np.array([1.5, -0.3])
    u0 = np.array([0.7])

    n_x = len(x0)
    n_u = len(u0)
    dt = 1.0

    # _linearize_dynamics returns Ad = I + A*dt and Bd = B*dt
    # With dt=1.0, Ad = I + A and Bd = B, so A = Ad - I and B = Bd
    Ad_num, Bd_num = solver._linearize_dynamics(_quadratic_dynamics, x0, u0, n_x, n_u, dt)
    A_num = Ad_num - np.eye(n_x)
    B_num = Bd_num

    A_exact = _exact_A(x0, u0)
    B_exact = _exact_B(x0, u0)

    # Central differences should achieve O(eps^2) ~ 1e-10 accuracy
    # Forward differences only achieve O(eps) ~ 1e-5 accuracy
    assert np.allclose(
        A_num, A_exact, atol=1e-8
    ), f"A matrix error too large: {np.max(np.abs(A_num - A_exact)):.2e}"
    assert np.allclose(
        B_num, B_exact, atol=1e-8
    ), f"B matrix error too large: {np.max(np.abs(B_num - B_exact)):.2e}"
