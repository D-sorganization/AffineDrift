from typing import Any

import numpy as np

# Physical constants
GRAVITY_M_S2 = 9.81


class DynamicalSystem:
    def dynamics(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any] | float | list[float]
    ) -> np.ndarray[Any, Any]:
        """Compute system dynamics x_dot = f(x, u)."""
        pass  # Abstract method

    def linearize(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any] | float | list[float]
    ) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
        """
        Returns A, B matrices where dx_dot = A*dx + B*du
        """
        pass  # Abstract method
        return np.array([]), np.array([])


class SimplePendulum(DynamicalSystem):
    def __init__(self, m: float = 1.0, L: float = 1.0, g: float = GRAVITY_M_S2) -> None:
        """Initialize simple pendulum parameters."""
        self.m = m
        self.L = L
        self.g = g

    def dynamics(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any] | float | list[float]
    ) -> np.ndarray[Any, Any]:
        """Compute pendulum dynamics."""
        # x = [theta, omega]
        theta, omega = x
        u_val = u[0] if isinstance(u, list | tuple | np.ndarray) else u

        dtheta = omega
        domega = -(self.g / self.L) * np.sin(theta) + u_val / (self.m * self.L**2)

        return np.array([dtheta, domega])

    def linearize(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any] | float | list[float]
    ) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
        """Linearize pendulum dynamics."""
        theta, _ = x

        A = np.array([[0, 1], [-(self.g / self.L) * np.cos(theta), 0]])

        B = np.array([[0], [1 / (self.m * self.L**2)]])

        return A, B


class SpacecraftRendezvous(DynamicalSystem):
    """
    Nonlinear relative motion dynamics (Clohessy-Wiltshire precursor).
    Target is in circular orbit with radius r_t and mean motion n.
    State x = [rx, ry, rz, vx, vy, vz] (Relative position and velocity in LVLH)
    """

    def __init__(self, mu: float = 3.986e14, r_t: float = 6771000.0, m: float = 100.0) -> None:
        """Initialize spacecraft parameters."""
        self.mu = mu
        self.r_t = r_t  # Orbit radius (m), e.g., ISS ~400km altitude
        self.n = np.sqrt(mu / r_t**3)  # Mean motion
        self.m = m  # Spacecraft mass

    def dynamics(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any] | float | list[float]
    ) -> np.ndarray[Any, Any]:
        """Compute spacecraft relative dynamics."""
        assert not isinstance(
            u, float | int
        ), "Control input must be a vector for SpacecraftRendezvous"
        rx, ry, rz, vx, vy, vz = x
        ux, uy, uz = u

        # Distance from center of Earth to chaser
        rc = np.sqrt((self.r_t + rx) ** 2 + ry**2 + rz**2)

        # Acceleration terms
        # x-direction (radial)
        ax = (
            2 * self.n * vy
            + self.n**2 * (self.r_t + rx)
            - (self.mu * (self.r_t + rx)) / rc**3
            + ux / self.m
        )

        # y-direction (along-track)
        ay = -2 * self.n * vx + self.n**2 * ry - (self.mu * ry) / rc**3 + uy / self.m

        # z-direction (cross-track)
        az = -(self.mu * rz) / rc**3 + uz / self.m

        # Note: The standard HCW derivation assumes n is constant and circular orbit.
        # The terms n^2 * (r_t + rx) and n^2 * ry come from transport acceleration
        # in rotating frame.

        return np.array([vx, vy, vz, ax, ay, az])

    def linearize(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any] | float | list[float]
    ) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
        """Linearize spacecraft dynamics."""
        assert not isinstance(u, float | int), "Control input must be a vector"
        # Linearization about equilibrium [0,0,0,0,0,0] yields HCW equations
        # But we want linearization about ANY point x for the Tangent Hyperplane theory.

        rx, ry, rz, _, _, _ = x

        # Partial derivatives of gravitational terms are complex.
        # For simplicity in this worked example, we can use numerical linearization
        # or implement the analytical Jacobian of the gravity vector.

        # Let's do analytical for precision.
        # Gx = -mu * (rt + rx) * rc^-3
        # dGx/drx = -mu * [ rc^-3 + (rt+rx) * (-3) * rc^-4 * (rt+rx)/rc ]
        #         = -mu/rc^3 * [ 1 - 3(rt+rx)^2/rc^2 ]

        # For the purpose of the article, calculating this exactly reinforces the "Exact" nature.

        A = np.zeros((6, 6))
        A[0:3, 3:6] = np.eye(3)

        # df_v / dr
        # We need d(ax)/drx, d(ax)/dry, etc.

        mu = self.mu
        rt = self.r_t
        n = self.n

        # Helper for gravity gradient
        def gravity_gradient(pos_vec: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
            """Compute gravity gradient matrix."""
            # pos_vec = [rt+rx, ry, rz]
            r_norm = np.linalg.norm(pos_vec)
            # -mu * r / |r|^3
            # Jacobian is -mu/|r|^3 * (I - 3 * r * r^T / |r|^2)
            mat = -(mu / r_norm**3) * (np.eye(3) - 3 * np.outer(pos_vec, pos_vec) / r_norm**2)
            return np.array(mat)

        pos_chaser = np.array([rt + rx, ry, rz])
        grad_grav = gravity_gradient(pos_chaser)

        # Centrifugal/Coriolis matrix parts
        # Dynamics: v_dot = F_grav + F_centrifugal + F_coriolis + F_control
        # F_centrifugal = [n^2(rt+rx), n^2 ry, 0]
        # F_coriolis = [2n vy, -2n vx, 0]

        # d(F_centrifugal)/dr
        dFcent_dr = np.zeros((3, 3))
        dFcent_dr[0, 0] = n**2
        dFcent_dr[1, 1] = n**2

        # d(F_grav)/dr is grad_grav

        # d(v_dot)/dr = dFcent_dr + grad_grav
        A[3:6, 0:3] = dFcent_dr + grad_grav

        # d(v_dot)/dv (Coriolis)
        # ax has +2n vy -> dax/dvy = 2n
        # ay has -2n vx -> day/dvx = -2n
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
        """Initialize quadrotor parameters."""
        self.m = m
        self.L = L  # Arm length
        self.moment_inertia = moment_inertia
        self.g = g

    def dynamics(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any] | float | list[float]
    ) -> np.ndarray[Any, Any]:
        """Compute quadrotor dynamics."""
        assert not isinstance(u, float | int), "Control input must be a vector"
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
        """Linearize quadrotor dynamics."""
        assert not isinstance(u, float | int), "Control input must be a vector"
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
        """Initialize robot arm parameters."""
        self.m1 = m1
        self.m2 = m2
        self.l1 = l1
        self.l2 = l2
        self.g = g

    def dynamics(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any] | float | list[float]
    ) -> np.ndarray[Any, Any]:
        """Compute robot arm dynamics."""
        assert not isinstance(u, float | int), "Control input must be a vector"
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
        """Linearize robot arm dynamics (numerical)."""
        assert not isinstance(u, float | int), "Control input must be a vector"
        # Using numerical linearization for the 2-link arm due to complexity
        epsilon = 1e-6
        n = 4
        m = 2

        A = np.zeros((n, n))
        B = np.zeros((n, m))

        f0 = self.dynamics(x, u)

        # Compute A
        for i in range(n):
            x_pert = x.copy()
            x_pert[i] += epsilon
            f_pert = self.dynamics(x_pert, u)
            A[:, i] = (f_pert - f0) / epsilon

        # Compute B
        u_arr = np.array(u, dtype=float)
        for i in range(m):
            u_pert = u_arr.copy()
            u_pert[i] += epsilon
            f_pert = self.dynamics(x, u_pert)
            B[:, i] = (f_pert - f0) / epsilon

        return A, B
