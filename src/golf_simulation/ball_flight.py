"""Golf ball flight dynamics model.

Implements aerodynamic ball flight including drag, Magnus effect (spin-induced lift),
wind, and gravity. Compatible with the DynamicalSystem ABC for integration with
the AffineDrift control framework.

State vector: [x, y, z, vx, vy, vz, wx, wy, wz] (9D)
  - position (x,y,z) in meters
  - velocity (vx,vy,vz) in m/s
  - spin (wx,wy,wz) in rad/s

Control vector: [0, 0, 0] (no active control during flight - ballistic)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

from src.core.constants import GRAVITY_M_S2
from src.core.contracts import check_non_negative, check_positive, require
from src.tangent_models.examples import DynamicalSystem

logger = logging.getLogger(__name__)

AIR_DYNAMIC_VISCOSITY_PAS = 1.81e-5
GOLF_BALL_ZERO_LIFT_DRAG = 0.47
GOLF_BALL_DRAG_TRANSITION_RE = 1.6e5
GOLF_BALL_DRAG_TRANSITION_WIDTH = 2.5e4
GOLF_BALL_LIFT_RESPONSE = 4.5


@dataclass(frozen=True)
class BallFlightState:
    """Immutable snapshot of golf ball state during flight.

    Attributes:
        position: 3D position vector [x, y, z] in meters.
        velocity: 3D velocity vector [vx, vy, vz] in m/s.
        spin: 3D angular velocity vector [wx, wy, wz] in rad/s.
    """

    position: np.ndarray
    velocity: np.ndarray
    spin: np.ndarray

    def __post_init__(self) -> None:
        """Validate state dimensions."""
        require(len(self.position) == 3, "position must be a 3D vector")
        require(len(self.velocity) == 3, "velocity must be a 3D vector")
        require(len(self.spin) == 3, "spin must be a 3D vector")

    @property
    def speed(self) -> float:
        """Scalar speed (magnitude of velocity) in m/s."""
        return float(np.linalg.norm(self.velocity))

    @property
    def state_vector(self) -> np.ndarray:
        """Concatenated 9D state vector [x, y, z, vx, vy, vz, wx, wy, wz]."""
        return np.concatenate([self.position, self.velocity, self.spin])

    def __eq__(self, other: object) -> bool:
        """Check equality by comparing all arrays element-wise."""
        if not isinstance(other, BallFlightState):
            return NotImplemented
        return (
            np.array_equal(self.position, other.position)
            and np.array_equal(self.velocity, other.velocity)
            and np.array_equal(self.spin, other.spin)
        )

    def __hash__(self) -> int:
        """Hash based on state vector bytes."""
        return hash(self.state_vector.tobytes())


class BallFlightDynamics(DynamicalSystem):
    """Aerodynamic golf ball flight dynamics.

    Models drag, Magnus effect (spin-induced lift), wind, and gravity
    for a golf ball in flight. Implements the DynamicalSystem ABC for
    compatibility with AffineDrift's control framework.

    The system is ballistic (no active control), so the control input
    is a 3D zero vector by convention.
    """

    def __init__(
        self,
        mass: float = 0.04593,
        radius: float = 0.02135,
        rho: float = 1.225,
        cd: float = 0.23,
        cl: float = 0.54,
        gravity: float = GRAVITY_M_S2,
        wind: np.ndarray | None = None,
        spin_decay_rate: float = 0.05,
    ) -> None:
        """Initialize ball flight dynamics model.

        Args:
            mass: Ball mass in kg (regulation: 0.04593 kg).
            radius: Ball radius in meters (regulation: 0.02135 m).
            rho: Air density in kg/m^3 (sea level: 1.225).
            cd: High-Reynolds-number drag coefficient asymptote.
            cl: Lift-scale parameter for the spin-dependent Magnus model.
            gravity: Gravitational acceleration in m/s^2.
            wind: 3D wind velocity vector [wx, wy, wz] in m/s (default: no wind).
            spin_decay_rate: Exponential spin decay rate in 1/s.
        """
        check_positive(mass, "mass")
        check_positive(radius, "radius")
        check_positive(rho, "air density")
        check_non_negative(cd, "drag coefficient")
        check_non_negative(cl, "lift coefficient")
        check_positive(gravity, "gravity")
        check_non_negative(spin_decay_rate, "spin_decay_rate")

        self.mass = mass
        self.radius = radius
        self.rho = rho
        self.cd = cd
        self.cl = cl
        self.gravity = gravity
        self.wind = wind if wind is not None else np.zeros(3)
        self.spin_decay_rate = spin_decay_rate

        require(len(self.wind) == 3, "wind must be a 3D vector")

    @property
    def area(self) -> float:
        """Cross-sectional area of the ball in m^2."""
        return np.pi * self.radius**2

    def _reynolds_number(self, speed_rel: float) -> float:
        """Compute the ball Reynolds number for a relative air speed."""
        return (self.rho * speed_rel * (2.0 * self.radius)) / AIR_DYNAMIC_VISCOSITY_PAS

    def _drag_coefficient(self, speed_rel: float) -> float:
        """Return a velocity-dependent drag coefficient.

        The curve blends a low-speed sphere-like drag coefficient toward the
        golf-ball asymptote as Reynolds number rises through the drag crisis.
        """
        if speed_rel <= 0.0:
            return self.cd

        reynolds = self._reynolds_number(speed_rel)
        blend = 1.0 / (
            1.0
            + np.exp((reynolds - GOLF_BALL_DRAG_TRANSITION_RE) / GOLF_BALL_DRAG_TRANSITION_WIDTH)
        )
        return float(self.cd + (GOLF_BALL_ZERO_LIFT_DRAG - self.cd) * blend)

    def _lift_coefficient(self, speed_rel: float, spin: np.ndarray[Any, Any]) -> float:
        """Return a spin-dependent lift coefficient.

        The coefficient scales with the spin parameter r * |omega| / |v| and
        saturates smoothly so the force uses the standard 0.5 * rho * v^2 * C_L * A
        form rather than a volumetric proxy.
        """
        if speed_rel <= 0.0:
            return 0.0

        spin_mag = float(np.linalg.norm(spin))
        if spin_mag <= 0.0:
            return 0.0

        spin_parameter = self.radius * spin_mag / speed_rel
        return float(self.cl * (1.0 - np.exp(-GOLF_BALL_LIFT_RESPONSE * spin_parameter)))

    def _drag_force(self, v_rel: np.ndarray[Any, Any], speed_rel: float) -> np.ndarray[Any, Any]:
        """Return aerodynamic drag force: -0.5 * rho * cd(Re) * A * |v_rel| * v_rel."""
        cd_eff = self._drag_coefficient(speed_rel)
        return -0.5 * self.rho * cd_eff * self.area * speed_rel * v_rel

    def _magnus_force(
        self,
        v_rel: np.ndarray[Any, Any],
        speed_rel: float,
        spin: np.ndarray[Any, Any],
    ) -> np.ndarray[Any, Any]:
        """Return Magnus (spin-induced lift) force using 0.5 * rho * v^2 * C_L * A."""
        if speed_rel <= 0.0:
            return np.zeros(3)
        lift_direction = np.cross(spin, v_rel)
        lift_direction_norm = float(np.linalg.norm(lift_direction))
        if lift_direction_norm <= 0.0:
            return np.zeros(3)
        cl_eff = self._lift_coefficient(speed_rel, spin)
        return (
            0.5
            * self.rho
            * speed_rel**2
            * cl_eff
            * self.area
            * (lift_direction / lift_direction_norm)
        )

    def dynamics(
        self,
        x: np.ndarray[Any, Any],
        u: np.ndarray[Any, Any] | float | list[float],
    ) -> np.ndarray[Any, Any]:
        """Compute the 9D state derivative for ball flight.

        Args:
            x: State vector [x, y, z, vx, vy, vz, wx, wy, wz] (9D).
            u: Control input (unused for ballistic flight, expected 3D zero vector).

        Returns:
            State derivative vector (9D).
        """
        require(len(x) == 9, "state vector must have 9 elements")

        velocity = x[3:6]
        spin = x[6:9]

        v_rel = velocity - self.wind
        speed_rel = float(np.linalg.norm(v_rel))

        drag = self._drag_force(v_rel, speed_rel)
        magnus = self._magnus_force(v_rel, speed_rel, spin)
        gravity_force = np.array([0.0, 0.0, -self.mass * self.gravity])

        acceleration = (drag + magnus + gravity_force) / self.mass
        spin_derivative = -self.spin_decay_rate * spin

        dx = np.zeros(9)
        dx[0:3] = velocity
        dx[3:6] = acceleration
        dx[6:9] = spin_derivative
        return dx

    def linearize(
        self,
        x: np.ndarray[Any, Any],
        u: np.ndarray[Any, Any] | float | list[float],
    ) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
        """Linearize ball flight dynamics using central finite differences.

        Args:
            x: State vector (9D).
            u: Control input (3D).

        Returns:
            Tuple of (A, B) Jacobian matrices.
        """
        x_arr = np.array(x, dtype=float)
        u_arr = np.array(u, dtype=float) if not isinstance(u, float) else np.array([u])
        require(len(x_arr) == 9, "state vector must have 9 elements")

        n = len(x_arr)
        m = len(u_arr)
        epsilon = 1e-6

        A = np.zeros((n, n))
        B = np.zeros((n, m))

        # Compute A via central differences
        for i in range(n):
            x_plus = x_arr.copy()
            x_minus = x_arr.copy()
            x_plus[i] += epsilon
            x_minus[i] -= epsilon
            A[:, i] = (self.dynamics(x_plus, u_arr) - self.dynamics(x_minus, u_arr)) / (2 * epsilon)

        # Compute B via central differences
        for i in range(m):
            u_plus = u_arr.copy()
            u_minus = u_arr.copy()
            u_plus[i] += epsilon
            u_minus[i] -= epsilon
            B[:, i] = (self.dynamics(x_arr, u_plus) - self.dynamics(x_arr, u_minus)) / (2 * epsilon)

        return A, B

    @staticmethod
    def _state_from_vector(state_vec: np.ndarray[Any, Any]) -> BallFlightState:
        """Build an immutable BallFlightState from a 9D raw state vector."""
        return BallFlightState(
            position=state_vec[0:3].copy(),
            velocity=state_vec[3:6].copy(),
            spin=state_vec[6:9].copy(),
        )

    def _clamp_landing(
        self,
        state_vec: np.ndarray[Any, Any],
        trajectory: list[BallFlightState],
        t: float,
    ) -> None:
        """Clamp the final state to ground level and log the landing."""
        state_vec[2] = 0.0
        trajectory[-1] = self._state_from_vector(state_vec)
        logger.debug("Ball landed at t=%.3f s, x=%.1f, y=%.1f", t, state_vec[0], state_vec[1])

    def simulate(
        self,
        initial_state: BallFlightState,
        dt: float = 0.001,
        max_time: float = 15.0,
    ) -> list[BallFlightState]:
        """Simulate ball flight from initial conditions using RK4 integration.

        Integration proceeds until the ball hits the ground (z <= 0) or
        max_time is exceeded.

        Args:
            initial_state: Initial ball state (position, velocity, spin).
            dt: Integration timestep in seconds.
            max_time: Maximum simulation time in seconds.

        Returns:
            List of BallFlightState snapshots along the trajectory.
        """
        check_positive(dt, "timestep")
        check_positive(max_time, "max_time")

        u = np.zeros(3)
        state_vec = initial_state.state_vector.copy()
        trajectory: list[BallFlightState] = [initial_state]

        t = 0.0
        while t < max_time:
            state_vec = self._rk4_step(state_vec, u, dt)
            t += dt
            trajectory.append(self._state_from_vector(state_vec))

            # Stop if ball has hit the ground (z <= 0) after initial launch
            if state_vec[2] <= 0.0 and t > dt:
                self._clamp_landing(state_vec, trajectory, t)
                break

        return trajectory

    def _rk4_step(
        self,
        state_vec: np.ndarray[Any, Any],
        u: np.ndarray[Any, Any],
        dt: float,
    ) -> np.ndarray:
        """Perform a single RK4 integration step.

        Args:
            state_vec: Current 9D state vector.
            u: Control input (3D).
            dt: Timestep in seconds.

        Returns:
            Updated 9D state vector.
        """
        k1 = self.dynamics(state_vec, u)
        k2 = self.dynamics(state_vec + 0.5 * dt * k1, u)
        k3 = self.dynamics(state_vec + 0.5 * dt * k2, u)
        k4 = self.dynamics(state_vec + dt * k3, u)

        return np.asarray(state_vec + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4))
