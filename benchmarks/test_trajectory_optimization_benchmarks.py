"""Benchmarks for trajectory optimization and cost computation."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
import pytest

from src.tools.trajectory_cost_benchmark import trajectory_tracking_cost


@pytest.mark.benchmark
def test_trajectory_cost_small_scale(benchmark: Callable[..., Any]) -> None:
    """Benchmark trajectory cost on small trajectory (32 points)."""
    reference = np.linspace(0.0, 1.0, 32, dtype=np.float64).reshape(-1, 1)
    perturbed = reference + np.random.randn(32, 1) * 0.01

    result = benchmark(trajectory_tracking_cost, perturbed, reference)

    assert isinstance(result, (float, np.floating))
    assert result >= 0.0
    assert np.isfinite(result)


@pytest.mark.benchmark
def test_trajectory_cost_medium_scale(benchmark: Callable[..., Any]) -> None:
    """Benchmark trajectory cost on medium trajectory (256 points)."""
    reference = np.linspace(0.0, 1.0, 256, dtype=np.float64).reshape(-1, 1)
    perturbed = reference + np.random.randn(256, 1) * 0.01

    result = benchmark(trajectory_tracking_cost, perturbed, reference)

    assert isinstance(result, (float, np.floating))
    assert result >= 0.0
    assert np.isfinite(result)


@pytest.mark.benchmark
def test_trajectory_cost_large_scale(benchmark: Callable[..., Any]) -> None:
    """Benchmark trajectory cost on large trajectory (1024 points)."""
    reference = np.linspace(0.0, 1.0, 1024, dtype=np.float64).reshape(-1, 1)
    perturbed = reference + np.random.randn(1024, 1) * 0.01

    result = benchmark(trajectory_tracking_cost, perturbed, reference)

    assert isinstance(result, (float, np.floating))
    assert result >= 0.0
    assert np.isfinite(result)


@pytest.mark.benchmark
def test_trajectory_cost_multivariate(benchmark: Callable[..., Any]) -> None:
    """Benchmark trajectory cost with multivariate trajectories (128 points, 4 dims)."""
    reference = np.random.randn(128, 4).astype(np.float64)
    perturbed = reference + np.random.randn(128, 4) * 0.01

    result = benchmark(trajectory_tracking_cost, perturbed, reference)

    assert isinstance(result, (float, np.floating))
    assert result >= 0.0
    assert np.isfinite(result)


@pytest.mark.benchmark
def test_trajectory_cost_worst_case(benchmark: Callable[..., Any]) -> None:
    """Benchmark trajectory cost with large perturbations (worst case)."""
    reference = np.linspace(0.0, 1.0, 256, dtype=np.float64).reshape(-1, 1)
    perturbed = reference + np.random.randn(256, 1) * 0.5

    result = benchmark(trajectory_tracking_cost, perturbed, reference)

    assert isinstance(result, (float, np.floating))
    assert result >= 0.0
    assert np.isfinite(result)
