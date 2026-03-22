"""Residual bound computation for affine drift control systems.

Provides Hessian bound estimation and residual monitoring utilities used to
certify convergence of the DDP optimiser and detect numerical instability
during trajectory tracking.
"""

import logging
from collections.abc import Callable
from typing import Any

import numpy as np

from src.core.constants import (
    DEFAULT_EPS_CRITICAL,
    DEFAULT_EPS_WARNING,
    DEFAULT_N_HYSTERESIS,
    FINITE_DIFF_STEP_HESSIAN_BOUND,
    FINITE_DIFF_STEP_HESSIAN_NORM,
)
from src.core.contracts import (
    ContractChecker,
    check_finite_array,
    check_positive,
    ensure,
    invariant_checked,
    require,
)

logger = logging.getLogger(__name__)


def compute_hessian_bound(
    f: Callable[[np.ndarray[Any, Any], np.ndarray[Any, Any]], np.ndarray[Any, Any]],
    x: np.ndarray[Any, Any],
    u: np.ndarray[Any, Any],
    epsilon: float = FINITE_DIFF_STEP_HESSIAN_BOUND,
) -> float:
    """
    Approximates the Hessian bound M for dynamics f(x, u).
    This is a simplified numerical approximation.
    In production, exact Hessians (via JAX/CasADi) should be used.

    Args:
        f: Dynamics function dx = f(x, u)
        x: State vector
        u: Control vector
        epsilon: Finite difference step

    Returns:
        M: Spectral norm of the Hessian
    """
    check_finite_array(x, "x")
    check_finite_array(u, "u")
    check_positive(epsilon, "epsilon")
    return compute_hessian_norm(f, x, u, epsilon)


def _finite_diff_jacobian(
    f: Callable[[np.ndarray[Any, Any], np.ndarray[Any, Any]], np.ndarray[Any, Any]],
    x0: np.ndarray[Any, Any],
    u: np.ndarray[Any, Any],
    epsilon: float,
) -> np.ndarray[Any, Any]:
    """Compute the Jacobian df/dx using central finite differences.

    Args:
        f: Dynamics function f(x, u).
        x0: State vector at which to evaluate.
        u: Control vector (held constant).
        epsilon: Finite difference step size.

    Returns:
        Jacobian matrix of shape (output_dim, state_dim).
    """
    n = len(x0)
    dx = len(f(x0, u))
    J = np.zeros((dx, n))
    for i in range(n):
        x_plus = x0.copy()
        x_plus[i] += epsilon
        x_minus = x0.copy()
        x_minus[i] -= epsilon
        J[:, i] = (f(x_plus, u) - f(x_minus, u)) / (2 * epsilon)
    return J


def _max_spectral_norm(H: np.ndarray[Any, Any]) -> float:
    """Compute the maximum spectral norm across component Hessian slices.

    Args:
        H: Hessian tensor of shape (output_dim, state_dim, state_dim).

    Returns:
        Maximum spectral norm across all output components.
    """
    M = 0.0
    for k in range(H.shape[0]):
        norm_k = np.linalg.norm(H[k, :, :], ord=2)
        M = max(M, float(norm_k))
    return M


def compute_hessian_norm(
    f: Callable[[np.ndarray[Any, Any], np.ndarray[Any, Any]], np.ndarray[Any, Any]],
    x: np.ndarray[Any, Any],
    u: np.ndarray[Any, Any],
    epsilon: float = FINITE_DIFF_STEP_HESSIAN_NORM,
) -> float:
    """Compute numerical approximation of the Hessian norm ||H_f||.

    H_f is the tensor [d^2f / dx_i dx_j].
    The norm used is the maximum spectral norm of the component Hessians.

    Args:
        f: Dynamics function dx = f(x, u).
        x: State vector.
        u: Control vector.
        epsilon: Finite difference step size.

    Returns:
        Maximum spectral norm of the component Hessians.
    """
    n = len(x)
    dx = len(f(x, u))

    # Hessian tensor H[k, i, j] = dJ_ki / dx_j via central differences on the Jacobian
    H = np.zeros((dx, n, n))
    base_x = x.copy()

    for j in range(n):
        x_plus = base_x.copy()
        x_plus[j] += epsilon
        x_minus = base_x.copy()
        x_minus[j] -= epsilon

        J_plus = _finite_diff_jacobian(f, x_plus, u, epsilon)
        J_minus = _finite_diff_jacobian(f, x_minus, u, epsilon)
        H[:, :, j] = (J_plus - J_minus) / (2 * epsilon)

    return _max_spectral_norm(H)


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
    check_finite_array(M_traj, "M_traj")
    check_finite_array(delta_x_traj, "delta_x_traj")
    check_finite_array(dt_traj, "dt_traj")
    require(len(dt_traj) > 0, "dt_traj must not be empty")
    require(
        len(M_traj) == len(delta_x_traj) == len(dt_traj),
        "all trajectory arrays must have equal length",
        (len(M_traj), len(delta_x_traj), len(dt_traj)),
    )

    r_accum = 0.0

    for i in range(len(dt_traj)):
        rate = float((M_traj[i] / 2.0) * (delta_x_traj[i] ** 2))
        r_accum += rate * float(dt_traj[i])

    ensure(r_accum >= 0, "residual bound must be non-negative", r_accum)
    return r_accum


class ResidualMonitor(ContractChecker):
    """
    Monitors residuals and triggers mode switching.
    """

    def __init__(
        self,
        eps_warning: float = DEFAULT_EPS_WARNING,
        eps_critical: float = DEFAULT_EPS_CRITICAL,
        n_hysteresis: int = DEFAULT_N_HYSTERESIS,
    ) -> None:
        """Initialize residual monitor."""
        check_positive(eps_warning, "eps_warning")
        check_positive(eps_critical, "eps_critical")
        require(
            eps_critical > eps_warning,
            "eps_critical must exceed eps_warning",
            eps_critical,
        )
        require(n_hysteresis >= 1, "n_hysteresis must be >= 1", n_hysteresis)
        self.eps_warning = eps_warning
        self.eps_critical = eps_critical
        self.n = n_hysteresis

        self.high_count = 0
        self.low_count = 0
        self.mode = "LQR"  # LQR, MPC_WARN, MPC_FULL

    def _get_invariants(self) -> list[tuple[Callable[[], bool], str]]:
        """Return class invariants for the monitor."""
        return [
            (lambda: self.eps_warning > 0, "eps_warning must be positive"),
            (
                lambda: self.eps_critical > self.eps_warning,
                "eps_critical must exceed eps_warning",
            ),
            (lambda: self.high_count >= 0, "high_count must be non-negative"),
            (lambda: self.low_count >= 0, "low_count must be non-negative"),
            (
                lambda: self.mode in ("LQR", "MPC_WARN", "MPC_FULL"),
                "mode must be a valid state",
            ),
        ]

    @invariant_checked
    def update(
        self, x_meas: np.ndarray[Any, Any], x_nom: np.ndarray[Any, Any]
    ) -> tuple[str, float]:
        """
        Update with new measurement.
        Approximate residual r ~ x_meas - x_nom (assuming drift is dominant error)
        In reality: r = x_meas - (x_nom + Phi * delta_x0)
        """
        check_finite_array(x_meas, "x_meas")
        check_finite_array(x_nom, "x_nom")
        require(x_meas.shape == x_nom.shape, "x_meas and x_nom must have same shape")

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
            pass  # No change in counters when in hysteresis band

        # Transitions
        if self.mode == "LQR":
            if self.high_count >= self.n:
                next_mode = "MPC_FULL"
        elif self.mode == "MPC_FULL" and self.low_count >= self.n:
            next_mode = "LQR"

        if next_mode != self.mode:
            logger.debug("Switching mode: %s -> %s (r=%.4f)", self.mode, next_mode, r_est)
            self.mode = next_mode

        return self.mode, float(r_est)
