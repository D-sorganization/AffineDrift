"""Consistent uniform-rod mechanics and a nonseparable integration example."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from src.core.constants import GRAVITY_M_S2

type Array = NDArray[np.float64]
RELATIVE_TO_ABSOLUTE = np.array([[1.0, 0.0], [1.0, 1.0]])
MOTOR_TO_ABSOLUTE_FORCE = np.array([[1.0, -1.0], [0.0, 1.0]])


def _vector(values: Array, size: int) -> Array:
    """Normalize finite vectors at the public calculation boundary."""
    result = np.asarray(values, dtype=float)
    if result.shape != (size,) or not np.isfinite(result).all():
        raise ValueError(f"expected a finite vector of length {size}")
    return result


def motor_generalized(torques: Array) -> Array:
    """Map base and elbow motor torques to absolute-angle generalized forces.

    Args:
        torques: Base torque and torque acting on rod 2 relative to rod 1.

    Returns:
        Forces conjugate to the two absolute angles. Power equals motor torque
        dotted with (first angular rate, second rate minus first rate).
    """
    return MOTOR_TO_ABSOLUTE_FORCE @ _vector(torques, 2)


@dataclass(frozen=True)
class RodPair:
    """Two uniform slender rods, fixed base, ideal planar hinges and gravity.

    Args:
        masses: Two positive masses in kilograms.
        lengths: Two positive lengths in metres.
        gravity: Nonnegative downward gravitational acceleration in m/s squared.

    Angles are absolute, counterclockwise from vertically downward. Rods have
    centre inertia m*l squared/12. Inputs to acceleration are physical motors,
    not forces independently applied to the two absolute coordinates.
    """

    masses: tuple[float, float] = (1.0, 1.0)
    lengths: tuple[float, float] = (1.0, 1.0)
    gravity: float = GRAVITY_M_S2

    def __post_init__(self) -> None:
        """Reject nonphysical rod parameters before evaluating dynamics."""
        for values in (self.masses, self.lengths):
            if np.any(_vector(np.asarray(values), 2) <= 0):
                raise ValueError("rod masses and lengths must be positive")
        if not np.isfinite(self.gravity) or self.gravity < 0:
            raise ValueError("gravity must be finite and nonnegative")

    def mass_matrix(self, angles: Array) -> Array:
        """Return the SPD kinetic Hessian for two finite absolute angles."""
        angles = _vector(angles, 2)
        first, second = self.masses
        proximal, distal = self.lengths
        coupling = second * proximal * distal * np.cos(angles[0] - angles[1]) / 2
        return np.array(
            [
                [(first / 3 + second) * proximal**2, coupling],
                [coupling, second * distal**2 / 3],
            ]
        )

    def coriolis_matrix(self, angles: Array, rates: Array) -> Array:
        """Return a Christoffel factor C with Mdot minus 2C skew-symmetric."""
        angles, rates = _vector(angles, 2), _vector(rates, 2)
        coupling = self.masses[1] * self.lengths[0] * self.lengths[1] / 2
        coefficient = coupling * np.sin(angles[0] - angles[1])
        return coefficient * np.array([[0, rates[1]], [-rates[0], 0]])

    def _potential_coefficients(self) -> Array:
        """Return gravity-energy coefficients for a pivot-height zero."""
        first, second = self.masses
        proximal, distal = self.lengths
        return self.gravity * np.array([(first / 2 + second) * proximal, second * distal / 2])

    def potential(self, angles: Array) -> float:
        """Return gravitational energy in joules with zero at pivot height."""
        return float(-self._potential_coefficients() @ np.cos(_vector(angles, 2)))

    def gravity_vector(self, angles: Array) -> Array:
        """Return positive potential gradient; applied gravity is its negative."""
        return self._potential_coefficients() * np.sin(_vector(angles, 2))

    def energy(self, state: Array) -> float:
        """Return mechanical energy for state (two angles, two angular rates)."""
        state = _vector(state, 4)
        kinetic = state[2:] @ self.mass_matrix(state[:2]) @ state[2:] / 2
        return float(kinetic + self.potential(state[:2]))

    def acceleration(self, state: Array, torques: Array) -> Array:
        """Solve accelerations from finite state and two physical motor torques."""
        state = _vector(state, 4)
        angles, rates = state[:2], state[2:]
        force = motor_generalized(torques) - self.gravity_vector(angles)
        force -= self.coriolis_matrix(angles, rates) @ rates
        return np.asarray(np.linalg.solve(self.mass_matrix(angles), force), dtype=np.float64)

    def relative_arm_terms(self, angles: Array, rates: Array) -> tuple[Array, Array, Array]:
        """Return M, C, G for relative joints with first angle from horizontal.

        Args:
            angles: Base angle from horizontal and relative elbow angle.
            rates: Their coordinate rates.

        Returns:
            Inertia, Christoffel factor and holding-gravity vector, all conjugate
            to relative coordinates. The constant chart derivative preserves power.
        """
        transform = RELATIVE_TO_ABSOLUTE
        absolute = transform @ _vector(angles, 2) + np.pi / 2
        velocity = transform @ _vector(rates, 2)
        return (
            transform.T @ self.mass_matrix(absolute) @ transform,
            transform.T @ self.coriolis_matrix(absolute, velocity) @ transform,
            transform.T @ self.gravity_vector(absolute),
        )


def variable_mass_step(state: Array, step: float) -> Array:
    """Take momentum-implicit symplectic Euler for H=exp(-2q)*p squared/2.

    Args:
        state: Finite scalar coordinate and its canonical momentum.
        step: Nonnegative finite time step, small enough for a real local branch.

    Returns:
        New (q, p) on the root continuous from step zero. This nondimensional
        free-particle example uses x=exp(q); it is not a general robot solver.
    """
    coordinate, momentum = _vector(state, 2)
    if not np.isfinite(step) or step < 0:
        raise ValueError("step must be finite and nonnegative")
    with np.errstate(over="ignore", invalid="ignore"):
        scale = np.exp(-2 * coordinate)
        discriminant = 1 - 4 * step * scale * momentum
    if not np.isfinite(scale) or not np.isfinite(discriminant) or discriminant <= 0:
        raise ValueError("step leaves the regular real implicit branch")
    updated = 2 * momentum / (1 + np.sqrt(discriminant))
    return np.array([coordinate + step * scale * updated, updated])
