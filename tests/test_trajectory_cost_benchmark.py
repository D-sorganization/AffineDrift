"""Tests for trajectory-tracking benchmark utilities."""

from __future__ import annotations

import numpy as np

from src.tools.trajectory_cost_benchmark import (
    benchmark_cost_gap,
    setpoint_cost,
    trajectory_tracking_cost,
)


def test_trajectory_tracking_cost_penalizes_path_deviation() -> None:
    """Trajectory cost should penalize off-trajectory behavior."""
    reference = np.array([[0.0], [1.0], [2.0], [3.0]])
    on_path = np.array([[0.0], [1.0], [2.0], [3.0]])
    shortcut = np.array([[0.0], [3.0], [3.0], [3.0]])
    assert trajectory_tracking_cost(on_path, reference) < trajectory_tracking_cost(
        shortcut, reference
    )


def test_setpoint_cost_can_ignore_transient_shape() -> None:
    """Setpoint-only objective should focus on final target error."""
    target = np.array([3.0])
    fast_shortcut = np.array([[0.0], [3.0], [3.0], [3.0]])
    smooth_path = np.array([[0.0], [1.0], [2.0], [3.0]])
    assert setpoint_cost(fast_shortcut, target) == setpoint_cost(smooth_path, target)


def test_benchmark_cost_gap_reports_positive_advantage() -> None:
    """Benchmark summary should show trajectory objective favors path adherence."""
    result = benchmark_cost_gap()
    assert result["tracking_advantage"] > 0.0
