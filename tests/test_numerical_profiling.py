"""Tests for numerical profiling infrastructure (issue #2075).

TDD test suite: memory profiling decorator, benchmark harness for DDP solver
and ball flight simulation, and baseline performance metric reporting.
"""

from __future__ import annotations

import time

import numpy as np
import pytest

from src.tools.utils.profiling_utils import (
    NumericalProfileResult,
    profile_memory,
    run_numerical_benchmark,
)


class TestNumericalProfileResult:
    def test_result_stores_function_name(self) -> None:
        result = NumericalProfileResult(
            function_name="my_func", elapsed_seconds=0.5, peak_memory_bytes=1024, iterations=1
        )
        assert result.function_name == "my_func"

    def test_result_stores_elapsed_seconds(self) -> None:
        result = NumericalProfileResult(
            function_name="f", elapsed_seconds=1.23, peak_memory_bytes=0, iterations=1
        )
        assert result.elapsed_seconds == pytest.approx(1.23)

    def test_result_stores_peak_memory_bytes(self) -> None:
        result = NumericalProfileResult(
            function_name="f", elapsed_seconds=0.0, peak_memory_bytes=2048, iterations=1
        )
        assert result.peak_memory_bytes == 2048

    def test_result_stores_iterations(self) -> None:
        result = NumericalProfileResult(
            function_name="f", elapsed_seconds=0.0, peak_memory_bytes=0, iterations=5
        )
        assert result.iterations == 5

    def test_result_mean_elapsed_divides_by_iterations(self) -> None:
        result = NumericalProfileResult(
            function_name="f", elapsed_seconds=3.0, peak_memory_bytes=0, iterations=3
        )
        assert result.mean_elapsed_seconds == pytest.approx(1.0)

    def test_result_summary_contains_function_name(self) -> None:
        result = NumericalProfileResult(
            function_name="solve_ddp", elapsed_seconds=0.1, peak_memory_bytes=512, iterations=1
        )
        assert "solve_ddp" in result.summary()

    def test_result_summary_contains_elapsed(self) -> None:
        result = NumericalProfileResult(
            function_name="f", elapsed_seconds=2.5, peak_memory_bytes=1024, iterations=1
        )
        summary = result.summary()
        assert "2.5" in summary or "2.50" in summary

    def test_result_summary_contains_memory(self) -> None:
        result = NumericalProfileResult(
            function_name="f", elapsed_seconds=0.0, peak_memory_bytes=4096, iterations=1
        )
        summary = result.summary()
        assert "4096" in summary or "4.0" in summary or "KB" in summary


class TestProfileMemory:
    def test_decorator_preserves_return_value(self) -> None:
        @profile_memory
        def add(a: int, b: int) -> int:
            return a + b

        assert add(2, 3) == 5

    def test_decorator_preserves_function_name(self) -> None:
        @profile_memory
        def my_special_function() -> None:
            pass

        assert my_special_function.__name__ == "my_special_function"

    def test_decorator_logs_memory_info(self, caplog: pytest.LogCaptureFixture) -> None:
        import logging

        caplog.set_level(logging.INFO)

        @profile_memory
        def allocate_array() -> np.ndarray:
            return np.zeros(10_000)

        allocate_array()
        assert "memory" in caplog.text.lower() or "bytes" in caplog.text.lower()

    def test_decorator_works_with_numpy_allocation(self) -> None:
        @profile_memory
        def make_array(n: int) -> np.ndarray:
            return np.ones(n, dtype=np.float64)

        result = make_array(1000)
        assert result.shape == (1000,)

    def test_decorator_handles_exception_without_swallowing(self) -> None:
        @profile_memory
        def raises() -> None:
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            raises()


class TestRunNumericalBenchmark:
    def test_returns_numerical_profile_result(self) -> None:
        def noop() -> int:
            return 42

        result = run_numerical_benchmark(noop, iterations=1)
        assert isinstance(result, NumericalProfileResult)

    def test_function_name_captured(self) -> None:
        def my_solver() -> None:
            pass

        result = run_numerical_benchmark(my_solver, iterations=1)
        assert result.function_name == "my_solver"

    def test_iterations_stored(self) -> None:
        def fast() -> None:
            pass

        result = run_numerical_benchmark(fast, iterations=3)
        assert result.iterations == 3

    def test_elapsed_is_non_negative(self) -> None:
        def fast() -> None:
            pass

        result = run_numerical_benchmark(fast, iterations=1)
        assert result.elapsed_seconds >= 0.0

    def test_elapsed_accumulates_across_iterations(self) -> None:
        def slow() -> None:
            time.sleep(0.005)

        result_1 = run_numerical_benchmark(slow, iterations=1)
        result_3 = run_numerical_benchmark(slow, iterations=3)
        assert result_3.elapsed_seconds >= result_1.elapsed_seconds

    def test_peak_memory_is_non_negative(self) -> None:
        def fast() -> None:
            pass

        result = run_numerical_benchmark(fast, iterations=1)
        assert result.peak_memory_bytes >= 0

    def test_accepts_args_and_kwargs(self) -> None:
        def add(a: int, b: int = 0) -> int:
            return a + b

        result = run_numerical_benchmark(add, iterations=1, args=(1,), kwargs={"b": 2})
        assert isinstance(result, NumericalProfileResult)

    def test_default_iterations_is_one(self) -> None:
        def noop() -> None:
            pass

        result = run_numerical_benchmark(noop)
        assert result.iterations == 1


class TestDDPSolverBenchmark:
    def _dynamics(self) -> object:
        def f(x: np.ndarray, u: np.ndarray) -> np.ndarray:
            return -0.1 * x + u

        return f

    def test_ddp_benchmark_completes(self) -> None:
        """DDP solver benchmark should run without error."""
        import warnings

        from src.affine_control.ddp import adaptive_timestep_ddp_mock

        f = self._dynamics()
        x0, xf = np.zeros(2), np.ones(2)
        u_init = [np.zeros(2)] * 5

        def run_ddp() -> None:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                adaptive_timestep_ddp_mock(f, x0, xf, u_init, max_iters=2)

        result = run_numerical_benchmark(run_ddp, iterations=1)
        assert isinstance(result, NumericalProfileResult)
        assert result.elapsed_seconds >= 0.0

    def test_ddp_benchmark_peak_memory_tracked(self) -> None:
        """DDP solver benchmark should report peak memory usage."""
        import warnings

        from src.affine_control.ddp import adaptive_timestep_ddp_mock

        f = self._dynamics()
        x0, xf = np.zeros(2), np.ones(2)
        u_init = [np.zeros(2)] * 5

        def run_ddp() -> None:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                adaptive_timestep_ddp_mock(f, x0, xf, u_init, max_iters=2)

        result = run_numerical_benchmark(run_ddp, iterations=1)
        assert result.peak_memory_bytes >= 0

    def test_ddp_benchmark_summary_readable(self) -> None:
        """DDP solver benchmark summary string should reference function name."""
        import warnings

        from src.affine_control.ddp import adaptive_timestep_ddp_mock

        f = self._dynamics()
        x0, xf = np.zeros(2), np.ones(2)
        u_init = [np.zeros(2)] * 5

        def run_ddp() -> None:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                adaptive_timestep_ddp_mock(f, x0, xf, u_init, max_iters=2)

        result = run_numerical_benchmark(run_ddp, iterations=1)
        assert "run_ddp" in result.summary()


class TestBallFlightBenchmark:
    def _initial_state(self) -> object:
        from src.golf_simulation.ball_flight import BallFlightState

        return BallFlightState(
            position=np.array([0.0, 0.0, 0.0]),
            velocity=np.array([60.0, 0.0, 30.0]),
            spin=np.array([0.0, 200.0, 0.0]),
        )

    def test_ball_flight_benchmark_completes(self) -> None:
        """Ball flight simulation benchmark should run without error."""
        from src.golf_simulation.ball_flight import BallFlightDynamics

        dynamics = BallFlightDynamics()
        state = self._initial_state()

        def run_sim() -> None:
            dynamics.simulate(state, dt=0.01, max_time=3.0)

        result = run_numerical_benchmark(run_sim, iterations=1)
        assert isinstance(result, NumericalProfileResult)
        assert result.elapsed_seconds >= 0.0

    def test_ball_flight_benchmark_peak_memory_tracked(self) -> None:
        """Ball flight benchmark should track peak memory allocation."""
        from src.golf_simulation.ball_flight import BallFlightDynamics

        dynamics = BallFlightDynamics()
        state = self._initial_state()

        def run_sim() -> None:
            dynamics.simulate(state, dt=0.01, max_time=3.0)

        result = run_numerical_benchmark(run_sim, iterations=1)
        assert result.peak_memory_bytes >= 0

    def test_ball_flight_benchmark_summary_readable(self) -> None:
        """Ball flight benchmark summary string should reference function name."""
        from src.golf_simulation.ball_flight import BallFlightDynamics

        dynamics = BallFlightDynamics()
        state = self._initial_state()

        def run_sim() -> None:
            dynamics.simulate(state, dt=0.01, max_time=3.0)

        result = run_numerical_benchmark(run_sim, iterations=1)
        assert "run_sim" in result.summary()
