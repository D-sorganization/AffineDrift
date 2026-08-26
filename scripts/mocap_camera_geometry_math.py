"""Small, dependency-free equations for camera-geometry teaching fixtures."""

from __future__ import annotations

import math

Vector = tuple[float, ...]
Matrix3 = tuple[Vector, Vector, Vector]


def _matvec(matrix: Matrix3, vector: Vector) -> Vector:
    """Return a three-by-three matrix times a three-vector."""

    return tuple(sum(row[index] * vector[index] for index in range(3)) for row in matrix)


def distort_brown_conrady(point: tuple[float, float], coefficients: Vector) -> tuple[float, float]:
    """Apply the five-parameter Brown-Conrady distortion convention."""

    x_value, y_value = point
    k1, k2, p1, p2, k3 = coefficients
    radius2 = x_value * x_value + y_value * y_value
    radial = 1.0 + k1 * radius2 + k2 * radius2**2 + k3 * radius2**3
    x_tangent = 2.0 * p1 * x_value * y_value + p2 * (radius2 + 2.0 * x_value**2)
    y_tangent = p1 * (radius2 + 2.0 * y_value**2) + 2.0 * p2 * x_value * y_value
    return x_value * radial + x_tangent, y_value * radial + y_tangent


def pixel_from_normalized(
    normalized: tuple[float, float], intrinsic: Matrix3
) -> tuple[float, float]:
    """Apply an upper-triangular intrinsic matrix to a normalized point."""

    x_value, y_value = normalized
    return (
        intrinsic[0][0] * x_value + intrinsic[0][1] * y_value + intrinsic[0][2],
        intrinsic[1][0] * x_value + intrinsic[1][1] * y_value + intrinsic[1][2],
    )


def project_point(
    intrinsic: Matrix3,
    distortion: Vector,
    rotation: Matrix3,
    translation: Vector,
    world_point: Vector,
) -> tuple[float, float]:
    """Project a world point using the fixture's world-to-camera convention."""

    rotated = _matvec(rotation, world_point)
    camera_point = tuple(rotated[index] + translation[index] for index in range(3))
    if camera_point[2] <= 0.0:
        raise ValueError("projection requires positive camera-frame depth")
    normalized = (camera_point[0] / camera_point[2], camera_point[1] / camera_point[2])
    return pixel_from_normalized(distort_brown_conrady(normalized, distortion), intrinsic)


def rectified_stereo_depth_uncertainty(
    focal_length_px: float,
    baseline_m: float,
    disparity_px: float,
    independent_pixel_sigma_px: float,
) -> tuple[float, float]:
    """Return depth and first-order sigma for independent equal pixel errors."""

    depth = focal_length_px * baseline_m / disparity_px
    sigma = (
        math.sqrt(2.0)
        * independent_pixel_sigma_px
        * depth**2
        / (focal_length_px * baseline_m)
    )
    return depth, sigma


def euclidean_distance(first: Vector, second: Vector) -> float:
    """Return Euclidean distance between equal-length vectors."""

    return math.sqrt(sum((second[index] - first[index]) ** 2 for index in range(len(first))))
