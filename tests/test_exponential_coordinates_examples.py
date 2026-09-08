"""Independent matrix, velocity and branch checks for the exponential chapter."""

import importlib
from typing import Any

import numpy as np
import pytest
from scipy.integrate import quad_vec
from scipy.linalg import expm
from scipy.spatial.transform import Rotation


@pytest.fixture(scope="module")
def example() -> Any:
    """Collect the contracts before importing the implementation."""
    return importlib.import_module("src.tools.exponential_coordinates_examples")


def generator(twist: np.ndarray) -> np.ndarray:
    """Build the homogeneous generator directly, independent of source helpers."""
    angular_x, angular_y, angular_z = twist[:3]
    matrix = np.zeros((4, 4))
    matrix[:3, :3] = [
        [0, -angular_z, angular_y],
        [angular_z, 0, -angular_x],
        [-angular_y, angular_x, 0],
    ]
    matrix[:3, 3] = twist[3:]
    return matrix


@pytest.mark.parametrize("time", [0.0, -0.3, 1.0, 2.7])
@pytest.mark.parametrize("angular", [[0, 0, 0], [0, 0, 1], [0.3, -1.4, 2.1], [1e-9, 0, 0]])
def test_se3_exp_matches_independent_matrix_exponential(
    example: Any, time: float, angular: list[float]
) -> None:
    """Nonunit axes, elapsed time and pure translation must retain their units."""
    twist = np.r_[angular, [1.0, -0.2, 0.7]]
    expected = expm(time * generator(twist))
    np.testing.assert_allclose(example.se3_exp(time * twist), expected, atol=3e-14)


@pytest.mark.parametrize("angle", [0.0, 1e-12, 1e-6, 0.01, 1.3, np.pi - 1e-5, np.pi, np.pi + 1e-5])
def test_log_reconstructs_pose_without_snapping_near_half_turn(example: Any, angle: float) -> None:
    """A principal rotation branch can flip while the recovered pose stays exact."""
    twist = np.r_[angle * np.array([1, 2, 3]) / np.sqrt(14), [0.7, -0.4, 0.1]]
    expected = expm(generator(twist))
    recovered = example.se3_log(expected)
    np.testing.assert_allclose(expm(generator(recovered)), expected, atol=2e-14)
    if angle < np.pi:
        np.testing.assert_allclose(recovered, twist, atol=2e-14)
    assert np.linalg.norm(recovered[:3]) <= np.pi + 1e-14


@pytest.mark.parametrize("angle", [0.0, 1e-7, 0.4, np.pi, 2 * np.pi])
def test_left_jacobian_matches_integrated_rotation_and_singular_values(
    example: Any, angle: float
) -> None:
    """Quadrature verifies translation coupling without repeating its closed form."""
    rotvec = angle * np.array([1, -2, 3]) / np.sqrt(14)
    integral, _ = quad_vec(lambda scale: Rotation.from_rotvec(scale * rotvec).as_matrix(), 0, 1)
    actual = example.left_jacobian(rotvec)
    np.testing.assert_allclose(actual, integral, atol=2e-14)
    scale = abs(np.sinc(angle / (2 * np.pi)))
    np.testing.assert_allclose(
        np.linalg.svd(actual, compute_uv=False), [1, scale, scale], atol=2e-14
    )


def test_coordinate_rate_requires_left_or_right_jacobian(example: Any) -> None:
    """Finite differences of R distinguish coordinate rates from physical spin."""
    rotvec, rate = np.array([0.3, -0.8, 1.1]), np.array([0.7, 0.2, -0.1])
    step = 1e-6
    rotation = Rotation.from_rotvec(rotvec).as_matrix()
    derivative = (
        Rotation.from_rotvec(rotvec + step * rate).as_matrix()
        - Rotation.from_rotvec(rotvec - step * rate).as_matrix()
    ) / (2 * step)
    spatial = derivative @ rotation.T
    body = rotation.T @ derivative
    np.testing.assert_allclose(
        example.left_jacobian(rotvec) @ rate, spatial[[2, 0, 1], [1, 2, 0]], atol=2e-10
    )
    np.testing.assert_allclose(
        example.left_jacobian(-rotvec) @ rate, body[[2, 0, 1], [1, 2, 0]], atol=2e-10
    )
    assert np.linalg.norm(example.left_jacobian(rotvec) @ rate - rate) > 0.3


def test_published_offset_axis_example(example: Any) -> None:
    """Perpendicular linear velocity generates a circular translation, not a helix."""
    twist = np.array([0, 0, 1, 1, 0, 0], dtype=float)
    pose = example.se3_exp(twist)
    np.testing.assert_allclose(pose[:3, 3], [np.sin(1), 1 - np.cos(1), 0], atol=1e-15)
    np.testing.assert_allclose(example.se3_log(pose), twist, atol=1e-15)


@pytest.mark.parametrize(
    "bad", [np.zeros(3), np.zeros((6, 1)), np.full(6, np.nan), np.full(6, np.inf)]
)
def test_exp_rejects_invalid_coordinates(example: Any, bad: np.ndarray) -> None:
    """Malformed vectors must fail at the public boundary."""
    with pytest.raises(ValueError):
        example.se3_exp(bad)


@pytest.mark.parametrize("bad", [np.zeros(4), np.zeros((3, 1)), np.full(3, np.nan)])
def test_jacobian_rejects_invalid_coordinates(example: Any, bad: np.ndarray) -> None:
    """The differential accepts one finite rotation vector."""
    with pytest.raises(ValueError):
        example.left_jacobian(bad)


@pytest.mark.parametrize(
    "bad",
    [
        np.zeros((3, 3)),
        np.full((4, 4), np.nan),
        np.diag([-1.0, 1.0, 1.0, 1.0]),
        np.diag([1.0, 1.0, 1.0, 2.0]),
        np.diag([1.0, 1.0, 1.01, 1.0]),
    ],
)
def test_log_rejects_invalid_pose_instead_of_silently_projecting(
    example: Any, bad: np.ndarray
) -> None:
    """SciPy's optional nearest-rotation behavior must not hide invalid input."""
    with pytest.raises(ValueError):
        example.se3_log(bad)
