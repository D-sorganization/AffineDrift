"""Synthetic slack take-up study for "Slack Take-Up as a Witness" (#5136).

Three manufactured toys ask whether the order and timing of dead-zone take-up events carry
information about which end of a chain supplies the drive. Nothing here is a golfer model and
every parameter is declared, not identified.

* Toy A: a four-car train driven at either end (positive control).
* Toy B: lead hand, club and trail hand on one rotation axis, with both hands driving.
* Toy C: an exact rank count on the spatial two-hand grasp kernel.

A take-up event is the first instant at which a coupler stretch leaves the open band
``|e| < half_gap``. A coupler that starts at or beyond its band edge has no take-up until it
first re-enters the band. The dead zone is memoryless; backlash memory is not modelled.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]
Mask = NDArray[np.bool_]

SEED = 5136
TRAIN_TRIALS = 400
TEST_TRIALS = 400
PASS_MARGIN = 0.2  # held-out Wilson 95% lower bound must exceed chance (0.5) by this
WILSON_Z = 1.959964  # two-sided 95% normal quantile

# Toy A, dimensionless manufactured units.
TRAIN_CARS = 4
TRAIN_GAP = 1.0
TRAIN_STIFFNESS = 50.0
TRAIN_DAMPING = 2.0
TRAIN_DRIVE = 1.0


@dataclass(frozen=True)
class Chain:
    """A line of bodies joined by dead-zone couplers, batched over trials.

    ``inertia`` has shape ``(n,)``; ``forces`` has shape ``(trials, n)`` and is applied from
    ``t = 0``; ``half_gap``, ``stiffness`` and ``offset`` (initial stretch) have shape
    ``(trials, n - 1)``. Coupler ``i`` has stretch ``x[i] - x[i + 1] + offset[i]``.
    """

    inertia: Array
    forces: Array
    half_gap: Array
    stiffness: Array
    offset: Array
    damping: float


@dataclass(frozen=True)
class Clock:
    """Fixed integration step and horizon in the chain's time unit."""

    step: float
    horizon: float


TRAIN_CLOCK = Clock(step=1e-3, horizon=30.0)


def _validate(chain: Chain, clock: Clock) -> None:
    """Reject shapes and values that would make the integration meaningless."""
    trials, bodies = chain.forces.shape
    if chain.inertia.shape != (bodies,) or np.any(chain.inertia <= 0):
        raise ValueError("inertia must be positive with one entry per body")
    for name in ("half_gap", "stiffness", "offset"):
        if getattr(chain, name).shape != (trials, bodies - 1):
            raise ValueError(f"{name} must have shape (trials, bodies - 1)")
    if np.any(chain.half_gap < 0) or np.any(chain.stiffness <= 0):
        raise ValueError("half_gap must be non-negative and stiffness positive")
    if not 0 < clock.step < clock.horizon:
        raise ValueError("step must be positive and shorter than the horizon")


def _coupler_force(chain: Chain, stretch: Array, rate: Array) -> Array:
    """Dead-zone spring plus damping that acts only beyond the band edge."""
    excess = np.abs(stretch) - chain.half_gap
    engaged = excess > 0
    elastic = chain.stiffness * np.sign(stretch) * np.maximum(excess, 0.0)
    return np.where(engaged, elastic + chain.damping * rate, 0.0)


def simulate(chain: Chain, clock: Clock, record: bool = False) -> tuple[Array, Array | None]:
    """Integrate the chain from rest with semi-implicit Euler.

    Returns the first take-up time of every coupler (``nan`` if none before the horizon) and,
    when ``record`` is true, positions of shape ``(steps + 1, trials, n)``.
    """
    _validate(chain, clock)
    trials, bodies = chain.forces.shape
    position = np.zeros((trials, bodies))
    velocity = np.zeros((trials, bodies))
    events = np.full((trials, bodies - 1), np.nan)
    stretch = chain.offset.copy()
    steps = int(round(clock.horizon / clock.step))
    history = [position.copy()] if record else None
    for index in range(steps):
        rate = velocity[:, :-1] - velocity[:, 1:]
        force = _coupler_force(chain, stretch, rate)
        net = chain.forces.copy()
        net[:, :-1] -= force
        net[:, 1:] += force
        velocity += clock.step * net / chain.inertia
        position += clock.step * velocity
        new_stretch = position[:, :-1] - position[:, 1:] + chain.offset
        before, after = np.abs(stretch), np.abs(new_stretch)
        hit = (before < chain.half_gap) & (after >= chain.half_gap) & np.isnan(events)
        fraction = (chain.half_gap - before) / np.where(hit, after - before, 1.0)
        events = np.where(hit, (index + fraction) * clock.step, events)
        stretch = new_stretch
        if history is not None:
            history.append(position.copy())
    return events, (np.asarray(history) if history is not None else None)


def simulate_traced(chain: Chain, clock: Clock) -> tuple[Array, Array]:
    """Like :func:`simulate` with ``record=True``, returning events and the position history."""
    events, history = simulate(chain, clock, record=True)
    if history is None:
        raise RuntimeError("simulate did not record a history")
    return events, history


def train_chain(rng: np.random.Generator, front: Mask, taut: bool) -> Chain:
    """Toy A trials: unit drive at the front car (``front`` true) or the rear car.

    Gaps and stiffness vary by +/-50% and the slack state is uniform over 80% of the band. A
    ``taut`` train starts with every coupler at its tension edge.
    """
    trials, couplers = front.size, TRAIN_CARS - 1
    gap = TRAIN_GAP * rng.uniform(0.5, 1.5, (trials, couplers))
    forces = np.zeros((trials, TRAIN_CARS))
    forces[front, 0] = TRAIN_DRIVE
    forces[~front, -1] = TRAIN_DRIVE
    offset = gap.copy() if taut else gap * rng.uniform(-0.8, 0.8, (trials, couplers))
    stiffness = TRAIN_STIFFNESS * rng.uniform(0.5, 1.5, (trials, couplers))
    return Chain(np.ones(TRAIN_CARS), forces, gap, stiffness, offset, TRAIN_DAMPING)


def train_order_accuracy(rng: np.random.Generator, trials: int, taut: bool) -> dict[str, float]:
    """Score the fixed rule "the end whose coupler takes up first is the driven end"."""
    front = np.arange(trials) % 2 == 0
    events, _ = simulate(train_chain(rng, front, taut), TRAIN_CLOCK)
    first, last = events[:, 0], events[:, -1]
    both = ~np.isnan(first) & ~np.isnan(last)
    guess = np.where(both, first < last, rng.random(trials) < 0.5)
    guess = np.where(np.isnan(first) & ~np.isnan(last), False, guess)
    guess = np.where(~np.isnan(first) & np.isnan(last), True, guess)
    return {"accuracy": float(np.mean(guess == front)), "with_events": float(np.mean(both))}


def wilson_interval(successes: int, trials: int) -> tuple[float, float]:
    """Wilson score 95% interval for a binomial proportion."""
    if trials <= 0 or not 0 <= successes <= trials:
        raise ValueError("need 0 <= successes <= trials and trials > 0")
    share, z2 = successes / trials, WILSON_Z**2
    centre = (share + z2 / (2 * trials)) / (1 + z2 / trials)
    half = WILSON_Z * np.sqrt(share * (1 - share) / trials + z2 / (4 * trials**2))
    half /= 1 + z2 / trials
    return float(centre - half), float(centre + half)
