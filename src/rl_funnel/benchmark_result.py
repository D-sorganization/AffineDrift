"""Shared BenchmarkResult - centralises types for #2309."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BenchmarkResult:
    """Single benchmark episode result."""

    episode_id: int
    total_reward: float
    episode_length: int
    success: bool = False


def format_results(results: list[BenchmarkResult], title: str = "Benchmark") -> str:
    """Format benchmark results summary."""
    if not results:
        return f"{title}: No results"
    rewards = [r.total_reward for r in results]
    return (
        f"{title}: mean={sum(rewards) / len(rewards):.2f}, max={max(rewards):.2f}, n={len(results)}"
    )
