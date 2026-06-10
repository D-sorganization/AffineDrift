"""Tests for the ``src/tools/rl_funnel_reporting`` re-export shim (issue #3230).

This module is a thin facade that re-exports ``BenchmarkResult`` and
``format_results`` from ``rl_funnel_support``. The tests verify the facade
stays in sync with its source (identity, ``__all__`` completeness) and that the
re-exported callable actually works through this import path.
"""

from __future__ import annotations

import numpy as np

import src.tools.rl_funnel_reporting as reporting
from src.tools import rl_funnel_support


def test_reexports_are_the_same_objects_as_source() -> None:
    assert reporting.BenchmarkResult is rl_funnel_support.BenchmarkResult
    assert reporting.format_results is rl_funnel_support.format_results


def test_all_lists_only_reexported_names() -> None:
    assert set(reporting.__all__) == {"BenchmarkResult", "format_results"}
    for name in reporting.__all__:
        assert hasattr(reporting, name)


def test_format_results_callable_through_facade() -> None:
    result = reporting.BenchmarkResult(
        name="Setpoint controller",
        tracking_error=1.0,
        control_effort=2.0,
        runtime_sec=0.5,
        trajectory=np.zeros((4, 3)),
        t_grid=np.linspace(0.0, 1.0, 3),
    )
    table = reporting.format_results([result])
    assert "Setpoint controller" in table
    assert "Tracking Error" in table
