"""Tests for the rigid SE(3) golfer-club forward-kinematics provider (issue 4973)."""

from __future__ import annotations

import dataclasses
import math
import pathlib

import numpy as np
import pytest

from src.affine_control.golf_model import SEGMENTS
from src.affine_control.golf_model_3d import JOHNSON_2015_ARM, PLANAR_REDUCED, GolfModel3D

PLANAR_CONFIGS = [
    np.zeros(3),
    np.deg2rad([30.0, -40.0, 25.0]),
    np.deg2rad([120.0, -80.0, -60.0]),
    np.array([math.pi, -math.pi / 2, math.pi / 3]),
]


def _model(**overrides: object) -> GolfModel3D:
    fields = dataclasses.asdict(PLANAR_REDUCED) | overrides
    return GolfModel3D(**fields)


def test_identity_pose_is_a_straight_chain_along_x() -> None:
    poses = PLANAR_REDUCED.forward_kinematics(np.zeros(3))
    assert len(poses) == 4
    np.testing.assert_allclose(poses[0], np.eye(4))
    expected = np.cumsum([0.0, *PLANAR_REDUCED.segment_lengths_m])
    for pose, reach in zip(poses, expected, strict=True):
        np.testing.assert_allclose(pose[:3, :3], np.eye(3), atol=1e-12)
        np.testing.assert_allclose(pose[:3, 3], [reach, 0.0, 0.0], atol=1e-12)


def test_single_joint_rotation_matches_analytic_result() -> None:
    angle = 0.7
    poses = PLANAR_REDUCED.forward_kinematics(np.array([angle, 0.0, 0.0]))
    total = sum(PLANAR_REDUCED.segment_lengths_m)
    np.testing.assert_allclose(
        poses[-1][:3, 3], [total * math.cos(angle), total * math.sin(angle), 0.0], atol=1e-12
    )
    c, s = math.cos(angle), math.sin(angle)
    rz = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
    np.testing.assert_allclose(poses[-1][:3, :3], rz, atol=1e-12)


def test_out_of_plane_joint_lifts_the_tip_along_z() -> None:
    model = _model(joint_axes=((0.0, -1.0, 0.0), (0.0, 0.0, 1.0), (0.0, 0.0, 1.0)))
    tip = model.tip_position(np.array([math.pi / 2, 0.0, 0.0]))
    np.testing.assert_allclose(tip, [0.0, 0.0, sum(model.segment_lengths_m)], atol=1e-12)


@pytest.mark.parametrize("q", PLANAR_CONFIGS)
def test_planar_reduction_reproduces_the_planar_model(q: np.ndarray) -> None:
    angles = SEGMENTS.link_angles(q)
    expected = np.zeros(2)
    positions = PLANAR_REDUCED.joint_positions(q)
    for index, (length, angle) in enumerate(zip(SEGMENTS.lengths, angles, strict=True)):
        expected = expected + length * np.array([math.cos(angle), math.sin(angle)])
        np.testing.assert_allclose(positions[index + 1][:2], expected, atol=1e-12)
        assert positions[index + 1][2] == pytest.approx(0.0, abs=1e-12)


def test_planar_reduction_tip_speed_matches_planar_clubhead_speed() -> None:
    q = np.deg2rad([30.0, -40.0, 25.0])
    qd = np.array([2.0, -1.0, 3.0])
    step = 1e-6
    ahead = PLANAR_REDUCED.tip_position(q + step * qd)
    behind = PLANAR_REDUCED.tip_position(q - step * qd)
    speed = float(np.linalg.norm(ahead - behind) / (2.0 * step))
    assert speed == pytest.approx(SEGMENTS.clubhead_speed(q, qd), rel=1e-6)


@pytest.mark.parametrize(
    "axes",
    [
        ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        ((0.0, 0.6, 0.8), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
    ],
)
def test_rotations_stay_orthonormal_with_positive_determinant(
    axes: tuple[tuple[float, float, float], ...],
) -> None:
    model = _model(joint_axes=axes)
    rng = np.random.default_rng(7)
    for _ in range(50):
        q = rng.uniform(-1.5, 1.5, size=3)
        for pose in model.forward_kinematics(q):
            rot = pose[:3, :3]
            np.testing.assert_allclose(rot.T @ rot, np.eye(3), atol=1e-12)
            assert np.linalg.det(rot) == pytest.approx(1.0, abs=1e-12)
            np.testing.assert_allclose(pose[3], [0.0, 0.0, 0.0, 1.0])


@pytest.mark.parametrize(
    "overrides",
    [
        {"segment_lengths_m": (0.0, 0.0, 0.0)},
        {"segment_lengths_m": (0.3, -0.35, 1.15)},
        {"segment_lengths_m": (0.3, float("nan"), 1.15)},
        {"segment_lengths_m": (0.3, 0.35)},
        {"joint_axes": ((0.0, 0.0, 2.0),) * 3},
        {"joint_axes": ((0.0, 0.0, 0.0),) * 3},
        {"joint_axes": ((0.0, 0.0, 1.0),) * 2},
        {"joint_limits_rad": ((1.0, -1.0),) * 3},
        {"joint_limits_rad": ((-1.0, float("inf")),) * 3},
        {"provenance": ""},
    ],
)
def test_invalid_parameters_are_rejected(overrides: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        _model(**overrides)


def test_invalid_joint_values_are_rejected() -> None:
    model = _model(joint_limits_rad=((-1.0, 1.0),) * 3)
    with pytest.raises(ValueError, match="limit"):
        model.forward_kinematics(np.array([0.0, 1.5, 0.0]))
    with pytest.raises(ValueError, match="finite"):
        model.forward_kinematics(np.array([0.0, np.nan, 0.0]))
    with pytest.raises(ValueError, match="shape"):
        model.forward_kinematics(np.zeros(2))


def test_parameters_carry_units_and_provenance() -> None:
    assert PLANAR_REDUCED.segment_lengths_m == SEGMENTS.lengths
    assert PLANAR_REDUCED.provenance
    assert "placeholder: owner review required" in PLANAR_REDUCED.provenance
    with pytest.raises(dataclasses.FrozenInstanceError):
        PLANAR_REDUCED.provenance = "changed"  # type: ignore[misc]


BIB = pathlib.Path(__file__).resolve().parent.parent / "references" / "proximal-distal-energy.bib"


def test_zero_length_segment_acts_as_a_pure_rotation_joint() -> None:
    model = _model(segment_lengths_m=(0.3, 0.0, 1.15))
    tip = model.tip_position(np.array([0.0, 1.0, 0.0]))
    np.testing.assert_allclose(
        tip, [0.3 + 1.15 * math.cos(1.0), 1.15 * math.sin(1.0), 0.0], atol=1e-12
    )


def test_johnson_axes_limits_and_lengths_match_the_cited_tables() -> None:
    # Johnson 2015 Table 3.2 (arm 60 cm, hand and grip 20 cm), Table 3.4 breakpoints.
    assert JOHNSON_2015_ARM.segment_lengths_m == (0.60, 0.0, 0.20)
    assert JOHNSON_2015_ARM.joint_axes == ((0.0, 0.0, 1.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    assert JOHNSON_2015_ARM.joint_limits_rad == (
        (-1.289, 1.210),
        (-1.237, 1.340),
        (-1.171, 1.185),
    )


def test_forearm_roll_is_about_the_long_axis_and_keeps_the_hand_on_it() -> None:
    q = np.array([0.4, 1.0, 0.0])
    base = JOHNSON_2015_ARM.tip_position(np.array([0.4, 0.0, 0.0]))
    np.testing.assert_allclose(JOHNSON_2015_ARM.tip_position(q), base, atol=1e-12)


def test_wrist_deviation_leaves_the_plane_after_forearm_roll() -> None:
    q = np.array([0.0, 1.2, 0.5])
    flat = JOHNSON_2015_ARM.tip_position(np.array([0.0, 0.0, 0.5]))
    assert flat[2] == pytest.approx(0.0, abs=1e-12)
    # expected z = hand * sin(roll) * sin(deviation) (hand = 0.20 m)
    expected = 0.20 * math.sin(1.2) * math.sin(0.5)
    assert JOHNSON_2015_ARM.tip_position(q)[2] == pytest.approx(expected, abs=1e-12)


def test_johnson_provenance_cites_a_bibliography_key_that_exists() -> None:
    assert "johnson2015" in JOHNSON_2015_ARM.provenance
    assert "@mastersthesis{johnson2015," in BIB.read_text(encoding="utf8")
    assert "modeling assumption" in JOHNSON_2015_ARM.provenance
