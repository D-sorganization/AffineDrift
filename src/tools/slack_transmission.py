"""Two-channel slack transmission with interchangeable slack representations (#5135).

Each abstract actuator channel turns a desired torque into an equilibrium deflection, relaxes
toward it through first-order lags, and transmits torque through a declared characteristic.  The
dead-zone characteristic reproduces the published UpstreamDrift transmission law (dead zone,
linear series stiffness, first-order deflection lag) so the representations below can be
compared on the same task.  Every parameter is synthetic; none is an identified tissue, grip or
wrist property.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import brentq

type FloatArray = NDArray[np.float64]

ZERO_TOLERANCE_NM = 1e-12  # Torque magnitude counted as "zero transmission".
DELAY_FRACTION = 0.1  # Recovery = transmitted torque reaches 10% of target with the right sign.
BRACKET_GROWTH = 2.0  # Factor by which the inverse-characteristic bracket is widened.


class Shape(StrEnum):
    """Static torque-deflection characteristic of one channel."""

    DEAD_ZONE = "dead_zone"
    SMOOTH = "smooth"


@dataclass(frozen=True, slots=True)
class Representation:
    """One declared slack representation shared by both channels.

    ``dead_zone_rad`` is the gap (dead zone) or the softening length (smooth spring).  A positive
    ``activation_time_constant_s`` inserts a linear activation lag ahead of the deflection lag.
    ``wrist_time_constant_s`` (if given) gives the wrist channel its own deflection lag; otherwise
    both channels share ``time_constant_s``.
    """

    name: str
    shape: Shape
    dead_zone_rad: float
    time_constant_s: float = 0.018
    stiffness_nm_rad: float = 600.0
    activation_time_constant_s: float = 0.0
    wrist_time_constant_s: float | None = None

    @property
    def time_constants_s(self) -> tuple[float, float]:
        """Deflection lags of the (arm, wrist) channels."""
        wrist = (
            self.time_constant_s
            if self.wrist_time_constant_s is None
            else self.wrist_time_constant_s
        )
        return (self.time_constant_s, wrist)

    def __post_init__(self) -> None:
        """Validate representation parameters at construction."""
        if not self.name:
            raise ValueError("representation name must be non-empty")
        values = (self.dead_zone_rad, self.activation_time_constant_s)
        if not all(math.isfinite(value) and value >= 0.0 for value in values):
            raise ValueError("dead zone and activation time constant must be finite and >= 0")
        for positive in (*self.time_constants_s, self.stiffness_nm_rad):
            if not math.isfinite(positive) or positive <= 0.0:
                raise ValueError("time constant and stiffness must be finite and positive")


@dataclass(frozen=True, slots=True)
class Program:
    """Desired (arm, wrist) torques before and after the transition, in N m."""

    name: str
    pre_nm: tuple[float, float]
    post_nm: tuple[float, float]

    def __post_init__(self) -> None:
        """Validate program name and torque values."""
        if not self.name or not all(map(math.isfinite, (*self.pre_nm, *self.post_nm))):
            raise ValueError("program name must be non-empty and torques finite")


PERSISTENT = Program("persistent_direction", pre_nm=(10.0, -4.0), post_nm=(16.0, -6.0))
ROLE_REVERSAL = Program("role_reversal", pre_nm=(-4.0, 10.0), post_nm=(16.0, -6.0))


@dataclass(frozen=True, slots=True)
class Horizon:
    """Explicit-Euler grid for the post-transition interval."""

    duration_s: float = 0.25
    step_s: float = 1e-4

    def __post_init__(self) -> None:
        """Validate horizon duration and step size."""
        if not (0.0 < self.step_s <= self.duration_s) or not math.isfinite(self.duration_s):
            raise ValueError("step must be positive and no longer than a finite duration")

    @property
    def intervals(self) -> int:
        """Number of Euler steps in the post-transition interval."""
        return int(round(self.duration_s / self.step_s))


DEFAULT_HORIZON = Horizon()


@dataclass(frozen=True, slots=True)
class Trace:
    """Post-transition histories and the summary metrics reported by the article."""

    time_s: FloatArray
    desired_net_nm: float
    transmitted_nm: FloatArray  # shape (samples, 2): arm, wrist
    error_impulse_nms: float
    channel_error_impulse_nms: float
    peak_overshoot_nm: float
    zero_transmission_s: tuple[float, float]
    recovery_delay_s: tuple[float, float]


def channel_torque(deflection: FloatArray, rep: Representation) -> FloatArray:
    """Transmitted torque for an array of deflections (rad) under ``rep``'s characteristic."""
    magnitude = np.abs(deflection)
    gap = rep.dead_zone_rad
    if rep.shape is Shape.DEAD_ZONE or gap == 0.0:
        engaged = np.maximum(magnitude - gap, 0.0)
    else:
        engaged = magnitude - gap * np.log1p(magnitude / gap)
    return np.asarray(rep.stiffness_nm_rad * np.sign(deflection) * engaged, dtype=np.float64)


def command_deflection(torque_nm: float, rep: Representation) -> float:
    """Deflection whose steady transmitted torque equals ``torque_nm`` (inverse characteristic)."""
    if torque_nm == 0.0:
        return 0.0
    target = abs(torque_nm)
    if rep.shape is Shape.DEAD_ZONE or rep.dead_zone_rad == 0.0:
        return math.copysign(rep.dead_zone_rad + target / rep.stiffness_nm_rad, torque_nm)

    def residual(deflection: float) -> float:
        """Signed error between transmitted torque at deflection and the target."""
        return float(channel_torque(np.array([deflection]), rep)[0]) - target

    upper = target / rep.stiffness_nm_rad + rep.dead_zone_rad
    while residual(upper) < 0.0:
        upper *= BRACKET_GROWTH
    return math.copysign(float(brentq(residual, 0.0, upper, xtol=1e-15)), torque_nm)


def _targets(torques: tuple[float, float], rep: Representation) -> FloatArray:
    """Steady deflection targets for arm and wrist torques under ``rep``."""
    return np.array([command_deflection(value, rep) for value in torques], dtype=np.float64)


def _integrate(
    start: FloatArray, target: FloatArray, rep: Representation, grid: Horizon
) -> FloatArray:
    """Euler-integrate deflection (and activation, if declared) toward ``target``; rows are samples."""
    lags = 2 if rep.activation_time_constant_s > 0.0 else 1
    gains = (
        grid.step_s / np.asarray(rep.time_constants_s),
        grid.step_s / max(rep.activation_time_constant_s, grid.step_s),
    )
    deflection = np.empty((grid.intervals + 1, 2), dtype=np.float64)
    deflection[0] = start
    activation = start.copy()
    for index in range(grid.intervals):
        drive = target
        if lags == 2:
            activation = activation + gains[1] * (target - activation)
            drive = activation
        deflection[index + 1] = deflection[index] + gains[0] * (drive - deflection[index])
    return deflection


def _recovery(time: FloatArray, torque: FloatArray, target: float) -> float:
    """First time transmitted torque reaches the delay fraction of ``target``."""
    hits = np.flatnonzero(
        (np.sign(torque) == np.sign(target)) & (np.abs(torque) >= DELAY_FRACTION * abs(target))
    )
    return float(time[hits[0]]) if hits.size else float(time[-1])


def simulate(
    program: Program, rep: Representation, preloaded: bool = True, grid: Horizon | None = None
) -> Trace:
    """Simulate the post-transition interval from the loaded (or relaxed) pre-transition state.

    Postconditions: ``error_impulse_nms`` is the trapezoidal integral of
    ``|desired net - transmitted net|``; ``channel_error_impulse_nms`` sums the same integral
    over each channel's own target; ``peak_overshoot_nm`` is the largest excess of
    transmitted over desired net torque (zero if none); zero-transmission times are zero-sample
    occupancies.
    """
    grid = grid or DEFAULT_HORIZON
    start = _targets(program.pre_nm, rep) if preloaded else np.zeros(2)
    deflection = _integrate(start, _targets(program.post_nm, rep), rep, grid)
    torque = channel_torque(deflection, rep)
    time = np.arange(grid.intervals + 1, dtype=np.float64) * grid.step_s
    desired_net = float(sum(program.post_nm))
    signed_error = torque.sum(axis=1) - desired_net
    zero = np.count_nonzero(np.abs(torque) <= ZERO_TOLERANCE_NM, axis=0) * grid.step_s
    return Trace(
        time_s=time,
        desired_net_nm=desired_net,
        transmitted_nm=torque,
        error_impulse_nms=float(np.trapezoid(np.abs(signed_error), time)),
        channel_error_impulse_nms=float(
            np.trapezoid(np.abs(torque - np.asarray(program.post_nm)).sum(axis=1), time)
        ),
        peak_overshoot_nm=float(max(signed_error.max(), 0.0)),
        zero_transmission_s=(float(zero[0]), float(zero[1])),
        recovery_delay_s=(
            _recovery(time, torque[:, 0], program.post_nm[0]),
            _recovery(time, torque[:, 1], program.post_nm[1]),
        ),
    )


def relative_advantage(rep: Representation, grid: Horizon | None = None) -> float:
    """``(E_reversal - E_persistent) / E_persistent``; positive favours persistent direction."""
    grid = grid or DEFAULT_HORIZON
    persistent = simulate(PERSISTENT, rep, grid=grid).error_impulse_nms
    reversal = simulate(ROLE_REVERSAL, rep, grid=grid).error_impulse_nms
    return (reversal - persistent) / persistent


def preparation_split(internal_nm: float) -> Program:
    """Role-reversal preparation shifted by an internal pair (+c arm, -c wrist); net stays 6 N m.

    ``internal_nm = 14`` recovers the persistent-direction preparation exactly.
    """
    arm, wrist = ROLE_REVERSAL.pre_nm
    return Program(
        f"split_{internal_nm:g}", (arm + internal_nm, wrist - internal_nm), ROLE_REVERSAL.post_nm
    )


def play_operator(position: FloatArray, half_gap: float, initial_output: float = 0.0) -> FloatArray:
    """Kinematic play (backlash) operator ``y_n = clip(y_{n-1}, r_n - gap, r_n + gap)``."""
    if half_gap < 0.0 or not math.isfinite(half_gap):
        raise ValueError("half_gap must be finite and non-negative")
    output = np.empty_like(position, dtype=np.float64)
    previous = initial_output
    for index, value in enumerate(position):
        previous = min(max(previous, value - half_gap), value + half_gap)
        output[index] = previous
    return output
