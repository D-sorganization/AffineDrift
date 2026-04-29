"""Benchmarks for affine control module computations."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
import pytest

from src.affine_control.residuals import (
    compute_hessian_bound,
    compute_hessian_norm,
)


def simple_linear_dynamics(
    x: np.ndarray[Any, Any],
    u: np.ndarray[Any, Any],
) -> np.ndarray[Any, Any]:
    """Simple linear dynamics for benchmarking: dx = A*x + B*u."""
    A = np.array([[0.0, 1.0], [-1.0, -0.1]])
    B = np.array([[0.0], [1.0]])
    return A @ x + B @ u.reshape(-1, 1)


@pytest.mark.benchmark
def test_hessian_norm_computation(benchmark: Callable[..., Any]) -> None:
    """Benchmark Hessian norm computation for a simple 2D system."""
    x = np.array([1.0, 0.5])
    u = np.array([0.1])

    result = benchmark(
        compute_hessian_norm,
        simple_linear_dynamics,
        x,
        u,
        epsilon=1e-6,
    )

    assert isinstance(result, float)
    assert result >= 0.0
    assert np.isfinite(result)


@pytest.mark.benchmark
def test_hessian_bound_computation(benchmark: Callable[..., Any]) -> None:
    """Benchmark Hessian bound computation for control-affine system."""
    x = np.array([1.0, 0.5])
    u = np.array([0.1])

    result = benchmark(
        compute_hessian_bound,
        simple_linear_dynamics,
        x,
        u,
        epsilon=1e-6,
    )

    assert isinstance(result, float)
    assert result >= 0.0
    assert np.isfinite(result)


@pytest.mark.benchmark
def test_nonlinear_hessian_bound(benchmark: Callable[..., Any]) -> None:
    """Benchmark Hessian bound for a nonlinear system."""

    def nonlinear_dynamics(
        x: np.ndarray[Any, Any],
        u: np.ndarray[Any, Any],
    ) -> np.ndarray[Any, Any]:
        """Pendulum-like nonlinear dynamics."""
        return np.array([x[1], -np.sin(x[0]) + u[0]])

    x = np.array([np.pi / 4.0, 0.5])
    u = np.array([0.1])

    result = benchmark(
        compute_hessian_bound,
        nonlinear_dynamics,
        x,
        u,
        epsilon=1e-6,
    )

    assert isinstance(result, float)
    assert result >= 0.0
    assert np.isfinite(result)
