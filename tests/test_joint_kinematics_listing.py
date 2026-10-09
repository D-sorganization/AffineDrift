"""Verify the published ISA contracts against independent rigid-motion identities."""

import re
from pathlib import Path
from typing import Any

import numpy as np
import pytest

CHAPTER = (
    Path(__file__).resolve().parents[1]
    / "articles/The_Geometry_of_Motion/Volume_III/chapters/ch04_joint_kinematics.tex"
)


@pytest.fixture(scope="module")
def listing() -> dict[str, Any]:
    blocks = re.findall(
        r"\\begin\{lstlisting\}\[language=Python,[^\n]*\]\n(.*?)\\end\{lstlisting\}",
        CHAPTER.read_text(encoding="utf-8"),
        re.DOTALL,
    )
    assert blocks
    namespace: dict[str, Any] = {}
    for block in blocks:
        # Repository-owned listing at a fixed path, with no external input.
        # nosemgrep: python.lang.security.audit.exec-detected.exec-detected
        exec(compile(block, str(CHAPTER), "exec"), namespace)
    return namespace


def test_recover_axis_from_point_velocity(listing: dict[str, Any]) -> None:
    omega = np.array([0.0, 0.0, 2.0])
    axis = np.array([0.03, -0.02, 0.0])
    point = np.array([0.10, 0.20, -0.10])
    pitch = 0.005
    point_velocity = np.cross(omega, point - axis) + pitch * omega
    spatial_v = point_velocity - np.cross(omega, point)
    recovered, direction, h = listing["compute_isa"](omega, spatial_v)
    np.testing.assert_allclose(recovered, axis)
    np.testing.assert_allclose(direction, [0.0, 0.0, 1.0])
    assert h == pytest.approx(pitch)


@pytest.mark.parametrize(
    "omega,v",
    [
        ([0, 0, 0], [0, 0, 0]),
        ([0, 0, 0], [1, 0, 0]),
        ([0, 0, 1e-12], [0, 1, 0]),
        ([0, 0, np.nan], [0, 1, 0]),
        ([0, 0, 1], [0, np.inf, 0]),
        ([0, 1], [0, 0, 0]),
        ([[0, 0, 1]], [0, 0, 0]),
    ],
)
def test_unsupported_or_invalid_twist_is_rejected(
    listing: dict[str, Any], omega: list, v: list
) -> None:
    with pytest.raises(ValueError):
        listing["compute_isa"](np.asarray(omega), np.asarray(v))


@pytest.mark.parametrize("threshold", [0.0, -1.0, np.nan, np.inf])
def test_invalid_angular_threshold_is_rejected(listing: dict[str, Any], threshold: float) -> None:
    with pytest.raises(ValueError):
        listing["compute_isa"](np.array([0.0, 0.0, 1.0]), np.zeros(3), threshold)


def test_frame_change_preserves_axis_line_and_pitch(listing: dict[str, Any]) -> None:
    omega = np.array([0.5, -0.3, 1.2])
    v = np.array([0.03, -0.04, 0.02])
    shift = np.array([0.2, -0.1, 0.3])
    rotation = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    q, axis, pitch = listing["compute_isa"](omega, v)
    new_q, new_axis, new_pitch = listing["compute_isa"](
        rotation @ omega, rotation @ (v + np.cross(omega, shift))
    )
    transformed = rotation @ (q - shift)
    np.testing.assert_allclose(
        new_q, transformed - new_axis * np.dot(new_axis, transformed), atol=1e-14
    )
    np.testing.assert_allclose(new_axis, rotation @ axis)
    assert new_pitch == pytest.approx(pitch)
