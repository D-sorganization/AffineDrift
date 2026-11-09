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


def wrench_adjoint_inverse_transpose(r_ba: Vec3) -> NDArray[np.float64]:
    """Co-adjoint matrix mapping wrench at A to wrench at B (``r_BA = r_B - r_A``)."""
    s = -skew(r_ba)
    upper = np.hstack([np.eye(3), np.zeros((3, 3))])
    lower = np.hstack([s, np.eye(3)])
    return np.vstack([upper, lower])


def transport_wrench(wrench_a: Wrench6, r_ba: Vec3) -> Wrench6:
    """Transport spatial wrench from frame A to B along displacement ``r_ba``."""
    return wrench_adjoint_inverse_transpose(r_ba) @ np.asarray(wrench_a, dtype=np.float64)


def mechanical_power(wrench: Wrench6, twist: Twist6) -> float:
    """Mechanical power with force-first wrench ``[R; M]`` and twist ``[ω; v]``.

    Uses the dual pairing ``R·v + M·ω``, not the naive dot ``wrench.T @ twist``.
    """
    w = np.asarray(wrench, dtype=np.float64).reshape(6)
    v = np.asarray(twist, dtype=np.float64).reshape(6)
    return float(w[0:3] @ v[3:6] + w[3:6] @ v[0:3])


def twist_at_b(twist_a: Twist6, r_ba: Vec3) -> Twist6:
    """Adjoint transport of twist from A to B."""
    s = skew(r_ba)
    upper = np.hstack([np.eye(3), np.zeros((3, 3))])
    lower = np.hstack([-s, np.eye(3)])
    adj = np.vstack([upper, lower])
    return adj @ np.asarray(twist_a, dtype=np.float64)


def poinsot_moment_transport(moment_a: Vec3, force: Vec3, r_ba: Vec3) -> Vec3:
    """Moment at B given moment at A, shared force, and displacement r_BA."""
    return moment_a - np.cross(r_ba, force)


def triple_product_rhs(r: Vec3, force: Vec3, omega: Vec3) -> float:
    """Scalar ``R·(ω×r)`` used in the power-invariance cross-term."""
    return float(force @ np.cross(omega, r))


def triple_product_lhs(r: Vec3, force: Vec3, omega: Vec3) -> float:
    """Equivalent form ``(r×R)·ω`` for the same cross-term."""
    return float(np.cross(r, force) @ omega)
