"""Numerical profiling infrastructure for simulation and control code.

Provides a context manager and decorator for timing numerical operations,
with structured report output via logging.  Designed to complement the
existing :func:`profile_execution_time` decorator in ``profiling_utils``
with richer, simulation-specific instrumentation.

Usage (context manager)::

    with NumericalProfiler("rk4_step") as prof:
        result = dynamics.simulate(initial_state)
    # timing is logged automatically when the block exits

Usage (decorator)::

    @profile_numerical("hessian_computation")
    def expensive_hessian(f, x, u):
        ...

Usage (batch report)::

    collector = ProfilingCollector()
    with collector.track("forward_pass"):
        ...
    with collector.track("backward_pass"):
        ...
    collector.log_report()
"""

from __future__ import annotations

import functools
import logging
import timeit
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# Threshold (seconds) above which a timing is flagged as slow in the report.
_SLOW_THRESHOLD_DEFAULT = 1.0


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

    Logs the elapsed time at INFO level when the block exits normally,
    or at WARNING level if an exception propagates out.

    Example::

        with NumericalProfiler("simulate_trajectory", metadata={"dt": 0.001}) as p:
            result = model.simulate(state)
        # p.record is available after exit

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

    Wraps the target function in a :class:`NumericalProfiler` context and
    logs elapsed time via the module logger at INFO level.

    Args:
        label: Operation label.  Defaults to the decorated function's ``__name__``.
        slow_threshold: Duration (s) above which the timing is flagged SLOW.

    Returns:
        A decorator that wraps the target callable.

    Example::

        @profile_numerical("hessian_bound")
        def compute_hessian_bound(f, x, u):
            ...
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
    """Collects multiple :class:`ProfileRecord` entries and can emit a summary.

    Useful when you want to profile several named steps inside a simulation
    loop and then log a consolidated report at the end.

    Example::

        collector = ProfilingCollector("ddp_iteration")
        with collector.track("forward_pass"):
            ...
        with collector.track("backward_pass"):
            ...
        collector.log_report()
    """

    def __init__(self, name: str = "simulation") -> None:
        """Initialise the collector.

        Args:
            name: Top-level name used in the summary report header.
        """
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

    def log_report(
        self,
        slow_threshold: float = _SLOW_THRESHOLD_DEFAULT,
    ) -> None:
        """Emit a structured profiling report to the logger at INFO level.

        The report includes each individual timing and a summary line showing
        total elapsed time and the fraction spent in the slowest step.

        Args:
            slow_threshold: Duration (s) above which individual steps are flagged.
        """
        if not self._records:
            logger.info("[profile:report] %s — no records collected", self.name)
            return

        total = self.total_elapsed
        logger.info(
            "[profile:report] %s — %d step(s), total=%.6fs", self.name, len(self._records), total
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
