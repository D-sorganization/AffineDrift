"""Lie-group tangent chart transforms (#5186)."""

from __future__ import annotations

import unittest
from collections.abc import Callable

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
    omega_evolution_jacobian_body,
    omega_evolution_jacobian_spatial,
    propagate_rotation_body,
    so3_expm,
    so3_hat,
    so3_log,
)

Chart = Callable[[np.ndarray], np.ndarray]
RotFrom = Callable[[np.ndarray], np.ndarray]


def _random_rotation(rng: np.random.Generator) -> np.ndarray:
    axis = rng.normal(size=3)
    axis /= np.linalg.norm(axis)
    angle = float(rng.uniform(0.2, 2.4))
    return propagate_rotation_body(np.eye(3), axis * angle, 1.0)


def _central_jacobian(func: Chart, centre: np.ndarray, eps: float) -> np.ndarray:
    """Central-difference Jacobian of an R3 -> R3 map."""
    jac = np.zeros((3, 3))
    for axis in range(3):
        delta = np.eye(3)[axis] * eps
        jac[:, axis] = (func(centre + delta) - func(centre - delta)) / (2.0 * eps)
    return jac


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

    def test_spatial_body_rate_jacobian_is_adjoint_equivariant(self) -> None:
        """Rate-map Jacobians satisfy A_s = (R A_b) R^{-1} (T = R, Tdot = 0).

        This is the adjoint property of the one-step rate map only; the trajectory
        variational ``A`` with ``Tdot != 0`` is checked against the group flow in
        ``test_left_right_variational_a_from_group_flow_needs_tdot``.
        """
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

    def test_left_right_variational_a_from_group_flow_needs_tdot(self) -> None:
        """Body/spatial ``A`` from the real group flow obey ``(Tdot + T A_x) T^{-1}``.

        Constant body rate: ``R(t) = R0 exp(hat(w) t)``.  Perturb the attitude at ``t0``
        by ``exp(eps e_i)`` on the right (body chart) or left (spatial chart) and read
        the perturbation after the flow with ``so3_log``.  Analytically ``A_b = -hat(w)``
        and ``A_s = 0``; here both are measured by finite differences of the group
        operation, with ``T = R(t)`` and ``Tdot`` differenced from the same flow.
        """
        omega = np.array([0.8, -0.5, 0.6])
        rotation_t0 = propagate_rotation_body(np.eye(3), np.array([0.3, 0.9, -0.4]), 1.7)
        self.assertGreater(float(np.linalg.norm(rotation_t0 - np.eye(3))), 0.5)
        eps, half_step = 1.0e-5, 1.0e-3

        def reference(tau: float) -> np.ndarray:
            return np.asarray(rotation_t0 @ so3_expm(omega, tau), dtype=float)

        def variational(tau: float, chart: str) -> np.ndarray:
            """d xi(tau) / d xi(0) by central differences, ``xi`` in the given chart."""
            jac = np.zeros((3, 3))
            ref = reference(tau)
            for axis in range(3):
                outs = []
                for sign in (1.0, -1.0):
                    pert = so3_expm(np.eye(3)[axis], sign * eps)
                    if chart == "body":
                        flowed = rotation_t0 @ pert @ so3_expm(omega, tau)
                        outs.append(so3_log(ref.T @ flowed))
                    else:
                        flowed = pert @ rotation_t0 @ so3_expm(omega, tau)
                        outs.append(so3_log(flowed @ ref.T))
                jac[:, axis] = (outs[0] - outs[1]) / (2.0 * eps)
            return jac

        def a_from_flow(chart: str) -> np.ndarray:
            plus, minus = variational(half_step, chart), variational(-half_step, chart)
            return np.asarray((plus - minus) / (2.0 * half_step))

        a_body, a_spatial = a_from_flow("body"), a_from_flow("spatial")
        t_dot = (reference(half_step) - reference(-half_step)) / (2.0 * half_step)
        np.testing.assert_allclose(a_body, -so3_hat(omega), atol=1e-5)
        np.testing.assert_allclose(a_spatial, np.zeros((3, 3)), atol=1e-5)
        pushed = chart_pushforward_matrix(a_body, rotation_t0, t_dot)
        np.testing.assert_allclose(pushed, a_spatial, atol=1e-5)
        # Non-vacuity: dropping Tdot, flipping its sign, or using T^T all miss badly.
        for wrong in (
            chart_pushforward_matrix(a_body, rotation_t0, np.zeros((3, 3))),
            chart_pushforward_matrix(a_body, rotation_t0, -t_dot),
            chart_pushforward_matrix(a_body, rotation_t0.T, t_dot.T),
        ):
            self.assertGreater(float(np.linalg.norm(wrong - a_spatial)), 0.3)

    def test_quaternion_to_euler_chart_change_matches_rule(self) -> None:
        """``A_euler = (Tdot + T A_quat) T^{-1}`` with every term measured from the flow.

        ``A_quat``/``A_euler`` are time-derivatives of the variational flow matrices of
        ``R(t) = R0 exp(hat(w) t)`` in each chart (vector-part quaternion, ZYX Euler),
        and ``T(t) = D(euler o quat^{-1})`` is differenced in the same way.  The attitude
        is far from identity and the pitch is away from gimbal lock.
        """
        omega = np.array([0.8, -0.5, 0.6])
        rotation_t0 = euler_zyx_to_rotation(0.7, 0.4, -0.5)
        eps, half_step = 1.0e-5, 1.0e-3

        def quat_chart(rot: np.ndarray) -> np.ndarray:
            return np.asarray(rotation_to_quaternion(rot)[1:], dtype=float)

        def rot_from_quat(vec: np.ndarray) -> np.ndarray:
            return np.asarray(
                quaternion_to_rotation(np.array([np.sqrt(1.0 - vec @ vec), *vec])), dtype=float
            )

        def euler_chart(rot: np.ndarray) -> np.ndarray:
            return np.asarray(rotation_to_euler_zyx(rot), dtype=float)

        def rot_from_euler(angles: np.ndarray) -> np.ndarray:
            return np.asarray(
                euler_zyx_to_rotation(float(angles[0]), float(angles[1]), float(angles[2])),
                dtype=float,
            )

        def rate(chart: Chart, rot_from: RotFrom) -> np.ndarray:
            centre = chart(rotation_t0)

            def phi(tau: float) -> np.ndarray:
                return _central_jacobian(
                    lambda x: chart(rot_from(x) @ so3_expm(omega, tau)), centre, eps
                )

            return np.asarray((phi(half_step) - phi(-half_step)) / (2.0 * half_step))

        def transform(tau: float) -> np.ndarray:
            """T(tau) = d euler / d quat at the reference attitude R(t0 + tau)."""
            centre = quat_chart(rotation_t0 @ so3_expm(omega, tau))
            return _central_jacobian(lambda x: euler_chart(rot_from_quat(x)), centre, eps)

        a_quat = rate(quat_chart, rot_from_quat)
        a_euler = rate(euler_chart, rot_from_euler)
        t_mat = transform(0.0)
        t_dot = (transform(half_step) - transform(-half_step)) / (2.0 * half_step)
        pushed = chart_pushforward_matrix(a_quat, t_mat, t_dot)
        np.testing.assert_allclose(pushed, a_euler, atol=2e-5)
        # Non-vacuity: Tdot, the linearisation, and the transform sign all matter.
        self.assertGreater(float(np.linalg.norm(t_dot @ np.linalg.inv(t_mat))), 0.1)
        for wrong in (
            chart_pushforward_matrix(a_quat, t_mat, np.zeros((3, 3))),
            chart_pushforward_matrix(np.eye(3), t_mat, t_dot),
            chart_pushforward_matrix(a_quat, t_mat, -t_dot),
            chart_pushforward_matrix(a_quat, -t_mat, t_dot),
        ):
            self.assertGreater(float(np.linalg.norm(wrong - a_euler)), 0.1)


class TestSo3ExpLog(unittest.TestCase):
    """so3_log is the principal inverse of so3_expm with DbC input validation."""

    def test_round_trip_log_exp_across_angle_regimes(self) -> None:
        rng = np.random.default_rng(5190)
        angles = [1e-9, 1e-7, 1e-4, 0.3, 1.2, np.pi / 2 - 1e-9, np.pi / 2 + 1e-9]
        angles += [2.5, np.pi - 1e-3, np.pi - 1e-6, np.pi - 1e-9]
        for angle in angles:
            for _ in range(8):
                axis = rng.normal(size=3)
                axis /= np.linalg.norm(axis)
                omega = axis * angle
                recovered = so3_log(so3_expm(omega, 1.0))
                np.testing.assert_allclose(recovered, omega, rtol=0.0, atol=1e-8)

    def test_exp_log_exp_is_identity_at_and_near_pi(self) -> None:
        rng = np.random.default_rng(5191)
        axes = [np.eye(3)[k] for k in range(3)] + [-np.eye(3)[0], np.ones(3) / np.sqrt(3.0)]
        axes += [v / np.linalg.norm(v) for v in rng.normal(size=(5, 3))]
        for axis in axes:
            for angle in (np.pi, np.pi - 1e-12):
                rotation = so3_expm(axis * angle, 1.0)
                omega = so3_log(rotation)
                self.assertAlmostEqual(float(np.linalg.norm(omega)), angle, places=7)
                np.testing.assert_allclose(so3_expm(omega, 1.0), rotation, atol=1e-9)

    def test_log_is_principal_branch(self) -> None:
        omega = np.array([0.0, 0.0, 1.0]) * (np.pi + 0.5)
        recovered = so3_log(so3_expm(omega, 1.0))
        np.testing.assert_allclose(recovered, np.array([0.0, 0.0, -(np.pi - 0.5)]), atol=1e-12)

    def test_log_rejects_invalid_rotations(self) -> None:
        good = so3_expm(np.array([0.2, 0.1, -0.3]), 1.0)
        bad_inputs = [
            np.eye(2),
            np.zeros(9),
            good * 1.001,
            np.diag([1.0, 1.0, -1.0]),  # orthogonal, det -1
            np.where(np.eye(3) > 0, np.nan, 0.0),
        ]
        for matrix in bad_inputs:
            with self.assertRaises(ValueError):
                so3_log(matrix)


if __name__ == "__main__":
    unittest.main()
