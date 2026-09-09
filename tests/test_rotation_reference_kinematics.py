"""Independently check the reference's rate, frame and delivery derivations."""

import numpy as np
import pytest
from scipy.spatial.transform import Rotation


def _hat(vector: np.ndarray) -> np.ndarray:
    """Construct a cross-product operator from its action on basis vectors."""
    return np.column_stack([np.cross(vector, axis) for axis in np.eye(3)])


def test_ordered_rotation_example() -> None:
    x_rotation = Rotation.from_euler("x", np.pi / 2).as_matrix()
    z_rotation = Rotation.from_euler("z", np.pi / 2).as_matrix()
    np.testing.assert_allclose(z_rotation @ x_rotation @ [0, 1, 0], [0, 0, 1], atol=1e-15)
    np.testing.assert_allclose(x_rotation @ z_rotation @ [0, 1, 0], [-1, 0, 0], atol=1e-15)


@pytest.mark.parametrize("angles", [[0.4, 0.7, -0.6], [np.pi / 2, 0, 0]])
def test_spatial_euler_rate_columns(angles: list[float]) -> None:
    yaw, pitch, _ = angles
    columns = np.array(
        [
            [0, -np.sin(yaw), np.cos(yaw) * np.cos(pitch)],
            [0, np.cos(yaw), np.sin(yaw) * np.cos(pitch)],
            [1, 0, -np.sin(pitch)],
        ]
    )
    rates = np.array([0.2, -0.3, 1.1])
    step = 1e-6
    matrix = Rotation.from_euler("ZYX", angles).as_matrix()
    plus = Rotation.from_euler("ZYX", np.asarray(angles) + step * rates).as_matrix()
    minus = Rotation.from_euler("ZYX", np.asarray(angles) - step * rates).as_matrix()
    np.testing.assert_allclose(
        (plus - minus) @ matrix.T / (2 * step), _hat(columns @ rates), atol=2e-10
    )


def test_rotation_vector_left_jacobian_is_not_identity() -> None:
    vector = np.array([0.4, -0.7, 0.9])
    rate = np.array([-0.5, 0.3, 0.2])
    angle = np.linalg.norm(vector)
    skew = _hat(vector)
    jacobian = (
        np.eye(3)
        + (1 - np.cos(angle)) / angle**2 * skew
        + (angle - np.sin(angle)) / angle**3 * skew @ skew
    )
    step = 1e-6
    matrix = Rotation.from_rotvec(vector).as_matrix()
    plus = Rotation.from_rotvec(vector + step * rate).as_matrix()
    minus = Rotation.from_rotvec(vector - step * rate).as_matrix()
    np.testing.assert_allclose(
        (plus - minus) @ matrix.T / (2 * step), _hat(jacobian @ rate), atol=2e-10
    )
    assert np.linalg.norm(jacobian @ rate - rate) > 0.1


def test_relative_angular_velocity_and_world_frame_cancellation() -> None:
    first = Rotation.from_rotvec([0.2, -0.3, 0.4]).as_matrix()
    second = Rotation.from_rotvec([-0.5, 0.1, 0.7]).as_matrix()
    common = Rotation.from_rotvec([0.8, 0.4, -0.2]).as_matrix()
    np.testing.assert_allclose((common @ first).T @ (common @ second), first.T @ second)
    first_rate, second_rate = np.array([0.2, 0.5, -0.6]), np.array([-0.1, 0.2, 0.8])
    relative = first.T @ second
    derivative = -first.T @ _hat(first_rate) @ second + first.T @ _hat(second_rate) @ second
    np.testing.assert_allclose(
        relative.T @ derivative, _hat(second.T @ (second_rate - first_rate)), atol=1e-14
    )


def test_face_normal_linearization_and_covariance() -> None:
    normal = np.array([1.0, -2.0, 3.0]) / np.sqrt(14)
    perturbation = np.array([0.4, 0.1, -0.2])
    step = 1e-6
    perturbed = Rotation.from_rotvec(step * perturbation).apply(normal)
    np.testing.assert_allclose((perturbed - normal) / step, -_hat(normal) @ perturbation, atol=2e-7)
    np.testing.assert_allclose(np.cross(2.5 * normal, normal), 0, atol=1e-15)
    covariance = np.diag([0.01, 0.02, 0.03])
    output = _hat(normal) @ covariance @ _hat(normal).T
    np.testing.assert_allclose(output @ normal, 0, atol=1e-16)
    assert np.min(np.linalg.eigvalsh(output)) > -1e-16
