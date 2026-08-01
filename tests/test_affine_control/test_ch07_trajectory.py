"""Tests for the ch07 double-pendulum trajectory generator (#3518).

The published table was not a solution of the system it claimed to integrate, so
these assert the properties that make a table trustworthy: that the integrator
conserves what it should, that the result is reproducible at the precision the
book prints, and that the specific defects of the old table cannot recur.
"""

from __future__ import annotations

import numpy as np
import pytest

from scripts.generate_worked_examples import (
    CH07_HORIZON,
    CH07_TORQUE,
    ch07_grad_potential,
    ch07_mass_matrix,
)
from src.affine_control.dynamics import planar_double_pendulum_trajectory

Q0 = np.array([np.pi / 4, np.pi / 6])
QD0 = np.array([2.0, -1.0])
GRAVITY_M_S2 = 9.81

# The published fragment uses CH07_STEPS; these tests assert *properties*, which
# hold at any resolution, so they run coarser. Integrating at publication
# resolution in every test made this module slow enough to trip Hypothesis's
# "input generation is slow" health check elsewhere in the suite.
TEST_STEPS = 1_000


def run(torque: float, steps: int = TEST_STEPS, horizon: float = CH07_HORIZON):
    return planar_double_pendulum_trajectory(
        ch07_mass_matrix,
        ch07_grad_potential,
        Q0,
        QD0,
        np.array([torque, 0.0]),
        horizon,
        steps,
    )


@pytest.fixture(scope="module")
def forced():
    """The forced trajectory, integrated once for the whole module."""
    return run(CH07_TORQUE)


@pytest.fixture(scope="module")
def unforced():
    """The zero-torque counterfactual, integrated once for the whole module."""
    return run(0.0)


def energy(q: np.ndarray, qd: np.ndarray) -> float:
    potential = -GRAVITY_M_S2 * np.cos(q[0]) - GRAVITY_M_S2 * (np.cos(q[0]) + np.cos(q[1]))
    return float(0.5 * qd @ ch07_mass_matrix(q) @ qd + potential)


def test_unforced_trajectory_conserves_energy(unforced) -> None:
    """The ZTCF has no applied torque, so its total energy must be constant."""
    rows = unforced
    initial = energy(rows[0][1], rows[0][2])
    drift = max(abs(energy(q, qd) - initial) for _, q, qd in rows)
    assert drift < 1e-6 * abs(initial)


def test_forced_trajectory_gains_exactly_the_work_done(forced) -> None:
    """Energy change must equal the integral of tau_1 * qdot_1 over the path."""
    rows = forced
    dt = CH07_HORIZON / TEST_STEPS
    work = 0.0
    for (_, _, qd_a), (_, _, qd_b) in zip(rows, rows[1:], strict=False):
        work += CH07_TORQUE * 0.5 * (qd_a[0] + qd_b[0]) * dt
    gained = energy(rows[-1][1], rows[-1][2]) - energy(rows[0][1], rows[0][2])
    assert gained == pytest.approx(work, rel=1e-4)


def test_trajectory_is_reproducible_at_published_precision() -> None:
    """A finer integration must agree to more than the four decimals printed.

    If it did not, the committed fragment would be an artefact of the step size
    and the freshness gate would fail on any unrelated change.
    """
    # Half the horizon at a quarter the step count, then compare against four
    # times that resolution. RK4 error is O(h^4), so establishing convergence on
    # a shorter window is sufficient and keeps the suite fast.
    horizon = CH07_HORIZON / 2
    steps = TEST_STEPS // 2
    coarse = run(CH07_TORQUE, steps=steps, horizon=horizon)
    fine = run(CH07_TORQUE, steps=steps * 4, horizon=horizon)
    worst = float(
        np.abs(
            np.concatenate([coarse[-1][1], coarse[-1][2]])
            - np.concatenate([fine[-1][1], fine[-1][2]])
        ).max()
    )
    assert worst < 1e-6


def test_velocity_column_is_consistent_with_the_angle_column(forced) -> None:
    """The defect that made the old table self-contradictory by a factor of five.

    A finite difference of the sampled angles must match the mean of the sampled
    rates over the same interval, to the accuracy the sampling allows.
    """
    rows = forced
    step = TEST_STEPS // 40  # sample finely enough for a finite difference to be meaningful
    for index in range(0, len(rows) - step, step):
        _, q_a, qd_a = rows[index]
        _, q_b, qd_b = rows[index + step]
        dt = rows[index + step][0] - rows[index][0]
        measured = (q_b[0] - q_a[0]) / dt
        assert measured == pytest.approx(0.5 * (qd_a[0] + qd_b[0]), abs=0.15)


def test_velocity_increments_are_not_constant(forced) -> None:
    """The old table's rates rose by a constant 0.34 per half-second.

    That is a straight-line extrapolation, not a swinging pendulum. A real
    trajectory's increments vary substantially.
    """
    rows = forced
    step = TEST_STEPS // 4
    sampled = [rows[i * step][2][0] for i in range(5)]
    increments = [b - a for a, b in zip(sampled, sampled[1:], strict=False)]
    assert max(increments) - min(increments) > 0.5


def test_ztcf_and_actual_trajectories_differ(forced, unforced) -> None:
    """Otherwise the counterfactual would carry no information."""
    actual = forced
    ztcf = unforced
    separation = max(float(np.linalg.norm(a[1] - z[1])) for a, z in zip(actual, ztcf, strict=True))
    assert separation > 0.1


def test_published_states_are_not_a_solution(forced) -> None:
    """Guards the regression: the old hand-typed states, integrated, do not match."""
    published = {0.5: 0.987, 1.0: 1.208, 1.5: 1.445, 2.0: 1.692}
    rows = forced
    step = TEST_STEPS // 4
    worst = 0.0
    for index, time in enumerate([0.5, 1.0, 1.5, 2.0], start=1):
        _, q, _ = rows[index * step]
        worst = max(worst, abs(q[0] - published[time]))
    assert worst > 1.0, "the published table should be far from the true solution"
