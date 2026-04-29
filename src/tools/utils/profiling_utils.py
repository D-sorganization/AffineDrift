"""Profiling utilities for performance analysis of numerical simulation code.

This module provides tools to measure and analyze the performance of
functions and code blocks, including:
- Execution time profiling (decorator)
- Memory profiling via tracemalloc (decorator and context manager)
- Lightweight benchmark harness for numerical functions
- Profiling report collection and formatting

All profiling is opt-in and zero-overhead when disabled.
"""

from __future__ import annotations

import functools
import statistics
import timeit
import tracemalloc
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

from .logging_utils import setup_logging

logger = setup_logging(__name__)


# ---------------------------------------------------------------------------
# Data classes for profiling results
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TimingResult:
    """Result from a single timing measurement.

    Attributes:
        function_name: Name of the profiled function.
        elapsed_seconds: Wall-clock time in seconds.
    """

    function_name: str
    elapsed_seconds: float


@dataclass(frozen=True)
class MemoryResult:
    """Result from a memory profiling measurement.

    Attributes:
        label: Human-readable label for the profiled block.
        peak_bytes: Peak memory usage in bytes during the block.
        current_bytes: Memory usage at the end of the block.
    """

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


@dataclass(frozen=True)
class BenchmarkResult:
    """Result from a benchmark run.

    Attributes:
        function_name: Name of the benchmarked function.
        iterations: Number of iterations run.
        times: List of individual iteration times in seconds.
    """

    function_name: str
    iterations: int
    times: list[float]

    @property
    def mean(self) -> float:
        """Mean execution time in seconds."""
        return statistics.mean(self.times)

    @property
    def median(self) -> float:
        """Median execution time in seconds."""
        return statistics.median(self.times)

    @property
    def stdev(self) -> float:
        """Standard deviation of execution times. Returns 0.0 for single-run benchmarks."""
        if len(self.times) < 2:
            return 0.0
        return statistics.stdev(self.times)

    @property
    def min_time(self) -> float:
        """Minimum execution time in seconds."""
        return min(self.times)

    @property
    def max_time(self) -> float:
        """Maximum execution time in seconds."""
        return max(self.times)


@dataclass
class ProfilingReport:
    """Collects and formats profiling results from multiple measurements.

    Use as a central accumulator during a profiling session, then call
    ``format_report()`` to get a human-readable summary.
    """

    timing_results: list[TimingResult] = field(default_factory=list)
    memory_results: list[MemoryResult] = field(default_factory=list)
    benchmark_results: list[BenchmarkResult] = field(default_factory=list)

    def add_timing(self, result: TimingResult) -> None:
        """Record a timing result."""
        self.timing_results.append(result)

    def add_memory(self, result: MemoryResult) -> None:
        """Record a memory result."""
        self.memory_results.append(result)

    def add_benchmark(self, result: BenchmarkResult) -> None:
        """Record a benchmark result."""
        self.benchmark_results.append(result)

    def format_report(self) -> str:
        """Format all collected results into a human-readable report string."""
        lines: list[str] = ["=== Profiling Report ===", ""]

        if self.timing_results:
            lines.append("--- Timing ---")
            for t in self.timing_results:
                lines.append(f"  {t.function_name}: {t.elapsed_seconds:.4f}s")
            lines.append("")

        if self.memory_results:
            lines.append("--- Memory ---")
            for m in self.memory_results:
                lines.append(f"  {m.label}: peak={m.peak_mb:.2f} MB, current={m.current_mb:.2f} MB")
            lines.append("")

        if self.benchmark_results:
            lines.append("--- Benchmarks ---")
            for b in self.benchmark_results:
                lines.append(
                    f"  {b.function_name} ({b.iterations} iters): "
                    f"mean={b.mean:.4f}s, median={b.median:.4f}s, "
                    f"stdev={b.stdev:.4f}s, min={b.min_time:.4f}s, "
                    f"max={b.max_time:.4f}s"
                )
            lines.append("")

        if not (self.timing_results or self.memory_results or self.benchmark_results):
            lines.append("  (no results collected)")
            lines.append("")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Timing decorator (original, preserved for backward compatibility)
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
            logger.info(
                "Function %s took %.4f seconds to execute.",
                func.__name__,
                execution_time,
            )

    return wrapper


# ---------------------------------------------------------------------------
# Memory profiling
# ---------------------------------------------------------------------------


def profile_memory(
    func: Callable[..., Any] | None = None,
    *,
    label: str | None = None,
    report: ProfilingReport | None = None,
) -> Any:
    """Decorator to measure peak memory usage of a function via tracemalloc.

    Can be used with or without arguments::

        @profile_memory
        def my_func(): ...

        @profile_memory(label="DDP solve", report=my_report)
        def my_func(): ...

    Args:
        func: The function to profile (when used without arguments).
        label: Optional human-readable label (defaults to function name).
        report: Optional ProfilingReport to collect the result into.

    Returns:
        The wrapped function (or a decorator if called with arguments).
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        """Wrap *fn* with tracemalloc memory measurement."""
        fn_label = label or fn.__name__

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Measure memory usage and call the original function."""
            tracemalloc_was_running = tracemalloc.is_tracing()
            if not tracemalloc_was_running:
                tracemalloc.start()

            # Reset peak to get an accurate delta
            tracemalloc.reset_peak()

            try:
                result = fn(*args, **kwargs)
                return result
            finally:
                current, peak = tracemalloc.get_traced_memory()
                mem_result = MemoryResult(
                    label=fn_label,
                    peak_bytes=peak,
                    current_bytes=current,
                )
                logger.info(
                    "Memory [%s]: peak=%.2f MB, current=%.2f MB",
                    fn_label,
                    mem_result.peak_mb,
                    mem_result.current_mb,
                )
                if report is not None:
                    report.add_memory(mem_result)

                if not tracemalloc_was_running:
                    tracemalloc.stop()

        return wrapper

    if func is not None:
        # Called as @profile_memory (no arguments)
        return decorator(func)
    # Called as @profile_memory(...) (with arguments)
    return decorator


@contextmanager
def memory_tracking(
    label: str = "block",
    report: ProfilingReport | None = None,
) -> Iterator[None]:
    """Context manager to measure peak memory usage of a code block.

    Example::

        with memory_tracking("DDP iteration"):
            result = ddp_solve(...)

    Args:
        label: Human-readable label for this block.
        report: Optional ProfilingReport to collect the result into.

    Yields:
        None
    """
    tracemalloc_was_running = tracemalloc.is_tracing()
    if not tracemalloc_was_running:
        tracemalloc.start()

    tracemalloc.reset_peak()
    try:
        yield
    finally:
        current, peak = tracemalloc.get_traced_memory()
        mem_result = MemoryResult(label=label, peak_bytes=peak, current_bytes=current)
        logger.info(
            "Memory [%s]: peak=%.2f MB, current=%.2f MB",
            label,
            mem_result.peak_mb,
            mem_result.current_mb,
        )
        if report is not None:
            report.add_memory(mem_result)

        if not tracemalloc_was_running:
            tracemalloc.stop()


# ---------------------------------------------------------------------------
# Benchmark harness
# ---------------------------------------------------------------------------


def benchmark(
    func: Callable[..., Any],
    args: tuple[Any, ...] = (),
    kwargs: dict[str, Any] | None = None,
    iterations: int = 5,
    warmup: int = 1,
    label: str | None = None,
    report: ProfilingReport | None = None,
) -> BenchmarkResult:
    """Run a lightweight benchmark of a callable.

    Executes *warmup* untimed iterations followed by *iterations* timed runs,
    collecting wall-clock times for each.

    Args:
        func: The callable to benchmark.
        args: Positional arguments to pass.
        kwargs: Keyword arguments to pass.
        iterations: Number of timed iterations (must be >= 1).
        warmup: Number of untimed warmup iterations.
        label: Optional label (defaults to ``func.__name__``).
        report: Optional ProfilingReport to collect the result into.

    Returns:
        A BenchmarkResult with per-iteration timings.

    Raises:
        ValueError: If iterations < 1.
    """
    if iterations < 1:
        msg = "iterations must be >= 1"
        raise ValueError(msg)
    if kwargs is None:
        kwargs = {}

    fn_label: str = label or str(getattr(func, "__name__", "anonymous"))

    # Warmup
    for _ in range(warmup):
        func(*args, **kwargs)

    # Timed runs
    times: list[float] = []
    for _ in range(iterations):
        start = timeit.default_timer()
        func(*args, **kwargs)
        end = timeit.default_timer()
        times.append(end - start)

    result = BenchmarkResult(function_name=fn_label, iterations=iterations, times=times)
    logger.info(
        "Benchmark [%s] (%d iters): mean=%.4fs, median=%.4fs",
        fn_label,
        iterations,
        result.mean,
        result.median,
    )
    if report is not None:
        report.add_benchmark(result)

    return result
