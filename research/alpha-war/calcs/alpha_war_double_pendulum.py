"""Planar double-pendulum mass matrix and free-hinge algebra for Appendix B.1 (#5460)."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

type Vec2 = NDArray[np.float64]
type Mat2 = NDArray[np.float64]

GRAVITY_M_S2 = 9.81


@dataclass(frozen=True)
class DoublePendulumParams:
    """Inertial and geometric parameters for the draft B.1 arm–club pair."""

    i1_o: float
    m2: float
    l1: float
    r_g2: float
    i_g2: float
    m1: float
    g: float = GRAVITY_M_S2

    @property
    def j1(self) -> float:
        """Arm rotational inertia about O (club translation handled via COM speed)."""
        return self.i1_o


@dataclass(frozen=True)
class PendulumState:
    """Generalized coordinates and rates (absolute angles from horizontal)."""

    theta1: float
    theta2: float
    theta1_dot: float
    theta2_dot: float


def hinge_angle(state: PendulumState) -> float:
    """Wrist cock angle phi = theta2 - theta1."""
    return state.theta2 - state.theta1


def mass_matrix(params: DoublePendulumParams, phi: float) -> Mat2:
    """Return 2x2 mass matrix M(phi) as the velocity Hessian of draft T."""
    m12 = params.m2 * params.l1 * params.r_g2 * math.cos(phi)
    m11 = params.i1_o + params.m2 * params.l1**2
    return np.array(
        [
            [m11, m12],
            [m12, params.i_g2 + params.m2 * params.r_g2**2],
        ],
        dtype=np.float64,
    )


def velocity_quadratic_terms(params: DoublePendulumParams, state: PendulumState) -> Vec2:
    """Coriolis/centrifugal vector C(q, qdot) * qdot in the draft's sign convention."""
    phi = hinge_angle(state)
    scale = params.m2 * params.l1 * params.r_g2 * math.sin(phi)
    return np.array(
        [
            -scale * state.theta2_dot**2,
            scale * state.theta1_dot**2,
        ],
        dtype=np.float64,
    )


def gravity_generalized(params: DoublePendulumParams, state: PendulumState) -> Vec2:
    """Gravity generalized forces G1, G2 for absolute-angle coordinates."""
    g1 = (params.m1 * params.g * (params.l1 / 2.0) + params.m2 * params.g * params.l1) * math.cos(
        state.theta1
    )
    g2 = params.m2 * params.g * params.r_g2 * math.cos(state.theta2)
    return np.array([g1, g2], dtype=np.float64)


def kinetic_energy(params: DoublePendulumParams, state: PendulumState) -> float:
    """Kinetic energy T from draft B.1 (split form equivalent to COM kinematics)."""
    phi = hinge_angle(state)
    c = math.cos(phi)
    t = 0.5 * params.i1_o * state.theta1_dot**2
    inner = (
        params.l1**2 * state.theta1_dot**2
        + params.r_g2**2 * state.theta2_dot**2
        + 2.0 * params.l1 * params.r_g2 * state.theta1_dot * state.theta2_dot * c
    )
    t += 0.5 * params.m2 * inner + 0.5 * params.i_g2 * state.theta2_dot**2
    return float(t)


def kinetic_energy_from_com_kinematics(params: DoublePendulumParams, state: PendulumState) -> float:
    """Kinetic energy from independent planar position kinematics (COM velocity)."""
    t1, t2 = state.theta1, state.theta2
    v1, v2 = state.theta1_dot, state.theta2_dot
    vx = -params.l1 * math.sin(t1) * v1 - params.r_g2 * math.sin(t2) * v2
    vy = params.l1 * math.cos(t1) * v1 + params.r_g2 * math.cos(t2) * v2
    v_com_sq = vx * vx + vy * vy
    return float(
        0.5 * params.i1_o * v1 * v1 + 0.5 * params.m2 * v_com_sq + 0.5 * params.i_g2 * v2 * v2
    )


def _kinetic_at_vel(
    params: DoublePendulumParams, state: PendulumState, v1: float, v2: float
) -> float:
    """Kinetic energy at arbitrary generalized velocities."""
    return kinetic_energy(params, PendulumState(state.theta1, state.theta2, v1, v2))


def mass_matrix_from_kinetic_hessian(
    params: DoublePendulumParams, state: PendulumState, eps: float = 1e-4
) -> Mat2:
    """Numerical Hessian of T with respect to [theta1_dot, theta2_dot]."""
    v1, v2 = state.theta1_dot, state.theta2_dot
    t0 = _kinetic_at_vel(params, state, v1, v2)
    hess = np.zeros((2, 2), dtype=np.float64)
    hess[0, 0] = (
        _kinetic_at_vel(params, state, v1 + eps, v2)
        - 2.0 * t0
        + _kinetic_at_vel(params, state, v1 - eps, v2)
    ) / (eps * eps)
    hess[1, 1] = (
        _kinetic_at_vel(params, state, v1, v2 + eps)
        - 2.0 * t0
        + _kinetic_at_vel(params, state, v1, v2 - eps)
    ) / (eps * eps)
    hess[0, 1] = hess[1, 0] = (
        _kinetic_at_vel(params, state, v1 + eps, v2 + eps)
        - _kinetic_at_vel(params, state, v1 + eps, v2 - eps)
        - _kinetic_at_vel(params, state, v1 - eps, v2 + eps)
        + _kinetic_at_vel(params, state, v1 - eps, v2 - eps)
    ) / (4.0 * eps * eps)
    return hess


def wrist_torque(
    params: DoublePendulumParams,
    state: PendulumState,
    theta1_ddot: float,
    theta2_ddot: float,
) -> float:
    """Active hinge torque tau2 from row 2 of the draft equations."""
    phi = hinge_angle(state)
    m = mass_matrix(params, phi)
    c = velocity_quadratic_terms(params, state)
    g = gravity_generalized(params, state)
    return float(m[1, 0] * theta1_ddot + m[1, 1] * theta2_ddot + c[1] + g[1])


def free_hinge_theta2_accel(
    params: DoublePendulumParams,
    state: PendulumState,
    theta1_ddot: float,
) -> float:
    """ddtheta2 when tau2=0 with gravity and velocity terms retained (row 2)."""
    phi = hinge_angle(state)
    m = mass_matrix(params, phi)
    c = velocity_quadratic_terms(params, state)
    g = gravity_generalized(params, state)
    rhs = -(m[1, 0] * theta1_ddot + c[1] + g[1])
    return float(rhs / m[1, 1])


def passive_release_accel_formula(
    params: DoublePendulumParams, state: PendulumState, theta1_ddot: float
) -> float:
    """Row-2 interaction pass-through at tau2=0 without gravity (see full free_hinge helper)."""
    phi = hinge_angle(state)
    m = mass_matrix(params, phi)
    c = velocity_quadratic_terms(params, state)
    return float(-(m[1, 0] * theta1_ddot + c[1]) / m[1, 1])
