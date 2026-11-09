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


class TestLieGroupTangentTransform(unittest.TestCase):
    """SO(3) left/right and quaternion-to-Euler chart rules."""

    def test_left_right_trivialised_A_related_by_adjoint(self) -> None:
        """Left and right numerically linearised A matrices satisfy A_s = R A_b R^T."""
        rng = np.random.default_rng(5186)
        dt = ADJOINT_FD_DT
        eps = ADJOINT_FD_EPS
        for _ in range(48):
            rotation = _random_rotation(rng)
            omega_body = rng.normal(size=3)
            omega_spatial = body_to_spatial_omega(rotation, omega_body)
            a_body = omega_evolution_jacobian_body(rotation, omega_body, dt, eps=eps)
            a_spatial = omega_evolution_jacobian_spatial(rotation, omega_spatial, dt, eps=eps)
            adjoint_push = rotation @ a_body @ rotation.T
            np.testing.assert_allclose(a_spatial, adjoint_push, rtol=0.0, atol=1e-8)

    def test_quaternion_to_euler_chart_change_matches_rule(self) -> None:
        """Euler linearisation agrees with pushforward through quaternion chart Jacobian."""
        rng = np.random.default_rng(5187)
        dt = 1e-5
        euler0 = rng.uniform(-0.35, 0.35, size=3)
        omega_body = np.array([0.4, -0.2, 0.15])
        linearisation_identity = np.eye(3)

        def euler_step(euler: np.ndarray) -> np.ndarray:
            yaw, pitch, roll = (float(euler[0]), float(euler[1]), float(euler[2]))
            rotation = euler_zyx_to_rotation(yaw, pitch, roll)
            rotation_next = propagate_rotation_body(rotation, omega_body, dt)
            return np.asarray(rotation_to_euler_zyx(rotation_next), dtype=float)

        a_euler = numerical_jacobian(euler_step, euler0, eps=1e-7)

        rotation = euler_zyx_to_rotation(float(euler0[0]), float(euler0[1]), float(euler0[2]))
        quat = rotation_to_quaternion(rotation)

        def euler_from_imaginary_quat(perturbation: np.ndarray) -> np.ndarray:
            q_next = quat + np.array([0.0, *perturbation])
            q_next /= np.linalg.norm(q_next)
            return np.asarray(rotation_to_euler_zyx(quaternion_to_rotation(q_next)), dtype=float)

        chart_jacobian = numerical_jacobian(euler_from_imaginary_quat, np.zeros(3), eps=1e-7)
        pushed = chart_pushforward_matrix(linearisation_identity, chart_jacobian, np.zeros((3, 3)))
        np.testing.assert_allclose(a_euler, pushed, atol=2e-4)


if __name__ == "__main__":
    unittest.main()
