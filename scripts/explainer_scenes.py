"""Scene definitions for the WEB-08.4 animated explainers (#4555).

Each explainer is generated from ``src/`` trajectories, never hand-animated:
the drift-versus-control scene replays the WEB-06.3 sandbox scenario through
``double_pendulum_affine.simulate`` and the ZTCF scene replays the WEB-06.4
explorer through ``ztcf_explorer.explore``. Captions are the single source for
the WebVTT track and the on-page transcript.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np

from scripts.generate_widget_parity import (
    SANDBOX_HORIZON,
    SANDBOX_PARAMS,
    SANDBOX_PRESETS,
    SANDBOX_Q0,
    SANDBOX_QD0,
    SANDBOX_STEPS,
)
from src.affine_control.double_pendulum_affine import (
    DoublePendulumParams,
    generalized_torque,
    simulate,
    tip_acceleration_split,
    tip_position,
)
from src.affine_control.ztcf_contract import supported_model
from src.affine_control.ztcf_explorer import HORIZON, STEPS, explore, load_fixture

FPS = 20
WIDTH, HEIGHT = 640, 400
INK, DRIFT, INPUT, GHOST = "#1f2937", "#2563eb", "#c2410c", "#6b7280"


@dataclass(frozen=True)
class Cue:
    """One caption: start and end in seconds, and its text."""

    start: float
    end: float
    text: str


@dataclass(frozen=True)
class Explainer:
    """One explainer: id, title, duration, captions, data sources and frame painter."""

    id: str
    title: str
    duration: float
    cues: tuple[Cue, ...]
    sources: tuple[str, ...]
    paint: Callable[[Any, float], None]
    poster_time: float


def _fraction(t: float, duration: float) -> float:
    """Animation progress in [0, 1], holding the last frame for the final 15 %."""
    return min(1.0, t / (0.85 * duration))


# ---------------------------------------------------------------------------
# Drift versus control (double pendulum)
# ---------------------------------------------------------------------------

_DP_PARAMS = DoublePendulumParams(**SANDBOX_PARAMS)
_DP_TORQUE = generalized_torque(**SANDBOX_PRESETS["shoulder-drive"])
_DP_RUN = simulate(_DP_PARAMS, SANDBOX_Q0, SANDBOX_QD0, _DP_TORQUE, SANDBOX_HORIZON, SANDBOX_STEPS)
_DP_GHOST = simulate(
    _DP_PARAMS, SANDBOX_Q0, SANDBOX_QD0, np.zeros(2), SANDBOX_HORIZON, SANDBOX_STEPS
)
_DP_TIPS = [
    tip_acceleration_split(s.q, s.qd, s.drift_qdd, s.input_qdd, _DP_PARAMS) for s in _DP_RUN
]


def _linkage(q: Any) -> np.ndarray:
    """Pivot, elbow and tip of the double pendulum, angles from the downward vertical."""
    elbow = (_DP_PARAMS.l1 * np.sin(q[0]), -_DP_PARAMS.l1 * np.cos(q[0]))
    return np.array([(0.0, 0.0), elbow, tuple(tip_position(q, _DP_PARAMS))])


def paint_drift_vs_control(ax: Any, t: float) -> None:
    """Draw the driven linkage, its zero-torque ghost and the tip-acceleration split."""
    index = round(_fraction(t, DRIFT_VS_CONTROL.duration) * (len(_DP_RUN) - 1))
    reach = _DP_PARAMS.l1 + _DP_PARAMS.l2
    ax.set_xlim(-1.05 * reach, 1.05 * reach)
    ax.set_ylim(-1.05 * reach, 1.05 * reach)
    if t >= 30.0:
        ghost = _linkage(_DP_GHOST[index].q)
        ax.plot(ghost[:, 0], ghost[:, 1], color=GHOST, lw=2, ls="--")
    points = _linkage(_DP_RUN[index].q)
    ax.plot(points[:, 0], points[:, 1], color=INK, lw=4, marker="o", ms=5)
    tip_drift, tip_input = _DP_TIPS[index]
    # Arrow lengths are rescaled each frame so both stay legible; compare them within a frame.
    scale = 0.45 * reach / max(float(np.hypot(*tip_drift)), float(np.hypot(*tip_input)), 1e-9)
    for vector, colour, shown in ((tip_drift, DRIFT, t >= 14.0), (tip_input, INPUT, t >= 22.0)):
        if shown:
            ax.annotate(
                "",
                xy=points[2] + scale * np.asarray(vector),
                xytext=points[2],
                arrowprops={"arrowstyle": "-|>", "color": colour, "lw": 2.5},
            )
    ax.text(
        0.02,
        0.96,
        f"t = {_DP_RUN[index].t:.3f} s (model time)",
        transform=ax.figure.transFigure,
        va="top",
        fontsize=10,
        color=INK,
    )
    if t >= 14.0:
        ax.text(
            0.02,
            0.89,
            "blue: drift",
            transform=ax.figure.transFigure,
            va="top",
            fontsize=10,
            color=DRIFT,
        )
    if t >= 22.0:
        ax.text(
            0.02,
            0.83,
            "orange: input",
            transform=ax.figure.transFigure,
            va="top",
            fontsize=10,
            color=INPUT,
        )
        ax.text(
            0.02,
            0.77,
            "arrows rescaled each frame",
            transform=ax.figure.transFigure,
            va="top",
            fontsize=8,
            color=GHOST,
        )


DRIFT_VS_CONTROL = Explainer(
    id="drift-vs-control",
    title="Drift and control in a two-link model",
    duration=44.0,
    cues=(
        Cue(0.0, 6.0, "A two-link model: an arm-like link and a club-like link, starting at rest."),
        Cue(6.0, 14.0, "At every state, the model's acceleration splits into two parts."),
        Cue(14.0, 22.0, "Blue arrow: drift, what the model does at this state with zero input."),
        Cue(22.0, 30.0, "Orange arrow: the extra acceleration from the declared shoulder torque."),
        Cue(
            30.0,
            38.0,
            "Dashed: a separate zero-torque run. The paths separate, so later drift "
            "belongs to states the torque helped reach.",
        ),
        Cue(38.0, 44.0, "Model output with illustrative values. It is not a golfer measurement."),
    ),
    sources=(
        "src/affine_control/double_pendulum_affine.py",
        "src/affine_control/dynamics.py",
        "scripts/generate_widget_parity.py",
    ),
    paint=paint_drift_vs_control,
    poster_time=34.0,
)


# ---------------------------------------------------------------------------
# Zero-torque counterfactual (three-link explorer)
# ---------------------------------------------------------------------------

_ZTCF_STEP = 50
_ZTCF_RUN = explore(_ZTCF_STEP)
_ZTCF_MODEL = supported_model(load_fixture())


def _chain(q: Any) -> np.ndarray:
    """Base, joints and club tip of the three-link chain."""
    angles = _ZTCF_MODEL.link_angles(q)
    points = [np.zeros(2)]
    for angle, length in zip(angles, _ZTCF_MODEL.lengths, strict=True):
        points.append(points[-1] + length * np.array([np.cos(angle), np.sin(angle)]))
    return np.array(points)


def paint_ztcf(ax: Any, t: float) -> None:
    """Draw the declared-torque run and, after the intervention, the zero-torque branch."""
    step = round(_fraction(t, ZTCF.duration) * STEPS)
    actual = _ZTCF_RUN.actual
    tips = np.array([_chain(s[1])[3] for s in actual[: step + 1]])
    every = np.concatenate([_chain(s[1]) for s in (*actual, *_ZTCF_RUN.branch)])
    lo, hi = every.min(axis=0) - 0.15, every.max(axis=0) + 0.15
    side = max(hi - lo) / 2
    centre = (hi + lo) / 2
    ax.set_xlim(centre[0] - side, centre[0] + side)
    ax.set_ylim(centre[1] - side, centre[1] + side)
    ax.plot(tips[:, 0], tips[:, 1], color=INK, lw=1.5)
    chain = _chain(actual[step][1])
    ax.plot(chain[:, 0], chain[:, 1], color=INK, lw=4, marker="o", ms=5)
    if step >= _ZTCF_STEP and t >= 14.0:
        k = step - _ZTCF_STEP
        branch_tips = np.array([_chain(s[1])[3] for s in _ZTCF_RUN.branch[: k + 1]])
        ax.plot(branch_tips[:, 0], branch_tips[:, 1], color=DRIFT, lw=1.5, ls="--")
        branch = _chain(_ZTCF_RUN.branch[k][1])
        ax.plot(branch[:, 0], branch[:, 1], color=DRIFT, lw=3, ls="--")
        start = _chain(actual[_ZTCF_STEP][1])
        ax.plot(start[:, 0], start[:, 1], color=GHOST, lw=1.5)
    speed = actual[step][3]
    ax.text(
        0.02,
        0.96,
        f"t = {actual[step][0]:.3f} s, run speed {speed:.2f} m/s",
        transform=ax.figure.transFigure,
        va="top",
        fontsize=10,
        color=INK,
    )
    if step == STEPS and t >= 30.0:
        ax.text(
            0.02,
            0.89,
            f"difference at {HORIZON} s: {_ZTCF_RUN.difference.clubhead_speed:.2f} m/s",
            transform=ax.figure.transFigure,
            va="top",
            fontsize=10,
            color=DRIFT,
        )


ZTCF = Explainer(
    id="ztcf",
    title="A zero-torque counterfactual, step by step",
    duration=44.0,
    cues=(
        Cue(0.0, 7.0, "A three-link model runs under a declared, constant joint torque."),
        Cue(7.0, 14.0, "At the intervention time, we copy the state of the model."),
        Cue(14.0, 22.0, "From that copy, a second branch runs with the torque set to zero."),
        Cue(22.0, 30.0, "Solid: the declared-torque run. Dashed: the zero-torque branch."),
        Cue(30.0, 38.0, "The gap at the end is a simulated difference inside this model."),
        Cue(
            38.0,
            44.0,
            "It is not a share of speed supplied by the golfer, and not a muscle measurement.",
        ),
    ),
    sources=(
        "src/affine_control/ztcf_explorer.py",
        "src/affine_control/golf_model.py",
        "src/affine_control/ztcf_contract.py",
        "data/ztcf/planar_golf_forward_fixture_v2.json",
    ),
    paint=paint_ztcf,
    poster_time=40.0,
)

EXPLAINERS: tuple[Explainer, ...] = (DRIFT_VS_CONTROL, ZTCF)
