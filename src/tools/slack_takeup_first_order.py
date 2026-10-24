"""First-order take-up representation of Toy B, after the independent check in PR #5140.

Each hand channel relaxes toward its band edge as ``T x' = x* - x`` with target
``x* = delta + tau / k``. Starting at ``x(0)``, the channel engages at
``t = T ln(1 + k d / tau)`` with remaining gap ``d = delta - x(0)``. The hand torques are
``tau_lead = net / 2 - s`` and ``tau_trail = net / 2 + s``, so ``s`` is the internal
(null-space) torque and positive ``s`` means the trail hand supplies more of the drive.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.tools.slack_takeup_witness import HAND_GAP, HAND_STIFFNESS, Array

TIME_CONSTANT = 0.018  # s, the record's synthetic torque-development time
NET_TORQUE = 10.0  # N m
INTERNAL_PRIOR = 2.5  # N m, one-sigma prior on s
GAP_PRIOR = 0.008  # rad, one-sigma prior on each remaining gap
COARSE_TIMING = 5e-3  # s, conservative resolution matching the record's 5 ms horizon
FINE_TIMING = 0.5e-3  # s, the jitter declared for the inertial toy
FLIP_TORQUE = 2.0  # N m, |s| in the counterexample


def engagement_times(internal: float, remaining: Array) -> Array:
    """Lead and trail engagement times for internal torque ``internal`` and gaps ``remaining``."""
    torques = np.array([0.5 * NET_TORQUE - internal, 0.5 * NET_TORQUE + internal])
    if np.any(torques <= 0) or np.any(np.asarray(remaining) < 0):
        raise ValueError("both hand torques must be positive and gaps non-negative")
    times: Array = TIME_CONSTANT * np.log1p(HAND_STIFFNESS * np.asarray(remaining) / torques)
    return times


def jacobian(internal: float, remaining: Array) -> Array:
    """Analytic 2x3 Jacobian of the engagement times in ``(s, d_lead, d_trail)``."""
    torques = np.array([0.5 * NET_TORQUE - internal, 0.5 * NET_TORQUE + internal])
    ratio = HAND_STIFFNESS * np.asarray(remaining) / torques
    d_torque = -TIME_CONSTANT * ratio / (torques * (1.0 + ratio))
    d_gap = TIME_CONSTANT * HAND_STIFFNESS / (torques * (1.0 + ratio))
    result: Array = np.column_stack([np.array([-1.0, 1.0]) * d_torque, np.diag(d_gap)])
    return result


def marginalized_singular_value(matrix: Array, timing: float) -> float:
    """Scaled information on ``s`` once the gaps are marginalized under their Gaussian prior."""
    split, nuisance = matrix[:, :1], matrix[:, 1:]
    covariance = timing**2 * np.eye(2) + GAP_PRIOR**2 * nuisance @ nuisance.T
    return float(INTERNAL_PRIOR * np.sqrt((split.T @ np.linalg.solve(covariance, split)).item()))


def preload_flip() -> dict[str, Any]:
    """Exact pair: trail-led with zero preload and lead-led with flipped preloads, same times."""
    gaps = np.full(2, HAND_GAP)
    target = engagement_times(FLIP_TORQUE, gaps)
    torques = np.array([0.5 * NET_TORQUE + FLIP_TORQUE, 0.5 * NET_TORQUE - FLIP_TORQUE])
    remaining = torques * np.expm1(target / TIME_CONSTANT) / HAND_STIFFNESS
    matched = engagement_times(-FLIP_TORQUE, remaining)
    return {
        "trail_led_times": [float(value) for value in target],
        "lead_led_initial_states": [float(value) for value in HAND_GAP - remaining],
        "max_time_error": float(np.max(np.abs(matched - target))),
    }


def first_order_summary() -> dict[str, Any]:
    """Rank, null direction, marginalized singular values and the preload flip."""
    matrix = jacobian(0.0, np.full(2, HAND_GAP))
    _, _, rows = np.linalg.svd(matrix)
    null = rows[-1] / rows[-1][0]
    return {
        "rank": int(np.linalg.matrix_rank(matrix)),
        "unknowns": 3,
        "dt_ds": float(matrix[1, 0]),
        "dt_dgap": float(matrix[0, 1]),
        "null_direction": [float(value) for value in null],
        "singular_value_coarse": marginalized_singular_value(matrix, COARSE_TIMING),
        "singular_value_fine": marginalized_singular_value(matrix, FINE_TIMING),
        "preload_flip": preload_flip(),
    }
