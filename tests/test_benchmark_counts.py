"""Benchmark count contracts reject inputs before invoking the workload."""

from unittest.mock import Mock

import pytest

from src.tools.utils.profiling_utils import ProfilingReport, benchmark


@pytest.mark.parametrize("iterations", [True, False, 1.5, "2", None, 0, -1])
def test_invalid_iterations_have_no_side_effects(iterations: object) -> None:
    """Invalid timed counts must fail before the default warmup executes."""
    workload = Mock()
    report = ProfilingReport()
    with pytest.raises(ValueError, match="iterations"):
        benchmark(workload, iterations=iterations, report=report)  # type: ignore[arg-type]
    workload.assert_not_called()
    assert report.benchmark_results == []


@pytest.mark.parametrize("warmup", [True, False, 1.5, "2", None, -1])
def test_invalid_warmup_has_no_side_effects(warmup: object) -> None:
    """Warmup counts must be nonnegative integers, excluding booleans."""
    workload = Mock()
    report = ProfilingReport()
    with pytest.raises(ValueError, match="warmup"):
        benchmark(workload, warmup=warmup, report=report)  # type: ignore[arg-type]
    workload.assert_not_called()
    assert report.benchmark_results == []


def test_zero_warmup_runs_only_timed_iterations() -> None:
    """A zero warmup count remains valid and retains every measurement."""
    workload = Mock()
    report = ProfilingReport()
    result = benchmark(workload, iterations=2, warmup=0, report=report)
    assert workload.call_count == 2
    assert len(result.times) == result.iterations == 2
    assert report.benchmark_results == [result]
