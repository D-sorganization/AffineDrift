"""Benchmarks for optimization algorithms performance.

Measures the performance of the swing optimization pipeline, including:
- Cost computation (instantaneous, terminal, and trajectory costs)
- Optimizer initialization and setup
- Complete optimization iterations
"""

from __future__ import annotations

import numpy as np
import pytest

from src.affine_control.swing_optimizer import SwingOptimizer
from src.affine_control.swing_types import SwingOptimizationConfig


def simple_double_integrator_dynamics(x: np.ndarray, u: np.ndarray) -> np.ndarray:
    """Simple linear double-integrator dynamics for benchmarking.

    State: [q1, q2, ..., qn, dq1, dq2, ..., dqn] (n positions + n velocities)
    Control: [u1, u2, ..., un] (n joint accelerations)
    """
    n = len(x) // 2
    dq = x[n:]
    ddq = u
    return np.concatenate([dq, ddq])


@pytest.mark.benchmark(group="optimizer")
class TestOptimizerBenchmarks:
    """Benchmark suite for swing optimization algorithms."""

    def test_benchmark_optimizer_instantiation(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark SwingOptimizer initialization.

        Optimizer setup includes building cost weight matrices and
        initializing internal state. This happens once per optimization problem.
        """
        config = SwingOptimizationConfig(
            n_joints=3,
            horizon_steps=50,
            allow_mock_solver=True,
        )

        def create_optimizer() -> SwingOptimizer:
            return SwingOptimizer(config)

        optimizer = benchmark(create_optimizer)
        assert optimizer is not None
        assert optimizer.config.n_joints == 3

    def test_benchmark_instantaneous_cost_computation(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark instantaneous cost c(x, u) computation.

        Instantaneous costs are computed frequently during optimization
        iterations (once per timestep per iteration), making their speed critical.
        """
        config = SwingOptimizationConfig(n_joints=3, horizon_steps=50, allow_mock_solver=True)
        optimizer = SwingOptimizer(config)

        state = np.zeros(config.state_dim)
        control = np.ones(config.control_dim) * 0.1

        def compute_cost() -> float:
            return optimizer.compute_cost(state, control)

        result = benchmark(compute_cost)
        assert isinstance(result, float)
        assert result >= 0.0

    def test_benchmark_terminal_cost_computation(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark terminal cost c_f(x_T) computation.

        Terminal costs are computed once per optimization iteration but with
        a higher weight, making their computational cost significant.
        """
        config = SwingOptimizationConfig(n_joints=3, horizon_steps=50, allow_mock_solver=True)
        optimizer = SwingOptimizer(config)

        state = np.zeros(config.state_dim)
        state[config.n_joints :] = 5.0  # Target velocity

        def compute_terminal_cost() -> float:
            return optimizer.compute_terminal_cost(state)

        result = benchmark(compute_terminal_cost)
        assert isinstance(result, float)
        assert result >= 0.0

    def test_benchmark_trajectory_cost_short_horizon(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark trajectory cost computation for short horizon (10 steps).

        Trajectory cost requires summing costs over the entire time horizon,
        so this tests computational scaling with horizon length.
        """
        config = SwingOptimizationConfig(n_joints=2, horizon_steps=10, allow_mock_solver=True)
        optimizer = SwingOptimizer(config)

        trajectory = [np.zeros(config.state_dim) for _ in range(11)]
        controls = [np.ones(config.control_dim) * 0.1 for _ in range(10)]

        def compute_trajectory_cost() -> float:
            return optimizer.compute_trajectory_cost(trajectory, controls)

        result = benchmark(compute_trajectory_cost)
        assert isinstance(result, float)
        assert result >= 0.0

    def test_benchmark_trajectory_cost_long_horizon(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark trajectory cost computation for long horizon (100 steps).

        This tests scalability of cost computation to longer planning horizons,
        which is important for high-resolution trajectory planning.
        """
        config = SwingOptimizationConfig(n_joints=2, horizon_steps=100, allow_mock_solver=True)
        optimizer = SwingOptimizer(config)

        trajectory = [np.zeros(config.state_dim) for _ in range(101)]
        controls = [np.ones(config.control_dim) * 0.1 for _ in range(100)]

        def compute_trajectory_cost() -> float:
            return optimizer.compute_trajectory_cost(trajectory, controls)

        result = benchmark(compute_trajectory_cost)
        assert isinstance(result, float)
        assert result >= 0.0

    def test_benchmark_high_dimensional_optimizer(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark optimizer for high-dimensional system (6 joints).

        This tests how optimizer performance scales with system dimensionality,
        which is important for complex multi-joint mechanisms.
        """
        config = SwingOptimizationConfig(
            n_joints=6,
            horizon_steps=50,
            allow_mock_solver=True,
        )
        optimizer = SwingOptimizer(config)

        state = np.zeros(config.state_dim)
        control = np.ones(config.control_dim) * 0.1

        def compute_cost() -> float:
            return optimizer.compute_cost(state, control)

        result = benchmark(compute_cost)
        assert isinstance(result, float)
        assert result >= 0.0


@pytest.mark.benchmark(group="optimizer")
def test_benchmark_optimizer_cost_matrix_construction(
    benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
) -> None:
    """Benchmark cost weight matrix construction.

    This is a module-level benchmark measuring the time to build Q, R, and Q_f
    matrices, which scales with state and control dimensions.
    """
    config = SwingOptimizationConfig(n_joints=4, horizon_steps=50, allow_mock_solver=True)

    def create_optimizer_and_access_matrices() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        optimizer = SwingOptimizer(config)
        return optimizer.Q, optimizer.R, optimizer.Q_f

    Q, R, Q_f = benchmark(create_optimizer_and_access_matrices)
    assert Q.shape == (config.state_dim, config.state_dim)
    assert R.shape == (config.control_dim, config.control_dim)
    assert Q_f.shape == (config.state_dim, config.state_dim)


@pytest.mark.benchmark(group="optimizer")
def test_benchmark_full_trajectory_cost_realistic_problem(
    benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
) -> None:
    """Benchmark trajectory cost for a realistic 3-joint swing optimization problem.

    This measures the cost computation for a realistic golf swing optimization
    problem with 3 joints and 50-step horizon, executed 10 times (typical for
    optimization convergence checks).
    """
    config = SwingOptimizationConfig(n_joints=3, horizon_steps=50, allow_mock_solver=True)
    optimizer = SwingOptimizer(config)

    # Generate a realistic trajectory (e.g., from a DDP solver)
    trajectory = [np.random.normal(0, 0.1, config.state_dim) for _ in range(51)]
    controls = [np.random.normal(0, 0.01, config.control_dim) for _ in range(50)]

    def compute_full_cost() -> float:
        return optimizer.compute_trajectory_cost(trajectory, controls)

    benchmark(compute_full_cost)
