"""Benchmarks for trajectory cost computation performance.

Measures the performance of trajectory-tracking and setpoint control
cost metrics, which are used to evaluate control laws and compare
different control strategies.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.tools.trajectory_cost_benchmark import (
    benchmark_cost_gap,
    setpoint_cost,
    trajectory_tracking_cost,
)


@pytest.mark.benchmark(group="trajectory_cost")
class TestTrajectoryCostBenchmarks:
    """Benchmark suite for trajectory cost computation."""

    def test_benchmark_setpoint_cost_small(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark setpoint cost for a small trajectory (4 states).

        Setpoint cost ignores the path taken and only measures final
        deviation from the target state.
        """
        trajectory = np.array([[0.0], [1.0], [2.0], [3.0]])
        target = np.array([3.0])

        def compute_cost() -> float:
            """Compute setpoint cost for the small trajectory."""
            return setpoint_cost(trajectory, target)

        result = benchmark(compute_cost)
        assert isinstance(result, (float, np.floating))
        assert result >= 0.0

    def test_benchmark_setpoint_cost_medium(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark setpoint cost for a medium trajectory (100 states).

        This reflects realistic trajectory lengths used in control
        problems with moderate time horizons.
        """
        trajectory = np.linspace(0.0, 5.0, 100).reshape(-1, 1)
        target = np.array([5.0])

        def compute_cost() -> float:
            """Compute setpoint cost for the medium trajectory."""
            return setpoint_cost(trajectory, target)

        result = benchmark(compute_cost)
        assert isinstance(result, (float, np.floating))
        assert result >= 0.0

    def test_benchmark_trajectory_tracking_cost_small(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark trajectory tracking cost for a small reference (4 states).

        Trajectory tracking penalizes deviation from a reference path,
        not just final state error.
        """
        reference = np.linspace(0.0, 3.0, 4).reshape(-1, 1)
        trajectory = reference.copy()

        def compute_cost() -> float:
            """Compute trajectory tracking cost for the small reference."""
            return trajectory_tracking_cost(trajectory, reference)

        result = benchmark(compute_cost)
        assert isinstance(result, (float, np.floating))
        assert result >= 0.0

    def test_benchmark_trajectory_tracking_cost_medium(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark trajectory tracking cost for a medium reference (100 states).

        This reflects realistic reference trajectories in trajectory-tracking
        control with moderate time horizons.
        """
        reference = np.linspace(0.0, 5.0, 100).reshape(-1, 1)
        trajectory = reference.copy()

        def compute_cost() -> float:
            """Compute trajectory tracking cost for the medium reference."""
            return trajectory_tracking_cost(trajectory, reference)

        result = benchmark(compute_cost)
        assert isinstance(result, (float, np.floating))
        assert result >= 0.0

    def test_benchmark_trajectory_tracking_cost_large(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark trajectory tracking cost for a large reference (1000 states).

        This represents a high-resolution trajectory with many control steps,
        which tests scalability of the cost computation.
        """
        reference = np.linspace(0.0, 10.0, 1000).reshape(-1, 1)
        trajectory = reference.copy() + np.random.normal(0, 0.01, reference.shape)

        def compute_cost() -> float:
            """Compute trajectory tracking cost for the large reference."""
            return trajectory_tracking_cost(trajectory, reference)

        result = benchmark(compute_cost)
        assert isinstance(result, (float, np.floating))
        assert result >= 0.0

    def test_benchmark_trajectory_tracking_with_deviation(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark trajectory tracking cost when actual deviates from reference.

        This tests cost computation when the trajectory diverges from
        the planned reference, which is the typical use case.
        """
        reference = np.linspace(0.0, 5.0, 50).reshape(-1, 1)
        # Create a trajectory that deviates in the middle
        trajectory = reference.copy()
        trajectory[20:30] += 0.5  # Introduce 0.5 unit deviation

        def compute_cost() -> float:
            """Compute trajectory tracking cost when actual deviates from reference."""
            return trajectory_tracking_cost(trajectory, reference)

        result = benchmark(compute_cost)
        assert isinstance(result, (float, np.floating))
        assert result > 0.0

    def test_benchmark_setpoint_vs_tracking_gap(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark the cost gap analysis between setpoint and tracking objectives.

        This measures the time to compute the complete benchmark comparison,
        which evaluates the advantage of trajectory tracking over setpoint control.
        """

        def compute_gap() -> dict[str, float]:
            """Compute the cost gap between setpoint and tracking objectives."""
            return benchmark_cost_gap()

        result = benchmark(compute_gap)
        assert isinstance(result, dict)
        assert "tracking_advantage" in result
        assert result["tracking_advantage"] >= 0.0


@pytest.mark.benchmark(group="trajectory_cost")
def test_benchmark_cost_computation_scaling(
    benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
) -> None:
    """Benchmark how trajectory cost scales with trajectory length.

    This is a module-level benchmark that measures cost computation time
    for a realistic multi-dimensional trajectory (4D state space, 100 steps).
    """
    # 4D state space trajectory (e.g., double pendulum: [th1, th2, dth1, dth2])
    reference = np.zeros((4, 100))
    reference[0, :] = np.linspace(0.0, np.pi, 100)
    reference[1, :] = np.linspace(0.0, np.pi / 2, 100)
    trajectory = reference.copy() + np.random.normal(0, 0.05, reference.shape)

    def compute_cost() -> float:
        """Compute tracking cost for the 4D scaling trajectory."""
        return trajectory_tracking_cost(trajectory, reference)

    benchmark(compute_cost)
