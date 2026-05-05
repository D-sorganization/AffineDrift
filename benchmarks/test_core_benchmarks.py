"""Lightweight baseline benchmarks for stable computational paths."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

from src.tools.rl_funnel_dynamics import double_pendulum_drift, double_pendulum_mass_matrix
from src.tools.trajectory_cost_benchmark import trajectory_tracking_cost


def test_double_pendulum_drift_baseline(benchmark: Callable[..., Any]) -> None:
    """Benchmark one passive double-pendulum drift evaluation."""
    state = np.array([np.pi / 2.0, np.pi / 4.0, 1.0, -1.0], dtype=np.float64)

    result = benchmark(double_pendulum_drift, 0.0, state)

    assert result.shape == (4,)
    assert np.all(np.isfinite(result))


def test_double_pendulum_mass_matrix_baseline(benchmark: Callable[..., Any]) -> None:
    """Benchmark the small dense mass-matrix calculation used by drift dynamics."""
    result = benchmark(double_pendulum_mass_matrix, np.pi / 2.0, np.pi / 4.0)

    assert result.shape == (2, 2)
    assert np.all(np.isfinite(result))


def test_trajectory_tracking_cost_baseline(benchmark: Callable[..., Any]) -> None:
    """Benchmark a vectorized trajectory-tracking cost on a small fixed path."""
    reference = np.linspace(0.0, 1.0, 128, dtype=np.float64).reshape(-1, 1)
    perturbed = reference + 0.05

    result = benchmark(trajectory_tracking_cost, perturbed, reference)

    assert result > 0.0
    assert np.isfinite(result)
