"""Precomputed frames of the cited 3D arm chain for the spatial swing viewer (#4973).

Phase 2 of the swing viewer (ADR 0002): the browser only draws the frames built
here, so the kinematics have one source, ``JOHNSON_2015_ARM`` in
``golf_model_3d``. The motion is a *prescribed* joint sweep, not a simulated
swing: each joint follows a sinusoid inside its declared limits. Nothing is
measured and no dynamics are computed.
"""

from __future__ import annotations

import math

import numpy as np

from src.affine_control.golf_model_3d import JOHNSON_2015_ARM, GolfModel3D
from src.core.contracts import require

__all__ = [
    "CAVEATS",
    "JOINT_NAMES",
    "LIMIT_FRACTION",
    "PHASES_RAD",
    "build_frames",
    "build_joint_table",
]

JOINT_NAMES = ("Shoulder transverse flexion", "Forearm pronation", "Wrist deviation")
LIMIT_FRACTION = 0.8
PHASES_RAD = (0.0, math.pi / 2.0, math.pi)
DIGITS = 6

CAVEATS = (
    "Joint limits are passive-moment breakpoints from Johnson (2015) Table 3.4: where "
    "passive restoring moments begin, not hard anatomical stops.",
    "The shoulder and wrist axes (+z) and the forearm axis (+x) are assumed; the axis "
    "directions in Johnson's Figure 3.1 are not stated in its text.",
    "The sign of each positive angle against the anatomical direction is unverified.",
    "The motion is a prescribed sweep through the joints, not a measured or simulated swing.",
    "Torso rotation and the club shaft are not modelled; the tip is the grip end.",
    "Johnson's 30 and 50 degree torso and swing-plane inclinations are viewer placement "
    "only and are not applied here.",
)


def _amplitude(limits: tuple[float, float]) -> float:
    """Sweep amplitude: a fixed fraction of the nearer joint limit, so q stays inside."""
    return LIMIT_FRACTION * min(abs(limits[0]), abs(limits[1]))


def build_joint_table(model: GolfModel3D = JOHNSON_2015_ARM) -> list[dict[str, object]]:
    """Name, axis, limits (rad) and segment length of every joint, for the page."""
    require(len(JOINT_NAMES) == len(model.joint_axes), "one name per joint", len(JOINT_NAMES))
    return [
        {"name": name, "axis": list(axis), "limitsRad": list(limits), "segmentM": length}
        for name, axis, limits, length in zip(
            JOINT_NAMES,
            model.joint_axes,
            model.joint_limits_rad,
            model.segment_lengths_m,
            strict=True,
        )
    ]


def build_frames(count: int = 61, model: GolfModel3D = JOHNSON_2015_ARM) -> list[dict[str, object]]:
    """``count`` frames of one sweep cycle: joint angles and 3D frame-origin points (m)."""
    require(count >= 2, "at least two frames are needed", count)
    amplitudes = [_amplitude(limits) for limits in model.joint_limits_rad]
    frames = []
    for index in range(count):
        phase = 2.0 * math.pi * index / (count - 1)
        q = np.array([a * math.sin(phase + p) for a, p in zip(amplitudes, PHASES_RAD, strict=True)])
        frames.append(
            {
                "s": round(index / (count - 1), DIGITS),
                "q": np.round(q, DIGITS).tolist(),
                "points": np.round(model.joint_positions(q), DIGITS).tolist(),
            }
        )
    return frames
