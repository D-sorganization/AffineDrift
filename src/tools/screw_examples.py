"""Checked angular-first examples for the introductory screw-axis chapter."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

from src.affine_control.dynamics import skew

type Array = NDArray[np.float64]
ROTATION_TOLERANCE = 1e-10
MINIMUM_AXIS_ANGLE = 1e-8


def rigid_transform(transform: Array) -> Array:
    """Require a finite proper rigid transform, mapping B coordinates to A."""
    value = np.asarray(transform, dtype=float)
    if value.shape != (4, 4) or not np.isfinite(value).all():
        raise ValueError("transform must be a finite 4 by 4 matrix")
    if not np.allclose(value[3], [0, 0, 0, 1], atol=ROTATION_TOLERANCE, rtol=0):
        raise ValueError("transform must have homogeneous last row")
    rotation = value[:3, :3]
    if not np.allclose(rotation.T @ rotation, np.eye(3), atol=ROTATION_TOLERANCE, rtol=0):
        raise ValueError("rotation must be orthogonal")
    if abs(np.linalg.det(rotation) - 1) > ROTATION_TOLERANCE:
        raise ValueError("rotation must be proper")
    return value


def adjoint(transform: Array) -> Array:
    """Map the same physical twist V_B to V_A with T_AB."""
    value = rigid_transform(transform)
    rotation, offset = value[:3, :3], value[:3, 3]
    return np.block([[rotation, np.zeros((3, 3))], [skew(offset) @ rotation, rotation]])


def reexpress_wrench(transform: Array, wrench_b: Array) -> Array:
    """Map moment-first F_B to F_A; this is inverse transpose, not transpose."""
    value = np.asarray(wrench_b, dtype=float)
    if value.shape != (6,) or not np.isfinite(value).all():
        raise ValueError("wrench must have six finite components")
    return np.asarray(np.linalg.solve(adjoint(transform).T, value), dtype=float)


@dataclass(frozen=True)
class ScrewDisplacement:
    """Principal finite rotation and its geometric axis, expressed in one frame."""

    angle: float
    direction: Array
    point: Array
    axial_displacement: float

    @property
    def pitch(self) -> float:
        """Return signed axial displacement per radian on the selected branch."""
        return self.axial_displacement / self.angle


def finite_screw(displacement: Array) -> ScrewDisplacement:
    """Recover the closest axis point for a resolved nonzero principal rotation.

    Use T1 @ inverse(T0) for a spatial interpose displacement. Angles at or below
    MINIMUM_AXIS_ANGLE are rejected: pure translation has no unique rotational
    axis, and axis estimation becomes ill-conditioned near zero. At pi the axis
    direction follows SciPy's choice; its opposite describes the same line.
    """
    value = rigid_transform(displacement)
    rotvec = Rotation.from_matrix(value[:3, :3]).as_rotvec()
    angle = float(np.linalg.norm(rotvec))
    if angle <= MINIMUM_AXIS_ANGLE:
        raise ValueError("rotation is too small to resolve a unique finite screw axis")
    direction = rotvec / angle
    axial = float(direction @ value[:3, 3])
    perpendicular = value[:3, 3] - axial * direction
    point = (perpendicular + np.cross(direction, perpendicular) / np.tan(angle / 2)) / 2
    return ScrewDisplacement(angle, direction, point, axial)


@dataclass(frozen=True)
class FourBarEquilibrium:
    """Forces on the coupler at B/C and ground-to-input motor torque at A."""

    force_b: Array
    force_c: Array
    torque_a: float


def four_bar_equilibrium(load_x: float, downward_force: float) -> FourBarEquilibrium:
    """Solve the chapter's massless planar linkage with an optional motor at A.

    Coordinates in metres: A=(0,0), B=(1,1), C=(3,1), D=(4,0).
    A vertical downward load acts on the rigid coupler at E=(load_x,1).
    Positive motor torque is counterclockwise. Passive equilibrium requires the
    returned torque to vanish. The geometry is fixed, not a general solver.
    """
    if not np.isfinite([load_x, downward_force]).all() or downward_force < 0:
        raise ValueError("load position and nonnegative downward force must be finite")
    span_m = 2.0
    force_c_y = downward_force * (load_x - 1.0) / span_m
    force_c = np.array([-force_c_y, force_c_y])
    force_b = np.array([force_c_y, downward_force - force_c_y])
    torque_a = float(force_b[1] - force_b[0])  # AB has unit x and y offsets in metres.
    return FourBarEquilibrium(force_b, force_c, torque_a)
