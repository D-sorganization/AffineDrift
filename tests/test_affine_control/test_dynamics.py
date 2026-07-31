"""Property tests for the dynamics reference implementation.

Each test corresponds to a claim the textbooks make, and to a defect the
2026-07-31 content review found in the published text. They are written as
property checks against an independent computation -- classical Newton-Euler, a
KKT solve, a symbolic identity -- rather than against a restatement of the same
formula, since restating a formula cannot catch a sign error in it.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.affine_control.dynamics import (
    constrained_affine_fields,
    double_pendulum_coriolis,
    double_pendulum_mass_matrix,
    force_cross,
    motion_cross,
    skew,
    spatial_inertia,
    spatial_newton_euler,
)

RNG = np.random.default_rng(20260731)


def newton_euler_about_origin(mass, com, inertia_com, omega, v_o, omega_dot, a_o):
    """Classical Newton-Euler about the origin. Independent ground truth.

    The term that is easy to drop: a spatial acceleration is not a classical
    acceleration. The classical acceleration of the body-fixed point at the
    origin is ``a_O + omega x v_O``.
    """
    a_o_classical = a_o + np.cross(omega, v_o)
    a_com = a_o_classical + np.cross(omega_dot, com) + np.cross(omega, np.cross(omega, com))
    force = mass * a_com
    moment_com = inertia_com @ omega_dot + np.cross(omega, inertia_com @ omega)
    return np.concatenate([moment_com + np.cross(com, force), force])


class TestSkew:
    def test_reproduces_the_cross_product(self):
        a, b = RNG.normal(size=3), RNG.normal(size=3)
        assert np.allclose(skew(a) @ b, np.cross(a, b))

    def test_is_antisymmetric(self):
        a = RNG.normal(size=3)
        assert np.allclose(skew(a).T, -skew(a))


class TestSpatialInertia:
    def test_is_symmetric_positive_definite(self):
        """The property the published worked example violated."""
        inertia = spatial_inertia(2.0, np.array([0.3, 0.0, 0.0]), np.diag([0.05, 0.05, 0.01]))
        assert np.allclose(inertia, inertia.T)
        assert (np.linalg.eigvalsh(inertia) > 0).all()

    def test_parallel_axis_matches_the_classical_theorem(self):
        """Offset d along x: unchanged about x, gains m d^2 about y and z."""
        mass, d = 2.0, 0.3
        inertia_com = np.diag([0.05, 0.05, 0.01])
        block = spatial_inertia(mass, np.array([d, 0.0, 0.0]), inertia_com)[:3, :3]
        assert block[0, 0] == pytest.approx(0.05)
        assert block[1, 1] == pytest.approx(0.05 + mass * d**2)
        assert block[2, 2] == pytest.approx(0.01 + mass * d**2)

    def test_published_example_values(self):
        """Guards the corrected ch08 numbers against regression."""
        block = spatial_inertia(2.0, np.array([0.3, 0.0, 0.0]), np.diag([0.05, 0.05, 0.01]))
        assert np.allclose(np.diag(block)[:3], [0.05, 0.23, 0.19])

    def test_zero_offset_reduces_to_the_com_inertia(self):
        inertia_com = np.diag([0.05, 0.05, 0.01])
        block = spatial_inertia(3.0, np.zeros(3), inertia_com)
        assert np.allclose(block[:3, :3], inertia_com)
        assert np.allclose(block[:3, 3:], 0.0)

    def test_rejects_non_positive_mass(self):
        with pytest.raises(ValueError, match="mass must be positive"):
            spatial_inertia(0.0, np.zeros(3), np.eye(3))


class TestSpatialCrossProducts:
    def test_force_cross_is_negative_transpose_of_motion_cross(self):
        v = RNG.normal(size=6)
        assert np.allclose(force_cross(v), -motion_cross(v).T)

    def test_motion_cross_reproduces_the_screw_cross_product(self):
        v, w = RNG.normal(size=6), RNG.normal(size=6)
        expected = np.concatenate(
            [
                np.cross(v[:3], w[:3]),
                np.cross(v[:3], w[3:]) + np.cross(v[3:], w[:3]),
            ]
        )
        assert np.allclose(motion_cross(v) @ w, expected)


class TestSpatialNewtonEuler:
    def test_matches_classical_newton_euler(self):
        """The bias term is ADDED. The published text subtracted it."""
        mass = 2.7
        com = np.array([0.11, -0.05, 0.23])
        inertia_com = np.diag([0.031, 0.044, 0.019])
        inertia = spatial_inertia(mass, com, inertia_com)

        worst = 0.0
        for _ in range(200):
            omega, v_o = RNG.normal(size=3) * 3.0, RNG.normal(size=3) * 2.0
            omega_dot, a_o = RNG.normal(size=3) * 5.0, RNG.normal(size=3) * 4.0
            got = spatial_newton_euler(
                inertia, np.concatenate([omega, v_o]), np.concatenate([omega_dot, a_o])
            )
            want = newton_euler_about_origin(mass, com, inertia_com, omega, v_o, omega_dot, a_o)
            worst = max(worst, np.abs(got - want).max())
        assert worst < 1e-9

    def test_the_subtracted_form_is_wrong(self):
        """Pins the sign: flipping it must break agreement, not preserve it."""
        mass = 2.7
        com = np.array([0.11, -0.05, 0.23])
        inertia_com = np.diag([0.031, 0.044, 0.019])
        inertia = spatial_inertia(mass, com, inertia_com)
        omega, v_o = np.array([1.0, 2.0, 3.0]), np.array([0.5, -1.0, 0.2])
        omega_dot, a_o = np.array([0.3, 0.1, -0.4]), np.array([1.0, 0.0, -2.0])

        v = np.concatenate([omega, v_o])
        a = np.concatenate([omega_dot, a_o])
        subtracted = inertia @ a - force_cross(v) @ (inertia @ v)
        want = newton_euler_about_origin(mass, com, inertia_com, omega, v_o, omega_dot, a_o)
        assert not np.allclose(subtracted, want)

    def test_zero_velocity_leaves_only_the_inertial_term(self):
        inertia = spatial_inertia(1.5, np.array([0.1, 0.0, 0.0]), np.eye(3) * 0.02)
        a = RNG.normal(size=6)
        assert np.allclose(spatial_newton_euler(inertia, np.zeros(6), a), inertia @ a)


class TestDoublePendulum:
    PARAMS = dict(m1=1.3, m2=0.8, l1=0.6, l2=0.45)

    def test_mass_matrix_is_symmetric_positive_definite(self):
        for _ in range(50):
            q = RNG.uniform(-np.pi, np.pi, size=2)
            mass_matrix = double_pendulum_mass_matrix(q, **self.PARAMS)
            assert np.allclose(mass_matrix, mass_matrix.T)
            assert (np.linalg.eigvalsh(mass_matrix) > 0).all()

    def test_mass_matrix_reproduces_the_kinetic_energy(self):
        """M must be the Hessian of T in qd -- the definition it is read from."""
        m1, m2, l1, l2 = (self.PARAMS[k] for k in ("m1", "m2", "l1", "l2"))
        for _ in range(50):
            q = RNG.uniform(-np.pi, np.pi, size=2)
            qd = RNG.normal(size=2)
            energy = 0.5 * (
                (m1 / 4 + m2) * l1**2 * qd[0] ** 2
                + m2 * l2**2 / 4 * qd[1] ** 2
                + m2 * l1 * l2 * np.cos(q[0] - q[1]) * qd[0] * qd[1]
            )
            quadratic = 0.5 * qd @ double_pendulum_mass_matrix(q, **self.PARAMS) @ qd
            assert quadratic == pytest.approx(energy)

    def test_mdot_minus_2c_is_skew_symmetric(self):
        """The property the published M and C violated."""
        m2, l1, l2 = self.PARAMS["m2"], self.PARAMS["l1"], self.PARAMS["l2"]
        eps = 1e-7
        for _ in range(50):
            q = RNG.uniform(-np.pi, np.pi, size=2)
            qd = RNG.normal(size=2)

            # Mdot by finite difference along the trajectory direction.
            forward = double_pendulum_mass_matrix(q + eps * qd, **self.PARAMS)
            backward = double_pendulum_mass_matrix(q - eps * qd, **self.PARAMS)
            mass_dot = (forward - backward) / (2 * eps)

            residual = mass_dot - 2 * double_pendulum_coriolis(q, qd, m2, l1, l2)
            assert np.abs(residual + residual.T).max() < 1e-6

    def test_coriolis_vanishes_when_the_links_are_aligned(self):
        m2, l1, l2 = self.PARAMS["m2"], self.PARAMS["l1"], self.PARAMS["l2"]
        coriolis = double_pendulum_coriolis(np.array([0.7, 0.7]), np.array([1.0, -2.0]), m2, l1, l2)
        assert np.allclose(coriolis, 0.0)


class TestConstrainedAffineFields:
    @staticmethod
    def random_system(n=4, m=2, k=1):
        a = RNG.normal(size=(n, n))
        return (
            a @ a.T + n * np.eye(n),
            RNG.normal(size=n),
            RNG.normal(size=(n, m)),
            RNG.normal(size=(k, n)),
            RNG.normal(size=k),
        )

    @staticmethod
    def kkt_acceleration(mass_matrix, bias, input_matrix, jac, jac_bias, u):
        """Ground truth: solve the constrained system as a saddle-point problem."""
        n, k = mass_matrix.shape[0], jac.shape[0]
        saddle = np.block([[mass_matrix, -jac.T], [jac, np.zeros((k, k))]])
        rhs = np.concatenate([input_matrix @ u - bias, -jac_bias])
        return np.linalg.solve(saddle, rhs)[:n]

    def test_reproduces_the_constrained_acceleration(self):
        system = self.random_system()
        drift, input_field = constrained_affine_fields(*system)
        for _ in range(100):
            u = RNG.normal(size=system[2].shape[1])
            assert np.allclose(drift + input_field @ u, self.kkt_acceleration(*system, u))

    def test_accelerations_satisfy_the_constraint(self):
        mass_matrix, bias, input_matrix, jac, jac_bias = self.random_system()
        drift, input_field = constrained_affine_fields(
            mass_matrix, bias, input_matrix, jac, jac_bias
        )
        for _ in range(50):
            qdd = drift + input_field @ RNG.normal(size=input_matrix.shape[1])
            assert np.abs(jac @ qdd + jac_bias).max() < 1e-9

    def test_unprojected_input_field_violates_the_constraint(self):
        """Why the projector is needed, not merely tidier."""
        mass_matrix, bias, input_matrix, jac, jac_bias = self.random_system()
        minv = np.linalg.inv(mass_matrix)
        u = RNG.normal(size=input_matrix.shape[1])
        naive = -minv @ bias + minv @ input_matrix @ u
        assert np.abs(jac @ naive + jac_bias).max() > 1e-6

    def test_drift_does_not_depend_on_the_input(self):
        """df/du = 0 -- the property the Zero-Torque Counterfactual rests on."""
        system = self.random_system()
        drift, _ = constrained_affine_fields(*system)
        for _ in range(20):
            again, _ = constrained_affine_fields(*system)
            assert np.allclose(drift, again)

    def test_rejects_a_rank_deficient_constraint(self):
        mass_matrix, bias, input_matrix, _, _ = self.random_system()
        duplicated = np.array([[1.0, 0.0, 0.0, 0.0], [2.0, 0.0, 0.0, 0.0]])
        with pytest.raises(np.linalg.LinAlgError, match="rank deficient"):
            constrained_affine_fields(mass_matrix, bias, input_matrix, duplicated, np.zeros(2))
