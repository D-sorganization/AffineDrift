from typing import Any

import numpy as np

from src.affine_control.residuals import compute_hessian_norm


def test_compute_hessian_norm() -> None:
    """Test compute_hessian_norm function."""
    # Quadratic function f(x) = x^T A x
    # Hessian should be 2A
    A = np.array([[2.0, 0.0], [0.0, 1.0]])

    def f(x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        """Quadratic dynamics."""
        # Returns vector of size 1 (scalar function output treated as vector)
        val = float(x.T @ A @ x)
        return np.array([val])

    x0 = np.array([1.0, 1.0])
    u0 = np.array([0.0])

    # True Hessian is [[4, 0], [0, 2]]
    # Spectral norm is max singular value = 4
    # Note: Our function returns spectral norm of component Hessians.
    # Here we have 1 component.

    # Numerical norm
    norm = compute_hessian_norm(f, x0, u0, epsilon=1e-3)

    # Should be close to 4.0
    # Numerical error might be significant with central difference on Jacobian
    assert np.isclose(norm, 4.0, atol=0.1)
