"""Lie-group tangent chart transforms (#5186)."""

from __future__ import annotations

import unittest

import numpy as np

from src.tools.rotation_reference_examples import (
    euler_zyx_to_rotation,
    quaternion_to_rotation,
    rotation_to_euler_zyx,
    rotation_to_quaternion,
)
from src.tools.so3_tangent_transform import (
    ADJOINT_FD_DT,
    ADJOINT_FD_EPS,
    body_to_spatial_omega,
    chart_pushforward_matrix,
    numerical_jacobian,
    omega_evolution_jacobian_body,
    omega_evolution_jacobian_spatial,
    propagate_rotation_body,
)


def _random_rotation(rng: np.random.Generator) -> np.ndarray:
    axis = rng.normal(size=3)
    axis /= np.linalg.norm(axis)
    angle = float(rng.uniform(0.2, 2.4))
    return propagate_rotation_body(np.eye(3), axis * angle, 1.0)


def _normalize_quaternion(quaternion: np.ndarray) -> np.ndarray:
    return quaternion / np.linalg.norm(quaternion)


class TestLieGroupTangentTransform(unittest.TestCase):
    """SO(3) left/right and quaternion-to-Euler chart rules."""

    def test_chart_pushforward_matrix_identity(self) -> None:
        """Synthetic matrices satisfy A_y = (Tdot + T A_x) T^{-1}."""
        rng = np.random.default_rng(5188)
        linearisation_x = rng.normal(size=(3, 3))
        transform = rng.normal(size=(3, 3)) + np.eye(3) * 2.0
        transform_dot = rng.normal(size=(3, 3)) * 0.05
        expected = (transform_dot + transform @ linearisation_x) @ np.linalg.inv(transform)
        pushed = chart_pushforward_matrix(linearisation_x, transform, transform_dot)
        np.testing.assert_allclose(pushed, expected, rtol=0.0, atol=1e-12)

    def test_spatial_body_jacobian_matches_chart_pushforward(self) -> None:
        """Body/spatial rate Jacobians satisfy A_s = (T A_b) T^{-1} with T = R, Tdot = 0."""
        rng = np.random.default_rng(5186)
        dt = ADJOINT_FD_DT
        eps = ADJOINT_FD_EPS
        for _ in range(48):
            rotation = _random_rotation(rng)
            omega_body = rng.normal(size=3)
            omega_spatial = body_to_spatial_omega(rotation, omega_body)
            a_body = omega_evolution_jacobian_body(rotation, omega_body, dt, eps=eps)
            a_spatial = omega_evolution_jacobian_spatial(rotation, omega_spatial, dt, eps=eps)
            pushed = chart_pushforward_matrix(a_body, rotation, np.zeros((3, 3), dtype=np.float64))
            np.testing.assert_allclose(a_spatial, pushed, rtol=0.0, atol=1e-8)

    def test_euler_step_map_jacobian_nontrivial_with_quat_pushforward(self) -> None:
        """Euler-step linearisation is nontrivial; zero Tdot and A_x=I do not reproduce it."""
        rng = np.random.default_rng(5187)
        dt = 5.0e-2
        euler0 = rng.uniform(-0.35, 0.35, size=3)
        omega_body = np.array([0.4, -0.2, 0.15])
        rotation0 = euler_zyx_to_rotation(float(euler0[0]), float(euler0[1]), float(euler0[2]))
        quat0 = rotation_to_quaternion(rotation0)

        def euler_step(euler: np.ndarray) -> np.ndarray:
            yaw, pitch, roll = (float(euler[0]), float(euler[1]), float(euler[2]))
            rotation = euler_zyx_to_rotation(yaw, pitch, roll)
            rotation_next = propagate_rotation_body(rotation, omega_body, dt)
            return np.asarray(rotation_to_euler_zyx(rotation_next), dtype=float)

        a_euler = numerical_jacobian(euler_step, euler0, eps=1e-6)
        self.assertGreater(float(np.linalg.norm(a_euler - np.eye(3))), 1e-9)

        def euler_from_imaginary(imaginary: np.ndarray) -> np.ndarray:
            quaternion = _normalize_quaternion(quat0 + np.array([0.0, *imaginary]))
            return np.asarray(
                rotation_to_euler_zyx(quaternion_to_rotation(quaternion)), dtype=float
            )

        chart_jacobian = numerical_jacobian(euler_from_imaginary, np.zeros(3), eps=1e-7)
        vacuous_push = chart_pushforward_matrix(
            np.eye(3), chart_jacobian, np.zeros((3, 3), dtype=np.float64)
        )
        np.testing.assert_allclose(vacuous_push, np.eye(3), atol=1e-10)
        self.assertGreater(float(np.linalg.norm(a_euler - vacuous_push)), 1e-3)


if __name__ == "__main__":
    unittest.main()
