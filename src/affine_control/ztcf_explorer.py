"""Reference computation for the WEB-06.4 ZTCF counterfactual explorer (#4534).

The browser widget ``js/ztcf-explorer.js`` mirrors this module; parity is pinned
by ``tests/fixtures/widgets/ztcf-explorer.parity.json``.

One declared, illustrative constant joint torque drives the registered planar
golf model from the state in ``data/ztcf/planar_golf_forward_fixture_v2.json``.
At a chosen intervention step the explorer branches a zero-torque counterfactual
from the *actual* state at that time and integrates both branches to the same
horizon. Each branch is written as a ``ZTCFIntervention`` record and replayed
through ``execute_ztcf_intervention``, so the widget shows the contract's own
rollout. The terminal difference is a simulated trajectory difference inside
this model, not a contribution fraction, a muscle measurement or a golfer
result (see ``critiques/ztcf_identifiability.md``).
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from src.affine_control.golf_model import GolfModel
from src.affine_control.ztcf_contract import (
    TerminalState,
    ZTCFIntervention,
    execute_ztcf_intervention,
    supported_model,
)

__all__ = [
    "DECLARED_TORQUE",
    "FIXTURE_PATH",
    "HORIZON",
    "STEPS",
    "ExplorerRun",
    "TerminalDifference",
    "actual_trajectory",
    "branch_intervention",
    "explore",
    "load_fixture",
]

type Array = NDArray[np.float64]
type Sample = tuple[float, Array, Array, float]

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "ztcf" / "planar_golf_forward_fixture_v2.json"
)
#: Declared illustrative joint torques (N*m), held constant; not fitted to a golfer.
DECLARED_TORQUE: tuple[float, float, float] = (40.0, 15.0, 3.0)
#: Horizon (s) and step count; the step size equals the fixture's 1 ms.
HORIZON = 0.2
STEPS = 200


@dataclass(frozen=True)
class TerminalDifference:
    """Actual minus zero-torque branch at the horizon."""

    q: Array
    qd: Array
    clubhead_speed: float


@dataclass(frozen=True)
class ExplorerRun:
    """One explorer evaluation: both branches, their difference and the record."""

    intervention_step: int
    actual: list[Sample]
    branch: list[Sample]
    difference: TerminalDifference
    record: ZTCFIntervention


def load_fixture(path: Path = FIXTURE_PATH) -> ZTCFIntervention:
    """Load and validate the registered forward ZTCF fixture."""
    return ZTCFIntervention.model_validate(json.loads(path.read_text(encoding="utf-8")))


def _forced_acceleration(model: GolfModel, q: Array, qd: Array, torque: Array) -> Array:
    """``qddot = f(x) + M(q)^-1 tau``: the drift plus the declared input term."""
    input_term = np.linalg.solve(model.rigid_mass_matrix(q), torque)
    return np.asarray(model.drift_acceleration(q, qd) + input_term, dtype=np.float64)


def actual_trajectory(
    model: GolfModel, q0: Array, qd0: Array, torque: Array, duration: float, steps: int
) -> list[Sample]:
    """Integrate the declared constant-torque run with the same fixed-step RK4."""
    dt = duration / steps

    def derivative(state: Array) -> Array:
        """State derivative of the driven system, ``[qdot, qddot]``."""
        pos, vel = state[:3], state[3:]
        return np.concatenate([vel, _forced_acceleration(model, pos, vel, torque)])

    state = np.concatenate([np.asarray(q0, dtype=float), np.asarray(qd0, dtype=float)])
    out: list[Sample] = [
        (0.0, state[:3].copy(), state[3:].copy(), model.clubhead_speed(state[:3], state[3:]))
    ]
    for index in range(steps):
        k1 = derivative(state)
        k2 = derivative(state + 0.5 * dt * k1)
        k3 = derivative(state + 0.5 * dt * k2)
        k4 = derivative(state + dt * k3)
        state = state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        out.append(
            (
                (index + 1) * dt,
                state[:3].copy(),
                state[3:].copy(),
                model.clubhead_speed(state[:3], state[3:]),
            )
        )
    return out


def _terminal(source: ZTCFIntervention, sample: Sample) -> TerminalState:
    """Express one branch sample as a terminal state in the source's frame and units."""
    time, q, qd, speed = sample
    return TerminalState(
        time=time,
        q=(float(q[0]), float(q[1]), float(q[2])),
        qd=(float(qd[0]), float(qd[1]), float(qd[2])),
        clubhead_speed=float(speed),
        frame=source.state.frame,
        position_units=source.state.position_units,
        velocity_units=source.state.velocity_units,
        speed_units="m/s",
    )


def branch_intervention(
    source: ZTCFIntervention,
    start_step: int,
    q: Array | tuple[float, ...],
    qd: Array | tuple[float, ...],
    expected: TerminalState,
) -> ZTCFIntervention:
    """Return the validated record of a branch from step ``start_step`` to ``HORIZON``.

    Raises ``ValueError`` unless ``execute_ztcf_intervention`` replays the record
    to exactly ``expected``.
    """
    record = source.model_dump()
    record["intervention_id"] = f"{source.intervention_id}/explorer-step-{start_step}"
    record["state"] |= {"q": [float(v) for v in q], "qd": [float(v) for v in qd]}
    record["integration"] |= {
        "start_time": start_step * (HORIZON / STEPS),
        "end_time": HORIZON,
        "steps": STEPS - start_step,
    }
    record["expected"] = expected.model_dump()
    intervention = ZTCFIntervention.model_validate(record)
    if execute_ztcf_intervention(intervention) != intervention.expected:
        raise ValueError("branch record does not replay to its expected terminal state")
    return intervention


def explore(
    intervention_step: int,
    torque: tuple[float, ...] = DECLARED_TORQUE,
    source: ZTCFIntervention | None = None,
) -> ExplorerRun:
    """Branch a ZTCF from the actual run at ``intervention_step`` and compare at ``HORIZON``."""
    if not isinstance(intervention_step, int) or not 0 <= intervention_step < STEPS:
        raise ValueError(f"intervention_step must be an integer in [0, {STEPS})")
    if len(torque) != 3 or not all(math.isfinite(value) for value in torque):
        raise ValueError("torque must be three finite joint torques")
    source = load_fixture() if source is None else source
    model = supported_model(source)
    actual = actual_trajectory(
        model,
        np.asarray(source.state.q),
        np.asarray(source.state.qd),
        np.asarray(torque, dtype=float),
        HORIZON,
        STEPS,
    )
    t_i, q_i, qd_i, _ = actual[intervention_step]
    relative = model.ztcf_trajectory(q_i, qd_i, HORIZON - t_i, STEPS - intervention_step)
    branch = [(t_i + t, q, qd, speed) for t, q, qd, speed in relative]
    record = branch_intervention(
        source, intervention_step, q_i, qd_i, _terminal(source, branch[-1])
    )
    _, q_a, qd_a, speed_a = actual[-1]
    _, q_b, qd_b, speed_b = branch[-1]
    difference = TerminalDifference(q=q_a - q_b, qd=qd_a - qd_b, clubhead_speed=speed_a - speed_b)
    return ExplorerRun(intervention_step, actual, branch, difference, record)
