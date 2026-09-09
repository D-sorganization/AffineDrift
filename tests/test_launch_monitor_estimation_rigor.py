"""Independent geometry and inference checks for launch-monitor article #4309."""

from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray
from scipy.linalg import expm
from scipy.spatial.transform import Rotation

SOURCE = Path(__file__).resolve().parents[1] / "articles/technology-launch-monitors.qmd"
LIGHT_SPEED = 299792458.0
MPH_TO_MPS = 0.44704


def skew(vector: NDArray[np.float64]) -> NDArray[np.float64]:
    x, y, z = vector
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])


def doppler_rows(
    origin: NDArray[np.float64],
    offsets: NDArray[np.float64],
    sensor: NDArray[np.float64],
) -> NDArray[np.float64]:
    directions = origin + offsets - sensor
    directions /= np.linalg.norm(directions, axis=1)[:, None]
    return np.column_stack((np.cross(offsets, directions), directions))


@pytest.mark.parametrize("carrier_ghz,expected", [(24.0, 71.5759167), (10.5, 31.3144636)])
def test_doppler_frequency_uses_two_way_path(carrier_ghz: float, expected: float) -> None:
    frequency = 2 * carrier_ghz * 1e9 * MPH_TO_MPS / LIGHT_SPEED
    assert frequency == pytest.approx(expected, abs=1e-7)


@pytest.mark.parametrize("sensor_count,rank", [(1, 3), (2, 5), (3, 6)])
def test_separate_monostatic_doppler_rank(sensor_count: int, rank: int) -> None:
    origin = np.array([2.0, 0.2, 0.1])
    offsets = np.random.default_rng(4309).uniform(-0.05, 0.05, (30, 3))
    sensors = [np.zeros(3), np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 1.0])]
    matrix = np.vstack([doppler_rows(origin, offsets, s) for s in sensors[:sensor_count]])
    assert np.linalg.matrix_rank(matrix) == rank


def test_single_sensor_nullspace_is_exact_even_with_diverging_sightlines() -> None:
    origin = np.array([2.0, 0.2, 0.1])
    sensor = np.array([0.1, -0.3, 0.5])
    offsets = np.random.default_rng(19).uniform(-0.3, 0.3, (40, 3))
    delta_omega = np.array([0.7, -0.2, 0.9])
    delta_velocity = np.cross(delta_omega, origin - sensor)
    residual = doppler_rows(origin, offsets, sensor) @ np.r_[delta_omega, delta_velocity]
    assert np.max(np.abs(residual)) < 1e-14


def test_two_sensors_retain_baseline_rotation_null_direction() -> None:
    origin = np.array([2.0, 0.2, 0.1])
    offsets = np.random.default_rng(20).uniform(-0.1, 0.1, (40, 3))
    first, second = np.zeros(3), np.array([0.0, 1.0, 0.0])
    delta_omega = second - first
    null = np.r_[delta_omega, np.cross(delta_omega, origin - first)]
    matrix = np.vstack([doppler_rows(origin, offsets, s) for s in [first, second]])
    assert np.max(np.abs(matrix @ null)) < 1e-14


def test_point_transport_has_no_universal_left_or_shallow_sign() -> None:
    velocity = np.array([45.0, 0.0, -3.0])
    offset, omega = np.array([0.04, 0.0, 0.0]), np.array([0.0, -10.0, 30.0])
    first, second = velocity + np.cross(omega, offset), velocity - np.cross(omega, offset)
    assert first[1] > velocity[1] > second[1]
    assert first[2] > velocity[2] > second[2]
    assert np.linalg.norm(first) != pytest.approx(np.linalg.norm(second))


def test_spatial_twist_translation_is_not_body_origin_velocity() -> None:
    position, velocity = np.array([1.0, 2.0, 3.0]), np.array([4.0, 5.0, 6.0])
    omega = np.array([0.2, -0.3, 0.5])
    transform = np.eye(4)
    transform[:3, :3] = Rotation.from_rotvec([0.1, 0.2, 0.3]).as_matrix()
    transform[:3, 3] = position
    derivative = np.zeros((4, 4))
    derivative[:3, :3] = skew(omega) @ transform[:3, :3]
    derivative[:3, 3] = velocity
    spatial = derivative @ np.linalg.inv(transform)
    assert spatial[:3, 3] == pytest.approx(velocity - np.cross(omega, position))
    assert not np.allclose(spatial[:3, 3], velocity)


def test_screw_axis_velocity_is_parallel_to_nonzero_angular_velocity() -> None:
    omega, velocity = np.array([2.0, -3.0, 4.0]), np.array([5.0, 6.0, 7.0])
    point = np.cross(omega, velocity) / np.dot(omega, omega)
    pitch = np.dot(omega, velocity) / np.dot(omega, omega)
    axis_velocity = velocity + np.cross(omega, point)
    assert axis_velocity == pytest.approx(pitch * omega)
    assert point @ omega == pytest.approx(0.0, abs=1e-14)


def test_body_and_spatial_rotation_updates_agree() -> None:
    rotation = Rotation.from_rotvec([0.3, -0.1, 0.4]).as_matrix()
    body_omega, interval = np.array([2.0, -1.0, 3.0]), 0.02
    spatial_omega = rotation @ body_omega
    assert rotation @ expm(skew(body_omega) * interval) == pytest.approx(
        expm(skew(spatial_omega) * interval) @ rotation
    )


def test_noncommuting_integration_cannot_exponentiate_summed_axes() -> None:
    first, second = np.array([np.pi / 3, 0.0, 0.0]), np.array([0.0, np.pi / 4, 0.0])
    ordered = expm(skew(second)) @ expm(skew(first))
    naive = expm(skew(first + second))
    error = np.degrees(Rotation.from_matrix(ordered @ naive.T).magnitude())
    assert error == pytest.approx(22.500474, abs=1e-6)


def test_lift_and_total_spin_do_not_resolve_parallel_spin_sign() -> None:
    velocity = np.array([50.0, 0.0, 0.0])
    first, second = np.array([80.0, -200.0, 40.0]), np.array([-80.0, -200.0, 40.0])
    assert np.linalg.norm(first) == pytest.approx(np.linalg.norm(second))
    assert np.cross(first, velocity) == pytest.approx(np.cross(second, velocity))
    lift = np.cross(first, velocity)
    perpendicular = np.cross(velocity, lift) / np.dot(velocity, velocity)
    assert perpendicular == pytest.approx([0.0, -200.0, 40.0])


@pytest.mark.parametrize("changing_direction,rank", [(False, 1), (True, 2)])
def test_lift_orthogonality_requires_directional_information(
    changing_direction: bool, rank: int
) -> None:
    velocities = np.array([[50.0, 0.0, 0.0], [45.0, 0.0, -5.0], [40.0, 0.0, -10.0]])
    if not changing_direction:
        velocities[:] = velocities[0]
    lift = np.cross(np.array([0.0, -200.0, 0.0]), velocities)
    assert np.linalg.matrix_rank(lift) == rank


def test_interframe_rotation_has_temporal_aliases() -> None:
    true = Rotation.from_rotvec([0.0, 0.0, 1.5 * np.pi])
    principal = true.as_rotvec()
    assert np.degrees(principal) == pytest.approx([0.0, 0.0, -90.0])
    assert true.as_matrix() == pytest.approx(Rotation.from_rotvec(principal).as_matrix())


def test_two_grooves_can_have_identical_images_and_different_normals() -> None:
    first = np.array([[0.0, -0.001, 1.0], [0.0, 0.001, 1.0]])
    second = np.array([[0.0, -0.000998, 0.998], [0.0, 0.001002, 1.002]])
    normals = []
    for points in [first, second]:
        points *= 0.002 / np.linalg.norm(points[1] - points[0])
        normal = np.cross([1.0, 0.0, 0.0], points[1] - points[0])
        normals.append(normal / np.linalg.norm(normal))
    assert first[:, 1] / first[:, 2] == pytest.approx(second[:, 1] / second[:, 2])
    assert np.linalg.norm(first[1] - first[0]) == pytest.approx(0.002)
    assert np.linalg.norm(second[1] - second[0]) == pytest.approx(0.002)
    angle = np.degrees(np.arccos(normals[0] @ normals[1]))
    assert angle == pytest.approx(63.4349488, abs=1e-7)


def test_reflection_normal_requires_both_ray_directions() -> None:
    to_light, to_camera = np.array([1.0, 0.0, 1.0]), np.array([-0.3, 0.2, 1.0])
    to_light /= np.linalg.norm(to_light)
    to_camera /= np.linalg.norm(to_camera)
    normal = to_light + to_camera
    normal /= np.linalg.norm(normal)
    incoming = -to_light
    reflected = incoming - 2 * np.dot(incoming, normal) * normal
    assert reflected == pytest.approx(to_camera)
    assert not np.allclose(normal, to_camera)


def test_inverse_launch_uncertainty_includes_weight_and_path() -> None:
    launch, path, weight = 0.5, -2.0, 0.76
    gradient = np.array([1 / weight, 1 - 1 / weight, -(launch - path) / weight**2])
    covariance = np.diag([0.1**2, 0.2**2, 0.03**2])
    sigma = np.sqrt(gradient @ covariance @ gradient)
    assert path + (launch - path) / weight == pytest.approx(1.2894736842)
    assert sigma == pytest.approx(0.1953518622)
    assert 0.85 / 0.76 == pytest.approx(1.1184210526)


def test_timing_error_rotates_a_face_normal() -> None:
    omega_z, interval = 30.0, 0.0001
    initial = np.array([1.0, 0.0, 0.0])
    final = Rotation.from_rotvec([0.0, 0.0, omega_z * interval]).apply(initial)
    azimuth = np.degrees(np.arctan2(final[1], final[0]))
    assert azimuth == pytest.approx(0.1718873385)


@pytest.mark.parametrize(
    "unsupported",
    [
        r"\exp\!\left(\int_{t_0}^{t_{\text{impact}}}",
        "roughly twice the sensitivity",
        "determines the face plane's orientation directly",
        "**Swing plane, rigorously defined** — the orientation and trajectory of the ISA",
    ],
)
def test_article_does_not_repeat_disproved_inference(unsupported: str) -> None:
    assert unsupported not in SOURCE.read_text(encoding="utf-8")
