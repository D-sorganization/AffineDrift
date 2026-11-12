"""Pinned simulations backing core-theory SVG figures (#5590).

Each public function reads a committed JSON pin under ``data/core_theory/`` and
returns arrays consumed by ``scripts/core_theory_figures/``. The pins record
model parameters, initial states, and solver settings so figures are not drawn
from closed-form logistic or polynomial placeholders.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import partial
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from src.affine_control.double_pendulum_affine import (
    DoublePendulumParams,
    generalized_torque,
    grad_potential,
)
from src.affine_control.dynamics import (
    double_pendulum_coriolis,
    double_pendulum_mass_matrix,
    planar_double_pendulum_trajectory,
)
from src.affine_control.golf_model import SEGMENTS, GolfModel
from src.affine_control.ztcf_explorer import actual_trajectory

type Array = NDArray[np.float64]

REPO_ROOT = Path(__file__).resolve().parents[2]
ZTcf_PIN = REPO_ROOT / "data/core_theory/ztcf_figure_run_v1.json"
SUP_BREAKDOWN_PIN = REPO_ROOT / "data/core_theory/superposition_breakdown_run_v1.json"
SUP_PARALLELOGRAM_PIN = REPO_ROOT / "data/core_theory/superposition_parallelogram_run_v1.json"

__all__ = [
    "InstantaneousAccelerationVectors",
    "ModalResponseBars",
    "SuperpositionBreakdownSeries",
    "ZtcfFigureSeries",
    "load_json_pin",
    "superposition_breakdown_series",
    "superposition_instantaneous_vectors",
    "superposition_modal_responses",
    "ztcf_figure_series",
]


def load_json_pin(path: Path) -> dict:
    """Load one core-theory figure pin record."""
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class ZtcfFigureSeries:
    """Time series for the three ZTCF teaching-model figures."""

    time_s: Array
    actual_speed_m_s: Array
    actual_tip_xy: Array
    branch_steps: tuple[int, ...]
    branch_speeds_m_s: dict[int, Array]
    branch_tip_xy: dict[int, Array]
    distal_drift_qdd: Array
    distal_input_qdd: Array


@dataclass(frozen=True)
class SuperpositionBreakdownSeries:
    """Finite-horizon superposition breakdown for the double pendulum."""

    time_s: Array
    exact_q1: Array
    naive_q1: Array
    drift_q1: Array
    position_error_norm: Array
    velocity_error_norm: Array
    torque_scales: tuple[float, ...]
    scaled_position_error_norm: dict[float, Array]


@dataclass(frozen=True)
class InstantaneousAccelerationVectors:
    """Joint acceleration vectors for the parallelogram figure."""

    baseline: Array
    delta_u1: Array
    delta_u2: Array
    combined: Array


@dataclass(frozen=True)
class ModalResponseBars:
    """Unit-torque induced accelerations at a pinned GolfModel configuration."""

    joint_labels: tuple[str, ...]
    responses: Array


def _fixture_initial_state(pin: dict) -> tuple[Array, Array]:
    """Load ``(q, qd)`` from the JSON fixture path referenced by a figure pin."""
    fixture = json.loads((REPO_ROOT / pin["model_fixture"]).read_text(encoding="utf-8"))
    q = np.asarray(fixture["state"]["q"], dtype=float)
    qd = np.asarray(fixture["state"]["qd"], dtype=float)
    return q, qd


def _integrate_branches(
    model: GolfModel,
    actual: list,
    horizon: float,
    steps: int,
    branch_steps: tuple[int, ...],
) -> tuple[dict[int, Array], dict[int, Array]]:
    """Return clubhead tip paths and speed traces for each ZTCF branch."""
    branch_speeds: dict[int, Array] = {}
    branch_tips: dict[int, Array] = {}
    for step in branch_steps:
        t_i, q_i, qd_i, _ = actual[step]
        rolled = model.ztcf_trajectory(q_i, qd_i, horizon - t_i, steps - step)
        branch = actual[: step + 1] + [(t_i + t, q, qd, speed) for t, q, qd, speed in rolled[1:]]
        branch_speeds[step] = np.array([row[3] for row in branch], dtype=float)
        branch_tips[step] = np.stack([model.joint_positions(row[1])[-1] for row in branch])
    return branch_speeds, branch_tips


def ztcf_figure_series(pin_path: Path = ZTcf_PIN) -> ZtcfFigureSeries:
    """Simulate the registered GolfModel constant-torque run and ZTCF branches."""
    pin = load_json_pin(pin_path)
    q0, qd0 = _fixture_initial_state(pin)
    torque = np.asarray(pin["declared_torque_nm"], dtype=float)
    horizon, steps = float(pin["horizon_s"]), int(pin["steps"])
    model = SEGMENTS
    actual = actual_trajectory(model, q0, qd0, torque, horizon, steps)
    times = np.array([row[0] for row in actual], dtype=float)
    speeds = np.array([row[3] for row in actual], dtype=float)
    tips = np.stack([model.joint_positions(row[1])[-1] for row in actual])
    branch_steps = tuple(int(value) for value in pin["branch_intervention_steps"])
    branch_speeds, branch_tips = _integrate_branches(model, actual, horizon, steps, branch_steps)
    drift = []
    inputs = []
    for _, q, qd, _ in actual:
        drift.append(model.drift_acceleration(q, qd)[2])
        inputs.append(model.input_acceleration(q, torque)[2])
    return ZtcfFigureSeries(
        time_s=times,
        actual_speed_m_s=speeds,
        actual_tip_xy=tips,
        branch_steps=branch_steps,
        branch_speeds_m_s=branch_speeds,
        branch_tip_xy=branch_tips,
        distal_drift_qdd=np.asarray(drift, dtype=float),
        distal_input_qdd=np.asarray(inputs, dtype=float),
    )


def _position_superposition_error(
    q0: Array,
    qd0: Array,
    params: DoublePendulumParams,
    u1: Array,
    u2: Array,
    horizon: float,
    steps: int,
) -> tuple[Array, Array, Array, Array, Array, Array]:
    """Return trajectories and superposition error norms for one torque pair."""
    grad = partial(grad_potential, params=params)

    def run(torque: Array) -> list[tuple[float, Array, Array]]:
        """Integrate the pinned pendulum under constant generalized torque."""
        return planar_double_pendulum_trajectory(
            params.mass_matrix, grad, q0, qd0, torque, horizon, steps
        )

    x0 = run(np.zeros(2))
    xu1 = run(u1)
    xu2 = run(u2)
    xuc = run(u1 + u2)
    times = np.array([row[0] for row in x0], dtype=float)
    exact = np.array([row[1][0] for row in xuc], dtype=float)
    q_u1 = np.array([row[1][0] for row in xu1], dtype=float)
    q_u2 = np.array([row[1][0] for row in xu2], dtype=float)
    naive = q_u1 + q_u2
    naive -= np.array([row[1][0] for row in x0], dtype=float)
    drift = np.array([row[1][0] for row in x0], dtype=float)
    pos_err = []
    vel_err = []
    for index in range(len(times)):
        eq = xuc[index][1] - xu1[index][1] - xu2[index][1] + x0[index][1]
        ev = xuc[index][2] - xu1[index][2] - xu2[index][2] + x0[index][2]
        pos_err.append(float(np.linalg.norm(eq)))
        vel_err.append(float(np.linalg.norm(ev)))
    return times, exact, naive, drift, np.asarray(pos_err), np.asarray(vel_err)


def superposition_breakdown_series(
    pin_path: Path = SUP_BREAKDOWN_PIN,
) -> SuperpositionBreakdownSeries:
    """Simulate trajectory superposition breakdown for the pinned pendulum."""
    pin = load_json_pin(pin_path)
    p = pin["params"]
    params = DoublePendulumParams(
        m1=float(p["m1_kg"]),
        m2=float(p["m2_kg"]),
        l1=float(p["l1_m"]),
        l2=float(p["l2_m"]),
        gravity=float(p["gravity_m_s2"]),
    )
    q0 = np.asarray(pin["initial_state"]["q_rad"], dtype=float)
    qd0 = np.asarray(pin["initial_state"]["qd_rad_s"], dtype=float)
    u1 = generalized_torque(*pin["torques_nm"]["u1_shoulder_wrist"])
    u2 = generalized_torque(*pin["torques_nm"]["u2_shoulder_wrist"])
    horizon, steps = float(pin["horizon_s"]), int(pin["steps"])
    series = _position_superposition_error(q0, qd0, params, u1, u2, horizon, steps)
    scales = (0.2, 1.0, 2.0)
    scaled_errors: dict[float, Array] = {}
    for scale in scales:
        scaled_errors[scale] = _position_superposition_error(
            q0, qd0, params, scale * u1, scale * u2, horizon, steps
        )[4]
    return SuperpositionBreakdownSeries(
        time_s=series[0],
        exact_q1=series[1],
        naive_q1=series[2],
        drift_q1=series[3],
        position_error_norm=series[4],
        velocity_error_norm=series[5],
        torque_scales=scales,
        scaled_position_error_norm=scaled_errors,
    )


def _phi_without_gravity(q: Array, qd: Array, torque: Array) -> Array:
    """Return ``M^{-1}(tau - C(q, qdot) qdot)`` for the unit mid-link pendulum."""
    mass = double_pendulum_mass_matrix(q, 1.0, 1.0, 1.0, 1.0)
    bias = double_pendulum_coriolis(q, qd, 1.0, 1.0, 1.0) @ qd
    return np.linalg.solve(mass, torque - bias)


def superposition_instantaneous_vectors(
    pin_path: Path = SUP_PARALLELOGRAM_PIN,
) -> InstantaneousAccelerationVectors:
    """Instantaneous joint accelerations for the parallelogram schematic."""
    pin = load_json_pin(pin_path)
    q = np.asarray(pin["state"]["q_rad"], dtype=float)
    qd = np.asarray(pin["state"]["qd_rad_s"], dtype=float)
    tau1 = np.asarray(pin["torques_nm"]["tau1"], dtype=float)
    tau2 = np.asarray(pin["torques_nm"]["tau2"], dtype=float)
    baseline = _phi_without_gravity(q, qd, np.zeros(2))
    phi1 = _phi_without_gravity(q, qd, tau1)
    phi2 = _phi_without_gravity(q, qd, tau2)
    combined = _phi_without_gravity(q, qd, tau1 + tau2)
    return InstantaneousAccelerationVectors(
        baseline=baseline,
        delta_u1=phi1 - baseline,
        delta_u2=phi2 - baseline,
        combined=combined,
    )


def superposition_modal_responses(
    pin_path: Path = ZTcf_PIN,
    unit_torque_nm: float = 100.0,
) -> ModalResponseBars:
    """Cross-coupling bars from ``M(q)^{-1}`` at the ZTCF fixture configuration."""
    pin = load_json_pin(pin_path)
    q, _ = _fixture_initial_state(pin)
    model = SEGMENTS
    minv = np.linalg.inv(model.rigid_mass_matrix(q))
    responses = unit_torque_nm * minv
    return ModalResponseBars(
        joint_labels=("q1", "q2", "q3"),
        responses=np.asarray(responses, dtype=float),
    )
