"""Rigid multi-segment SE(3) forward kinematics for a golfer-club chain.

Slice 1 of issue 4973 (Phase 2 swing viewer, ADR 0002): a genuine spatial
kinematics provider with *declared* parameters. It is rigid: there is no shaft
flexibility, no dynamics and no viewer wiring.

Conventions follow the planar teaching model in ``golf_model``: segment ``i``
extends along its own local ``+x`` axis, joint ``i`` rotates by ``q[i]``
(radians, right-handed) about ``joint_axes[i]`` expressed in the parent frame,
and with every axis equal to ``+z`` the chain reduces exactly to the planar
model's ``link_angles`` / ``(cos, sin)`` geometry in the x-y plane.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from src.affine_control.golf_model import SEGMENTS

__all__ = ["JOHNSON_2015_ARM", "PLANAR_REDUCED", "GolfModel3D"]

logger = logging.getLogger(__name__)

type Array = NDArray[np.float64]
type Vec3 = tuple[float, float, float]

_AXIS_TOL = 1e-9
_ROT_TOL = 1e-9


def _rotation(axis: Array, angle: float) -> Array:
    """Rodrigues rotation matrix about a unit ``axis``."""
    x, y, z = axis
    skew = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    return np.asarray(
        np.eye(3) + math.sin(angle) * skew + (1.0 - math.cos(angle)) * (skew @ skew),
        dtype=np.float64,
    )


@dataclass(frozen=True)
class GolfModel3D:
    """Declared parameters of a rigid serial golfer-club chain.

    Units: lengths in metres, angles in radians. ``provenance`` states where
    every value comes from; it must be non-empty. A zero-length segment is
    allowed: it makes its joint a pure rotation at the previous joint's
    location, which is how several rotations share one anatomical joint.
    """

    segment_lengths_m: tuple[float, ...]
    joint_axes: tuple[Vec3, ...]
    joint_limits_rad: tuple[tuple[float, float], ...]
    provenance: str

    def __post_init__(self) -> None:
        """Validate the declared parameters (design by contract)."""
        count = len(self.segment_lengths_m)
        if count == 0:
            raise ValueError("at least one segment is required")
        if len(self.joint_axes) != count or len(self.joint_limits_rad) != count:
            raise ValueError("segment_lengths_m, joint_axes and joint_limits_rad must match")
        if not all(math.isfinite(v) and v >= 0.0 for v in self.segment_lengths_m):
            raise ValueError("segment lengths must be finite and non-negative")
        if sum(self.segment_lengths_m) <= 0.0:
            raise ValueError("at least one segment must have positive length")
        self._validate_axes_and_limits()
        if not self.provenance.strip():
            raise ValueError("provenance must be a non-empty string")

    def _validate_axes_and_limits(self) -> None:
        """Axes must be finite unit 3-vectors; limits finite with lower < upper."""
        for axis in self.joint_axes:
            if len(axis) != 3 or not all(math.isfinite(v) for v in axis):
                raise ValueError("joint axes must be finite 3-vectors")
            if abs(math.sqrt(sum(v * v for v in axis)) - 1.0) > _AXIS_TOL:
                raise ValueError("joint axes must be unit vectors")
        for lower, upper in self.joint_limits_rad:
            if not (math.isfinite(lower) and math.isfinite(upper) and lower < upper):
                raise ValueError("joint limits must be finite with lower < upper")

    def forward_kinematics(self, q: Array) -> list[Array]:
        """Return the ``4x4`` SE(3) pose of every frame, base first.

        ``result[0]`` is the identity base frame; ``result[i + 1]`` is the
        distal end of segment ``i`` (so ``result[-1]`` is the club tip).
        """
        angles = np.asarray(q, dtype=np.float64)
        if angles.shape != (len(self.segment_lengths_m),):
            raise ValueError(f"q must have shape ({len(self.segment_lengths_m)},)")
        if not np.all(np.isfinite(angles)):
            raise ValueError("q must be finite")
        for value, (lower, upper) in zip(angles, self.joint_limits_rad, strict=True):
            if not lower <= value <= upper:
                raise ValueError(f"joint value {value} outside limit [{lower}, {upper}]")

        pose = np.eye(4)
        poses = [pose.copy()]
        for angle, axis, length in zip(
            angles, self.joint_axes, self.segment_lengths_m, strict=True
        ):
            step = np.eye(4)
            step[:3, :3] = _rotation(np.asarray(axis, dtype=np.float64), float(angle))
            step[:3, 3] = step[:3, :3] @ np.array([length, 0.0, 0.0])
            pose = pose @ step
            poses.append(pose.copy())
        self._check_postconditions(poses)
        return poses

    def joint_positions(self, q: Array) -> Array:
        """Positions of every frame origin, shape ``(n + 1, 3)``, in metres."""
        stacked: Array = np.stack([pose[:3, 3] for pose in self.forward_kinematics(q)])
        return stacked

    def tip_position(self, q: Array) -> Array:
        """Position of the distal end of the last segment, in metres."""
        tip: Array = self.joint_positions(q)[-1]
        return tip

    @staticmethod
    def _check_postconditions(poses: list[Array]) -> None:
        """Every rotation must be orthonormal with determinant +1."""
        for pose in poses:
            rot = pose[:3, :3]
            if not (
                np.allclose(rot.T @ rot, np.eye(3), atol=_ROT_TOL)
                and abs(np.linalg.det(rot) - 1.0) <= _ROT_TOL
            ):
                logger.error("non-rigid pose produced by forward kinematics")
                raise ArithmeticError("forward kinematics produced a non-rotation")


PLANAR_REDUCED = GolfModel3D(
    segment_lengths_m=SEGMENTS.lengths,
    joint_axes=((0.0, 0.0, 1.0),) * 3,
    joint_limits_rad=((-2.0 * math.pi, 2.0 * math.pi),) * 3,
    provenance=(
        "segment lengths: src/affine_control/golf_model.py GolfModel.lengths (illustrative, "
        "not anthropometry); joint axes: planar reduction about +z; "
        "joint limits: placeholder: owner review required"
    ),
)
"""The planar three-link model embedded in the x-y plane (rotation about +z)."""


JOHNSON_2015_ARM = GolfModel3D(
    segment_lengths_m=(0.60, 0.0, 0.20),
    joint_axes=((0.0, 0.0, 1.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
    joint_limits_rad=((-1.289, 1.210), (-1.237, 1.340), (-1.171, 1.185)),
    provenance=(
        "Arm of the four-degree-of-freedom golfer of johnson2015 Section 3.1 (after "
        "mackenzie2009), torso rotation omitted. Joints: shoulder transverse "
        "flexion/adduction, forearm pronation/supination, wrist radial/ulnar deviation "
        "(johnson2015 Section 3.1). Lengths: arm 0.60 m and hand-and-grip 0.20 m "
        "(johnson2015 Table 3.2); the club shaft is not modelled. Limits: the "
        "passive-moment breakpoints theta-/theta+ in johnson2015 Table 3.4 for shoulder, "
        "forearm and wrist, fitted there to experimental passive-moment data; they mark "
        "where passive restoring moments begin, so they are comfortable-range limits "
        "and not hard anatomical stops. Axes: pronation/supination is a rotation about "
        "the forearm long axis (local +x here); the shoulder axis +z (normal to the arm "
        "swing plane) and the wrist axis +z (cocking in the swing plane at neutral "
        "forearm roll, turned out of it by roll) are a modeling "
        "assumption because the axis directions of johnson2015 Figure 3.1 are not "
        "stated in its text; the sign of each positive angle versus the anatomical "
        "direction is also a modeling assumption; the 30 degree torso and 50 degree "
        "swing-plane inclinations of johnson2015 are viewer placement, not kinematics."
    ),
)
"""Cited 3D arm chain: shoulder (z), forearm roll (x, zero length), wrist (z)."""
