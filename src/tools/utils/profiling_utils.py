"""Profiling utilities for performance analysis.

This module provides tools to measure and analyze the performance of
functions and code blocks.
"""

from __future__ import annotations

import contextlib
import functools
import logging
import statistics
import timeit
import tracemalloc
from collections.abc import Callable, Generator
from dataclasses import dataclass, field
from typing import Any

from .logging_utils import setup_logging

logger = logging.getLogger(__name__)

logger = setup_logging(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TimingResult:
    """Result of a single timed function execution."""

    function_name: str
    elapsed_seconds: float


@dataclass(frozen=True)
class MemoryResult:
    """Result of memory profiling for a function or code block."""

    label: str
    peak_bytes: int
    current_bytes: int

    @property
    def peak_mb(self) -> float:
        """Peak memory usage in megabytes."""
        return self.peak_bytes / (1024 * 1024)

    @property
    def current_mb(self) -> float:
        """Current memory usage in megabytes."""
        return self.current_bytes / (1024 * 1024)


@dataclass
class BenchmarkResult:
    """Result of a benchmarked function run over multiple iterations."""

    function_name: str
    iterations: int
    times: list[float]

    @property
    def mean(self) -> float:
        """Mean elapsed time across all iterations."""
        return statistics.mean(self.times)

    @property
    def median(self) -> float:
        """Median elapsed time."""
        return statistics.median(self.times)

    @property
    def min_time(self) -> float:
        """Minimum elapsed time."""
        return min(self.times)

    @property
    def max_time(self) -> float:
        """Maximum elapsed time."""
        return max(self.times)

    @property
    def stdev(self) -> float:
        """Sample standard deviation; 0.0 for a single iteration."""
        if len(self.times) < 2:
            return 0.0
        return statistics.stdev(self.times)


# ---------------------------------------------------------------------------
# Report collector
# ---------------------------------------------------------------------------


@dataclass
class ProfilingReport:
    """Collects and formats profiling results."""

    timing_results: list[TimingResult] = field(default_factory=list)
    memory_results: list[MemoryResult] = field(default_factory=list)
    benchmark_results: list[BenchmarkResult] = field(default_factory=list)

    def add_timing(self, result: TimingResult) -> None:
        """Append a timing result."""
        self.timing_results.append(result)

    def add_memory(self, result: MemoryResult) -> None:
        """Append a memory result."""
        self.memory_results.append(result)

    def add_benchmark(self, result: BenchmarkResult) -> None:
        """Append a benchmark result."""
        self.benchmark_results.append(result)

    def format_report(self) -> str:
        """Return a human-readable profiling report string."""
        if not (self.timing_results or self.memory_results or self.benchmark_results):
            return "Profiling report: no results collected."

        lines: list[str] = []

        if self.timing_results:
            lines.append("=== Timing ===")
            for r in self.timing_results:
                lines.append(f"  {r.function_name}: {r.elapsed_seconds:.4f}s")

        if self.memory_results:
            lines.append("=== Memory ===")
            for r in self.memory_results:
                lines.append(f"  {r.label}: peak={r.peak_mb:.2f} MB, current={r.current_mb:.2f} MB")

        if self.benchmark_results:
            lines.append("=== Benchmarks ===")
            for r in self.benchmark_results:
                lines.append(f"  {r.function_name}: {r.iterations} iters, mean={r.mean:.4f}s")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------


def profile_execution_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to measure and log the execution time of a function.

    Args:
        func: The function to profile.

    Returns:
        The wrapped function.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Measure execution time and call the original function."""
        start_time = timeit.default_timer()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = timeit.default_timer()
            execution_time = end_time - start_time
            logger.info(f"Function {func.__name__} took {execution_time:.4f} seconds to execute.")

    return wrapper


def profile_memory(
    func: Callable[..., Any] | None = None,
    *,
    label: str | None = None,
    report: ProfilingReport | None = None,
) -> Any:
    """Decorator to measure and log peak memory usage of a function.

    Can be used with or without arguments::

        @profile_memory
        def my_func(): ...

        @profile_memory(label="big alloc", report=my_report)
        def my_func(): ...

    Args:
        func: The function to wrap (when used without arguments).
        label: Label for the memory result. Defaults to the function name.
        report: Optional ProfilingReport to collect the result.
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        """Wrap fn with memory profiling."""

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Run fn with tracemalloc to measure peak memory."""
            _label = label if label is not None else fn.__name__
            tracemalloc.start()
            try:
                result = fn(*args, **kwargs)
                current, peak = tracemalloc.get_traced_memory()
            finally:
                tracemalloc.stop()
            mem_result = MemoryResult(label=_label, peak_bytes=peak, current_bytes=current)
            logger.info(f"Memory [{_label}]: peak={mem_result.peak_mb:.2f} MB")
            if report is not None:
                report.add_memory(mem_result)
            return result

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def memory_tracking(
    label: str = "block",
    *,
    report: ProfilingReport | None = None,
) -> Generator[None, None, None]:
    """Context manager to track peak memory usage of a code block.

    Args:
        label: Descriptive label for this block.
        report: Optional ProfilingReport to collect the result.

    Yields:
        None.
    """
    tracemalloc.start()
    try:
        yield
    finally:
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    mem_result = MemoryResult(label=label, peak_bytes=peak, current_bytes=current)
    logger.info(f"Memory [{label}]: peak={mem_result.peak_mb:.2f} MB")
    if report is not None:
        report.add_memory(mem_result)


# ---------------------------------------------------------------------------
# Benchmark harness
# ---------------------------------------------------------------------------


def benchmark(
    func: Callable[..., Any],
    *,
    args: tuple[Any, ...] = (),
    kwargs: dict[str, Any] | None = None,
    iterations: int = 10,
    warmup: int = 0,
    label: str | None = None,
    report: ProfilingReport | None = None,
) -> BenchmarkResult:
    """Run *func* repeatedly and collect timing statistics.

    Args:
        func: Callable to benchmark.
        args: Positional arguments passed to func.
        kwargs: Keyword arguments passed to func.
        iterations: Number of timed calls (must be >= 1).
        warmup: Number of un-timed warm-up calls before timing begins.
        label: Name for the result. Defaults to ``func.__name__``.
        report: Optional ProfilingReport to collect the result.

    Returns:
        BenchmarkResult with timing statistics.

    Raises:
        ValueError: If iterations < 1.
    """
    if iterations < 1:
        raise ValueError("iterations must be >= 1")

    _kwargs = kwargs or {}
    _label = label if label is not None else getattr(func, "__name__", "lambda")

    for _ in range(warmup):
        func(*args, **_kwargs)

    times: list[float] = []
    for _ in range(iterations):
        t0 = timeit.default_timer()
        func(*args, **_kwargs)
        times.append(timeit.default_timer() - t0)

    result = BenchmarkResult(function_name=_label, iterations=iterations, times=times)
    if report is not None:
        report.add_benchmark(result)
    return result
