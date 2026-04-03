"""Numerical profiling infrastructure for simulation and control code.

Provides a benchmark harness, a memory-profiling decorator, and a structured
result type for timing DDP solver and ball flight simulation code.  All output
is routed through :mod:`logging` — no ``print`` calls.

Usage (benchmark harness)::

    result = run_numerical_benchmark(my_function, iterations=5)
    logger.info(result.summary())

Usage (memory decorator)::

    @profile_memory
    def expensive_function(x):
        ...

Usage (context manager)::

    with NumericalProfiler("rk4_step") as prof:
        result = dynamics.simulate(initial_state)
    # timing is logged automatically when the block exits
"""

from __future__ import annotations

import functools
import logging
import timeit
import tracemalloc
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

_SLOW_THRESHOLD_DEFAULT = 1.0


@dataclass
class NumericalProfileResult:
    """Result of benchmarking a numerical function with timing and memory metrics.

    Attributes:
        function_name: Name of the profiled callable.
        elapsed_seconds: Total wall-clock time across all iterations, in seconds.
        peak_memory_bytes: Peak heap allocation in bytes (tracemalloc).
        iterations: Number of times the function was executed.
    """

    function_name: str
    elapsed_seconds: float
    peak_memory_bytes: int
    iterations: int

    @property
    def mean_elapsed_seconds(self) -> float:
        """Mean wall-clock time per iteration, in seconds."""
        if self.iterations <= 0:
            return 0.0
        return self.elapsed_seconds / self.iterations

    def summary(self) -> str:
        """Return a human-readable one-line summary suitable for logging.

        Returns:
            Formatted string with function name, total/mean elapsed time,
            peak memory in KB, and iteration count.
        """
        peak_kb = self.peak_memory_bytes / 1024.0
        return (
            f"[profile] {self.function_name}: "
            f"total={self.elapsed_seconds:.4f}s "
            f"mean={self.mean_elapsed_seconds:.4f}s/iter "
            f"peak_memory={peak_kb:.1f} KB "
            f"iterations={self.iterations}"
        )


def run_numerical_benchmark(
    func: Callable[..., Any],
    iterations: int = 1,
    args: tuple[Any, ...] = (),
    kwargs: dict[str, Any] | None = None,
) -> NumericalProfileResult:
    """Run a numerical callable multiple times and collect timing and memory metrics.

    Measures total wall-clock time via :func:`timeit.default_timer` and peak
    heap allocation via :mod:`tracemalloc`.  Both measurements span the full
    sequence of ``iterations`` calls.

    Args:
        func: The callable to benchmark.
        iterations: Number of times to invoke ``func`` (default: 1).
        args: Positional arguments forwarded to ``func`` on each call.
        kwargs: Keyword arguments forwarded to ``func`` on each call.

    Returns:
        A :class:`NumericalProfileResult` with timing and memory data.
    """
    if kwargs is None:
        kwargs = {}

    tracemalloc.start()
    start_time = timeit.default_timer()
    try:
        for _ in range(iterations):
            func(*args, **kwargs)
    finally:
        end_time = timeit.default_timer()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    elapsed = end_time - start_time
    result = NumericalProfileResult(
        function_name=getattr(func, "__name__", repr(func)),
        elapsed_seconds=elapsed,
        peak_memory_bytes=peak,
        iterations=iterations,
    )
    logger.info(result.summary())
    return result


def profile_memory(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to measure and log peak memory usage of a function.

    Uses :mod:`tracemalloc` to track allocations during the call.  Logs
    elapsed time and peak memory at INFO level.  The decorated function's
    return value and ``__name__`` are preserved.

    Args:
        func: The function to profile.

    Returns:
        The wrapped function with identical signature and return value.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Measure peak memory and elapsed time, then call the original function."""
        tracemalloc.start()
        start_time = timeit.default_timer()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = timeit.default_timer()
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            elapsed = end_time - start_time
            logger.info(
                "Function %s took %.4fs; peak memory %d bytes (%.1f KB).",
                func.__name__,
                elapsed,
                peak,
                peak / 1024.0,
            )

    return wrapper


@dataclass
class ProfileRecord:
    """A single timing observation for one named numerical operation.

    Attributes:
        label: Human-readable name for the operation being timed.
        elapsed: Wall-clock duration in seconds.
        metadata: Optional free-form metadata (e.g. array shapes, iteration count).
    """

    label: str
    elapsed: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_log_line(self, slow_threshold: float = _SLOW_THRESHOLD_DEFAULT) -> str:
        """Format this record as a single log-friendly string.

        Args:
            slow_threshold: Duration (s) above which the record is marked SLOW.

        Returns:
            Formatted string suitable for ``logger.info``.
        """
        flag = " [SLOW]" if self.elapsed >= slow_threshold else ""
        base = f"[profile] {self.label}: {self.elapsed:.6f}s{flag}"
        if self.metadata:
            meta_str = ", ".join(f"{k}={v}" for k, v in sorted(self.metadata.items()))
            return f"{base} ({meta_str})"
        return base


class NumericalProfiler:
    """Context manager for timing a single numerical operation.

    Logs elapsed time at INFO level on clean exit, or WARNING if an exception
    propagates out of the block.

    Args:
        label: Name of the operation (used in log output).
        slow_threshold: Duration (s) above which the result is flagged SLOW.
        metadata: Arbitrary key-value pairs appended to the log line.
    """

    def __init__(
        self,
        label: str,
        slow_threshold: float = _SLOW_THRESHOLD_DEFAULT,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if not label:
            raise ValueError("label must be a non-empty string")
        if slow_threshold <= 0:
            raise ValueError("slow_threshold must be positive")
        self.label = label
        self.slow_threshold = slow_threshold
        self.metadata: dict[str, Any] = metadata or {}
        self._start: float = 0.0
        self.record: ProfileRecord | None = None

    def __enter__(self) -> NumericalProfiler:
        """Start the timer."""
        self._start = timeit.default_timer()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Stop the timer and emit the log record."""
        elapsed = timeit.default_timer() - self._start
        self.record = ProfileRecord(label=self.label, elapsed=elapsed, metadata=self.metadata)
        line = self.record.as_log_line(self.slow_threshold)
        if exc_type is None:
            logger.info(line)
        else:
            logger.warning("%s (aborted by exception: %s)", line, exc_type.__name__)


def profile_numerical(
    label: str | None = None,
    slow_threshold: float = _SLOW_THRESHOLD_DEFAULT,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory for timing a numerical function.

    Wraps the target function in a :class:`NumericalProfiler` context.

    Args:
        label: Operation label.  Defaults to the decorated function name.
        slow_threshold: Duration (s) above which the timing is flagged SLOW.

    Returns:
        A decorator that wraps the target callable.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        op_label = label if label is not None else func.__name__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with NumericalProfiler(op_label, slow_threshold=slow_threshold):
                return func(*args, **kwargs)

        return wrapper

    return decorator


class ProfilingCollector:
    """Collects multiple :class:`ProfileRecord` entries and emits a summary report.

    Useful when profiling several named steps inside a simulation loop and then
    logging a consolidated report at the end.

    Args:
        name: Top-level name used in the summary report header.
    """

    def __init__(self, name: str = "simulation") -> None:
        if not name:
            raise ValueError("name must be a non-empty string")
        self.name = name
        self._records: list[ProfileRecord] = []

    @contextmanager
    def track(
        self,
        label: str,
        slow_threshold: float = _SLOW_THRESHOLD_DEFAULT,
        metadata: dict[str, Any] | None = None,
    ) -> Generator[NumericalProfiler, None, None]:
        """Context manager that profiles a block and stores the record.

        Args:
            label: Name of the operation.
            slow_threshold: Duration (s) above which the result is flagged SLOW.
            metadata: Optional key-value pairs appended to the log line.

        Yields:
            The :class:`NumericalProfiler` instance (record available after exit).
        """
        profiler = NumericalProfiler(label, slow_threshold=slow_threshold, metadata=metadata or {})
        with profiler:
            yield profiler
        if profiler.record is not None:
            self._records.append(profiler.record)

    @property
    def records(self) -> list[ProfileRecord]:
        """Return a read-only view of collected records."""
        return list(self._records)

    @property
    def total_elapsed(self) -> float:
        """Sum of elapsed times across all collected records."""
        return sum(r.elapsed for r in self._records)

    def log_report(self, slow_threshold: float = _SLOW_THRESHOLD_DEFAULT) -> None:
        """Emit a structured profiling report to the logger at INFO level.

        Args:
            slow_threshold: Duration (s) above which individual steps are flagged.
        """
        if not self._records:
            logger.info("[profile:report] %s — no records collected", self.name)
            return

        total = self.total_elapsed
        logger.info(
            "[profile:report] %s — %d step(s), total=%.6fs",
            self.name,
            len(self._records),
            total,
        )
        for record in self._records:
            pct = (record.elapsed / total * 100) if total > 0 else 0.0
            flag = " [SLOW]" if record.elapsed >= slow_threshold else ""
            logger.info(
                "[profile:report]   %-30s %8.6fs  (%5.1f%%)%s",
                record.label,
                record.elapsed,
                pct,
                flag,
            )
        if self._records:
            slowest = max(self._records, key=lambda r: r.elapsed)
            logger.info("[profile:report] slowest step: %s (%.6fs)", slowest.label, slowest.elapsed)
