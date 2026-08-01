"""Tests for the Volume 0 Chapter 4 quaternion worked example.

The chapter enumerates six things the listing demonstrates. Each is asserted
here against an independent route -- a rotation matrix built from the axis-angle
form, or a property that holds for every rotation -- so the listing is an
example the reader can trust rather than a claim.
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np
import pytest

# The listing is deliberately not importable as a package: it lives beside the
# chapter that typesets it, so that the file the reader sees is the file the
# tests run.
_DEMO = (
    Path(__file__).resolve().parents[2]
    / "articles"
    / "The_Geometry_of_Motion"
    / "Volume_0"
    / "code"
    / "quaternion_demo.py"
)
_spec = importlib.util.spec_from_file_location("quaternion_demo", _DEMO)
assert _spec is not None and _spec.loader is not None
qd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(qd)


AXES = [
    np.array([0.0, 0.0, 1.0]),
    np.array([1.0, 0.0, 0.0]),
    np.array([1.0, 2.0, -3.0]),
]
ANGLES = [0.0, 0.3, math.pi / 2, 2.0, math.pi - 0.05]


def test_the_listing_the_chapter_typesets_actually_exists() -> None:
    """Guards the defect this file was written to fix.

    The chapter said "below is a complete Python implementation" and pointed at
    a file that did not exist, via a package the preamble did not load. It had
    therefore never rendered.
    """
    assert _DEMO.is_file()


@pytest.mark.parametrize("axis", AXES)
@pytest.mark.parametrize("angle", ANGLES)
def test_axis_angle_quaternion_is_a_unit_quaternion(axis: np.ndarray, angle: float) -> None:
    assert np.linalg.norm(qd.from_axis_angle(axis, angle)) == pytest.approx(1.0)


@pytest.mark.parametrize("axis", AXES)
@pytest.mark.parametrize("angle", ANGLES)
def test_matrix_is_a_rotation(axis: np.ndarray, angle: float) -> None:
    """Orthogonal with determinant +1 -- the definition of SO(3)."""
    matrix = qd.to_matrix(qd.from_axis_angle(axis, angle))
    np.testing.assert_allclose(matrix @ matrix.T, np.eye(3), atol=1e-12)
    assert np.linalg.det(matrix) == pytest.approx(1.0)


@pytest.mark.parametrize("axis", AXES)
@pytest.mark.parametrize("angle", ANGLES)
def test_matrix_matches_rodrigues(axis: np.ndarray, angle: float) -> None:
    """Independent route: the chapter's own Rodrigues formula."""
    unit = axis / np.linalg.norm(axis)
    skew = np.array(
        [
            [0.0, -unit[2], unit[1]],
            [unit[2], 0.0, -unit[0]],
            [-unit[1], unit[0], 0.0],
        ]
    )
    rodrigues = np.eye(3) + math.sin(angle) * skew + (1 - math.cos(angle)) * (skew @ skew)
    got = qd.to_matrix(qd.from_axis_angle(axis, angle))
    np.testing.assert_allclose(got, rodrigues, atol=1e-12)


@pytest.mark.parametrize("axis", AXES)
@pytest.mark.parametrize("angle", ANGLES)
def test_sandwich_product_agrees_with_the_matrix(axis: np.ndarray, angle: float) -> None:
    """Rotating without forming a matrix must give the same answer."""
    q = qd.from_axis_angle(axis, angle)
    rng = np.random.default_rng(11)
    for _ in range(10):
        v = rng.normal(size=3)
        np.testing.assert_allclose(qd.rotate(q, v), qd.to_matrix(q) @ v, atol=1e-12)


def test_hamilton_product_composes_rotations_in_order() -> None:
    """q_p * q_q must be the matrix product, in the same order."""
    p = qd.from_axis_angle(np.array([0.0, 0.0, 1.0]), 0.7)
    q = qd.from_axis_angle(np.array([0.0, 1.0, 0.0]), -1.1)
    np.testing.assert_allclose(
        qd.to_matrix(qd.hamilton_product(p, q)), qd.to_matrix(p) @ qd.to_matrix(q), atol=1e-12
    )


def test_hamilton_product_is_not_commutative() -> None:
    """Stated in the chapter; a test that passes either way would prove nothing."""
    p = qd.from_axis_angle(np.array([0.0, 0.0, 1.0]), 0.7)
    q = qd.from_axis_angle(np.array([0.0, 1.0, 0.0]), -1.1)
    assert not np.allclose(qd.hamilton_product(p, q), qd.hamilton_product(q, p))


def test_conjugate_inverts_a_unit_quaternion() -> None:
    q = qd.from_axis_angle(np.array([1.0, 2.0, -3.0]), 1.3)
    identity = qd.hamilton_product(q, qd.conjugate(q))
    np.testing.assert_allclose(identity, np.array([1.0, 0.0, 0.0, 0.0]), atol=1e-12)


def test_normalize_rejects_the_zero_quaternion() -> None:
    with pytest.raises(ValueError, match="zero quaternion"):
        qd.normalize(np.zeros(4))


def test_slerp_hits_both_endpoints() -> None:
    q0 = qd.from_axis_angle(np.array([0.0, 0.0, 1.0]), 0.0)
    q1 = qd.from_axis_angle(np.array([0.0, 0.0, 1.0]), 1.5)
    np.testing.assert_allclose(qd.slerp(q0, q1, 0.0), q0, atol=1e-12)
    np.testing.assert_allclose(qd.slerp(q0, q1, 1.0), q1, atol=1e-12)


def test_slerp_stays_on_the_unit_sphere() -> None:
    q0 = qd.from_axis_angle(np.array([1.0, 0.0, 0.0]), 0.2)
    q1 = qd.from_axis_angle(np.array([0.0, 1.0, 1.0]), 2.4)
    for t in np.linspace(0.0, 1.0, 25):
        assert np.linalg.norm(qd.slerp(q0, q1, t)) == pytest.approx(1.0)


def test_slerp_has_constant_angular_velocity() -> None:
    """This is the property that distinguishes SLERP from normalised lerp."""
    q0 = qd.from_axis_angle(np.array([0.0, 0.0, 1.0]), 0.0)
    q1 = qd.from_axis_angle(np.array([0.0, 0.0, 1.0]), 2.0)
    samples = [qd.slerp(q0, q1, t) for t in np.linspace(0.0, 1.0, 21)]
    steps = [
        2.0 * math.acos(min(1.0, abs(float(np.dot(a, b)))))
        for a, b in zip(samples[:-1], samples[1:], strict=True)
    ]
    assert max(steps) - min(steps) < 1e-9


def test_slerp_takes_the_short_arc() -> None:
    """With a negative dot product the naive formula goes the long way round."""
    q0 = qd.from_axis_angle(np.array([0.0, 0.0, 1.0]), 0.0)
    q1 = -qd.from_axis_angle(np.array([0.0, 0.0, 1.0]), 0.4)
    midpoint = qd.slerp(q0, q1, 0.5)
    expected = qd.from_axis_angle(np.array([0.0, 0.0, 1.0]), 0.2)
    assert abs(float(np.dot(midpoint, expected))) == pytest.approx(1.0, abs=1e-12)


def test_slerp_falls_back_cleanly_for_nearby_quaternions() -> None:
    """The branch exists because sin(Omega) is in a denominator."""
    q0 = qd.from_axis_angle(np.array([0.0, 0.0, 1.0]), 0.5)
    q1 = qd.from_axis_angle(np.array([0.0, 0.0, 1.0]), 0.5 + 1e-12)
    result = qd.slerp(q0, q1, 0.5)
    assert np.all(np.isfinite(result))
    assert np.linalg.norm(result) == pytest.approx(1.0)


def test_point_cloud_interpolation_returns_one_frame_each() -> None:
    points = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    q0 = qd.from_axis_angle(np.array([0.0, 0.0, 1.0]), 0.0)
    q1 = qd.from_axis_angle(np.array([0.0, 0.0, 1.0]), math.pi / 2)
    frames = qd.interpolate_point_cloud(points, q0, q1, 5)
    assert len(frames) == 5
    np.testing.assert_allclose(frames[0], points, atol=1e-12)
    # A rigid rotation preserves every pairwise distance.
    for frame in frames:
        np.testing.assert_allclose(np.linalg.norm(frame[0] - frame[1]), math.sqrt(2.0), atol=1e-12)
