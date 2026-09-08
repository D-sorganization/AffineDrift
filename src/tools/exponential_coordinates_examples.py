"""Checked angular-first exponential coordinates for the introductory chapter."""

import numpy as np
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

from src.affine_control.dynamics import skew
from src.tools.screw_examples import rigid_transform

type Array = NDArray[np.float64]
SERIES_ANGLE = 1e-3  # Radians; avoid subtractive cancellation near identity.
ANGULAR_SIZE = 3
TWIST_SIZE = 6


def _finite_vector(vector: Array, size: int) -> Array:
    """Require a single finite vector with the declared coordinate dimension."""
    value = np.asarray(vector, dtype=float)
    if value.shape != (size,) or not np.isfinite(value).all():
        raise ValueError(f"coordinates must have {size} finite components")
    return value


def left_jacobian(rotvec: Array) -> Array:
    """Map rotation-coordinate rates to spatial angular velocity.

    Args:
        rotvec: One finite rotation vector, in radians.

    Returns:
        The integral of exp(s * skew(rotvec)) from s=0 to s=1.
        It is finite at zero and pi, and singular at nonzero full turns.
    """
    value = _finite_vector(rotvec, ANGULAR_SIZE)
    angle = float(np.linalg.norm(value))
    cross = skew(value)
    if angle < SERIES_ANGLE:
        squared = angle * angle
        # Taylor coefficients of (1-cos(theta))/theta^2 and (theta-sin(theta))/theta^3.
        first = 1 / 2 - squared / 24 + squared**2 / 720
        second = 1 / 6 - squared / 120 + squared**2 / 5040
    else:
        first = 2 * (np.sin(angle / 2) / angle) ** 2
        second = (1 - np.sin(angle) / angle) / angle**2
    return np.asarray(np.eye(3) + first * cross + second * (cross @ cross), dtype=float)


def se3_exp(coordinates: Array) -> Array:
    """Exponentiate an integrated angular-first six-vector.

    Args:
        coordinates: (phi, rho), with phi in radians and rho in length units.
            For a constant twist (omega, v) acting for time t, pass t * twist.

    Returns:
        A homogeneous rigid transform; its translation is J_left(phi) @ rho.
    """
    value = _finite_vector(coordinates, TWIST_SIZE)
    result = np.eye(4)
    result[:3, :3] = Rotation.from_rotvec(value[:3]).as_matrix()
    result[:3, 3] = left_jacobian(value[:3]) @ value[3:]
    return result


def se3_log(transform: Array) -> Array:
    """Recover coordinates using a shortest rotation branch.

    Args:
        transform: A finite proper rigid transform, validated without projection.

    Returns:
        Angular-first (phi, rho). At pi, SciPy selects one of two axis signs;
        this function is not globally continuous and cannot recover full turns.
    """
    value = rigid_transform(transform)
    rotvec = Rotation.from_matrix(value[:3, :3]).as_rotvec()
    linear = np.linalg.solve(left_jacobian(rotvec), value[:3, 3])
    return np.asarray(np.r_[rotvec, linear], dtype=float)
