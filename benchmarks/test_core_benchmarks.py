"""Lightweight baseline benchmarks for stable computational paths."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
import pytest

from src.tools.rl_funnel_dynamics import (
    double_pendulum_drift,
    double_pendulum_mass_matrix,
    generate_reference_trajectory,
)
from src.tools.trajectory_cost_benchmark import trajectory_tracking_cost


@pytest.mark.benchmark
def test_double_pendulum_drift_baseline(benchmark: Callable[..., Any]) -> None:
    """Benchmark one passive double-pendulum drift evaluation."""
    state = np.array([np.pi / 2.0, np.pi / 4.0, 1.0, -1.0], dtype=np.float64)

    result = benchmark(double_pendulum_drift, 0.0, state)

    assert result.shape == (4,)
    assert np.all(np.isfinite(result))


@pytest.mark.benchmark
def test_double_pendulum_mass_matrix_baseline(benchmark: Callable[..., Any]) -> None:
    """Benchmark the small dense mass-matrix calculation used by drift dynamics."""
    result = benchmark(double_pendulum_mass_matrix, np.pi / 2.0, np.pi / 4.0)

    assert result.shape == (2, 2)
    assert np.all(np.isfinite(result))


@pytest.mark.benchmark
def test_trajectory_tracking_cost_baseline(benchmark: Callable[..., Any]) -> None:
    """Benchmark a vectorized trajectory-tracking cost on a small fixed path."""
    reference = np.linspace(0.0, 1.0, 128, dtype=np.float64).reshape(-1, 1)
    perturbed = reference + 0.05

    result = benchmark(trajectory_tracking_cost, perturbed, reference)

    assert result > 0.0
    assert np.isfinite(result)


@pytest.mark.benchmark
def test_reference_trajectory_generation_short(benchmark: Callable[..., Any]) -> None:
    """Benchmark short reference trajectory generation (0.1s, 10ms steps)."""
    result = benchmark(generate_reference_trajectory, (0.0, 0.1), dt=0.01)

    assert len(result) > 0
    assert all(np.all(np.isfinite(state)) for state in result)


@pytest.mark.benchmark
def test_reference_trajectory_generation_medium(benchmark: Callable[..., Any]) -> None:
    """Benchmark medium reference trajectory generation (1s, 10ms steps)."""
    result = benchmark(generate_reference_trajectory, (0.0, 1.0), dt=0.01)

    assert len(result) > 0
    assert all(np.all(np.isfinite(state)) for state in result)


@pytest.mark.benchmark
def test_drift_dynamics_batch(benchmark: Callable[..., Any]) -> None:
    """Benchmark drift dynamics on multiple states (100 evaluations)."""
    states = np.random.randn(100, 4).astype(np.float64)

    def batch_drift() -> np.ndarray[Any, Any]:
        return np.array([double_pendulum_drift(0.0, s) for s in states])

    result = benchmark(batch_drift)

    assert result.shape == (100, 4)
    assert np.all(np.isfinite(result))
