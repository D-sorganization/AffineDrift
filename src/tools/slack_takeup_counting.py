"""Rank counting and counterexamples for "Slack Take-Up as a Witness" (#5136).

The event-time Jacobian of Toy B is scaled as in the record's observation accounting: rows by the
declared timing noise and columns by declared prior half-ranges, so a singular value below one is a
direction the timing data cannot resolve. Toy C counts which grasp-kernel directions a slack channel
could see at best, using the grasp map ``G`` and kernel basis ``K`` of the record.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.optimize import least_squares

from src.tools.slack_takeup_witness import (
    HALF_RANGES,
    HAND_CLOCK,
    HAND_GAP,
    HAND_STIFFNESS,
    NOMINAL_SPLIT,
    PARAMETERS,
    TIMING_NOISE,
    Array,
    HandDraw,
    hand_chain,
    simulate,
    simulate_traced,
)

RANK_TOLERANCE = 1e-9  # relative to the largest singular value
STEP_FRACTION = 0.01  # central-difference step as a fraction of each half-range
GRIP_HALF_SEPARATION = 0.06  # m, manufactured; matches the independent check in PR #5140
SPLIT_NAMES = ("axial squeeze", "shear y", "shear z", "twist couple", "bending y", "bending z")


def draw_from_vector(values: Array) -> HandDraw:
    """Map rows of ``PARAMETERS``-ordered values to an unloaded Toy B draw."""
    values = np.atleast_2d(values)
    return HandDraw(
        split=values[:, 0],
        gap=values[:, 1:3],
        state=values[:, 3:5],
        stiffness=values[:, 5:7],
        preload=np.zeros(values.shape[0]),
    )


def nominal_vector(split: float = NOMINAL_SPLIT) -> Array:
    """Symmetric nominal parameters with centred slack states."""
    return np.array([split, HAND_GAP, HAND_GAP, 0.0, 0.0, HAND_STIFFNESS, HAND_STIFFNESS])


def event_times(values: Array) -> Array:
    """Lead and trail take-up times for each parameter row."""
    events, _ = simulate(hand_chain(draw_from_vector(values)), HAND_CLOCK)
    return events


def scaled_jacobian(centre: Array) -> Array:
    """Central-difference event-time Jacobian scaled by noise (rows) and half-ranges (columns)."""
    steps = STEP_FRACTION * np.asarray(HALF_RANGES)
    rows = [centre]
    for index, step in enumerate(steps):
        for sign in (1.0, -1.0):
            shifted = centre.copy()
            shifted[index] += sign * step
            rows.append(shifted)
    times = event_times(np.asarray(rows))
    if np.isnan(times).any():
        raise ValueError("an event is missing at the sensitivity point")
    jacobian: Array = (times[1::2] - times[2::2]).T / (2.0 * steps)
    scaled: Array = jacobian * np.asarray(HALF_RANGES) / TIMING_NOISE
    return scaled


def _rank(matrix: Array) -> int:
    """Numerical rank with the module's relative tolerance."""
    values = np.linalg.svd(matrix, compute_uv=False)
    return int(np.sum(values > RANK_TOLERANCE * max(values.max(initial=0.0), 1e-300)))


def split_visibility(jacobian: Array) -> dict[str, float | int | list[float]]:
    """Counting for the split: alone, and with every nuisance parameter free.

    ``split_residual`` is the norm of the split axis projected onto the null space of the scaled
    Jacobian; it is zero exactly when the split is a first-order identifiable functional.
    """
    _, singular, rows = np.linalg.svd(jacobian)
    rank = _rank(jacobian)
    null_basis = rows[rank:]
    return {
        "singular_values": [float(value) for value in singular],
        "rank_all": rank,
        "rank_nuisance": _rank(jacobian[:, 1:]),
        "unknowns": len(PARAMETERS),
        "split_column_norm": float(np.linalg.norm(jacobian[:, 0])),
        "split_residual": float(np.linalg.norm(null_basis[:, 0])),
    }


MATCHED_INDICES = (2, 3, 4)  # gap_trail, state_lead, state_trail
MATCHED_LOWER = np.array([1.0, -0.8, -0.8]) * HAND_GAP
MATCHED_UPPER = np.array([1.5, 0.8, 0.8]) * HAND_GAP


def _with_nuisance(split: float, nuisance: Array) -> Array:
    """Nominal parameters with the matched nuisance entries replaced."""
    values = nominal_vector(split)
    values[list(MATCHED_INDICES)] = nuisance
    return values


def matched_pair(lead_split: float = 0.7) -> dict[str, Any]:
    """Find nuisance values inside the uncertain-regime prior support that make a trail-led
    trial reproduce the event times of the nominal lead-led trial."""
    target = event_times(nominal_vector(lead_split))[0]
    trail_split = 1.0 - lead_split

    def residual(nuisance: Array) -> Array:
        """Scaled timing mismatch between matched and nominal lead-led take-up."""
        mismatch: Array = event_times(_with_nuisance(trail_split, nuisance))[0] - target
        return mismatch / TIMING_NOISE

    start = np.array([1.2, 1.0 - trail_split / lead_split, 0.5]) * HAND_GAP
    fit = least_squares(residual, start, bounds=(MATCHED_LOWER, MATCHED_UPPER), diff_step=1e-3)
    return {
        "lead_split": lead_split,
        "trail_split": trail_split,
        "nuisance": [float(value) for value in fit.x],
        "target_times": [float(value) for value in target],
        "matched_times": [
            float(value) for value in event_times(_with_nuisance(trail_split, fit.x))[0]
        ],
        "max_time_error": float(np.max(np.abs(residual(fit.x))) * TIMING_NOISE),
    }


def pair_traces(lead_split: float, nuisance: list[float], stride: int = 20) -> dict[str, Array]:
    """Positions of the matched pair, thinned by ``stride``, for the counterexample figure."""
    lead = nominal_vector(lead_split)
    trail = _with_nuisance(1.0 - lead_split, np.asarray(nuisance))
    chain = hand_chain(draw_from_vector(np.vstack([lead, trail])))
    _, history = simulate_traced(chain, HAND_CLOCK)
    time: Array = np.arange(history.shape[0], dtype=np.float64) * HAND_CLOCK.step
    return {"time": time[::stride], "positions": history[::stride]}


def grasp_matrices(half_separation: float = GRIP_HALF_SEPARATION) -> tuple[Array, Array]:
    """Grasp map ``G`` (6x12) and kernel basis ``K`` (12x6) for hands at ``-d`` and ``+d``."""
    d = np.array([half_separation, 0.0, 0.0])
    skew = np.array([[0.0, -d[2], d[1]], [d[2], 0.0, -d[0]], [-d[1], d[0], 0.0]])
    eye, zero = np.eye(3), np.zeros((3, 3))
    grasp = np.block([[eye, zero, eye, zero], [-skew, eye, skew, eye]])
    kernel = np.block([[-eye, zero], [-skew, -eye], [eye, zero], [-skew, eye]])
    return grasp, kernel


GRASP_CHANNELS = {
    "no slack observed": (),
    "force-axis slack, both hands": (0, 1, 2, 6, 7, 8),
    "couple-axis slack, both hands": (3, 4, 5, 9, 10, 11),
    "twist-axis slack only": (3, 9),
    "every axis except axial force": (1, 2, 3, 4, 5, 7, 8, 9, 10, 11),
    "every axis, both hands": tuple(range(12)),
}


def grasp_visibility() -> list[dict[str, object]]:
    """Exact rank of each slack channel restricted to the six-dimensional grasp kernel."""
    grasp, kernel = grasp_matrices()
    if _rank(grasp @ kernel) != 0 or _rank(kernel) != 6:
        raise ValueError("K must be a basis of the grasp-map kernel")
    table = []
    for name, rows in GRASP_CHANNELS.items():
        seen = kernel[list(rows)] if rows else np.zeros((0, 6))
        rank = _rank(seen) if rows else 0
        norms = np.linalg.norm(seen, axis=0) if rows else np.zeros(6)
        hidden = [SPLIT_NAMES[i] for i in range(6) if norms[i] == 0.0]
        seen_norms = norms[norms > 0]
        spread = float(seen_norms.max() / seen_norms.min()) if seen_norms.size else 0.0
        table.append(
            {
                "channel": name,
                "rank": rank,
                "nullity": 6 - rank,
                "hidden": hidden,
                "column_norms": [float(value) for value in norms],
                "norm_spread": spread,
            }
        )
    return table
