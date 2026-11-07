"""Synthetic stick-figure golfer clip for the 3D viewer draft (#5425): keyframed angles drive a
skeleton, so it is hand-shaped, not measured, not licensed motion capture and not a traced
UpstreamDrift render. Metres, +y up, golfer facing +z, target toward +x."""

from __future__ import annotations

import numpy as np

MARKERS = (
    "head", "neck", "left shoulder", "right shoulder", "left elbow", "right elbow", "hands",
    "clubhead", "pelvis", "left hip", "right hip", "left knee", "right knee", "left ankle",
    "right ankle",
)  # fmt: skip
SEGMENTS = (
    (0, 1), (1, 2), (1, 3), (2, 4), (4, 6), (3, 5), (5, 6), (6, 7),
    (1, 8), (8, 9), (8, 10), (9, 11), (11, 13), (10, 12), (12, 14),
)  # fmt: skip
CAVEATS = (
    "Synthetic, hand-shaped motion from keyframed angles: not measured, not simulated.",
    "Not licensed motion capture and not a traced UpstreamDrift render.",
    "Elbows are midpoints of shoulder and hands; the figure has no wrist or foot detail.",
)

# Swing progress keyframes (address, top, impact, finish) and the angles they set, in radians.
KEY_S = np.array([0.0, 0.6, 0.85, 1.0])
ARM_ANGLE = np.array([0.0, -2.3, 0.0, 1.4])
WRIST_HINGE = np.array([0.0, -1.3, 0.0, 0.5])
SHOULDER_TURN = np.array([0.0, -1.4, 0.3, 0.9])
HIP_TURN = np.array([0.0, -0.6, 0.5, 0.8])

PELVIS = np.array([0.0, 0.9, -0.05])
NECK = np.array([0.0, 1.45, 0.2])
HEAD_OFFSET = np.array([0.0, 0.2, 0.08])
SHOULDER_HALF_WIDTH = 0.19
HIP_HALF_WIDTH = 0.12
ARM_REACH = 0.65
CLUB_LENGTH = 1.0
TARGET_AXIS = np.array([1.0, 0.0, 0.0])
PLANE_DOWN = np.array([0.0, -0.8, 0.6])  # address direction from neck to hands, in the swing plane
LEGS = np.array([[0.17, 0.5, 0.08], [-0.17, 0.5, 0.08], [0.18, 0.05, 0.0], [-0.18, 0.05, 0.0]])
DECIMALS = 3


def _eased(values: np.ndarray, s: float) -> float:
    """Cosine-eased interpolation of keyframe ``values`` at swing progress ``s``."""
    k = min(int(np.searchsorted(KEY_S, s, side="right")) - 1, len(KEY_S) - 2)
    t = (s - KEY_S[k]) / (KEY_S[k + 1] - KEY_S[k])
    w = (1 - np.cos(np.pi * t)) / 2
    return float(values[k] + w * (values[k + 1] - values[k]))


def _lateral(turn: float, half_width: float) -> np.ndarray:
    """Left-side offset of a body pair turned by ``turn`` about the vertical."""
    return half_width * np.array([np.cos(turn), 0.0, -np.sin(turn)])


def _in_plane(angle: float) -> np.ndarray:
    """Unit direction in the inclined swing plane, ``angle`` from the address direction."""
    return float(np.sin(angle)) * TARGET_AXIS + float(np.cos(angle)) * PLANE_DOWN


def pose(s: float) -> np.ndarray:
    """Marker positions (``len(MARKERS)`` x 3) at swing progress ``s`` in [0, 1]."""
    if not 0.0 <= s <= 1.0:
        raise ValueError(f"swing progress must be in [0, 1], got {s}")
    arm = _eased(ARM_ANGLE, s)
    shoulder = _lateral(_eased(SHOULDER_TURN, s), SHOULDER_HALF_WIDTH)
    hip = _lateral(_eased(HIP_TURN, s), HIP_HALF_WIDTH)
    hands = NECK + ARM_REACH * _in_plane(arm)
    club = hands + CLUB_LENGTH * _in_plane(arm + _eased(WRIST_HINGE, s))
    left, right = NECK + shoulder, NECK - shoulder
    torso = [NECK + HEAD_OFFSET, NECK, left, right, (left + hands) / 2, (right + hands) / 2]
    return np.array([*torso, hands, club, PELVIS, PELVIS + hip, PELVIS - hip, *LEGS])


def build_frames(count: int = 25) -> list[dict[str, object]]:
    """``count`` evenly spaced frames, each ``{"s": progress, "points": [[x, y, z], ...]}``."""
    if count < 2:
        raise ValueError("a clip needs at least two frames")
    progress = np.linspace(0.0, 1.0, count)
    return [
        {"s": round(float(s), DECIMALS), "points": np.round(pose(s), DECIMALS).tolist()}
        for s in progress
    ]
