"""Universal joint physics - extracted from Universal_Joint_Model_Enhanced.py.

Fixes #2359: decomposes the 1710-LOC monolith into targeted physics modules.
"""
from __future__ import annotations
import math
import numpy as np
from typing import Any


def compute_joint_angles(theta1: float, theta2: float, theta_drive: float) -> tuple[float, float]:
    """Compute universal joint output angles from input drive angle.

    Uses the standard Hooke's coupling kinematic formula.

    Args:
        theta1: Angle of input shaft axis 1 (radians).
        theta2: Angle of input shaft axis 2 (radians).
        theta_drive: Drive/input angle (radians).

    Returns:
        Tuple of (output_angle, velocity_ratio).
    """
    # Hooke's coupling: tan(theta_out) = tan(theta_in) * cos(beta)
    beta = math.acos(math.cos(theta1) * math.cos(theta2))
    tan_out = math.tan(theta_drive) * math.cos(beta)
    theta_out = math.atan(tan_out)
    # Velocity ratio (derivative)
    velocity_ratio = math.cos(beta) / (1 - math.sin(beta) ** 2 * math.sin(theta_drive) ** 2)
    return theta_out, velocity_ratio


def compute_joint_torque(input_torque: float, velocity_ratio: float) -> float:
    """Compute output torque from input torque and velocity ratio.

    Uses power conservation: T_out * omega_out = T_in * omega_in.
    """
    if abs(velocity_ratio) < 1e-12:
        raise ValueError("Velocity ratio near zero - singular configuration")
    return input_torque / velocity_ratio


def wrist_euler_angles_to_rotation(alpha: float, beta: float, gamma: float) -> np.ndarray:
    """Convert Euler angles (ZYX convention) to 3x3 rotation matrix.

    Args:
        alpha: Yaw angle (radians) - rotation about Z.
        beta:  Pitch angle (radians) - rotation about Y.
        gamma: Roll angle (radians) - rotation about X.

    Returns:
        3x3 rotation matrix R.
    """
    ca, sa = math.cos(alpha), math.sin(alpha)
    cb, sb = math.cos(beta), math.sin(beta)
    cg, sg = math.cos(gamma), math.sin(gamma)
    return np.array([
        [ca * cb,  ca * sb * sg - sa * cg,  ca * sb * cg + sa * sg],
        [sa * cb,  sa * sb * sg + ca * cg,  sa * sb * cg - ca * sg],
        [-sb,      cb * sg,                  cb * cg],
    ])
