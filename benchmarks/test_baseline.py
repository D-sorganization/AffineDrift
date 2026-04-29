"""Minimal baseline benchmark test."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest


@pytest.mark.benchmark
def test_baseline(benchmark: Callable[..., Any]) -> None:
    """Baseline benchmark test - just a simple computation."""

    def simple_computation() -> float:
        """Simple test computation."""
        return sum(range(1000)) / 1000.0

    result = benchmark(simple_computation)

    assert isinstance(result, float)
    assert result > 0.0
