"""Property-based tests for AffineDrift physics and control computations.

Uses the *hypothesis* library to verify mathematical invariants that must
hold for **all** valid inputs, not just hand-picked examples.  Each test
targets a specific function and checks a well-defined algebraic property.

Coverage targets
----------------
* ``compute_hessian_norm``  -- non-negativity, scaling, symmetry.
* ``estimate_perturbation_size`` -- monotonicity, lower-bound, non-negativity.
* ``predict_residual_bound`` -- non-negativity, monotonicity in each factor.
* ``universal_joint_transmission_ratio`` -- power conservation, periodicity.
* ``distribute_torque_by_grip_angle`` -- Pythagorean identity for torque
  decomposition.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from src.affine_control.ddp import estimate_perturbation_size
from src.affine_control.residuals import (
    compute_hessian_norm,
    predict_residual_bound,
)
from src.tools.wrist_universal_joint.torque_calculator import (
    distribute_torque_by_grip_angle,
    universal_joint_transmission_ratio,
)

# ── Strategies ──────────────────────────────────────────────────────────────

# Finite floats that are safe for multiplication (no overflow / underflow)
_safe_float = st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
_positive_float = st.floats(min_value=1e-6, max_value=1e4, allow_nan=False, allow_infinity=False)
_non_negative_float = st.floats(min_value=0.0, max_value=1e4, allow_nan=False, allow_infinity=False)
_angle_rad = st.floats(min_value=-np.pi, max_value=np.pi, allow_nan=False, allow_infinity=False)
_small_dim = st.integers(min_value=1, max_value=4)

# 1-D numpy state vectors
_state_vector = arrays(
    dtype=np.float64,
    shape=st.integers(min_value=1, max_value=6),
    elements=st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
)


# ── compute_hessian_norm properties ──────────────────────────────────────────


def _make_quadratic(
    n: int,
) -> tuple[
    Any,
    np.ndarray[Any, Any],
    np.ndarray[Any, Any],
]:
    """Return (f, x, u) for f(x, u) = x^T x  (scalar output per component)."""
    x = np.ones(n, dtype=np.float64)
    u = np.zeros(n, dtype=np.float64)

    def f(x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        return x * x  # element-wise square

    return f, x, u


@given(n=st.integers(min_value=1, max_value=4))
@settings(max_examples=20, deadline=5000)
def test_hessian_norm_is_non_negative(n: int) -> None:
    """The Hessian spectral norm must always be >= 0."""
    f, x, u = _make_quadratic(n)
    M = compute_hessian_norm(f, x, u)
    assert M >= 0.0, f"Hessian norm was negative: {M}"


@given(n=st.integers(min_value=1, max_value=3))
@settings(max_examples=10, deadline=5000)
def test_hessian_norm_of_quadratic_is_approximately_2(n: int) -> None:
    """For f(x) = x_i^2 (element-wise), each component Hessian is 2*I.

    The spectral norm of 2*I is 2, so M should be close to 2.
    """
    f, x, u = _make_quadratic(n)
    M = compute_hessian_norm(f, x, u)
    assert abs(M - 2.0) < 0.5, f"Expected M ~ 2.0, got {M}"


@given(n=st.integers(min_value=1, max_value=3))
@settings(max_examples=10, deadline=5000)
def test_hessian_norm_of_linear_is_near_zero(n: int) -> None:
    """For a linear function f(x, u) = x, the Hessian is zero everywhere."""

    def f_linear(x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        return x.copy()

    x = np.ones(n, dtype=np.float64)
    u = np.zeros(n, dtype=np.float64)
    M = compute_hessian_norm(f_linear, x, u)
    assert M < 1e-2, f"Hessian of linear function should be ~0, got {M}"


# ── estimate_perturbation_size properties ────────────────────────────────────


@given(x=_state_vector)
@settings(max_examples=50)
def test_perturbation_is_non_negative(x: np.ndarray[Any, Any]) -> None:
    """Perturbation estimate must always be >= 0."""
    u = np.zeros_like(x)
    p = estimate_perturbation_size(x, u)
    assert p >= 0.0


@given(x=_state_vector)
@settings(max_examples=50)
def test_perturbation_at_least_base_noise(x: np.ndarray[Any, Any]) -> None:
    """Perturbation must be >= base_noise (the noise floor)."""
    u = np.zeros_like(x)
    base = 0.01
    p = estimate_perturbation_size(x, u, base_noise=base, state_scale=0.0)
    assert p >= base - 1e-12


@given(
    scale_a=_non_negative_float,
    scale_b=_non_negative_float,
)
@settings(max_examples=50)
def test_perturbation_monotone_in_state_scale(scale_a: float, scale_b: float) -> None:
    """Larger state_scale => larger (or equal) perturbation."""
    x = np.array([1.0, 2.0, 3.0])
    u = np.zeros(3)
    lo, hi = sorted([scale_a, scale_b])
    p_lo = estimate_perturbation_size(x, u, state_scale=lo)
    p_hi = estimate_perturbation_size(x, u, state_scale=hi)
    assert p_hi >= p_lo - 1e-12


# ── predict_residual_bound properties ─────────────────────────────────────


@given(
    n=st.integers(min_value=1, max_value=20),
    M_val=_positive_float,
    dx_val=_non_negative_float,
    dt_val=_positive_float,
)
@settings(max_examples=50)
def test_residual_bound_is_non_negative(n: int, M_val: float, dx_val: float, dt_val: float) -> None:
    """Residual bound (sum of non-negative terms) must be >= 0."""
    M_traj = np.full(n, M_val)
    dx_traj = np.full(n, dx_val)
    dt_traj = np.full(n, dt_val)
    r = predict_residual_bound(M_traj, dx_traj, dt_traj)
    assert r >= 0.0


@given(
    n=st.integers(min_value=1, max_value=10),
    M_val=_positive_float,
    dx_val=_positive_float,
)
@settings(max_examples=30)
def test_residual_bound_monotone_in_timestep(n: int, M_val: float, dx_val: float) -> None:
    """Larger timestep => larger (or equal) residual bound."""
    M_traj = np.full(n, min(M_val, 100.0))
    dx_traj = np.full(n, min(dx_val, 100.0))

    dt_small = np.full(n, 0.001)
    dt_large = np.full(n, 0.01)

    r_small = predict_residual_bound(M_traj, dx_traj, dt_small)
    r_large = predict_residual_bound(M_traj, dx_traj, dt_large)
    assert r_large >= r_small - 1e-12


@given(n=st.integers(min_value=1, max_value=20))
@settings(max_examples=30)
def test_residual_bound_zero_perturbation_gives_zero(n: int) -> None:
    """If perturbation is zero everywhere, the residual bound is zero."""
    M_traj = np.ones(n) * 5.0
    dx_traj = np.zeros(n)
    dt_traj = np.ones(n) * 0.01
    r = predict_residual_bound(M_traj, dx_traj, dt_traj)
    assert abs(r) < 1e-12


# ── universal_joint_transmission_ratio properties ────────────────────────


@given(phi=_angle_rad)
@settings(max_examples=50)
def test_joint_power_conservation(phi: float) -> None:
    """omega_ratio * tau_ratio == 1 (power conservation P = tau * omega)."""
    delta = np.radians(30.0)  # fixed bend angle
    omega_ratio, tau_ratio = universal_joint_transmission_ratio(phi, delta)
    product = omega_ratio * tau_ratio
    assert abs(product - 1.0) < 1e-10, f"Power not conserved: {product}"


@given(phi=_angle_rad)
@settings(max_examples=50)
def test_joint_ratio_at_zero_bend_is_unity(phi: float) -> None:
    """At zero bend angle, both ratios are 1 (straight shaft)."""
    omega_ratio, tau_ratio = universal_joint_transmission_ratio(phi, 0.0)
    assert abs(omega_ratio - 1.0) < 1e-10
    assert abs(tau_ratio - 1.0) < 1e-10


@given(phi=_angle_rad)
@settings(max_examples=50)
def test_joint_ratio_periodic_in_phi(phi: float) -> None:
    """Transmission ratio has period pi in phi (sin^2 phi symmetry)."""
    delta = np.radians(20.0)
    omega1, tau1 = universal_joint_transmission_ratio(phi, delta)
    omega2, tau2 = universal_joint_transmission_ratio(phi + np.pi, delta)
    assert abs(omega1 - omega2) < 1e-10
    assert abs(tau1 - tau2) < 1e-10


# ── distribute_torque_by_grip_angle properties ──────────────────────────


@given(
    torque=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
    theta=_angle_rad,
)
@settings(max_examples=100)
def test_torque_decomposition_pythagorean(torque: float, theta: float) -> None:
    """tau_alpha^2 + tau_gamma^2 == torque^2 (Pythagorean decomposition).

    Since tau_alpha = T*sin(theta) and tau_gamma = T*cos(theta), we have
    tau_alpha^2 + tau_gamma^2 = T^2 * (sin^2 + cos^2) = T^2.
    """
    tau_alpha, tau_gamma = distribute_torque_by_grip_angle(torque, theta)
    lhs = float(tau_alpha) ** 2 + float(tau_gamma) ** 2
    rhs = torque**2
    assert abs(lhs - rhs) < 1e-6 * max(abs(rhs), 1.0), (
        f"Pythagorean identity violated: {lhs} != {rhs}"
    )


@given(
    torque=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=50)
def test_torque_at_zero_grip_angle_goes_to_gamma(torque: float) -> None:
    """At theta=0 (neutral grip), all torque goes to gamma axis."""
    tau_alpha, tau_gamma = distribute_torque_by_grip_angle(torque, 0.0)
    assert abs(float(tau_alpha)) < 1e-10
    assert abs(float(tau_gamma) - torque) < 1e-10


@given(
    torque=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=50)
def test_torque_at_90_deg_grip_goes_to_alpha(torque: float) -> None:
    """At theta=pi/2 (full rotation), all torque goes to alpha axis."""
    tau_alpha, tau_gamma = distribute_torque_by_grip_angle(torque, np.pi / 2)
    assert abs(float(tau_alpha) - torque) < 1e-10
    assert abs(float(tau_gamma)) < 1e-10
