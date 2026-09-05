"""Independent counterexamples for configuration geometry and rigid-body control."""

from pathlib import Path

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
GRAVITY_M_S2 = 9.81


def _hat(vector: np.ndarray) -> np.ndarray:
    """Map a three-vector to its cross-product matrix."""
    x, y, z = vector
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])


def test_exponential_differential_is_regular_at_half_turn() -> None:
    for angle, expected in [(np.pi, 4 / np.pi**2), (2 * np.pi, 0.0)]:
        skew = _hat(np.array([0.0, 0.0, angle]))
        jacobian = (
            np.eye(3)
            - (1 - np.cos(angle)) / angle**2 * skew
            + (angle - np.sin(angle)) / angle**3 * skew @ skew
        )
        assert np.linalg.det(jacobian) == pytest.approx(expected, abs=1e-14)
    positive = Rotation.from_rotvec([0.0, 0.0, np.pi]).as_matrix()
    negative = Rotation.from_rotvec([0.0, 0.0, -np.pi]).as_matrix()
    np.testing.assert_allclose(positive, negative, atol=1e-14)


def test_zyx_rate_singularity_does_not_require_unbounded_physical_velocity() -> None:
    roll = 0.4
    for pitch in [0.0, 0.7, np.pi / 2]:
        mapping = np.array(
            [
                [1, 0, -np.sin(pitch)],
                [0, np.cos(roll), np.sin(roll) * np.cos(pitch)],
                [0, -np.sin(roll), np.cos(roll) * np.cos(pitch)],
            ]
        )
        assert np.linalg.det(mapping) == pytest.approx(np.cos(pitch))
        np.testing.assert_allclose(
            mapping @ np.array([0.0, 1.0, 0.0]),
            [0.0, np.cos(roll), -np.sin(roll)],
            atol=1e-14,
        )


def test_configuration_metric_length_does_not_fix_work() -> None:
    angle = np.pi / 18
    torso, wrist = 12.0, 0.03
    assert np.sqrt(torso) * angle / (np.sqrt(wrist) * angle) == pytest.approx(20.0)
    wrist_duration, torso_duration = 1.0, 20.0
    assert 0.5 * torso * (angle / torso_duration) ** 2 == pytest.approx(
        0.5 * wrist * (angle / wrist_duration) ** 2
    )


def test_force_covectors_preserve_power_under_coordinate_change() -> None:
    change = np.array([[2.0, 1.0], [0.0, 3.0]])
    metric = np.array([[3.0, 0.4], [0.4, 2.0]])
    velocity, force = np.array([0.7, -0.2]), np.array([4.0, 5.0])
    inverse = np.linalg.inv(change)
    new_metric = inverse.T @ metric @ inverse
    new_velocity, new_force = change @ velocity, inverse.T @ force
    assert new_force @ new_velocity == pytest.approx(force @ velocity)
    assert new_velocity @ new_metric @ new_velocity == pytest.approx(velocity @ metric @ velocity)
    assert new_force @ np.linalg.solve(new_metric, new_force) == pytest.approx(
        force @ np.linalg.solve(metric, force)
    )


def test_straight_cartesian_motion_has_nonzero_polar_connection_terms() -> None:
    time = 0.6
    radius = np.sqrt(1 + time**2)
    radius_rate, radius_acceleration = time / radius, 1 / radius**3
    angle_rate, angle_acceleration = 1 / radius**2, -2 * time / radius**4
    assert radius_acceleration > 0
    assert radius_acceleration - radius * angle_rate**2 == pytest.approx(0.0, abs=1e-14)
    assert angle_acceleration + 2 * radius_rate * angle_rate / radius == pytest.approx(
        0.0, abs=1e-14
    )


def test_passive_gravity_motion_is_not_kinetic_metric_geodesic() -> None:
    gravity, length, angle, speed = GRAVITY_M_S2, 1.0, np.pi / 6, 2.0
    acceleration = -gravity / length * np.sin(angle)
    assert acceleration == pytest.approx(-4.905)
    energy_rate = length**2 * speed * acceleration + gravity * length * np.sin(angle) * speed
    assert energy_rate == pytest.approx(0.0, abs=1e-13)


def test_flat_polar_metric_has_zero_intrinsic_curvature() -> None:
    radius = 1.7
    # R^r_{theta r theta} = d_r Gamma^r_{theta theta}
    # - Gamma^r_{theta theta} Gamma^theta_{r theta} = -1 + 1.
    connection_radial, connection_angular = -radius, 1 / radius
    assert -1 - connection_radial * connection_angular == pytest.approx(0.0)


def test_common_world_angular_velocity_requires_reference_to_actual_transform() -> None:
    actual = Rotation.from_rotvec([0.5, -0.1, 0.3]).as_matrix()
    desired = Rotation.from_rotvec([-0.2, 0.6, 0.1]).as_matrix()
    world_velocity = np.array([0.8, -0.4, 0.3])
    omega, desired_omega = actual.T @ world_velocity, desired.T @ world_velocity
    np.testing.assert_allclose(omega - actual.T @ desired @ desired_omega, 0.0, atol=1e-14)
    assert np.linalg.norm(omega - desired.T @ actual @ desired_omega) > 0.1


def test_attitude_feedforward_cancels_transport_derivative() -> None:
    actual = Rotation.from_rotvec([0.5, -0.1, 0.3]).as_matrix()
    desired = Rotation.from_rotvec([-0.2, 0.6, 0.1]).as_matrix()
    transform = actual.T @ desired
    omega, desired_omega = np.array([0.4, 0.2, -0.3]), np.array([-0.2, 0.7, 0.5])
    desired_acceleration = np.array([0.1, -0.3, 0.2])
    inertia = np.diag([2.0, 3.0, 4.0])
    relative = desired.T @ actual
    skew_error = 0.5 * (relative - relative.T)
    attitude_error = np.array([skew_error[2, 1], skew_error[0, 2], skew_error[1, 0]])
    velocity_error = omega - transform @ desired_omega
    transport_rate = -np.cross(omega, transform @ desired_omega) + transform @ desired_acceleration
    torque = (
        -4 * attitude_error
        - 2 * velocity_error
        + np.cross(omega, inertia @ omega)
        + inertia @ transport_rate
    )
    acceleration = np.linalg.solve(inertia, torque - np.cross(omega, inertia @ omega))
    np.testing.assert_allclose(
        inertia @ (acceleration - transport_rate), -4 * attitude_error - 2 * velocity_error
    )
    potential_rate = attitude_error @ velocity_error
    energy_rate = velocity_error @ inertia @ (acceleration - transport_rate) + 4 * potential_rate
    assert energy_rate == pytest.approx(-2 * velocity_error @ velocity_error)


def test_smooth_attitude_error_vanishes_at_undesired_half_turn() -> None:
    rotation = Rotation.from_rotvec([np.pi, 0.0, 0.0]).as_matrix()
    assert 0.5 * np.trace(np.eye(3) - rotation) == pytest.approx(2.0)
    np.testing.assert_allclose(rotation - rotation.T, 0.0, atol=1e-14)


def test_quaternion_orientation_distance_respects_double_cover() -> None:
    quaternion = Rotation.from_rotvec([0.2, 0.3, -0.4]).as_quat()
    opposite = -quaternion
    assert np.linalg.norm(quaternion - opposite) == pytest.approx(2.0)
    angle = 2 * np.arccos(np.clip(abs(quaternion @ opposite), 0.0, 1.0))
    assert angle == pytest.approx(0.0, abs=5e-8)


@pytest.mark.parametrize(
    "relative",
    [
        "articles/The_Geometry_of_Motion/Volume_II/chapters/ch03_configuration_manifolds.tex",
        "articles/motion-control/chapter3.tex",
        "articles/motion-control/Control_Is_Motion_Complete.tex",
        "articles/The_Geometry_of_Motion/quarto/volume2_content.qmd",
    ],
)
def test_manifold_editions_remove_invalid_mechanical_and_control_claims(relative: str) -> None:
    text = (ROOT / relative).read_text(encoding="utf-8")
    for invalid in [
        "Every modern spacecraft avoids",
        "the follow-through is nearly geodesic",
        "rotating the torso requires 400 times more energy",
        "On a flat manifold",
    ]:
        assert invalid not in text
    assert "manifold_polar_geodesic" in text
    assert "manifold_attitude_transport" in text
