"""Tests for rl_funnel_benchmark.py — pure math and benchmark functions."""

from __future__ import annotations

import numpy as np
import pytest

from src.core.contracts.definitions import ContractViolationError
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
    """Tests for print_results()."""

    def test_prints_to_stdout(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Should print formatted results to stdout."""
        from src.tools.rl_funnel_benchmark import print_results

        t = np.linspace(0, 1, 10)
        traj = np.zeros((4, 10))
        results = [
            BenchmarkResult("Setpoint LQR", 0.5, 1.0, 0.1, traj, t),
            BenchmarkResult("Trajectory Tracking (TTCF)", 0.3, 1.2, 0.15, traj, t),
        ]
        print_results(results)
        captured = capsys.readouterr()
        assert "Setpoint" in captured.out
        assert "Trajectory" in captured.out

    def test_prints_improvement_when_ttcf_better(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Should print improvement percentage when TTCF outperforms setpoint."""
        from src.tools.rl_funnel_benchmark import print_results

        t = np.linspace(0, 1, 10)
        traj = np.zeros((4, 10))
        results = [
            BenchmarkResult("Setpoint LQR", 1.0, 1.0, 0.1, traj, t),
            BenchmarkResult("Trajectory Tracking (TTCF)", 0.5, 1.2, 0.15, traj, t),
        ]
        print_results(results)
        captured = capsys.readouterr()
        assert "%" in captured.out

    def test_handles_empty_results(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Should not crash with empty results list."""
        from src.tools.rl_funnel_benchmark import print_results

        print_results([])
        captured = capsys.readouterr()
        assert "=" in captured.out


class TestInputValidation:
    """Tests for DbC input validation on all public functions (GH1670)."""

    # --- double_pendulum_drift ---

    def test_drift_wrong_shape_raises(self) -> None:
        """double_pendulum_drift should raise on wrong state dimension."""
        x_bad = np.array([0.1, 0.2, 0.0])  # shape (3,) — wrong
        with pytest.raises(ContractViolationError):
            double_pendulum_drift(0.0, x_bad)

    def test_drift_non_array_raises(self) -> None:
        """double_pendulum_drift should raise if x is not an ndarray."""
        with pytest.raises((ContractViolationError, AttributeError)):
            double_pendulum_drift(0.0, [0.1, 0.2, 0.0, 0.0])  # type: ignore[arg-type]

    def test_drift_nan_raises(self) -> None:
        """double_pendulum_drift should raise on NaN in state."""
        x_bad = np.array([np.nan, 0.2, 0.0, 0.0])
        with pytest.raises(ContractViolationError):
            double_pendulum_drift(0.0, x_bad)

    def test_drift_negative_gravity_raises(self) -> None:
        """double_pendulum_drift should raise on non-positive gravity."""
        x = np.array([0.1, 0.2, 0.0, 0.0])
        with pytest.raises(ContractViolationError):
            double_pendulum_drift(0.0, x, g=-9.81)

    def test_drift_zero_gravity_raises(self) -> None:
        """double_pendulum_drift should raise on zero gravity."""
        x = np.array([0.1, 0.2, 0.0, 0.0])
        with pytest.raises(ContractViolationError):
            double_pendulum_drift(0.0, x, g=0.0)

    # --- double_pendulum_B ---

    def test_B_wrong_shape_raises(self) -> None:
        """double_pendulum_B should raise on wrong state dimension."""
        x_bad = np.array([0.1, 0.2])  # shape (2,)
        with pytest.raises(ContractViolationError):
            double_pendulum_B(x_bad)

    def test_B_nan_raises(self) -> None:
        """double_pendulum_B should raise on NaN in state."""
        x_bad = np.array([np.nan, 0.2, 0.0, 0.0])
        with pytest.raises(ContractViolationError):
            double_pendulum_B(x_bad)

    # --- generate_reference_trajectory ---

    def test_traj_reversed_t_span_raises(self) -> None:
        """generate_reference_trajectory should raise when tf <= t0."""
        with pytest.raises(ContractViolationError):
            generate_reference_trajectory((1.0, 0.0))

    def test_traj_equal_t_span_raises(self) -> None:
        """generate_reference_trajectory should raise when t0 == tf."""
        with pytest.raises(ContractViolationError):
            generate_reference_trajectory((0.5, 0.5))

    def test_traj_negative_dt_raises(self) -> None:
        """generate_reference_trajectory should raise on negative dt."""
        with pytest.raises(ContractViolationError):
            generate_reference_trajectory((0.0, 0.1), dt=-0.01)

    def test_traj_zero_dt_raises(self) -> None:
        """generate_reference_trajectory should raise on zero dt."""
        with pytest.raises(ContractViolationError):
            generate_reference_trajectory((0.0, 0.1), dt=0.0)

    def test_traj_bad_x0_shape_raises(self) -> None:
        """generate_reference_trajectory should raise on wrong x0 shape."""
        x0_bad = np.array([0.1, 0.2, 0.0])  # shape (3,)
        with pytest.raises(ContractViolationError):
            generate_reference_trajectory((0.0, 0.1), x0=x0_bad)

    def test_traj_nan_x0_raises(self) -> None:
        """generate_reference_trajectory should raise on NaN in x0."""
        x0_bad = np.array([np.nan, 0.2, 0.0, 0.0])
        with pytest.raises(ContractViolationError):
            generate_reference_trajectory((0.0, 0.1), x0=x0_bad)

    # --- setpoint_lqr_controller ---

    def test_setpoint_wrong_shape_raises(self) -> None:
        """setpoint_lqr_controller should raise on wrong x_target shape."""
        x_bad = np.array([0.1, 0.2])  # shape (2,)
        with pytest.raises(ContractViolationError):
            setpoint_lqr_controller(x_bad)

    def test_setpoint_nan_raises(self) -> None:
        """setpoint_lqr_controller should raise on NaN in x_target."""
        x_bad = np.array([np.nan, 0.0, 0.0, 0.0])
        with pytest.raises(ContractViolationError):
            setpoint_lqr_controller(x_bad)

    # --- trajectory_tracking_lqr ---

    def test_ttlqr_bad_t_ref_raises(self) -> None:
        """trajectory_tracking_lqr should raise on 1-element t_ref."""
        from src.tools.rl_funnel_benchmark import trajectory_tracking_lqr

        t_ref = np.array([0.0])  # only 1 element
        x_ref = np.zeros((4, 1))
        with pytest.raises(ContractViolationError):
            trajectory_tracking_lqr(t_ref, x_ref)

    def test_ttlqr_mismatched_x_ref_raises(self) -> None:
        """trajectory_tracking_lqr should raise when x_ref columns != len(t_ref)."""
        from src.tools.rl_funnel_benchmark import trajectory_tracking_lqr

        t_ref = np.array([0.0, 0.1, 0.2])
        x_ref = np.zeros((4, 5))  # 5 cols but t_ref has 3 elements
        with pytest.raises(ContractViolationError):
            trajectory_tracking_lqr(t_ref, x_ref)

    def test_ttlqr_wrong_state_rows_raises(self) -> None:
        """trajectory_tracking_lqr should raise when x_ref has != 4 rows."""
        from src.tools.rl_funnel_benchmark import trajectory_tracking_lqr

        t_ref = np.array([0.0, 0.1, 0.2])
        x_ref = np.zeros((3, 3))  # 3 rows instead of 4
        with pytest.raises(ContractViolationError):
            trajectory_tracking_lqr(t_ref, x_ref)

    def test_ttlqr_nan_t_ref_raises(self) -> None:
        """trajectory_tracking_lqr should raise on NaN in t_ref."""
        from src.tools.rl_funnel_benchmark import trajectory_tracking_lqr

        t_ref = np.array([0.0, np.nan, 0.2])
        x_ref = np.zeros((4, 3))
        with pytest.raises(ContractViolationError):
            trajectory_tracking_lqr(t_ref, x_ref)

    # --- run_benchmark ---

    def test_run_benchmark_non_callable_raises(self) -> None:
        """run_benchmark should raise when controller is not callable."""
        from src.tools.rl_funnel_benchmark import run_benchmark

        t_ref, x_ref = generate_reference_trajectory((0.0, 0.05), dt=0.01)
        x0 = x_ref[:, 0]
        with pytest.raises(ContractViolationError):
            run_benchmark("not_a_callable", x0, (0.0, 0.05), t_ref, x_ref, "test")  # type: ignore[arg-type]

    def test_run_benchmark_bad_x0_shape_raises(self) -> None:
        """run_benchmark should raise on wrong x0 shape."""
        from src.tools.rl_funnel_benchmark import run_benchmark

        t_ref, x_ref = generate_reference_trajectory((0.0, 0.05), dt=0.01)
        x0_bad = np.array([0.1, 0.2])  # wrong shape
        ctrl = setpoint_lqr_controller(x_ref[:, -1])
        with pytest.raises(ContractViolationError):
            run_benchmark(ctrl, x0_bad, (0.0, 0.05), t_ref, x_ref, "test")

    def test_run_benchmark_reversed_t_span_raises(self) -> None:
        """run_benchmark should raise when t_span is reversed."""
        from src.tools.rl_funnel_benchmark import run_benchmark

        t_ref, x_ref = generate_reference_trajectory((0.0, 0.05), dt=0.01)
        x0 = x_ref[:, 0]
        ctrl = setpoint_lqr_controller(x_ref[:, -1])
        with pytest.raises(ContractViolationError):
            run_benchmark(ctrl, x0, (0.05, 0.0), t_ref, x_ref, "test")

    def test_run_benchmark_negative_dt_raises(self) -> None:
        """run_benchmark should raise on negative dt."""
        from src.tools.rl_funnel_benchmark import run_benchmark

        t_ref, x_ref = generate_reference_trajectory((0.0, 0.05), dt=0.01)
        x0 = x_ref[:, 0]
        ctrl = setpoint_lqr_controller(x_ref[:, -1])
        with pytest.raises(ContractViolationError):
            run_benchmark(ctrl, x0, (0.0, 0.05), t_ref, x_ref, "test", dt=-0.001)

    # --- run_comparison ---

    def test_run_comparison_negative_perturbation_raises(self) -> None:
        """run_comparison should raise on negative perturbation_scale."""
        from src.tools.rl_funnel_benchmark import run_comparison

        with pytest.raises(ContractViolationError):
            run_comparison(perturbation_scale=-0.1, t_span=(0.0, 0.05), dt=0.005)

    def test_run_comparison_reversed_t_span_raises(self) -> None:
        """run_comparison should raise when t_span is reversed."""
        from src.tools.rl_funnel_benchmark import run_comparison

        with pytest.raises(ContractViolationError):
            run_comparison(perturbation_scale=0.1, t_span=(0.5, 0.0), dt=0.005)

    def test_run_comparison_negative_dt_raises(self) -> None:
        """run_comparison should raise on negative dt."""
        from src.tools.rl_funnel_benchmark import run_comparison

        with pytest.raises(ContractViolationError):
            run_comparison(perturbation_scale=0.1, t_span=(0.0, 0.05), dt=-0.005)
