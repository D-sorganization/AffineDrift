"""Reporting utilities for the RL funnel benchmark."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy.typing as npt


@dataclass
class BenchmarkResult:
    """Summary metrics for one benchmark controller run."""

    name: str
    tracking_error: float
    control_effort: float
    runtime_sec: float
    trajectory: npt.NDArray[Any] = field(repr=False)
    t_grid: npt.NDArray[Any] = field(repr=False)


def format_results(results: list[BenchmarkResult]) -> str:
    """Return a formatted benchmark comparison table."""
    lines = ["", "=" * 70]
    lines.append(f"{'Controller':<30} {'Tracking Error':>15} {'Control Effort':>15}")
    lines.append("=" * 70)
    for result in results:
        lines.append(
            f"{result.name:<30} {result.tracking_error:>15.4f} "
            f"{result.control_effort:>15.4f}  ({result.runtime_sec:.2f}s)"
        )
    lines.append("=" * 70)

    if len(results) >= 2:
        setpoint = next(result for result in results if "Setpoint" in result.name)
        tracking = next(result for result in results if "Trajectory" in result.name)
        improvement = (setpoint.tracking_error - tracking.tracking_error) / setpoint.tracking_error
        lines.append("")
        lines.append(f"TTCF tracking improvement over setpoint: {improvement * 100:.1f}%")
        if improvement > 0:
            lines.append("Trajectory tracking cost functional outperforms setpoint control.")
        else:
            lines.append("Setpoint control outperforms TTCF in this scenario.")

    return "\n".join(lines)


__all__ = ["BenchmarkResult", "format_results"]
