"""Quaternion operations and SLERP, as developed in Volume 0 Chapter 4.

Self-contained by design: this file is typeset into the chapter as a worked
example, so it depends only on NumPy and repeats nothing the chapter has not
already derived. Equation numbers in the comments refer to Chapter 4.

Correctness is pinned by tests/test_affine_control/test_quaternion_demo.py --
the properties asserted there (unit norm, orthogonality of the rotation matrix,
agreement between quaternion rotation and matrix rotation, SLERP endpoints and
constant angular velocity) are what make this an example rather than a claim.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

type Array = NDArray[np.float64]

# Below this angle the small-angle expansion of SLERP is better conditioned
# than the closed form: sin(Omega) appears in a denominator, so the closed form
# loses precision as the two quaternions approach each other.
SLERP_LINEAR_THRESHOLD = 1.0 - 1.0e-9


def hamilton_product(p: Array, q: Array) -> Array:
    """Quaternion product, equation (eq:hamilton_product).

    Both arguments are ordered [w, x, y, z]. The product is not commutative;
    ``hamilton_product(p, q)`` applies ``q`` first, then ``p``.
    """
    pw, px, py, pz = p
    qw, qx, qy, qz = q
    return np.array(
        [
            pw * qw - px * qx - py * qy - pz * qz,
            pw * qx + px * qw + py * qz - pz * qy,
            pw * qy - px * qz + py * qw + pz * qx,
            pw * qz + px * qy - py * qx + pz * qw,
        ]
    )


def normalize(q: Array) -> Array:
    """Project onto the unit sphere, which is where rotations live."""
    norm = float(np.linalg.norm(q))
    if norm == 0.0:
        msg = "the zero quaternion represents no rotation and cannot be normalised"
        raise ValueError(msg)
    return q / norm


def conjugate(q: Array) -> Array:
    """For a unit quaternion this is also the inverse."""
    w, x, y, z = q
    return np.array([w, -x, -y, -z])


def from_axis_angle(axis: Array, angle: float) -> Array:
    """Unit quaternion for a rotation of ``angle`` about ``axis``.

    Note the half-angle: a quaternion covers SO(3) twice, so q and -q are the
    same rotation.
    """
    unit = normalize(np.asarray(axis, dtype=float))
    return np.concatenate([[np.cos(angle / 2.0)], np.sin(angle / 2.0) * unit])


def to_matrix(q: Array) -> Array:
    """Rotation matrix of a unit quaternion, equation (eq:quat_to_matrix)."""
    w, x, y, z = normalize(q)
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
            [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
            [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
        ]
    )


def rotate(q: Array, v: Array) -> Array:
    """Rotate a vector by the sandwich product q v q*, without forming a matrix."""
    pure = np.concatenate([[0.0], np.asarray(v, dtype=float)])
    return hamilton_product(hamilton_product(q, pure), conjugate(q))[1:]


def slerp(q0: Array, q1: Array, t: float) -> Array:
    """Spherical linear interpolation, equation (eq:slerp).

    Two details matter and neither is cosmetic:

    * If the dot product is negative the interpolation would take the long way
      round the sphere -- 360 degrees minus the short arc. Negating one input
      selects the short arc, which is legitimate because q and -q denote the
      same rotation.
    * As the quaternions approach each other sin(Omega) approaches zero and the
      closed form loses precision, so below a threshold we fall back to
      normalised linear interpolation, which agrees to first order.
    """
    a = normalize(np.asarray(q0, dtype=float))
    b = normalize(np.asarray(q1, dtype=float))

    dot = float(np.dot(a, b))
    if dot < 0.0:
        b, dot = -b, -dot

    if dot > SLERP_LINEAR_THRESHOLD:
        return normalize(a + t * (b - a))

    omega = float(np.arccos(np.clip(dot, -1.0, 1.0)))
    sin_omega = np.sin(omega)
    return (np.sin((1.0 - t) * omega) / sin_omega) * a + (np.sin(t * omega) / sin_omega) * b


def interpolate_point_cloud(points: Array, q0: Array, q1: Array, frames: int) -> list[Array]:
    """Carry a point cloud through the interpolated frames.

    Returns one rotated copy of ``points`` per frame, which is what the
    chapter's visualisation plots.
    """
    return [
        (to_matrix(slerp(q0, q1, t)) @ np.asarray(points, dtype=float).T).T
        for t in np.linspace(0.0, 1.0, frames)
    ]
