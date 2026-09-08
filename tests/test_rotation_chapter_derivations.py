"""Independently verify frame, rate and task examples from the rotation chapter."""

import math

import numpy as np
import pytest
from scipy.spatial.transform import Rotation


def _hat(vector: np.ndarray) -> np.ndarray:
    """Construct the cross-product operator from its action on basis vectors."""
    return np.column_stack([np.cross(vector, basis) for basis in np.eye(3)])


def test_zyx_example_and_spatial_rate_columns() -> None:
    """Differentiate independently constructed rotations, retaining rate ordering."""
    angles = np.deg2rad([45.0, 30.0, 60.0])
    matrix = Rotation.from_euler("ZYX", angles[::-1]).as_matrix()
    np.testing.assert_allclose(
        matrix,
        [[0.433013, -0.435596, 0.789149], [0.75, 0.659740, -0.047367], [-0.5, 0.612372, 0.612372]],
        atol=5e-7,
        rtol=0,
    )
    _, pitch, yaw = angles
    expected = np.array(
        [
            [np.cos(yaw) * np.cos(pitch), -np.sin(yaw), 0],
            [np.sin(yaw) * np.cos(pitch), np.cos(yaw), 0],
            [-np.sin(pitch), 0, 1],
        ]
    )
    step = 1e-6
    for column in range(3):
        change = np.eye(3)[column] * step
        plus = Rotation.from_euler("ZYX", (angles + change)[::-1]).as_matrix()
        minus = Rotation.from_euler("ZYX", (angles - change)[::-1]).as_matrix()
        spatial = ((plus - minus) / (2 * step)) @ matrix.T
        np.testing.assert_allclose(spatial, _hat(expected[:, column]), atol=1e-9)


def test_euler_inverse_conditioning_without_forward_blowup() -> None:
    pitch = np.deg2rad(89.0)
    jacobian = np.array([[np.cos(pitch), 0, 0], [0, 1, 0], [-np.sin(pitch), 0, 1]])
    assert np.linalg.cond(jacobian) == pytest.approx(114.5886501293)
    assert np.linalg.norm(jacobian, ord=2) < math.sqrt(2)
    singular = np.array([[0, 0, 0], [0, 1, 0], [-1, 0, 1]])
    np.testing.assert_array_equal(singular @ [1, 0, 1], np.zeros(3))
    assert np.linalg.matrix_rank(singular) == 2


@pytest.mark.parametrize("angle", [0.7, math.pi, 2 * math.pi])
def test_exponential_differential_distinguishes_pi_from_two_pi(angle: float) -> None:
    """Finite-difference the exponential instead of differentiating its closed form."""
    vector = np.array([angle, 0.0, 0.0])
    base = Rotation.from_rotvec(vector).as_matrix()
    columns = []
    step = 1e-6
    for basis in np.eye(3):
        plus = Rotation.from_rotvec(vector + step * basis).as_matrix()
        minus = Rotation.from_rotvec(vector - step * basis).as_matrix()
        tangent = ((plus - minus) / (2 * step)) @ base.T
        columns.append([tangent[2, 1], tangent[0, 2], tangent[1, 0]])
    singular_values = np.linalg.svd(np.array(columns).T, compute_uv=False)
    expected = [1.0, 2 * abs(math.sin(angle / 2)) / angle, 2 * abs(math.sin(angle / 2)) / angle]
    np.testing.assert_allclose(singular_values, expected, atol=2e-9, rtol=0)


def test_body_and_spatial_rates_have_distinct_components() -> None:
    time, step = 0.4, 1e-6
    fixed = Rotation.from_rotvec([math.pi / 2, 0, 0]).as_matrix()
    matrix = Rotation.from_rotvec([0, 0, time]).as_matrix() @ fixed
    plus = Rotation.from_rotvec([0, 0, time + step]).as_matrix() @ fixed
    minus = Rotation.from_rotvec([0, 0, time - step]).as_matrix() @ fixed
    derivative = (plus - minus) / (2 * step)
    np.testing.assert_allclose(derivative @ matrix.T, _hat(np.array([0, 0, 1])), atol=1e-9)
    np.testing.assert_allclose(matrix.T @ derivative, _hat(np.array([0, 1, 0])), atol=1e-9)


def test_orientation_task_null_direction_and_point_sensitivity() -> None:
    angle = 1e-6
    rotation = Rotation.from_rotvec([0, 0, angle]).as_matrix()
    normal, point = np.array([0, 0, 1]), np.array([1, 0, 0])
    np.testing.assert_array_equal(rotation @ normal, normal)
    np.testing.assert_allclose((rotation @ point - point) / angle, [0, 1, 0], atol=1e-6)
    covariance = _hat(normal) @ _hat(normal).T
    np.testing.assert_array_equal(covariance, np.diag([1, 1, 0]))


def test_timestamp_shift_is_not_a_control_error_measurement() -> None:
    normal = np.array([1.0, 0.0, 0.0])
    shifted = Rotation.from_rotvec([0, 0, 10 * 0.001]).apply(normal)
    first_order = np.array([0.0, 0.01, 0.0])
    assert np.linalg.norm(shifted - normal - first_order) < 0.000051
