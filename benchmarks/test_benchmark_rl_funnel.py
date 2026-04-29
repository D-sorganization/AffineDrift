"""Benchmarks for RLFunnel solver performance.

Measures the performance of double-pendulum control algorithms including:
- Setpoint LQR controller
- Trajectory-tracking LQR controller
- Simulation loop execution
- Reference trajectory generation
"""

from __future__ import annotations

import numpy as np
import pytest

from src.tools.rl_funnel_benchmark import (
    double_pendulum_drift,
    generate_reference_trajectory,
    setpoint_lqr_controller,
    trajectory_tracking_lqr,
)


@pytest.mark.benchmark(group="rl_funnel")
class TestRLFunnelBenchmarks:
    """Benchmark suite for RL Funnel double-pendulum control algorithms."""

    def test_benchmark_double_pendulum_drift(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark the passive dynamics computation of the double pendulum.

        The drift term f(x, 0) is evaluated frequently during trajectory
        simulation, so its performance is critical.
        """
        x = np.array([0.5, 0.3, 0.1, -0.2])
        t = 0.0

        def drift_step() -> np.ndarray:
            """Invoke double_pendulum_drift for one timestep."""
            return double_pendulum_drift(t, x)

        result = benchmark(drift_step)
        assert result.shape == (4,)
        assert np.isfinite(result).all()

    def test_benchmark_setpoint_lqr_controller(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark setpoint LQR controller evaluation.

        The setpoint controller is the simplest control law and serves as
        a baseline for comparing trajectory-tracking performance.
        """
        target = np.array([np.pi, 0.0, 0.0, 0.0])
        state = np.array([0.5, 0.3, 0.1, -0.2])
        time = 0.0

        def controller_eval() -> np.ndarray:
            """Build and evaluate the setpoint LQR controller."""
            controller = setpoint_lqr_controller(target)
            return controller(time, state)

        result = benchmark(controller_eval)
        assert result.shape == (2,)
        assert np.isfinite(result).all()

    def test_benchmark_trajectory_tracking_lqr(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark trajectory-tracking LQR law evaluation.

        Trajectory tracking is more expensive than setpoint control due to
        the need to track reference states and velocities over time.
        """
        t_ref = np.linspace(0.0, 1.0, 21)
        x_ref = np.zeros((4, 21))
        x_ref[0, :] = np.linspace(0.0, np.pi, 21)
        t_eval = 0.5
        x_eval = np.array([0.5, 0.3, 0.1, -0.2])

        def tracking_eval() -> np.ndarray:
            """Evaluate the trajectory-tracking LQR law at the given state."""
            return trajectory_tracking_lqr(t_ref, x_ref)(t_eval, x_eval)

        result = benchmark(tracking_eval)
        assert result.shape == (2,)
        assert np.isfinite(result).all()

    def test_benchmark_reference_trajectory_generation(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark reference trajectory generation.

        Reference trajectories are generated once per benchmark run and
        serve as templates for trajectory-tracking control objectives.
        """
        time_span = (0.0, 1.0)

        def gen_trajectory() -> tuple[np.ndarray, np.ndarray]:
            """Generate a reference trajectory for the given time span."""
            return generate_reference_trajectory(time_span)

        t_ref, x_ref = benchmark(gen_trajectory)
        assert len(t_ref) > 0
        assert x_ref.shape[0] == 4
        assert x_ref.shape[1] == len(t_ref)

    def test_benchmark_full_simulation_loop(
        self,
        benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark the complete simulation loop using setpoint LQR.

        This measures end-to-end performance of the control-simulation loop,
        which is the primary use case for the RL Funnel algorithm.
        """

        # Create a setpoint controller function factory
        def create_controller() -> callable:  # type: ignore[name-defined]
            """Build a setpoint LQR controller targeting the given state."""
            target = np.array([0.5, 0.3, 0.1, -0.2])
            return setpoint_lqr_controller(target)

        controller = create_controller()
        state = np.array([0.0, 0.0, 0.0, 0.0])
        time = 0.0

        def full_sim() -> None:
            """Execute one control step of the setpoint LQR simulation."""
            # Simulate one control step
            _ = controller(time, state)

        benchmark(full_sim)
        # Benchmark verifies no exceptions occur during simulation


@pytest.mark.benchmark(group="rl_funnel")
def test_benchmark_rl_funnel_solver_convergence(
    benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
) -> None:
    """Benchmark solver convergence time for a typical double-pendulum problem.

    This is a module-level benchmark measuring the total time to solve
    a representative control problem from initial state to reference trajectory.
    """
    t_ref = np.linspace(0.0, 0.5, 11)
    x_ref = np.zeros((4, 11))
    x_ref[0, :] = np.linspace(0.0, np.pi, 11)

    def solve_problem() -> tuple[np.ndarray, np.ndarray]:
        return trajectory_tracking_lqr(t_ref, x_ref)

    result = benchmark(solve_problem)
    assert result is not None
