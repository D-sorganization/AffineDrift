"""Physical segment and interface power for the textbook's two-rod example."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from src.tools.lagrangian_examples import RodPair

type Array = NDArray[np.float64]


@dataclass(frozen=True)
class EnergyLedger:
    """Energies in J and instantaneous powers in W for the declared inertial frame.

    The interface force acts on rod 2 at the shared hinge. Its opposite acts on
    rod 1. Motor 2 acts positively on rod 2 and negatively on rod 1. Gravitational
    potential has zero at the fixed base height, so individual values can be
    negative. No muscle, elasticity, contact-loss or metabolic model is implied.
    """

    kinetic: Array
    potential: Array
    mechanical_rates: Array
    interface_force: Array
    force_power: float
    club_moment_power: float
    actuator_power: float


def _centers(model: RodPair, state: Array, acceleration: Array) -> tuple[Array, Array, Array]:
    """Return rod-center positions, velocities and physical accelerations."""
    angles, rates = state[:2], state[2:]
    radial = np.column_stack([np.sin(angles), -np.cos(angles)])
    tangent = np.column_stack([np.cos(angles), np.sin(angles)])
    lengths = np.asarray(model.lengths)
    position = lengths[:, None] * radial
    velocity = (lengths * rates)[:, None] * tangent
    center_acceleration = lengths[:, None] * (
        acceleration[:, None] * tangent - rates[:, None] ** 2 * radial
    )
    for values in (position, velocity, center_acceleration):
        values[1] = values[0] + values[1] / 2
        values[0] /= 2
    return position, velocity, center_acceleration


def rod_energy_ledger(model: RodPair, state: Array, torques: Array) -> EnergyLedger:
    """Calculate physical energy rates independently of the generalized balance.

    Args:
        model: Shared uniform-rod model, fixed base and ideal planar hinges.
        state: Two absolute angles from downward, then their rates (rad, rad/s).
        torques: Base and relative-hinge motor torques, in N m.

    The shared model checks finite shapes and physical parameters. COM kinetic
    energy and Newton's force balance recover interface power; no coordinate
    coupling term is treated as a separate energy source.
    """
    state, torques = np.asarray(state, dtype=float), np.asarray(torques, dtype=float)
    acceleration = model.acceleration(state, torques)
    position, velocity, center_acceleration = _centers(model, state, acceleration)
    mass, lengths, rates = np.asarray(model.masses), np.asarray(model.lengths), state[2:]
    central = mass * lengths**2 / 12
    kinetic = (mass * np.sum(velocity**2, axis=1) + central * rates**2) / 2
    potential = mass * model.gravity * position[:, 1]
    mechanical_rates = mass * np.sum(velocity * center_acceleration, axis=1)
    mechanical_rates += central * rates * acceleration + mass * model.gravity * velocity[:, 1]
    force = mass[1] * (center_acceleration[1] + np.array([0, model.gravity]))
    return EnergyLedger(
        kinetic=kinetic,
        potential=potential,
        mechanical_rates=mechanical_rates,
        interface_force=force,
        force_power=float(force @ (2 * velocity[0])),
        club_moment_power=float(torques[1] * rates[1]),
        actuator_power=float(torques @ np.array([rates[0], rates[1] - rates[0]])),
    )
