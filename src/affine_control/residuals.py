from typing import Any
from collections.abc import Callable

import numpy as np


def compute_hessian_norm(
    f: Callable[[np.ndarray[Any, Any], np.ndarray[Any, Any]], np.ndarray[Any, Any]],
    x: np.ndarray[Any, Any],
    u: np.ndarray[Any, Any],
    epsilon: float = 1e-4,
) -> float:
    """
    Computes numerical approximation of the Hessian norm ||H_f||.
    H_f is the tensor [d^2f / dx_i dx_j].
    The norm used is the maximum spectral norm of the component Hessians.
    """
    n = len(x)
    dx = len(f(x, u))

    # Very expensive numerical Hessian for prototype
    # In practice: Use JAX or analytical derivatives
    # hessians = []

    # f(x) -> [f1, f2, ...]
    # For each fk, compute H_k

    # Simplified: Just compute trace or Frobenius of Jacobian variation?
    # Let's do a central difference on the Jacobian

    # Jacobian J(x) = df/dx
    def jacobian(x0: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        J = np.zeros((dx, n))
        for i in range(n):
            x_plus = x0.copy()
            x_plus[i] += epsilon
            x_minus = x0.copy()
            x_minus[i] -= epsilon
            J[:, i] = (f(x_plus, u) - f(x_minus, u)) / (2 * epsilon)
        return J

    # Hessian is derivative of Jacobian
    # Tensor H[k, i, j] = dJ_ki / dx_j
    H = np.zeros((dx, n, n))
    base_x = x.copy()

    for j in range(n):
        x_plus = base_x.copy()
        x_plus[j] += epsilon
        x_minus = base_x.copy()
        x_minus[j] -= epsilon

        J_plus = jacobian(x_plus)
        J_minus = jacobian(x_minus)

        # dJ / dx_j
        H[:, :, j] = (J_plus - J_minus) / (2 * epsilon)

    # Local bound M = max_k ||H_k||_2
    M = 0.0
    for k in range(dx):
        H_k = H[k, :, :]
        # Spectral norm
        norm_k = np.linalg.norm(H_k, ord=2)
        M = max(M, float(norm_k))

    return M


def predict_residual_bound(
    M_traj: np.ndarray[Any, Any], delta_x_traj: np.ndarray[Any, Any], dt_traj: np.ndarray[Any, Any]
) -> float:
    """
    Computes the upper bound on residual norm:
    ||r(t)|| <= sum( M_i/2 * ||delta_x_i||^2 * dt_i )

    Args:
        M_traj: List of Hessian bounds M_i
        delta_x_traj: List of perturbation norms ||delta_x_i||
        dt_traj: List of timesteps

    Returns:
        r_bound: Predicted residual bound at final time
    """
    r_accum = 0.0
    # Integral roughly sum( M/2 * dx^2 * dt )

    # Assume trapezoidal or simple left-rect
    for i in range(len(dt_traj)):
        # If trajectories match standard lengths
        if i >= len(M_traj) or i >= len(delta_x_traj):
            break

        rate = float((M_traj[i] / 2.0) * (delta_x_traj[i] ** 2))
        r_accum += rate * float(dt_traj[i])

    return r_accum


class ResidualMonitor:
    """
    Monitors residuals and triggers mode switching.
    """

    def __init__(
        self, eps_warning: float = 0.01, eps_critical: float = 0.05, n_hysteresis: int = 3
    ) -> None:
        self.eps_warning = eps_warning
        self.eps_critical = eps_critical
        self.n = n_hysteresis

        self.high_count = 0
        self.low_count = 0
        self.mode = "LQR"  # LQR, MPC_WARN, MPC_FULL

    def update(self, x_meas: np.ndarray[Any, Any], x_nom: np.ndarray[Any, Any]) -> tuple[str, float]:
        """
        Update with new measurement.
        Approximate residual r ~ x_meas - x_nom (assuming drift is dominant error)
        In reality: r = x_meas - (x_nom + Phi * delta_x0)
        """
        # Simplified: Use tracking error as proxy for drift if delta_x0 is small
        # Or better: passed in estimated residual
        r_est = np.linalg.norm(x_meas - x_nom)

        next_mode = self.mode

        if r_est > self.eps_critical:
            self.high_count += 1
            self.low_count = 0
        elif r_est < self.eps_warning:
            self.low_count += 1
            self.high_count = 0
        else:
            # Hysteresis zone
            pass

        # Transitions
        if self.mode == "LQR":
            if self.high_count >= self.n:
                next_mode = "MPC_FULL"
        elif self.mode == "MPC_FULL":
            if self.low_count >= self.n:
                next_mode = "LQR"

        if next_mode != self.mode:
            # print(f"Switching mode: {self.mode} -> {next_mode} (r={r_est:.4f})")
            self.mode = next_mode

        return self.mode, float(r_est)
