"""Residual bound computation for affine drift control systems.

Provides pointwise Hessian estimates, conditional flow-remainder bounds,
and tracking-discrepancy monitoring. These utilities alone do not certify
optimizer convergence, controller stability, or a physical source of error.
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
    Estimate the largest component state-Hessian norm at one point.

    Despite the historical name, this is not a certified regional bound.
    Automatic differentiation also gives point derivatives, not a supremum
    over a region. Control and mixed derivatives are not included.

    Args:
        f: Dynamics function dx = f(x, u)
        x: State vector
        u: Control vector
        epsilon: Finite difference step

    Returns:
        Maximum estimated component spectral norm, with control held fixed.
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


def _assemble_hessian_tensor(
    f: Callable[[np.ndarray[Any, Any], np.ndarray[Any, Any]], np.ndarray[Any, Any]],
    x: np.ndarray[Any, Any],
    u: np.ndarray[Any, Any],
    n: int | None = None,
    dx: int | None = None,
    epsilon: float = FINITE_DIFF_STEP_HESSIAN_NORM,
) -> np.ndarray[Any, Any]:
    """Build the Hessian tensor H[k, i, j] = dJ_ki / dx_j via central differences.

    Each Hessian slice is assembled from two Jacobian evaluations, giving
    O(n^2) dynamics calls in total.
    """
    n = len(x) if n is None else n
    dx = len(f(x, u)) if dx is None else dx
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

    return H


def _max_spectral_norm(H: np.ndarray[Any, Any]) -> float:
    """Compute the maximum spectral norm across component Hessian slices.

    Args:
        H: Hessian tensor of shape (output_dim, state_dim, state_dim).

    Returns:
        Maximum spectral norm across all output components.
    """
    # Vectorized: compute spectral norm for each component Hessian slice
    norms = np.array([np.linalg.norm(H[k, :, :], ord=2) for k in range(H.shape[0])])
    return float(np.max(norms)) if norms.size > 0 else 0.0


def compute_hessian_norm(
    f: Callable[[np.ndarray[Any, Any], np.ndarray[Any, Any]], np.ndarray[Any, Any]],
    x: np.ndarray[Any, Any],
    u: np.ndarray[Any, Any],
    epsilon: float = FINITE_DIFF_STEP_HESSIAN_NORM,
) -> float:
    """Estimate the maximum component state-Hessian spectral norm.

    The nested finite differences use 4*n**2 + 2*n + 1 dynamics calls.
    This counts calls, not their internal cost or the subsequent matrix SVDs.
    Automatic differentiation avoids finite-difference truncation, but its
    cost depends on the model, dimensions, and differentiation strategy.

    Args:
        f: Dynamics function dx = f(x, u).
        x: State vector.
        u: Control vector, held constant.
        epsilon: Finite difference step size.

    Returns:
        Maximum estimated spectral norm of the component state Hessians.

    Notes:
        This point estimate is not a regional upper bound. Even exact component
        norms bound the vector Hessian with Euclidean output norm only after
        combining components (e.g. their root sum of squares). Coordinates
        must have declared scales. Control and mixed derivatives are omitted.
    """
    n = len(x)
    dx = len(f(x, u))
    H = _assemble_hessian_tensor(f, x, u, n, dx, epsilon)
    return _max_spectral_norm(H)


def _validate_bound_intervals(
    M_traj: np.ndarray[Any, Any],
    delta_x_traj: np.ndarray[Any, Any],
    dt_traj: np.ndarray[Any, Any],
    growth_rates: np.ndarray[Any, Any],
) -> None:
    """Require finite interval data with an unambiguous norm convention."""
    for name, values in (
        ("M_traj", M_traj),
        ("delta_x_traj", delta_x_traj),
        ("dt_traj", dt_traj),
        ("growth_rates", growth_rates),
    ):
        require(values.ndim == 1, f"{name} must be one-dimensional")
        check_finite_array(values, name)
        if name != "growth_rates":
            require(bool(np.all(values >= 0)), f"{name} must be non-negative")
    require(len(dt_traj) > 0, "dt_traj must not be empty")
    require(
        len(M_traj) == len(delta_x_traj) == len(dt_traj) == len(growth_rates),
        "all trajectory arrays must have equal length",
    )


def _propagate_remainder(
    forcing: np.ndarray[Any, Any],
    durations: np.ndarray[Any, Any],
    growth_rates: np.ndarray[Any, Any],
) -> float:
    """Integrate the scalar comparison ODE without resetting earlier error."""
    residual = 0.0
    # The recurrence preserves causal accumulation without subtracting large
    # cumulative exponents. Each interval depends on the preceding bound.
    for source, duration, rate in zip(forcing, durations, growth_rates, strict=True):
        if duration == 0 or (source == 0 and residual == 0):
            continue
        exponent = rate * duration
        response = duration if rate == 0 else np.expm1(exponent) / rate
        residual = np.exp(exponent) * residual + source * response
    return float(residual)


def predict_residual_bound(
    M_traj: np.ndarray[Any, Any],
    delta_x_traj: np.ndarray[Any, Any],
    dt_traj: np.ndarray[Any, Any],
    growth_rates: np.ndarray[Any, Any] | None = None,
) -> float:
    """Propagate a conditional continuous-time Taylor flow-remainder bound.

    Solve R'=a_i*R + M_i*rho_i**2/2 on each interval, starting at R=0.
    Preconditions: the actual joined state/control deviation stays below rho_i;
    the regional vector-Hessian bilinear norm is bounded by M_i; and the
    linear propagator obeys ||Phi(t,s)|| <= exp(a_i*(t-s)) within that interval.
    All norms must use the same declared scaled coordinates. This computes
    the comparison formula in floating point, not an interval-arithmetic proof.

    Args:
        M_traj: Non-negative interval Hessian upper bounds, not point samples.
        delta_x_traj: Non-negative bounds on actual deviations, not linear predictions.
        dt_traj: Non-negative interval durations; at least one interval is required.
        growth_rates: Finite propagator growth bounds in inverse time. None means
            zero: the legacy sum then requires a nonexpansive propagator.

    Returns:
        Conditional final remainder bound, excluding model and integration errors.

    Raises:
        ValueError: The comparison calculation is not representable as a finite float.
    """
    rates = np.zeros_like(dt_traj, dtype=float) if growth_rates is None else growth_rates
    _validate_bound_intervals(M_traj, delta_x_traj, dt_traj, rates)
    try:
        with np.errstate(over="raise", invalid="raise"):
            r_accum = _propagate_remainder(M_traj / 2.0 * delta_x_traj**2, dt_traj, rates)
    except FloatingPointError as error:
        raise ValueError("residual bound is not representable as a finite float") from error
    if not np.isfinite(r_accum):
        raise ValueError("residual bound is not representable as a finite float")
    ensure(r_accum >= 0, "residual bound must be non-negative", r_accum)
    return r_accum


class ResidualMonitor(ContractChecker):
    """
    Label tracking discrepancies using a hysteretic state machine.

    Labels request a controller mode; this class implements no controller,
    feasibility check, observer, or stability guarantee. Input coordinates
    must be scaled consistently before taking a Euclidean norm.
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
        self.warn_count = 0
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
            (lambda: self.warn_count >= 0, "warn_count must be non-negative"),
        ]

    def _estimate_residual(
        self, x_meas: np.ndarray[Any, Any], x_nom: np.ndarray[Any, Any]
    ) -> float:
        """Measure tracking discrepancy, which does not isolate Taylor remainder."""
        check_finite_array(x_meas, "x_meas")
        check_finite_array(x_nom, "x_nom")
        require(x_meas.shape == x_nom.shape, "x_meas and x_nom must have same shape")
        return float(np.linalg.norm(x_meas - x_nom))

    def _update_hysteresis_counters(self, r_est: float) -> None:
        """Update high, warning, and low residual hysteresis counters."""
        if r_est > self.eps_critical:
            self.high_count += 1
            self.warn_count += 1
            self.low_count = 0
        elif r_est >= self.eps_warning:
            self.warn_count += 1
            self.high_count = 0
            self.low_count = 0
        else:
            self.low_count += 1
            self.high_count = 0
            self.warn_count = 0

    def _next_mode(self) -> str:
        """Return the state-machine mode implied by the current counters."""
        if self.mode == "LQR" and (self.high_count >= self.n or self.warn_count >= self.n):
            return "MPC_WARN"
        if self.mode == "MPC_WARN":
            if self.high_count >= self.n:
                return "MPC_FULL"
            if self.low_count >= self.n:
                return "LQR"
        if self.mode == "MPC_FULL" and self.low_count >= self.n:
            return "MPC_WARN"
        return self.mode

    def _compute_next_mode(self) -> str:
        """Backward-compatible alias for the residual mode state machine."""
        return self._next_mode()

    def _reset_hysteresis_counters(self) -> None:
        """Reset all hysteresis counters after a mode transition."""
        self.high_count = 0
        self.warn_count = 0
        self.low_count = 0

    def _apply_mode_transition(self, next_mode: str, r_est: float) -> None:
        """Apply a pending mode transition and reset hysteresis state."""
        if next_mode == self.mode:
            return
        logger.debug("Switching mode: %s -> %s (r=%.4f)", self.mode, next_mode, r_est)
        self._reset_hysteresis_counters()
        self.mode = next_mode

    @invariant_checked
    def update(
        self, x_meas: np.ndarray[Any, Any], x_nom: np.ndarray[Any, Any]
    ) -> tuple[str, float]:
        """
        Update the mode label from a measured/reference discrepancy.

        The reference must be constructed independently of this measurement.
        A nominal reference measures tracking error; a prior model prediction
        measures prediction discrepancy. Neither uniquely identifies curvature.
        """
        r_est = self._estimate_residual(x_meas, x_nom)
        self._update_hysteresis_counters(r_est)
        self._apply_mode_transition(self._next_mode(), r_est)
        return self.mode, r_est
