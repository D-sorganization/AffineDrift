"""Spatial wrench transport and power invariance helpers for Alpha War Appendix A (#5459)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

type Vec3 = NDArray[np.float64]
type Twist6 = NDArray[np.float64]
type Wrench6 = NDArray[np.float64]


def skew(v: Vec3) -> NDArray[np.float64]:
    """Return the skew-symmetric matrix for cross product with ``v``."""
    x, y, z = (float(v[0]), float(v[1]), float(v[2]))
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]], dtype=np.float64)


def dual_pairing_matrix() -> NDArray[np.float64]:
    """Block-swap ``J_sw`` for force-first wrench power ``W.T @ J_sw @ V``."""
    eye = np.eye(3)
    zeros = np.zeros((3, 3))
    return np.vstack([np.hstack([zeros, eye]), np.hstack([eye, zeros])])


def twist_adjoint(r_ba: Vec3) -> NDArray[np.float64]:
    """Twist adjoint ``Ad`` (angular-first ``V=[ω;v]``): ``V_B = Ad V_A`` for ``r_BA``."""
    s = skew(r_ba)
    eye = np.eye(3)
    zeros = np.zeros((3, 3))
    return np.vstack([np.hstack([eye, zeros]), np.hstack([-s, eye])])


def twist_adjoint_inverse_transpose(r_ba: Vec3) -> NDArray[np.float64]:
    """``Ad^{-T}`` acting on angular-first twists (not on force-first wrenches)."""
    s = skew(r_ba)
    eye = np.eye(3)
    zeros = np.zeros((3, 3))
    return np.vstack([np.hstack([eye, -s]), np.hstack([zeros, eye])])


def force_first_wrench_transport_matrix(r_ba: Vec3) -> NDArray[np.float64]:
    """Map force-first wrench at A to B: ``W_B = P Ad^{-T} P W_A`` (Poinsot moment term)."""
    p = dual_pairing_matrix()
    return p @ twist_adjoint_inverse_transpose(r_ba) @ p


def transport_wrench(wrench_a: Wrench6, r_ba: Vec3) -> Wrench6:
    """Transport spatial wrench ``[R; M]`` from frame A to B along displacement ``r_ba``."""
    transport = force_first_wrench_transport_matrix(r_ba)
    return transport @ np.asarray(wrench_a, dtype=np.float64)


def mechanical_power(wrench: Wrench6, twist: Twist6) -> float:
    """Mechanical power ``W.T @ P @ V`` with force-first ``W=[R;M]`` and ``V=[ω;v]``."""
    w = np.asarray(wrench, dtype=np.float64).reshape(6)
    v = np.asarray(twist, dtype=np.float64).reshape(6)
    pairing = dual_pairing_matrix()
    return float(w @ pairing @ v)


def point_force_power_oracle(
    force: Vec3,
    r_force_from_station: Vec3,
    omega: Vec3,
    vel_station: Vec3,
) -> float:
    """Instantaneous power from force ``F`` at material offset ``r``; no wrench transport."""
    vel_at_force = vel_station + np.cross(omega, r_force_from_station)
    return float(force @ vel_at_force)


def twist_at_b(twist_a: Twist6, r_ba: Vec3) -> Twist6:
    """Adjoint transport of twist from A to B."""
    return twist_adjoint(r_ba) @ np.asarray(twist_a, dtype=np.float64)


def poinsot_moment_transport(moment_a: Vec3, force: Vec3, r_ba: Vec3) -> Vec3:
    """Moment at B given moment at A, shared force, and displacement r_BA."""
    return moment_a - np.cross(r_ba, force)


def triple_product_rhs(r: Vec3, force: Vec3, omega: Vec3) -> float:
    """Scalar ``R·(ω×r)`` used in the power-invariance cross-term."""
    return float(force @ np.cross(omega, r))


def triple_product_lhs(r: Vec3, force: Vec3, omega: Vec3) -> float:
    """Equivalent form ``(r×R)·ω`` for the same cross-term."""
    return float(np.cross(r, force) @ omega)
