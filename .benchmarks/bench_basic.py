import numpy as np

from src.tools.rl_funnel_dynamics import (
    double_pendulum_drift,
    double_pendulum_mass_matrix,
    generate_reference_trajectory,
)


def test_benchmark_drift(benchmark):
    """Benchmark the double pendulum drift dynamics function."""
    x = np.array([np.pi / 2, np.pi / 4, 1.0, -1.0])

    def run():
        """Execute drift simulation."""
        return double_pendulum_drift(0.0, x)

    benchmark(run)


def test_benchmark_mass_matrix(benchmark):
    """Benchmark the double pendulum mass matrix calculation."""

    def run():
        """Calculate mass matrix."""
        return double_pendulum_mass_matrix(np.pi / 2, np.pi / 4)

    benchmark(run)


def test_benchmark_trajectory_generation(benchmark):
    """Benchmark the full reference trajectory generation."""

    # We use a very short time span to keep the benchmark fast
    def run():
        """Generate short trajectory."""
        return generate_reference_trajectory((0.0, 0.1), dt=0.01)

    benchmark(run)
