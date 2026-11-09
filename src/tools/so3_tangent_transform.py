"""SO(3) chart-change rules for tangent linearisations (#5186)."""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

import numpy as np
from numpy.typing import NDArray

type Vec3 = NDArray[np.float64]
type Mat3 = NDArray[np.float64]

# Finite-difference knobs tuned for adjoint checks on random SO(3) samples (#5186).
ADJOINT_FD_DT = 4.0e-3
ADJOINT_FD_EPS = 1.0e-5


def so3_hat(omega: Vec3) -> Mat3:
    """Map R3 to so(3)."""
    x, y, z = (float(omega[0]), float(omega[1]), float(omega[2]))
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]], dtype=np.float64)


def so3_vee(matrix: Mat3) -> Vec3:
    """Map so(3) to R3."""
    return (
        np.array(
            [matrix[2, 1] - matrix[1, 2], matrix[0, 2] - matrix[2, 0], matrix[1, 0] - matrix[0, 1]]
        )
        / 2.0
    )


def so3_expm(omega: Vec3, dt: float) -> Mat3:
    """Rodrigues exponential for incremental rotation ``exp(hat(omega) dt)``."""
    angle = float(np.linalg.norm(omega) * dt)
    if angle < 1e-12:
        return np.eye(3, dtype=np.float64) + so3_hat(omega) * dt
    axis = omega / np.linalg.norm(omega)
    hat = so3_hat(axis)
    return cast(
        Mat3,
        np.eye(3, dtype=np.float64) + np.sin(angle) * hat + (1.0 - np.cos(angle)) * (hat @ hat),
    )


def propagate_rotation_body(rotation: Mat3, omega_body: Vec3, dt: float) -> Mat3:
    """Advance rotation with body-fixed angular velocity."""
    if dt <= 0.0:
        raise ValueError("dt must be positive")
    return rotation @ so3_expm(omega_body, dt)


def propagate_rotation_spatial(rotation: Mat3, omega_spatial: Vec3, dt: float) -> Mat3:
    """Advance rotation with spatial angular velocity."""
    if dt <= 0.0:
        raise ValueError("dt must be positive")
    return so3_expm(omega_spatial, dt) @ rotation


def numerical_jacobian(
    func: Callable[[Vec3], Vec3],
    point: Vec3,
    eps: float = 1e-7,
) -> Mat3:
    """Central-difference Jacobian for a map R3 -> R3."""
    jac = np.zeros((3, 3), dtype=np.float64)
    base = np.asarray(func(point), dtype=np.float64).reshape(3)
    for axis in range(3):
        step = np.zeros(3, dtype=np.float64)
        step[axis] = eps
        forward = np.asarray(func(point + step), dtype=np.float64).reshape(3)
        backward = np.asarray(func(point - step), dtype=np.float64).reshape(3)
        jac[:, axis] = (forward - backward) / (2.0 * eps)
    _ = base  # anchor evaluation for deterministic call pattern
    return jac


def chart_pushforward_matrix(
    linearisation_x: Mat3,
    transform: Mat3,
    transform_dot: Mat3,
) -> Mat3:
    """Return A_y = (Tdot + T A_x) T^{-1} from the coordinate-change rule."""
    transform_inv = np.linalg.inv(transform)
    return cast(Mat3, (transform_dot + transform @ linearisation_x) @ transform_inv)


def body_to_spatial_omega(rotation: Mat3, omega_body: Vec3) -> Vec3:
    """Map body-frame angular velocity to spatial coordinates."""
    return rotation @ omega_body


def omega_evolution_jacobian_body(
    rotation: Mat3,
    omega_body: Vec3,
    dt: float,
    eps: float = 1e-7,
) -> Mat3:
    """Finite-difference Jacobian d omega_body^+ / d omega_body for one body step."""

    def step(omega: Vec3) -> Vec3:
        """One body-frame integration step mapped back to body angular rate."""
        rotation_next = propagate_rotation_body(rotation, omega, dt)
        return so3_vee(rotation.T @ rotation_next) / dt

    return numerical_jacobian(step, omega_body, eps=eps)


def omega_evolution_jacobian_spatial(
    rotation: Mat3,
    omega_spatial: Vec3,
    dt: float,
    eps: float = 1e-7,
) -> Mat3:
    """Finite-difference Jacobian d omega_spatial^+ / d omega_spatial for one spatial step."""

    def step(omega: Vec3) -> Vec3:
        """One spatial integration step mapped back to spatial angular rate."""
        rotation_next = propagate_rotation_spatial(rotation, omega, dt)
        return so3_vee(rotation_next @ rotation.T) / dt

    return numerical_jacobian(step, omega_spatial, eps=eps)
