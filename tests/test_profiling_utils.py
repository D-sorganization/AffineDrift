"""Tests for the numerical profiling infrastructure.

Covers: timing decorator, memory profiling (decorator + context manager),
benchmark harness, data classes, and ProfilingReport formatting.
"""

import logging
import time

import numpy as np
import pytest

from src.tools.utils.profiling_utils import (
    BenchmarkResult,
    MemoryResult,
    ProfilingReport,
    TimingResult,
    benchmark,
    memory_tracking,
    profile_execution_time,
    profile_memory,
)

# ---------------------------------------------------------------------------
# TimingResult
# ---------------------------------------------------------------------------


class TestTimingResult:
    def test_fields(self):
        r = TimingResult(function_name="foo", elapsed_seconds=1.23)
        assert r.function_name == "foo"
        assert r.elapsed_seconds == pytest.approx(1.23)

    def test_frozen(self):
        r = TimingResult(function_name="foo", elapsed_seconds=0.0)
        with pytest.raises(AttributeError):
            r.function_name = "bar"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# MemoryResult
# ---------------------------------------------------------------------------


class TestMemoryResult:
    def test_mb_conversion(self):
        r = MemoryResult(label="test", peak_bytes=1048576, current_bytes=524288)
        assert r.peak_mb == pytest.approx(1.0)
        assert r.current_mb == pytest.approx(0.5)

    def test_zero_bytes(self):
        r = MemoryResult(label="empty", peak_bytes=0, current_bytes=0)
        assert r.peak_mb == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# BenchmarkResult
# ---------------------------------------------------------------------------


class TestBenchmarkResult:
    def test_statistics(self):
        r = BenchmarkResult(function_name="f", iterations=3, times=[1.0, 2.0, 3.0])
        assert r.mean == pytest.approx(2.0)
        assert r.median == pytest.approx(2.0)
        assert r.min_time == pytest.approx(1.0)
        assert r.max_time == pytest.approx(3.0)
        assert r.stdev > 0

    def test_single_iteration_stdev(self):
        r = BenchmarkResult(function_name="f", iterations=1, times=[0.5])
        assert r.stdev == pytest.approx(0.0)

    def test_iterations_field(self):
        r = BenchmarkResult(function_name="g", iterations=5, times=[0.1] * 5)
        assert r.iterations == 5


# ---------------------------------------------------------------------------
# ProfilingReport
# ---------------------------------------------------------------------------


class TestProfilingReport:
    def test_empty_report(self):
        report = ProfilingReport()
        text = report.format_report()
        assert "no results collected" in text

    def test_add_and_format_timing(self):
        report = ProfilingReport()
        report.add_timing(TimingResult("solve", 0.1234))
        text = report.format_report()
        assert "Timing" in text
        assert "solve" in text
        assert "0.1234" in text

    def test_add_and_format_memory(self):
        report = ProfilingReport()
        report.add_memory(MemoryResult("alloc", peak_bytes=2097152, current_bytes=1048576))
        text = report.format_report()
        assert "Memory" in text
        assert "alloc" in text
        assert "2.00" in text  # peak MB

    def test_add_and_format_benchmark(self):
        report = ProfilingReport()
        report.add_benchmark(BenchmarkResult("fn", 3, [0.1, 0.2, 0.15]))
        text = report.format_report()
        assert "Benchmarks" in text
        assert "fn" in text
        assert "3 iters" in text

    def test_mixed_report(self):
        report = ProfilingReport()
        report.add_timing(TimingResult("a", 1.0))
        report.add_memory(MemoryResult("b", 1024, 512))
        report.add_benchmark(BenchmarkResult("c", 2, [0.1, 0.2]))
        text = report.format_report()
        assert "Timing" in text
        assert "Memory" in text
        assert "Benchmarks" in text


# ---------------------------------------------------------------------------
# profile_execution_time decorator
# ---------------------------------------------------------------------------


class TestProfileExecutionTime:
    def test_returns_result(self):
        @profile_execution_time
        def add(a, b):
            return a + b

        assert add(2, 3) == 5

    def test_logs_timing(self, caplog):
        caplog.set_level(logging.INFO)

        @profile_execution_time
        def slow_function(duration):
            time.sleep(duration)
            return "done"

        result = slow_function(0.01)
        assert result == "done"
        assert "seconds to execute" in caplog.text

    def test_preserves_name(self):
        @profile_execution_time
        def my_named_func():
            return None

        assert my_named_func.__name__ == "my_named_func"


# ---------------------------------------------------------------------------
# profile_memory decorator
# ---------------------------------------------------------------------------


class TestProfileMemory:
    def test_no_args_decorator(self, caplog):
        caplog.set_level(logging.INFO)

        @profile_memory
        def allocate():
            return bytearray(1024 * 1024)

        result = allocate()
        assert len(result) == 1024 * 1024
        assert "Memory" in caplog.text

    def test_with_label_and_report(self, caplog):
        caplog.set_level(logging.INFO)
        report = ProfilingReport()

        @profile_memory(label="big alloc", report=report)
        def allocate():
            return bytearray(1024 * 1024)

        allocate()
        assert len(report.memory_results) == 1
        assert report.memory_results[0].label == "big alloc"
        assert report.memory_results[0].peak_bytes > 0

    def test_preserves_function_name(self):
        @profile_memory
        def named_fn():
            return None

        assert named_fn.__name__ == "named_fn"

    def test_returns_value(self):
        @profile_memory
        def compute():
            return 42

        assert compute() == 42


# ---------------------------------------------------------------------------
# memory_tracking context manager
# ---------------------------------------------------------------------------


class TestMemoryTracking:
    def test_basic_tracking(self, caplog):
        caplog.set_level(logging.INFO)
        with memory_tracking("test block"):
            _ = bytearray(1024 * 1024)
        assert "Memory [test block]" in caplog.text

    def test_with_report(self):
        report = ProfilingReport()
        with memory_tracking("ctx block", report=report):
            _ = bytearray(512 * 1024)
        assert len(report.memory_results) == 1
        assert report.memory_results[0].label == "ctx block"
        assert report.memory_results[0].peak_bytes > 0

    def test_default_label(self, caplog):
        caplog.set_level(logging.INFO)
        with memory_tracking():
            pass
        assert "Memory [block]" in caplog.text


# ---------------------------------------------------------------------------
# benchmark harness
# ---------------------------------------------------------------------------


class TestBenchmark:
    def test_basic_benchmark(self):
        def noop():
            return None

        result = benchmark(noop, iterations=3)
        assert result.function_name == "noop"
        assert result.iterations == 3
        assert len(result.times) == 3
        assert all(t >= 0 for t in result.times)

    def test_with_args(self):
        def add(a, b):
            return a + b

        result = benchmark(add, args=(1, 2), iterations=2)
        assert result.iterations == 2

    def test_with_kwargs(self):
        def greet(name="world"):
            return f"hello {name}"

        result = benchmark(greet, kwargs={"name": "test"}, iterations=1)
        assert result.iterations == 1

    def test_invalid_iterations(self):
        with pytest.raises(ValueError, match="iterations must be >= 1"):
            benchmark(lambda: None, iterations=0)

    def test_warmup_runs(self):
        call_count = 0

        def counting():
            nonlocal call_count
            call_count += 1

        benchmark(counting, iterations=3, warmup=2)
        assert call_count == 5  # 2 warmup + 3 timed

    def test_with_report(self):
        report = ProfilingReport()

        def noop():
            return None

        benchmark(noop, iterations=2, report=report)
        assert len(report.benchmark_results) == 1
        assert report.benchmark_results[0].function_name == "noop"

    def test_custom_label(self):
        result = benchmark(lambda: None, iterations=1, label="custom")
        assert result.function_name == "custom"

    def test_numerical_function(self):
        """Benchmark a realistic numerical function (matrix multiply)."""

        def mat_mul():
            a = np.random.randn(50, 50)
            b = np.random.randn(50, 50)
            return a @ b

        result = benchmark(mat_mul, iterations=3, warmup=1)
        assert result.mean > 0
        assert result.median > 0


# ---------------------------------------------------------------------------
# Integration: profiling DDP and ball flight simulation code
# ---------------------------------------------------------------------------


class TestSimulationProfiling:
    """Integration tests that profile actual simulation code paths."""

    def test_profile_ball_flight_dynamics(self):
        """Benchmark BallFlightDynamics.dynamics evaluation."""
        from src.golf_simulation.ball_flight import BallFlightDynamics

        dynamics = BallFlightDynamics()
        state = np.array([0.0, 0.0, 0.0, 70.0, 0.0, 30.0, 0.0, 300.0, 0.0])
        control = np.zeros(3)

        result = benchmark(
            dynamics.dynamics,
            args=(state, control),
            iterations=5,
            warmup=1,
            label="ball_flight_dynamics",
        )
        assert result.mean < 1.0  # should be very fast

    def test_profile_ball_flight_simulate(self):
        """Benchmark a short ball flight simulation with memory tracking."""
        from src.golf_simulation.ball_flight import (
            BallFlightDynamics,
            BallFlightState,
        )

        report = ProfilingReport()
        dynamics = BallFlightDynamics()
        initial = BallFlightState(
            position=np.array([0.0, 0.0, 0.0]),
            velocity=np.array([50.0, 0.0, 20.0]),
            spin=np.array([0.0, 200.0, 0.0]),
        )

        with memory_tracking("ball_flight_simulate", report=report):
            trajectory = dynamics.simulate(initial, dt=0.01, max_time=1.0)

        assert len(trajectory) > 1
        assert len(report.memory_results) == 1
        assert report.memory_results[0].peak_bytes > 0

    def test_profile_ddp_mock(self):
        """Benchmark adaptive_timestep_ddp_mock with report collection."""
        import warnings

        from src.affine_control.ddp import adaptive_timestep_ddp_mock

        report = ProfilingReport()
        x0 = np.array([1.0, 0.0])
        xf = np.array([0.0, 0.0])
        u_init = [np.array([0.1]) for _ in range(10)]

        def f(x, u):
            return np.array([-x[0] + u[0], x[0] - x[1]])

        def run_ddp():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                adaptive_timestep_ddp_mock(f, x0, xf, u_init, max_iters=2)

        result = benchmark(run_ddp, iterations=3, warmup=1, report=report)
        assert result.mean > 0
        assert len(report.benchmark_results) == 1

    def test_full_profiling_report(self):
        """End-to-end: collect timing, memory, and benchmark into one report."""
        report = ProfilingReport()

        # Timing
        report.add_timing(TimingResult("setup", 0.001))

        # Memory via context manager
        with memory_tracking("array_alloc", report=report):
            _ = np.zeros((100, 100))

        # Benchmark
        benchmark(
            lambda: np.linalg.norm(np.random.randn(100)),
            iterations=3,
            label="norm_100d",
            report=report,
        )

        text = report.format_report()
        assert "Timing" in text
        assert "Memory" in text
        assert "Benchmarks" in text
        assert "setup" in text
        assert "array_alloc" in text
        assert "norm_100d" in text
