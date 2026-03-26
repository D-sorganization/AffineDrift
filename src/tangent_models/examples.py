"""Concrete dynamical system examples for AffineDrift.

This module provides the abstract base class ``DynamicalSystem`` and four
example systems used in the textbook chapters:

- ``SimplePendulum`` — torque-driven pendulum in 2D.
- ``SpacecraftRendezvous`` — nonlinear relative orbital motion (LVLH).
- ``PlanarQuadrotor`` — 2D quadrotor with two thrust inputs.
- ``RobotArm`` — 2-link planar manipulator with full Lagrangian dynamics.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from src.core.constants import (
    DEFAULT_SPACECRAFT_MASS_KG,
    EARTH_MU,
    GRAVITY_M_S2,
    ISS_ORBIT_RADIUS_M,
)
from src.core.contracts import check_finite_array, check_positive, require

logger = logging.getLogger(__name__)


def _central_difference_linearization(
    dynamics: "DynamicalSystem",
    x: np.ndarray[Any, Any],
    u: np.ndarray[Any, Any] | list[float],
    epsilon: float = 1e-6,
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """Numerically linearize a system with central differences."""
    x_arr = np.array(x, dtype=float)
    u_arr = np.array(u, dtype=float)
    n = len(x_arr)
    m = len(u_arr)
    A = np.zeros((n, n))
    B = np.zeros((n, m))

    for i in range(n):
        x_plus = x_arr.copy()
        x_minus = x_arr.copy()
        x_plus[i] += epsilon
        x_minus[i] -= epsilon
        A[:, i] = (dynamics.dynamics(x_plus, u_arr) - dynamics.dynamics(x_minus, u_arr)) / (
            2 * epsilon
        )

    for i in range(m):
        u_plus = u_arr.copy()
        u_minus = u_arr.copy()
        u_plus[i] += epsilon
        u_minus[i] -= epsilon
        B[:, i] = (dynamics.dynamics(x_arr, u_plus) - dynamics.dynamics(x_arr, u_minus)) / (
            2 * epsilon
        )

    return A, B


class DynamicalSystem(ABC):
    """Abstract base class for continuous-time dynamical systems.

    Subclasses must implement ``dynamics`` (the state derivative) and
    ``linearize`` (the tangent linear model A, B matrices).
    """

    @abstractmethod
    def dynamics(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any] | float | list[float]
    ) -> np.ndarray[Any, Any]:
        """Compute system dynamics."""
        pass  # Abstract method

    @abstractmethod
    def linearize(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any] | float | list[float]
    ) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
        """
        Returns A, B matrices where dx_dot = A*dx + B*du
        """
        pass  # Abstract method


class SimplePendulum(DynamicalSystem):
    """Simple pendulum dynamical system with torque input.

    State is [theta, omega] (angle from vertical, angular velocity).
    Control input is a scalar torque applied at the pivot.
    """

    def __init__(self, m: float = 1.0, L: float = 1.0, g: float = GRAVITY_M_S2) -> None:
        """Initialize simple pendulum."""
        check_positive(m, "mass")
        check_positive(L, "length")
        check_positive(g, "gravitational acceleration")
        self.m = m
        self.L = L
        self.g = g

    def dynamics(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any] | float | list[float]
    ) -> np.ndarray[Any, Any]:
        """Compute simple pendulum dynamics."""
        check_finite_array(x, "state vector")
        require(len(x) == 2, "state vector must have 2 elements (theta, omega)")
        # x = [theta, omega]
        theta, omega = x
        u_val = u[0] if isinstance(u, list | tuple | np.ndarray) else u

        dtheta = omega
        domega = -(self.g / self.L) * np.sin(theta) + u_val / (self.m * self.L**2)

        return np.array([dtheta, domega])

    def linearize(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any] | float | list[float]
    ) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
        """Linearize simple pendulum dynamics."""
        theta, _ = x

        A = np.array([[0, 1], [-(self.g / self.L) * np.cos(theta), 0]])

        B = np.array([[0], [1 / (self.m * self.L**2)]])

        return A, B


def _gravity_gradient(mu: float, pos_vec: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
    """Compute the gravity gradient tensor at a given position.

    The gravity gradient is the Jacobian of the gravitational acceleration
    -mu * r / |r|^3 with respect to the position vector.

    Args:
        mu: Gravitational parameter.
        pos_vec: Position vector (e.g. [rt+rx, ry, rz]).

    Returns:
        3x3 gravity gradient matrix.
    """
    r_norm = np.linalg.norm(pos_vec)
    mat = -(mu / r_norm**3) * (np.eye(3) - 3 * np.outer(pos_vec, pos_vec) / r_norm**2)
    return np.array(mat)


class SpacecraftRendezvous(DynamicalSystem):
    """Nonlinear relative motion dynamics (Clohessy-Wiltshire precursor).

    Target is in circular orbit with radius r_t and mean motion n.
    State x = [rx, ry, rz, vx, vy, vz] (Relative position and velocity in LVLH).
    """

    def __init__(
        self,
        mu: float = EARTH_MU,
        r_t: float = ISS_ORBIT_RADIUS_M,
        m: float = DEFAULT_SPACECRAFT_MASS_KG,
    ) -> None:
        """Initialize spacecraft rendezvous system."""
        check_positive(mu, "gravitational parameter")
        check_positive(r_t, "orbit radius")
        check_positive(m, "spacecraft mass")
        self.mu = mu
        self.r_t = r_t  # Orbit radius (m), e.g., ISS ~400km altitude
        self.n = np.sqrt(mu / r_t**3)  # Mean motion
        self.m = m  # Spacecraft mass

    def dynamics(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any] | float | list[float]
    ) -> np.ndarray[Any, Any]:
        """Compute spacecraft rendezvous dynamics."""
        if isinstance(u, float | int):
            raise ValueError("Control input must be a vector for SpacecraftRendezvous")
        rx, ry, rz, vx, vy, vz = x
        ux, uy, uz = u

        rc = np.sqrt((self.r_t + rx) ** 2 + ry**2 + rz**2)

        ax = (
            2 * self.n * vy
            + self.n**2 * (self.r_t + rx)
            - (self.mu * (self.r_t + rx)) / rc**3
            + ux / self.m
        )
        ay = -2 * self.n * vx + self.n**2 * ry - (self.mu * ry) / rc**3 + uy / self.m
        az = -(self.mu * rz) / rc**3 + uz / self.m

        return np.array([vx, vy, vz, ax, ay, az])

    def linearize(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any] | float | list[float]
    ) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
        """Linearize spacecraft rendezvous dynamics about a given state.

        Computes the analytical Jacobian of the nonlinear relative motion
        dynamics, yielding A and B matrices for the tangent linear model.
        """
        if isinstance(u, float | int):
            raise ValueError("Control input must be a vector")

        rx, ry, rz, _, _, _ = x
        n = self.n

        A = np.zeros((6, 6))
        A[0:3, 3:6] = np.eye(3)

        # Gravity gradient contribution to position Jacobian
        pos_chaser = np.array([self.r_t + rx, ry, rz])
        grad_grav = _gravity_gradient(self.mu, pos_chaser)

        # Centrifugal contribution: d(F_centrifugal)/dr
        dFcent_dr = np.zeros((3, 3))
        dFcent_dr[0, 0] = n**2
        dFcent_dr[1, 1] = n**2

        A[3:6, 0:3] = dFcent_dr + grad_grav

        # Coriolis contribution to velocity Jacobian
        A[3, 4] = 2 * n
        A[4, 3] = -2 * n

        B = np.zeros((6, 3))
        B[3:6, 0:3] = np.eye(3) / self.m

        return A, B


class PlanarQuadrotor(DynamicalSystem):
    """
    Planar Quadrotor dynamics.
    State x = [x, y, theta, vx, vy, omega]
    Input u = [u1, u2] (Thrusts)
    """

    def __init__(
        self,
        m: float = 1.0,
        L: float = 0.25,
        moment_inertia: float = 0.01,
        g: float = GRAVITY_M_S2,
    ) -> None:
        """Initialize planar quadrotor."""
        check_positive(m, "mass")
        check_positive(L, "arm length")
        check_positive(moment_inertia, "moment of inertia")
        self.m = m
        self.L = L  # Arm length
        self.moment_inertia = moment_inertia
        self.g = g

    def dynamics(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any] | float | list[float]
    ) -> np.ndarray[Any, Any]:
        """Compute planar quadrotor dynamics."""
        if isinstance(u, float | int):
            raise ValueError("Control input must be a vector")
        px, py, theta, vx, vy, omega = x
        u1, u2 = u

        # Total thrust
        T = u1 + u2

        ax = -(T / self.m) * np.sin(theta)
        ay = (T / self.m) * np.cos(theta) - self.g
        alpha = (self.L / self.moment_inertia) * (u2 - u1)

        return np.array([vx, vy, omega, ax, ay, alpha])

    def linearize(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any] | float | list[float]
    ) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
        """Linearize planar quadrotor dynamics."""
        if isinstance(u, float | int):
            raise ValueError("Control input must be a vector")
        px, py, theta, vx, vy, omega = x
        u1, u2 = u
        T = u1 + u2

        A = np.zeros((6, 6))
        A[0:3, 3:6] = np.eye(3)

        # d(ax)/dtheta = -(T/m) * cos(theta)
        A[3, 2] = -(T / self.m) * np.cos(theta)
        # d(ay)/dtheta = -(T/m) * sin(theta)
        A[4, 2] = -(T / self.m) * np.sin(theta)

        B = np.zeros((6, 2))
        # d(ax)/du1 = -sin(theta)/m
        B[3, 0] = -np.sin(theta) / self.m
        B[3, 1] = -np.sin(theta) / self.m

        # d(ay)/du1 = cos(theta)/m
        B[4, 0] = np.cos(theta) / self.m
        B[4, 1] = np.cos(theta) / self.m

        # d(alpha)/du1 = -L/I
        B[5, 0] = -self.L / self.moment_inertia
        B[5, 1] = self.L / self.moment_inertia

        return A, B


class RobotArm(DynamicalSystem):
    """
    2-Link Planar Robot Arm.
    State x = [q1, q2, dq1, dq2]
    Input u = [tau1, tau2]
    """

    def __init__(
        self,
        m1: float = 1.0,
        m2: float = 1.0,
        l1: float = 1.0,
        l2: float = 1.0,
        g: float = GRAVITY_M_S2,
    ) -> None:
        """Initialize robot arm."""
        check_positive(m1, "mass 1")
        check_positive(m2, "mass 2")
        check_positive(l1, "link length 1")
        check_positive(l2, "link length 2")
        self.m1 = m1
        self.m2 = m2
        self.l1 = l1
        self.l2 = l2
        self.g = g

    def dynamics(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any] | float | list[float]
    ) -> np.ndarray[Any, Any]:
        """Compute robot arm dynamics."""
        if isinstance(u, float | int):
            raise ValueError("Control input must be a vector")
        q1, q2, dq1, dq2 = x
        tau1, tau2 = u

        m1, m2, l1, l2, g = self.m1, self.m2, self.l1, self.l2, self.g

        # Mass matrix
        c2 = np.cos(q2)
        s2 = np.sin(q2)

        M11 = (m1 + m2) * l1**2 + m2 * l2**2 + 2 * m2 * l1 * l2 * c2
        M12 = m2 * l2**2 + m2 * l1 * l2 * c2
        M21 = M12
        M22 = m2 * l2**2

        M = np.array([[M11, M12], [M21, M22]])

        # Coriolis/Centrifugal
        h = m2 * l1 * l2 * s2
        C1 = -h * dq2 * (2 * dq1 + dq2)
        C2 = h * dq1**2
        C = np.array([C1, C2])

        # Gravity
        G1 = (m1 + m2) * g * l1 * np.cos(q1) + m2 * g * l2 * np.cos(q1 + q2)
        G2 = m2 * g * l2 * np.cos(q1 + q2)
        G = np.array([G1, G2])

        # M * ddq + C + G = tau
        # ddq = M_inv * (tau - C - G)

        invM = np.linalg.inv(M)
        ddq = invM @ (np.array([tau1, tau2]) - C - G)

        return np.array([dq1, dq2, ddq[0], ddq[1]])

    def linearize(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any] | float | list[float]
    ) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
        """Linearize robot arm dynamics using central finite differences.

        Central differences give O(epsilon^2) accuracy vs O(epsilon) for forward differences,
        consistent with _finite_diff_jacobian in residuals.py.
        """
        if isinstance(u, float | int):
            raise ValueError("Control input must be a vector")
        # Using numerical linearization for the 2-link arm due to complexity
        epsilon = 1e-6
        n = 4
        m = 2

        A = np.zeros((n, n))
        B = np.zeros((n, m))

        # Compute A using central differences: (f(x+eps) - f(x-eps)) / (2*eps)
        for i in range(n):
            x_plus = x.copy()
            x_plus[i] += epsilon
            x_minus = x.copy()
            x_minus[i] -= epsilon
            A[:, i] = (self.dynamics(x_plus, u) - self.dynamics(x_minus, u)) / (2 * epsilon)

        # Compute B using central differences: (f(u+eps) - f(u-eps)) / (2*eps)
        u_arr = np.array(u, dtype=float)
        for i in range(m):
            u_plus = u_arr.copy()
            u_plus[i] += epsilon
            u_minus = u_arr.copy()
            u_minus[i] -= epsilon
            B[:, i] = (self.dynamics(x, u_plus) - self.dynamics(x, u_minus)) / (2 * epsilon)

        return A, B
