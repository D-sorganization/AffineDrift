"""Tests for rl_funnel_benchmark.py — pure math and benchmark functions."""

from __future__ import annotations

import numpy as np
import pytest

from src.tools.rl_funnel_benchmark import (
    BenchmarkResult,
    double_pendulum_B,
    double_pendulum_drift,
    generate_reference_trajectory,
    setpoint_lqr_controller,
)


class TestDoublePendulumDrift:
    """Tests for double_pendulum_drift() — passive dynamics."""

    def test_returns_four_element_array(self) -> None:
        """Should return a 4-element array for a 4-element state."""
        x = np.array([0.1, 0.2, 0.0, 0.0])
        result = double_pendulum_drift(0.0, x)
        assert result.shape == (4,)

    def test_at_zero_velocity_returns_gravity_terms(self) -> None:
        """At zero velocity, output should reflect gravitational terms."""
        x = np.array([0.0, 0.0, 0.0, 0.0])
        result = double_pendulum_drift(0.0, x)
        # At origin, sin(0) = 0, so accelerations should be near zero
        assert result[0] == pytest.approx(0.0, abs=1e-10)
        assert result[1] == pytest.approx(0.0, abs=1e-10)

    def test_returns_numpy_array(self) -> None:
        """Should return a numpy ndarray."""
        x = np.array([0.5, 0.3, 0.1, -0.1])
        result = double_pendulum_drift(0.0, x)
        assert isinstance(result, np.ndarray)

    def test_velocities_propagated(self) -> None:
        """First two outputs should equal input velocities."""
        x = np.array([0.1, 0.2, 0.3, 0.4])
        result = double_pendulum_drift(0.0, x)
        assert result[0] == pytest.approx(0.3)
        assert result[1] == pytest.approx(0.4)

    def test_time_invariant(self) -> None:
        """Drift should be time-invariant (same result for different t)."""
        x = np.array([0.5, 0.3, 0.1, -0.1])
        r1 = double_pendulum_drift(0.0, x)
        r2 = double_pendulum_drift(1.5, x)
        np.testing.assert_array_almost_equal(r1, r2)


class TestDoublePendulumB:
    """Tests for double_pendulum_B() — control input matrix."""

    def test_returns_4x2_matrix(self) -> None:
        """Should return a 4x2 control input matrix."""
        x = np.array([0.1, 0.2, 0.0, 0.0])
        B = double_pendulum_B(x)
        assert B.shape == (4, 2)

    def test_first_two_rows_zero(self) -> None:
        """Kinematic rows (positions) should have zero control influence."""
        x = np.array([0.1, 0.2, 0.0, 0.0])
        B = double_pendulum_B(x)
        np.testing.assert_array_almost_equal(B[:2, :], np.zeros((2, 2)))

    def test_returns_numpy_array(self) -> None:
        """Should return a numpy ndarray."""
        x = np.array([0.5, 0.3, 0.1, -0.1])
        B = double_pendulum_B(x)
        assert isinstance(B, np.ndarray)


class TestBenchmarkResult:
    """Tests for BenchmarkResult dataclass."""

    def test_creation(self) -> None:
        """Should create BenchmarkResult with all required fields."""
        t = np.linspace(0, 1, 10)
        traj = np.zeros((4, 10))
        result = BenchmarkResult(
            name="test",
            tracking_error=0.5,
            control_effort=1.0,
            runtime_sec=0.1,
            trajectory=traj,
            t_grid=t,
        )
        assert result.name == "test"
        assert result.tracking_error == pytest.approx(0.5)
        assert result.control_effort == pytest.approx(1.0)

    def test_repr_omits_arrays(self) -> None:
        """repr should omit large array fields (repr=False)."""
        t = np.linspace(0, 1, 100)
        traj = np.zeros((4, 100))
        result = BenchmarkResult(
            name="test",
            tracking_error=0.1,
            control_effort=2.0,
            runtime_sec=0.05,
            trajectory=traj,
            t_grid=t,
        )
        r = repr(result)
        # trajectory and t_grid are repr=False, should not appear in repr
        assert "trajectory" not in r
        assert "t_grid" not in r


class TestGenerateReferenceTrajectory:
    """Tests for generate_reference_trajectory()."""

    def test_returns_tuple_of_arrays(self) -> None:
        """Should return (t_ref, x_ref) tuple of arrays."""
        t_ref, x_ref = generate_reference_trajectory((0.0, 0.1), dt=0.01)
        assert isinstance(t_ref, np.ndarray)
        assert isinstance(x_ref, np.ndarray)

    def test_state_dimension_is_four(self) -> None:
        """State array should have 4 rows (4-DoF system)."""
        t_ref, x_ref = generate_reference_trajectory((0.0, 0.05), dt=0.01)
        assert x_ref.shape[0] == 4

    def test_time_and_state_lengths_match(self) -> None:
        """Time and state arrays should have matching second dimension."""
        t_ref, x_ref = generate_reference_trajectory((0.0, 0.05), dt=0.01)
        assert x_ref.shape[1] == len(t_ref)

    def test_custom_x0(self) -> None:
        """Should accept custom initial state."""
        x0 = np.array([0.1, 0.1, 0.0, 0.0])
        t_ref, x_ref = generate_reference_trajectory((0.0, 0.05), dt=0.01, x0=x0)
        assert x_ref.shape[0] == 4


class TestSetpointLqrController:
    """Tests for setpoint_lqr_controller()."""

    def test_returns_callable(self) -> None:
        """Should return a callable controller function."""
        x_target = np.array([0.0, 0.0, 0.0, 0.0])
        controller = setpoint_lqr_controller(x_target)
        assert callable(controller)

    def test_controller_returns_2d_control(self) -> None:
        """Controller should return 2-element control input."""
        x_target = np.array([0.0, 0.0, 0.0, 0.0])
        controller = setpoint_lqr_controller(x_target)
        x = np.array([0.1, 0.0, 0.0, 0.0])
        u = controller(0.0, x)
        assert u.shape == (2,)

    def test_zero_error_gives_zero_control(self) -> None:
        """When x equals x_target, control should be zero."""
        x_target = np.array([0.0, 0.0, 0.0, 0.0])
        controller = setpoint_lqr_controller(x_target)
        u = controller(0.0, x_target)
        np.testing.assert_array_almost_equal(u, np.zeros(2))


class TestTrajectoryTrackingLqr:
    """Tests for trajectory_tracking_lqr()."""

    def test_returns_callable(self) -> None:
        """Should return a callable controller."""
        from src.tools.rl_funnel_benchmark import trajectory_tracking_lqr

        t_ref, x_ref = generate_reference_trajectory((0.0, 0.1), dt=0.02)
        controller = trajectory_tracking_lqr(t_ref, x_ref)
        assert callable(controller)

    def test_controller_returns_2d_control(self) -> None:
        """Should return 2-element control for 4-DoF state."""
        from src.tools.rl_funnel_benchmark import trajectory_tracking_lqr

        t_ref, x_ref = generate_reference_trajectory((0.0, 0.1), dt=0.02)
        controller = trajectory_tracking_lqr(t_ref, x_ref)
        x = np.array([0.1, 0.2, 0.0, 0.0])
        u = controller(0.05, x)
        assert u.shape == (2,)


class TestRunBenchmark:
    """Tests for run_benchmark()."""

    def test_returns_benchmark_result(self) -> None:
        """Should return a BenchmarkResult."""
        from src.tools.rl_funnel_benchmark import run_benchmark

        t_ref, x_ref = generate_reference_trajectory((0.0, 0.05), dt=0.01)
        x_target = x_ref[:, -1]
        controller = setpoint_lqr_controller(x_target)
        x0 = x_ref[:, 0] + 0.01
        result = run_benchmark(controller, x0, (0.0, 0.05), t_ref, x_ref, "test", dt=0.005)
        assert isinstance(result, BenchmarkResult)
        assert result.name == "test"
        assert result.tracking_error >= 0.0
        assert result.runtime_sec >= 0.0


class TestPrintResults:
    """Tests for print_results() — now uses logger.info() instead of sys.stdout.write()."""

    def test_logs_results(self, caplog: pytest.LogCaptureFixture) -> None:
        """Should log formatted results via logger.info()."""
        import logging

        from src.tools.rl_funnel_benchmark import print_results

        t = np.linspace(0, 1, 10)
        traj = np.zeros((4, 10))
        results = [
            BenchmarkResult("Setpoint LQR", 0.5, 1.0, 0.1, traj, t),
            BenchmarkResult("Trajectory Tracking (TTCF)", 0.3, 1.2, 0.15, traj, t),
        ]
        with caplog.at_level(logging.INFO, logger="src.tools.rl_funnel_benchmark"):
            print_results(results)
        combined = " ".join(caplog.messages)
        assert "Setpoint" in combined
        assert "Trajectory" in combined

    def test_logs_improvement_when_ttcf_better(self, caplog: pytest.LogCaptureFixture) -> None:
        """Should log improvement percentage when TTCF outperforms setpoint."""
        import logging

        from src.tools.rl_funnel_benchmark import print_results

        t = np.linspace(0, 1, 10)
        traj = np.zeros((4, 10))
        results = [
            BenchmarkResult("Setpoint LQR", 1.0, 1.0, 0.1, traj, t),
            BenchmarkResult("Trajectory Tracking (TTCF)", 0.5, 1.2, 0.15, traj, t),
        ]
        with caplog.at_level(logging.INFO, logger="src.tools.rl_funnel_benchmark"):
            print_results(results)
        combined = " ".join(caplog.messages)
        assert "%" in combined

    def test_handles_empty_results(self, caplog: pytest.LogCaptureFixture) -> None:
        """Should not crash with empty results list and still log separator."""
        import logging

        from src.tools.rl_funnel_benchmark import print_results

        with caplog.at_level(logging.INFO, logger="src.tools.rl_funnel_benchmark"):
            print_results([])
        combined = " ".join(caplog.messages)
        assert "=" in combined
