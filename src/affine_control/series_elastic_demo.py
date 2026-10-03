"""Manufactured series-spring model with a massless junction and explicit work.

A force acts on mass x; a grounded damper acts on that same mass. Two linear
springs join x to fixed ground through a massless junction. The example has no
muscle activation, tendon slack, physiological identification or metabolic cost.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from math import isfinite, sqrt

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.integrate import solve_ivp

RELATIVE_TOLERANCE = 1e-10
ABSOLUTE_TOLERANCE = 1e-12
SAMPLES_PER_STAGE = 101


@dataclass(frozen=True)
class SeriesElasticParameters:
    """Illustrative SI parameters; values are not measurements from a golfer."""

    mass: float = 0.45
    damping: float = 50.0
    proximal_stiffness: float = 1000.0
    distal_stiffness: float = 5000.0

    def __post_init__(self) -> None:
        """Require finite positive inertia/stiffness and nonnegative damping."""
        values = (self.mass, self.proximal_stiffness, self.distal_stiffness)
        if not all(isfinite(value) and value > 0.0 for value in values):
            raise ValueError("mass and both stiffnesses must be positive and finite")
        if not isfinite(self.damping) or self.damping < 0.0:
            raise ValueError("damping must be nonnegative and finite")

    @property
    def effective_stiffness(self) -> float:
        """Series stiffness in N/m, evaluated without multiplying large values."""
        smaller = min(self.proximal_stiffness, self.distal_stiffness)
        larger = max(self.proximal_stiffness, self.distal_stiffness)
        return smaller / (1.0 + smaller / larger)

    @property
    def damping_ratio(self) -> float:
        """Dimensionless damping ratio of the reduced mechanical oscillator."""
        return self.damping / (2.0 * sqrt(self.mass * self.effective_stiffness))


@dataclass(frozen=True)
class LoadStage:
    """A constant force in N for a positive duration in seconds."""

    duration: float
    force: float

    def __post_init__(self) -> None:
        """Reject missing-duration intervals and nonfinite prescribed loads."""
        if not isfinite(self.duration) or self.duration <= 0.0:
            raise ValueError("stage duration must be positive and finite")
        if not isfinite(self.force):
            raise ValueError("stage force must be finite")


@dataclass(frozen=True)
class SeriesElasticTrace:
    """Sampled SI motion, signed actuator work and nonnegative dissipated energy."""

    parameters: SeriesElasticParameters
    time: NDArray[np.float64]
    position: NDArray[np.float64]
    velocity: NDArray[np.float64]
    actuator_work: NDArray[np.float64]
    dissipated_energy: NDArray[np.float64]
    force: NDArray[np.float64]

    @property
    def junction(self) -> NDArray[np.float64]:
        """Massless junction position satisfying equal spring forces."""
        return self.position * (
            self.parameters.effective_stiffness / self.parameters.distal_stiffness
        )

    @property
    def kinetic_energy(self) -> NDArray[np.float64]:
        """Mass kinetic energy in joules."""
        return 0.5 * self.parameters.mass * self.velocity**2

    @property
    def proximal_energy(self) -> NDArray[np.float64]:
        """Stored energy in the spring between the mass and the junction."""
        return 0.5 * self.parameters.proximal_stiffness * (self.position - self.junction) ** 2

    @property
    def distal_energy(self) -> NDArray[np.float64]:
        """Stored energy in the spring between the junction and fixed ground."""
        return 0.5 * self.parameters.distal_stiffness * self.junction**2

    @property
    def energy(self) -> NDArray[np.float64]:
        """Total kinetic and elastic storage; excludes accumulated work/loss."""
        return self.kinetic_energy + self.proximal_energy + self.distal_energy


def _derivative(
    state: NDArray[np.float64], parameters: SeriesElasticParameters, force: float
) -> NDArray[np.float64]:
    """Advance displacement, speed, supplied work and dissipated energy."""
    position, velocity = state[:2]
    acceleration = (
        force - parameters.damping * velocity - parameters.effective_stiffness * position
    ) / parameters.mass
    return np.array(
        [velocity, acceleration, force * velocity, parameters.damping * velocity**2],
        dtype=np.float64,
    )


def _integrate_stage(
    parameters: SeriesElasticParameters, stage: LoadStage, initial: NDArray[np.float64]
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Integrate one smooth interval; never step across a prescribed force jump."""
    result = solve_ivp(
        lambda time, state: _derivative(state, parameters, stage.force),
        (0.0, stage.duration),
        initial,
        t_eval=np.linspace(0.0, stage.duration, SAMPLES_PER_STAGE),
        method="DOP853",
        rtol=RELATIVE_TOLERANCE,
        atol=ABSOLUTE_TOLERANCE,
    )
    if not result.success or not np.all(np.isfinite(result.y)):
        raise RuntimeError(f"series-elastic integration failed: {result.message}")
    return np.asarray(result.t), np.asarray(result.y)


def simulate_series_elastic(
    parameters: SeriesElasticParameters, stages: Sequence[LoadStage], initial: ArrayLike
) -> SeriesElasticTrace:
    """Integrate a finite load schedule with continuous state at every switch.

    Initial values are displacement (m) and velocity (m/s). Work and loss start
    at zero. Force is right-continuous at internal switches; the final sample
    uses the last interval's force. Both springs are bilateral linear elements.
    """
    initial_state = np.array(initial, dtype=np.float64, copy=True)
    if initial_state.shape != (2,) or not np.all(np.isfinite(initial_state)):
        raise ValueError("initial state must contain finite displacement and velocity")
    if not stages or not all(isinstance(stage, LoadStage) for stage in stages):
        raise ValueError("at least one valid load stage is required")
    state = np.concatenate((initial_state, np.zeros(2)))
    times, states, forces = [], [], []
    elapsed = 0.0
    for index, stage in enumerate(stages):
        local_time, solution = _integrate_stage(parameters, stage, state)
        state = solution[:, -1].copy()
        keep = slice(None) if index == len(stages) - 1 else slice(None, -1)
        times.append(local_time[keep] + elapsed)
        states.append(solution[:, keep])
        forces.append(np.full(local_time[keep].shape, stage.force))
        elapsed += stage.duration
    position, velocity, work, loss = np.concatenate(states, axis=1)
    return SeriesElasticTrace(
        parameters, np.concatenate(times), position, velocity, work, loss, np.concatenate(forces)
    )
