"""Tests for src.tangent_models.examples dynamical-system implementations.

Covers SimplePendulum, SpacecraftRendezvous, PlanarQuadrotor, RobotArm,
the central-difference linearization helper, and the gravity-gradient
helper. Verifies known closed-form values, Jacobian consistency between
analytical and numerical linearizations, equilibrium points, contract
violations on bad inputs, and edge cases (zero control, singular states).
"""

from __future__ import annotations

import numpy as np
import pytest

from src.core.constants import EARTH_MU, GRAVITY_M_S2, ISS_ORBIT_RADIUS_M
from src.core.contracts import ContractViolationError
from src.tangent_models.examples import (
    DynamicalSystem,
    PlanarQuadrotor,
    RobotArm,
    SimplePendulum,
    SpacecraftRendezvous,
    _central_difference_linearization,
    _gravity_gradient,
)

# ── DynamicalSystem ABC ────────────────────────────────────────────────────


class TestDynamicalSystemABC:
    def test_cannot_instantiate_abstract_class(self) -> None:
        with pytest.raises(TypeError):
            DynamicalSystem()  # type: ignore[abstract]


# ── _gravity_gradient helper ───────────────────────────────────────────────


class TestGravityGradient:
    def test_radial_pull_along_x_axis(self) -> None:
        # Along x-axis, gradient is 2*mu/r^3 in xx (outward stretch),
        # -mu/r^3 in yy and zz (compress).
        mu = 1.0
        r = 1.0
        pos = np.array([r, 0.0, 0.0])
        G = _gravity_gradient(mu, pos)
        assert G.shape == (3, 3)
        np.testing.assert_allclose(G[0, 0], 2 * mu / r**3, rtol=1e-10)
        np.testing.assert_allclose(G[1, 1], -mu / r**3, rtol=1e-10)
        np.testing.assert_allclose(G[2, 2], -mu / r**3, rtol=1e-10)

    def test_traceless(self) -> None:
        # The gravity gradient tensor has trace zero (Laplacian of -mu/r is 0).
        pos = np.array([3.0, 4.0, 5.0])
        G = _gravity_gradient(2.5, pos)
        np.testing.assert_allclose(np.trace(G), 0.0, atol=1e-12)

    def test_symmetric(self) -> None:
        pos = np.array([1.0, 2.0, -3.0])
        G = _gravity_gradient(1.0, pos)
        np.testing.assert_allclose(G, G.T, atol=1e-14)


# ── SimplePendulum ─────────────────────────────────────────────────────────


class TestSimplePendulum:
    def test_construction_defaults(self) -> None:
        p = SimplePendulum()
        assert p.m == 1.0 and p.L == 1.0 and p.g == GRAVITY_M_S2

    @pytest.mark.parametrize("kwarg", ["m", "L", "g"])
    def test_non_positive_params_rejected(self, kwarg: str) -> None:
        kwargs = {"m": 1.0, "L": 1.0, "g": 9.81, kwarg: -1.0}
        with pytest.raises(ContractViolationError):
            SimplePendulum(**kwargs)
        kwargs[kwarg] = 0.0
        with pytest.raises(ContractViolationError):
            SimplePendulum(**kwargs)

    def test_dynamics_at_equilibrium_no_torque(self) -> None:
        # theta=0, omega=0, u=0 -> derivative = [0, 0]
        p = SimplePendulum(m=1.0, L=1.0)
        dx = p.dynamics(np.array([0.0, 0.0]), 0.0)
        np.testing.assert_allclose(dx, [0.0, 0.0], atol=1e-12)

    def test_dynamics_known_value(self) -> None:
        # At theta=pi/2, omega=0, u=0: dtheta=0, domega = -(g/L)*sin(pi/2) = -g/L
        p = SimplePendulum(m=2.0, L=0.5, g=10.0)
        dx = p.dynamics(np.array([np.pi / 2, 0.0]), 0.0)
        np.testing.assert_allclose(dx[0], 0.0, atol=1e-12)
        np.testing.assert_allclose(dx[1], -(10.0 / 0.5), rtol=1e-12)

    def test_dynamics_torque_contribution(self) -> None:
        # At theta=0, omega=0: domega = u/(m*L^2)
        p = SimplePendulum(m=2.0, L=3.0, g=9.81)
        dx = p.dynamics(np.array([0.0, 0.0]), 18.0)
        np.testing.assert_allclose(dx[1], 18.0 / (2.0 * 9.0), rtol=1e-12)

    def test_dynamics_accepts_list_or_array_input(self) -> None:
        p = SimplePendulum()
        dx_list = p.dynamics(np.array([0.1, 0.2]), [0.5])
        dx_arr = p.dynamics(np.array([0.1, 0.2]), np.array([0.5]))
        dx_scalar = p.dynamics(np.array([0.1, 0.2]), 0.5)
        np.testing.assert_allclose(dx_list, dx_arr)
        np.testing.assert_allclose(dx_list, dx_scalar)

    def test_dynamics_rejects_non_finite_state(self) -> None:
        p = SimplePendulum()
        with pytest.raises(ContractViolationError):
            p.dynamics(np.array([np.nan, 0.0]), 0.0)
        with pytest.raises(ContractViolationError):
            p.dynamics(np.array([0.0, np.inf]), 0.0)

    def test_dynamics_rejects_wrong_state_length(self) -> None:
        p = SimplePendulum()
        with pytest.raises(ContractViolationError):
            p.dynamics(np.array([1.0, 2.0, 3.0]), 0.0)

    def test_linearize_matches_numerical_jacobian(self) -> None:
        p = SimplePendulum(m=1.5, L=0.8, g=9.81)
        x = np.array([0.3, -0.1])
        u = np.array([0.2])
        A, B = p.linearize(x, u)
        A_num, B_num = _central_difference_linearization(p, x, u)
        np.testing.assert_allclose(A, A_num, atol=1e-6)
        np.testing.assert_allclose(B, B_num, atol=1e-6)

    def test_linearize_shapes(self) -> None:
        p = SimplePendulum()
        A, B = p.linearize(np.array([0.0, 0.0]), 0.0)
        assert A.shape == (2, 2)
        assert B.shape == (2, 1)


# ── SpacecraftRendezvous ───────────────────────────────────────────────────


class TestSpacecraftRendezvous:
    def test_construction_computes_mean_motion(self) -> None:
        s = SpacecraftRendezvous()
        expected_n = np.sqrt(EARTH_MU / ISS_ORBIT_RADIUS_M**3)
        np.testing.assert_allclose(s.n, expected_n, rtol=1e-12)

    def test_origin_is_target_orbit_equilibrium(self) -> None:
        # At rx=ry=rz=0 with v=0, dynamics should give zero acceleration
        # (relative motion in target orbital frame, station-keeping at origin).
        s = SpacecraftRendezvous()
        dx = s.dynamics(np.zeros(6), np.zeros(3))
        np.testing.assert_allclose(dx, np.zeros(6), atol=1e-6)

    def test_dynamics_rejects_scalar_control(self) -> None:
        s = SpacecraftRendezvous()
        with pytest.raises(ValueError, match="vector"):
            s.dynamics(np.zeros(6), 1.0)
        with pytest.raises(ValueError, match="vector"):
            s.dynamics(np.zeros(6), 1)

    def test_thrust_applies_force_per_mass(self) -> None:
        # At origin/zero velocity: ax includes ux/m, ay includes uy/m, az = uz/m
        s = SpacecraftRendezvous(m=10.0)
        u = np.array([10.0, 20.0, 30.0])
        dx = s.dynamics(np.zeros(6), u)
        # The az has only uz/m since rz=0 cancels gravity and no Coriolis term.
        np.testing.assert_allclose(dx[5], 30.0 / 10.0, rtol=1e-9)

    def test_linearize_rejects_scalar_control(self) -> None:
        s = SpacecraftRendezvous()
        with pytest.raises(ValueError, match="vector"):
            s.linearize(np.zeros(6), 1.0)

    def test_linearize_shapes_and_topblock(self) -> None:
        s = SpacecraftRendezvous()
        A, B = s.linearize(np.zeros(6), np.zeros(3))
        assert A.shape == (6, 6) and B.shape == (6, 3)
        # Position-velocity coupling: top-right block is identity
        np.testing.assert_allclose(A[0:3, 3:6], np.eye(3))
        # Coriolis terms
        np.testing.assert_allclose(A[3, 4], 2 * s.n)
        np.testing.assert_allclose(A[4, 3], -2 * s.n)

    def test_linearize_matches_finite_difference_at_origin(self) -> None:
        s = SpacecraftRendezvous(m=500.0, r_t=7e6, mu=3.986e14)
        x0 = np.array([100.0, 50.0, -20.0, 0.5, -0.1, 0.2])
        u0 = np.array([0.0, 0.0, 0.0])
        A, B = s.linearize(x0, u0)
        A_num, B_num = _central_difference_linearization(s, x0, u0, epsilon=1e-2)
        # Looser tolerance — finite differences over a steep gravity term.
        np.testing.assert_allclose(A, A_num, atol=1e-4, rtol=1e-4)
        np.testing.assert_allclose(B, B_num, atol=1e-9)

    def test_negative_params_rejected(self) -> None:
        with pytest.raises(ContractViolationError):
            SpacecraftRendezvous(mu=-1.0)
        with pytest.raises(ContractViolationError):
            SpacecraftRendezvous(r_t=-1.0)
        with pytest.raises(ContractViolationError):
            SpacecraftRendezvous(m=0.0)


# ── PlanarQuadrotor ────────────────────────────────────────────────────────


class TestPlanarQuadrotor:
    def test_hover_thrust_balances_gravity(self) -> None:
        # At theta=0 with u1+u2 = m*g, ay should be 0 (hover equilibrium).
        q = PlanarQuadrotor(m=1.0, g=9.81)
        u_hover = 9.81 / 2.0
        dx = q.dynamics(np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]), [u_hover, u_hover])
        np.testing.assert_allclose(dx[3], 0.0, atol=1e-12)  # ax
        np.testing.assert_allclose(dx[4], 0.0, atol=1e-12)  # ay
        np.testing.assert_allclose(dx[5], 0.0, atol=1e-12)  # alpha

    def test_zero_thrust_gives_freefall(self) -> None:
        # With no thrust, ay = -g, ax = 0, alpha = 0
        q = PlanarQuadrotor(g=9.81)
        dx = q.dynamics(np.zeros(6), [0.0, 0.0])
        np.testing.assert_allclose(dx[3], 0.0)
        np.testing.assert_allclose(dx[4], -9.81)
        np.testing.assert_allclose(dx[5], 0.0)

    def test_differential_thrust_creates_torque(self) -> None:
        # u2 > u1 -> positive alpha
        q = PlanarQuadrotor(L=0.25, moment_inertia=0.01)
        dx = q.dynamics(np.zeros(6), [1.0, 2.0])
        # alpha = L/I * (u2 - u1) = 0.25/0.01 * 1 = 25
        np.testing.assert_allclose(dx[5], 25.0, rtol=1e-12)

    def test_dynamics_rejects_scalar(self) -> None:
        q = PlanarQuadrotor()
        with pytest.raises(ValueError, match="vector"):
            q.dynamics(np.zeros(6), 1.0)

    def test_linearize_rejects_scalar(self) -> None:
        q = PlanarQuadrotor()
        with pytest.raises(ValueError, match="vector"):
            q.linearize(np.zeros(6), 5.0)

    def test_linearize_matches_numerical(self) -> None:
        q = PlanarQuadrotor(m=1.2, L=0.3, moment_inertia=0.02)
        x = np.array([0.5, 1.0, 0.4, 0.1, -0.2, 0.05])
        u = np.array([3.0, 5.0])
        A, B = q.linearize(x, u)
        A_num, B_num = _central_difference_linearization(q, x, u)
        np.testing.assert_allclose(A, A_num, atol=1e-5)
        np.testing.assert_allclose(B, B_num, atol=1e-7)

    def test_linearize_shapes(self) -> None:
        q = PlanarQuadrotor()
        A, B = q.linearize(np.zeros(6), [0.0, 0.0])
        assert A.shape == (6, 6) and B.shape == (6, 2)

    def test_invalid_construction(self) -> None:
        with pytest.raises(ContractViolationError):
            PlanarQuadrotor(m=-1.0)
        with pytest.raises(ContractViolationError):
            PlanarQuadrotor(L=0.0)
        with pytest.raises(ContractViolationError):
            PlanarQuadrotor(moment_inertia=-0.01)


# ── RobotArm ───────────────────────────────────────────────────────────────


class TestRobotArm:
    def test_zero_velocity_zero_torque_yields_gravity_compensation(self) -> None:
        # With dq=0, tau=0: ddq must satisfy M*ddq = -G, so the joint
        # accelerations are nonzero (gravity pulls).
        arm = RobotArm()
        dx = arm.dynamics(np.array([np.pi / 2, 0.0, 0.0, 0.0]), [0.0, 0.0])
        # First two entries are dq1, dq2 -> 0
        np.testing.assert_allclose(dx[0:2], [0.0, 0.0])
        # Acceleration should be finite
        assert np.all(np.isfinite(dx[2:4]))

    def test_dynamics_rejects_scalar_control(self) -> None:
        arm = RobotArm()
        with pytest.raises(ValueError, match="vector"):
            arm.dynamics(np.zeros(4), 1.0)

    def test_linearize_rejects_scalar_control(self) -> None:
        arm = RobotArm()
        with pytest.raises(ValueError, match="vector"):
            arm.linearize(np.zeros(4), 1.0)

    def test_linearize_shapes(self) -> None:
        arm = RobotArm()
        A, B = arm.linearize(np.zeros(4), [0.0, 0.0])
        assert A.shape == (4, 4) and B.shape == (4, 2)

    def test_linearize_top_velocity_block(self) -> None:
        # The kinematic part of the Jacobian: d(dq1)/d(dq1) = 1, etc.
        # Using central differences this should hold to numerical precision.
        arm = RobotArm()
        A, _ = arm.linearize(np.array([0.1, 0.2, 0.0, 0.0]), [0.0, 0.0])
        # rows 0-1 are derivatives of dq1, dq2 (positions) wrt state.
        np.testing.assert_allclose(A[0:2, 2:4], np.eye(2), atol=1e-6)
        np.testing.assert_allclose(A[0:2, 0:2], np.zeros((2, 2)), atol=1e-6)

    def test_invalid_construction(self) -> None:
        with pytest.raises(ContractViolationError):
            RobotArm(m1=-1.0)
        with pytest.raises(ContractViolationError):
            RobotArm(m2=0.0)
        with pytest.raises(ContractViolationError):
            RobotArm(l1=-0.5)
        with pytest.raises(ContractViolationError):
            RobotArm(l2=0.0)


# ── _central_difference_linearization helper ──────────────────────────────


class TestCentralDifferenceLinearization:
    def test_identity_dynamics_yields_zero_jacobians(self) -> None:
        class Stationary(DynamicalSystem):
            def dynamics(self, x, u):  # type: ignore[no-untyped-def]
                return np.zeros_like(np.asarray(x, dtype=float))

            def linearize(self, x, u):  # type: ignore[no-untyped-def]
                return _central_difference_linearization(self, x, u)

        s = Stationary()
        A, B = _central_difference_linearization(s, np.zeros(3), np.zeros(2))
        assert A.shape == (3, 3) and B.shape == (3, 2)
        np.testing.assert_allclose(A, 0.0, atol=1e-12)
        np.testing.assert_allclose(B, 0.0, atol=1e-12)

    def test_linear_dynamics_recovers_matrices(self) -> None:
        # f(x, u) = A0 x + B0 u; central differences should recover A0, B0.
        A0 = np.array([[1.0, 2.0], [3.0, 4.0]])
        B0 = np.array([[0.5], [-1.0]])

        class Linear(DynamicalSystem):
            def dynamics(self, x, u):  # type: ignore[no-untyped-def]
                u_arr = np.atleast_1d(np.asarray(u, dtype=float))
                return A0 @ x + (B0 @ u_arr).ravel()

            def linearize(self, x, u):  # type: ignore[no-untyped-def]
                return A0, B0

        sys_ = Linear()
        A, B = _central_difference_linearization(sys_, np.array([0.1, -0.2]), np.array([0.3]))
        np.testing.assert_allclose(A, A0, atol=1e-7)
        np.testing.assert_allclose(B, B0, atol=1e-7)
