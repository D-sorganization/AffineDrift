"""Checked conversions for the published rotation reference.

Reuse the Volume 0 quaternion implementation rather than duplicate its algebra.
All rotations act on column vectors; quaternions use Hamilton scalar-first order.
Python matrix checks use the book's 1e-10 tolerance; the editable browser matrix
uses 1e-5 to accommodate six-decimal input. Neither is a statistical noise model.
"""

import numpy as np
from numpy.typing import NDArray

from articles.The_Geometry_of_Motion.Volume_0.code import quaternion_demo as quaternion

type Array = NDArray[np.float64]

GIMBAL_COSINE_TOLERANCE = 1e-12


def axis_angle_to_rotation(axis: Array, angle: float) -> Array:
    """Normalize a finite nonzero axis and return its rotation in radians."""
    return quaternion.to_matrix(quaternion.from_axis_angle(axis, angle))


def rotation_to_quaternion(matrix: Array) -> Array:
    """Validate a proper rotation and select a quaternion with nonnegative scalar."""
    result = quaternion.from_matrix(matrix)
    return -result if result[0] < 0 else result


def quaternion_to_rotation(value: Array) -> Array:
    """Normalize a finite nonzero scalar-first quaternion and return its rotation."""
    return quaternion.to_matrix(value)


def rotation_to_axis_angle(matrix: Array) -> tuple[Array, float]:
    """Return a principal angle in [0, pi], with a conventional axis at identity."""
    value = rotation_to_quaternion(matrix)
    sine_half = float(np.linalg.norm(value[1:]))
    if sine_half == 0:
        return np.array([0.0, 0.0, 1.0]), 0.0
    return value[1:] / sine_half, float(2 * np.arctan2(sine_half, value[0]))


def rotation_to_euler_zyx(matrix: Array) -> tuple[float, float, float]:
    """Return intrinsic ZYX yaw, pitch, roll, setting roll to zero only at lock.

    The numerical lock threshold is |cos(pitch)| < 1e-12. Just outside it,
    extraction is ill-conditioned but retains the small orientation components.
    """
    quaternion.from_matrix(matrix)  # Validate before extracting any coordinates.
    value = np.asarray(matrix, dtype=float)
    cosine_pitch = float(np.hypot(value[0, 0], value[1, 0]))
    pitch = float(np.arctan2(-value[2, 0], cosine_pitch))
    if cosine_pitch < GIMBAL_COSINE_TOLERANCE:
        return float(np.arctan2(-value[0, 1], value[1, 1])), pitch, 0.0
    return (
        float(np.arctan2(value[1, 0], value[0, 0])),
        pitch,
        float(np.arctan2(value[2, 1], value[2, 2])),
    )


def euler_zyx_to_rotation(yaw: float, pitch: float, roll: float) -> Array:
    """Compose intrinsic ZYX, equivalently fixed-axis XYZ with reversed angles."""
    if not np.isfinite([yaw, pitch, roll]).all():
        raise ValueError("Euler angles must be finite radians")
    axes = np.eye(3)
    return (
        axis_angle_to_rotation(axes[2], yaw)
        @ axis_angle_to_rotation(axes[1], pitch)
        @ axis_angle_to_rotation(axes[0], roll)
    )
