"""Prescribed oscillator ledger for a pedagogical figure, not a shaft fit."""

import numpy as np
from numpy.typing import NDArray

MASS_KG = 0.2
STIFFNESS_N_M = 80.0
DAMPING_N_S_M = 0.8
AMPLITUDE_M = 0.025
DURATION_S = 0.6


def prescribed_cycle() -> dict[str, NDArray[np.float64]]:
    """Return one fixed SI-unit illustration with signed input and passive loss.

    The drive enforces x=A sin²(pi t/T). Its power is determined by the required
    force m xddot + c xdot + k x, rather than prescribed independently of motion.
    No parameters or traces come from a golfer or an equipment calibration.
    """
    time = np.linspace(0, DURATION_S, 4001)
    frequency = np.pi / DURATION_S
    displacement = AMPLITUDE_M * np.sin(frequency * time) ** 2
    velocity = AMPLITUDE_M * frequency * np.sin(2 * frequency * time)
    acceleration = 2 * AMPLITUDE_M * frequency**2 * np.cos(2 * frequency * time)
    conservative_force = MASS_KG * acceleration + STIFFNESS_N_M * displacement
    return {
        "time": time,
        "displacement": displacement,
        "velocity": velocity,
        "elastic": STIFFNESS_N_M * displacement**2 / 2,
        "kinetic": MASS_KG * velocity**2 / 2,
        "input_power": (conservative_force + DAMPING_N_S_M * velocity) * velocity,
        "dissipation": DAMPING_N_S_M * velocity**2,
        "energy_rate": conservative_force * velocity,
    }
