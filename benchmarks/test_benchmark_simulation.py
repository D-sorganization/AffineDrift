"""Benchmarks for simulation engine performance.

Measures the performance of physical simulation including:
- Ball flight dynamics computation
- Trajectory integration (single step)
- Multi-step trajectory simulation
- Swing dynamics evaluation
"""

from __future__ import annotations

import numpy as np
import pytest

from src.affine_control.ddp import adaptive_timestep_ddp_mock
from src.golf_simulation.ball_flight import BallFlightDynamics, BallFlightState


@pytest.mark.benchmark(group="simulation")
class TestSimulationBenchmarks:
    """Benchmark suite for simulation engine performance."""

    def test_benchmark_ball_flight_dynamics_step(
        self, benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark single step of ball flight dynamics.

        The ball flight dynamics are evaluated at each integration timestep,
        making their performance critical for simulation speed.
        """
        dynamics = BallFlightDynamics()

        # Initial state: ball at origin with upward velocity and backspin
        state = np.array(
            [
                0.0,  # x position
                0.0,  # y position
                0.0,  # z position
                30.0,  # vx velocity (m/s)
                0.0,  # vy velocity
                20.0,  # vz velocity
                0.0,  # wx spin
                0.0,  # wy spin
                2500.0,  # wz spin (backspin, rad/s)
            ]
        )
        control = np.zeros(3)  # No active control during flight

        def compute_dynamics() -> np.ndarray:
            return dynamics.dynamics(state, control)

        result = benchmark(compute_dynamics)
        assert result.shape == (9,)
        assert np.isfinite(result).all()

    def test_benchmark_ball_flight_state_creation(
        self, benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark BallFlightState instantiation.

        State object creation is lightweight but happens frequently during
        trajectory tracking and analysis.
        """
        position = np.array([10.0, 5.0, 1.0])
        velocity = np.array([20.0, 0.0, 15.0])
        spin = np.array([0.0, 0.0, 2500.0])

        def create_state() -> BallFlightState:
            return BallFlightState(position, velocity, spin)

        state = benchmark(create_state)
        assert state.speed >= 0.0

    def test_benchmark_ball_flight_linearization(
        self, benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark linearization of ball flight dynamics.

        Linearization (computing Jacobians) is expensive but done infrequently
        (once per optimization iteration in DDP), making it a candidate for
        parallelization and caching.
        """
        dynamics = BallFlightDynamics()

        state = np.array([0.0, 0.0, 0.0, 30.0, 0.0, 20.0, 0.0, 0.0, 2500.0])
        control = np.zeros(3)

        def linearize() -> tuple[np.ndarray, np.ndarray]:
            # Use the built-in linearization method
            return dynamics.linearize(state, control)

        A, B = benchmark(linearize)
        assert A.shape == (9, 9)
        assert B.shape == (9, 3)

    def test_benchmark_trajectory_simulation_10_steps(
        self, benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark trajectory simulation for 10 integration steps.

        This is the minimal simulation length, testing baseline integration cost.
        """
        dynamics = BallFlightDynamics()
        dt = 0.01  # 10ms timesteps
        num_steps = 10

        # Initial state
        state = np.array([0.0, 0.0, 0.0, 30.0, 0.0, 20.0, 0.0, 0.0, 2500.0])
        control = np.zeros(3)

        def simulate_trajectory() -> list[np.ndarray]:
            trajectory = [state.copy()]
            current_state = state.copy()
            for _i in range(num_steps):
                # Simple Euler step
                dstate = dynamics.dynamics(current_state, control)
                current_state = current_state + dstate * dt
                trajectory.append(current_state.copy())
            return trajectory

        trajectory = benchmark(simulate_trajectory)
        assert len(trajectory) == num_steps + 1
        assert all(s.shape == (9,) for s in trajectory)

    def test_benchmark_trajectory_simulation_100_steps(
        self, benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark trajectory simulation for 100 integration steps.

        This represents a realistic trajectory of 1 second at 100Hz,
        testing scaling to typical simulation lengths.
        """
        dynamics = BallFlightDynamics()
        dt = 0.01  # 10ms timesteps
        num_steps = 100

        state = np.array([0.0, 0.0, 0.0, 30.0, 0.0, 20.0, 0.0, 0.0, 2500.0])
        control = np.zeros(3)

        def simulate_trajectory() -> list[np.ndarray]:
            trajectory = [state.copy()]
            current_state = state.copy()
            for _i in range(num_steps):
                dstate = dynamics.dynamics(current_state, control)
                current_state = current_state + dstate * dt
                trajectory.append(current_state.copy())
            return trajectory

        trajectory = benchmark(simulate_trajectory)
        assert len(trajectory) == num_steps + 1

    def test_benchmark_trajectory_simulation_1000_steps(
        self, benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark trajectory simulation for 1000 integration steps.

        This represents a long trajectory of 10 seconds at 100Hz,
        testing scaling to high-resolution simulations.
        """
        dynamics = BallFlightDynamics()
        dt = 0.01  # 10ms timesteps
        num_steps = 1000

        state = np.array([0.0, 0.0, 0.0, 30.0, 0.0, 20.0, 0.0, 0.0, 2500.0])
        control = np.zeros(3)

        def simulate_trajectory() -> list[np.ndarray]:
            trajectory = [state.copy()]
            current_state = state.copy()
            for _i in range(num_steps):
                dstate = dynamics.dynamics(current_state, control)
                current_state = current_state + dstate * dt
                trajectory.append(current_state.copy())
            return trajectory

        trajectory = benchmark(simulate_trajectory)
        assert len(trajectory) == num_steps + 1

    def test_benchmark_ddp_mock_initialization(
        self, benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
    ) -> None:
        """Benchmark DDP solver mock initialization.

        DDP is initialized once per optimization problem and includes
        memory allocation and cost function setup.
        """

        def init_ddp() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
            # Mock dynamics
            def dynamics_fn(x: np.ndarray, u: np.ndarray) -> np.ndarray:
                return np.concatenate([x[2:4], u])

            x0 = np.zeros(4)
            xf = np.array([1.0, 1.0, 0.0, 0.0])
            u_init = np.zeros((50, 2))

            return adaptive_timestep_ddp_mock(
                dynamics_fn, x0, xf, u_init
            )

        result = benchmark(init_ddp)
        assert len(result) == 3  # (x_traj, u_traj, t_traj)


@pytest.mark.benchmark(group="simulation")
def test_benchmark_complete_ball_flight_simulation(
    benchmark: pytest.BenchmarkFixture,  # type: ignore[name-defined]
) -> None:
    """Benchmark complete ball flight simulation from launch to landing.

    This is a module-level benchmark measuring realistic golf ball flight
    simulation including aerodynamic effects, typically lasting 5-7 seconds.
    """
    dynamics = BallFlightDynamics()
    dt = 0.001  # 1ms timesteps for accuracy
    max_time = 7.0  # 7 seconds (typical golf ball flight)

    initial_state = np.array(
        [0.0, 0.0, 0.0, 40.0, 0.0, 30.0, 0.0, 0.0, 3000.0]
    )
    control = np.zeros(3)

    def simulate_full_flight() -> list[np.ndarray]:
        trajectory = [initial_state.copy()]
        current_state = initial_state.copy()
        t = 0.0
        step = 0

        while t < max_time and current_state[2] > -0.1:  # Until landing
            dstate = dynamics.dynamics(current_state, control)
            current_state = current_state + dstate * dt
            trajectory.append(current_state.copy())
            t += dt
            step += 1
            if step > 10000:  # Safety limit
                break

        return trajectory

    trajectory = benchmark(simulate_full_flight)
    assert len(trajectory) > 0
    assert all(s.shape == (9,) for s in trajectory)
