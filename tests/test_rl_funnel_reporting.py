"""Tests for RL funnel reporting re-exports."""

from __future__ import annotations

from src.tools import rl_funnel_reporting
from src.tools.rl_funnel_support import BenchmarkResult, format_results


def test_reporting_module_reexports_public_contract() -> None:
    """Reporting module should expose the canonical result type and formatter."""
    assert rl_funnel_reporting.BenchmarkResult is BenchmarkResult
    assert rl_funnel_reporting.format_results is format_results
    assert sorted(rl_funnel_reporting.__all__) == ["BenchmarkResult", "format_results"]
