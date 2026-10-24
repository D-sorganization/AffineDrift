"""Sensitivity studies behind "Managing Slack in Linked Systems" (#5135).

Each ``*_section`` function returns a JSON-ready mapping; the builder
``scripts/build_slack_management_data.py`` writes them to ``data/slack_management/results.json``
and draws the figures.  All parameters are synthetic sensitivity values.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import brentq

from src.tools.slack_transmission import (
    PERSISTENT,
    ROLE_REVERSAL,
    Horizon,
    Program,
    Representation,
    Shape,
    preparation_split,
    relative_advantage,
    simulate,
)

STUDY_HORIZON = Horizon(duration_s=0.5)  # >= 14 time constants for the slowest channel (35 ms).
REPRODUCTION_HORIZON = Horizon(duration_s=0.12)  # The window the published values imply.
DECLARED_GAP_RAD = 0.012
ACTIVATION_LAG_S = 0.010
UNEQUAL_LAGS_S = (0.018, 0.036)  # Arm, wrist; the counterexample in Argon's review (PR #5140).
EQUIVALENCE_MARGINS = (0.01, 0.05, 0.10)
GAP_GRID_RAD = tuple(float(value) for value in np.linspace(0.0, 0.03, 31))
TIME_CONSTANTS_S = (0.008, 0.018, 0.035)
INTERNAL_PAIR_GRID_NM = tuple(float(value) for value in np.arange(0.0, 24.5, 1.0))
PERSISTENT_INTERNAL_PAIR_NM = 14.0
FLOOR_TOLERANCE = 1e-9  # N m s; ties at the minimum are rounding noise, not a unique optimum.
UPSTREAM_STUDY_URL = (
    "https://github.com/D-sorganization/UpstreamDrift/blob/b700e58941205af6f673f13ebbffcd30f8cca9d8"
    "/docs/research/proximal_distal_energy_transfer/data/torque_allocation_preload_study.json"
)
PUBLISHED_IMPULSES_NMS = {  # torque_allocation_preload_study.json, transmission_results
    "persistent_direction_preloaded": 0.0717103076307577,
    "role_reversal_preloaded": 0.19540693388776567,
    "relaxed": 0.20107138073005523,
}
MUSCLE_MODEL_SOURCE = (
    "articles/proximal-distal-energy-transfer.qmd"
    "#preparation-history-with-activation-and-series-force-dynamics @ 20584d4"
)
MUSCLE_PERSISTENT_NMS = 0.08998
MUSCLE_REVERSAL_NMS = 0.09084

REPRESENTATIONS = (
    Representation("rigid", Shape.DEAD_ZONE, 0.0),
    Representation("dead_zone", Shape.DEAD_ZONE, DECLARED_GAP_RAD),
    Representation("smooth_stiffening", Shape.SMOOTH, DECLARED_GAP_RAD),
    Representation(
        "series_elastic_activation",
        Shape.DEAD_ZONE,
        0.0,
        activation_time_constant_s=ACTIVATION_LAG_S,
    ),
    Representation(
        "rigid_unequal_lags",
        Shape.DEAD_ZONE,
        0.0,
        UNEQUAL_LAGS_S[0],
        wrist_time_constant_s=UNEQUAL_LAGS_S[1],
    ),
)


def _summary(program: Program, rep: Representation, grid: Horizon) -> dict[str, object]:
    trace = simulate(program, rep, grid=grid)
    return {
        "error_impulse_nms": trace.error_impulse_nms,
        "channel_error_impulse_nms": trace.channel_error_impulse_nms,
        "peak_overshoot_nm": trace.peak_overshoot_nm,
        "zero_transmission_s": list(trace.zero_transmission_s),
        "recovery_delay_s": list(trace.recovery_delay_s),
    }


def reproduction_section() -> dict[str, object]:
    """Re-run the published dead-zone case on the published window and record the deviation."""
    rep = REPRESENTATIONS[1]
    grid = REPRODUCTION_HORIZON
    ours = {
        "persistent_direction_preloaded": simulate(PERSISTENT, rep, True, grid).error_impulse_nms,
        "role_reversal_preloaded": simulate(ROLE_REVERSAL, rep, True, grid).error_impulse_nms,
        "relaxed": simulate(ROLE_REVERSAL, rep, False, grid).error_impulse_nms,
    }
    deviation = max(abs(ours[key] - PUBLISHED_IMPULSES_NMS[key]) for key in ours)
    return {
        "source": UPSTREAM_STUDY_URL,
        "horizon_s": grid.duration_s,
        "published_nms": dict(PUBLISHED_IMPULSES_NMS),
        "reproduced_nms": ours,
        "max_abs_deviation_nms": deviation,
        "role_reversal": _summary(ROLE_REVERSAL, rep, grid),
    }


def representation_section() -> dict[str, object]:
    """Both programs under every representation, on the long study window."""
    rows: dict[str, object] = {}
    for rep in REPRESENTATIONS:
        persistent = _summary(PERSISTENT, rep, STUDY_HORIZON)
        reversal = _summary(ROLE_REVERSAL, rep, STUDY_HORIZON)
        rows[rep.name] = {
            "persistent_direction": persistent,
            "role_reversal": reversal,
            "relative_advantage": relative_advantage(rep, STUDY_HORIZON),
        }
    return {"horizon_s": STUDY_HORIZON.duration_s, "representations": rows}


def unequal_lag_section() -> dict[str, object]:
    """Zero gap, unequal lags: the persistent-minus-reversal net torque, simulated and exact.

    For linear lags the difference is ``d(t) = D (exp(-t/Ta) - exp(-t/Tw))`` with
    ``D = 14 N m`` (the change in each channel's preparation), minimised at
    ``t* = ln(Tw/Ta) Ta Tw / (Tw - Ta)``.
    """
    rep = REPRESENTATIONS[-1]
    persistent = simulate(PERSISTENT, rep, grid=STUDY_HORIZON)
    reversal = simulate(ROLE_REVERSAL, rep, grid=STUDY_HORIZON)
    difference = persistent.transmitted_nm.sum(axis=1) - reversal.transmitted_nm.sum(axis=1)
    worst = int(np.argmin(difference))
    arm_lag, wrist_lag = UNEQUAL_LAGS_S
    jump = PERSISTENT.pre_nm[0] - ROLE_REVERSAL.pre_nm[0]
    exact_time = np.log(wrist_lag / arm_lag) * arm_lag * wrist_lag / (wrist_lag - arm_lag)
    exact = jump * (np.exp(-exact_time / arm_lag) - np.exp(-exact_time / wrist_lag))
    return {
        "lags_s": list(UNEQUAL_LAGS_S),
        "simulated_min_difference_nm": float(difference[worst]),
        "simulated_min_time_s": float(persistent.time_s[worst]),
        "exact_min_difference_nm": float(exact),
        "exact_min_time_s": float(exact_time),
    }


def _gap_threshold(shape: Shape, margin: float) -> float:
    """Smallest gap at which the persistent advantage exceeds ``margin`` (T = 18 ms)."""

    def excess(gap: float) -> float:
        rep = Representation("probe", shape, gap)
        return relative_advantage(rep, STUDY_HORIZON) - margin

    return float(brentq(excess, 1e-6, GAP_GRID_RAD[-1], xtol=1e-7))


def flip_section() -> dict[str, object]:
    """Advantage and zero-transmission time versus gap size, per shape and time constant."""
    curves: dict[str, object] = {}
    for shape in Shape:
        for time_constant in TIME_CONSTANTS_S:
            advantage, zero_time = [], []
            for gap in GAP_GRID_RAD:
                rep = Representation("grid", shape, gap, time_constant)
                advantage.append(relative_advantage(rep, STUDY_HORIZON))
                reversal = simulate(ROLE_REVERSAL, rep, grid=STUDY_HORIZON)
                zero_time.append(max(reversal.zero_transmission_s))
            curves[f"{shape.value}_{round(time_constant * 1000)}ms"] = {
                "relative_advantage": advantage,
                "max_zero_transmission_s": zero_time,
            }
    thresholds = {
        shape.value: {
            f"{margin:g}": _gap_threshold(shape, margin) for margin in EQUIVALENCE_MARGINS
        }
        for shape in Shape
    }
    stiffness = REPRESENTATIONS[1].stiffness_nm_rad
    return {
        "gap_grid_rad": list(GAP_GRID_RAD),
        "curves": curves,
        "gap_thresholds_rad": thresholds,
        "reference_stretch_rad": abs(ROLE_REVERSAL.post_nm[1]) / stiffness,
    }


def _floor_pairs(values: list[float]) -> list[float]:
    """Grid values of ``c`` whose metric ties the minimum to within ``FLOOR_TOLERANCE``."""
    floor = min(values)
    pairs = INTERNAL_PAIR_GRID_NM
    return [
        pair for pair, value in zip(pairs, values, strict=True) if value - floor <= FLOOR_TOLERANCE
    ]


def split_section() -> dict[str, object]:
    """Sweep the preparation split between the role-reversal and beyond-persistent extremes."""
    rows: dict[str, object] = {}
    for rep in REPRESENTATIONS[1:3]:
        traces = [
            simulate(preparation_split(c), rep, grid=STUDY_HORIZON) for c in INTERNAL_PAIR_GRID_NM
        ]
        impulse = [trace.error_impulse_nms for trace in traces]
        channel = [trace.channel_error_impulse_nms for trace in traces]
        rows[rep.name] = {
            "error_impulse_nms": impulse,
            "channel_error_impulse_nms": channel,
            "peak_overshoot_nm": [trace.peak_overshoot_nm for trace in traces],
            "best_internal_pair_nm": INTERNAL_PAIR_GRID_NM[int(np.argmin(impulse))],
            "channel_floor_pairs_nm": _floor_pairs(channel),
        }
    norms = [float(np.hypot(*preparation_split(pair).pre_nm)) for pair in INTERNAL_PAIR_GRID_NM]
    return {
        "internal_pair_grid_nm": list(INTERNAL_PAIR_GRID_NM),
        "persistent_internal_pair_nm": PERSISTENT_INTERNAL_PAIR_NM,
        "preparation_torque_norm_nm": norms,
        "representations": rows,
    }


def muscle_margin_section() -> dict[str, object]:
    """Apply the declared margins to the published reduced muscle-model impulses (not re-run)."""
    advantage = (MUSCLE_REVERSAL_NMS - MUSCLE_PERSISTENT_NMS) / MUSCLE_PERSISTENT_NMS
    return {
        "source": MUSCLE_MODEL_SOURCE,
        "persistent_direction_nms": MUSCLE_PERSISTENT_NMS,
        "role_reversal_nms": MUSCLE_REVERSAL_NMS,
        "relative_advantage": advantage,
        "within_margin": {f"{margin:g}": advantage <= margin for margin in EQUIVALENCE_MARGINS},
    }
