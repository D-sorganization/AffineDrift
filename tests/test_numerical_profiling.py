"""Tests for numerical profiling infrastructure.

TDD suite for src/tools/utils/numerical_profiling.py.
Covers NumericalProfiler, profile_numerical decorator, and ProfilingCollector.
"""

from __future__ import annotations

import logging
import time

import pytest

from src.tools.utils.numerical_profiling import (  # noqa: E402
    NumericalProfiler,
    ProfileRecord,
    ProfilingCollector,
    profile_numerical,
)

# ---------------------------------------------------------------------------
# ProfileRecord
# ---------------------------------------------------------------------------


class TestProfileRecord:
    def test_as_log_line_basic(self):
        record = ProfileRecord(label="rk4_step", elapsed=0.123456)
        line = record.as_log_line()
        assert "[profile]" in line
        assert "rk4_step" in line
        assert "0.123456" in line
        assert "[SLOW]" not in line

    def test_as_log_line_slow_flag(self):
        record = ProfileRecord(label="hessian", elapsed=2.5)
        line = record.as_log_line(slow_threshold=1.0)
        assert "[SLOW]" in line

    def test_as_log_line_exactly_at_threshold_is_slow(self):
        record = ProfileRecord(label="op", elapsed=1.0)
        line = record.as_log_line(slow_threshold=1.0)
        assert "[SLOW]" in line

    def test_as_log_line_with_metadata(self):
        record = ProfileRecord(label="sim", elapsed=0.05, metadata={"dt": 0.001, "steps": 100})
        line = record.as_log_line()
        assert "dt=0.001" in line
        assert "steps=100" in line

    def test_as_log_line_no_metadata_no_parens(self):
        record = ProfileRecord(label="sim", elapsed=0.05)
        line = record.as_log_line()
        assert "(" not in line


# ---------------------------------------------------------------------------
# NumericalProfiler context manager
# ---------------------------------------------------------------------------


class TestNumericalProfiler:
    def test_basic_timing_logged(self, caplog):
        caplog.set_level(logging.INFO)
        with NumericalProfiler("test_op"):
            time.sleep(0.01)
        assert "test_op" in caplog.text
        assert "[profile]" in caplog.text

    def test_record_populated_after_exit(self):
        with NumericalProfiler("my_op") as prof:
            time.sleep(0.005)
        assert prof.record is not None
        assert prof.record.label == "my_op"
        assert prof.record.elapsed >= 0.0

    def test_elapsed_is_positive(self):
        with NumericalProfiler("op") as prof:
            pass
        assert prof.record is not None
        assert prof.record.elapsed >= 0.0

    def test_metadata_passed_through_to_record(self):
        meta = {"shape": "(100,)", "dtype": "float64"}
        with NumericalProfiler("op", metadata=meta) as prof:
            pass
        assert prof.record is not None
        assert prof.record.metadata == meta

    def test_slow_threshold_flag_in_log(self, caplog):
        caplog.set_level(logging.INFO)
        # Use a tiny positive threshold so any real execution qualifies as SLOW
        with NumericalProfiler("slow_op", slow_threshold=1e-9):
            time.sleep(0.001)
        assert "[SLOW]" in caplog.text

    def test_exception_logs_warning(self, caplog):
        caplog.set_level(logging.WARNING)
        with pytest.raises(ValueError):
            with NumericalProfiler("failing_op"):
                raise ValueError("boom")
        assert "failing_op" in caplog.text
        # Warning should be emitted (not just INFO)
        assert any(r.levelno >= logging.WARNING for r in caplog.records)

    def test_exception_still_propagates(self):
        with pytest.raises(RuntimeError, match="propagate"):
            with NumericalProfiler("op"):
                raise RuntimeError("propagate")

    def test_invalid_empty_label_raises(self):
        with pytest.raises(ValueError, match="label"):
            NumericalProfiler("")

    def test_invalid_slow_threshold_raises(self):
        with pytest.raises(ValueError, match="slow_threshold"):
            NumericalProfiler("op", slow_threshold=0.0)

    def test_negative_slow_threshold_raises(self):
        with pytest.raises(ValueError, match="slow_threshold"):
            NumericalProfiler("op", slow_threshold=-1.0)

    def test_record_none_before_exit(self):
        prof = NumericalProfiler("op")
        assert prof.record is None
        prof.__enter__()
        assert prof.record is None
        prof.__exit__(None, None, None)
        assert prof.record is not None


# ---------------------------------------------------------------------------
# profile_numerical decorator
# ---------------------------------------------------------------------------


class TestProfileNumericalDecorator:
    def test_decorator_logs_function_name_as_label(self, caplog):
        caplog.set_level(logging.INFO)

        @profile_numerical()
        def my_numerical_function():
            return 42

        result = my_numerical_function()
        assert result == 42
        assert "my_numerical_function" in caplog.text

    def test_decorator_uses_custom_label(self, caplog):
        caplog.set_level(logging.INFO)

        @profile_numerical("custom_label")
        def some_func():
            return "result"

        some_func()
        assert "custom_label" in caplog.text

    def test_decorator_preserves_return_value(self):
        @profile_numerical()
        def add(a, b):
            return a + b

        assert add(3, 4) == 7

    def test_decorator_preserves_function_name(self):
        @profile_numerical()
        def important_function():
            pass

        assert important_function.__name__ == "important_function"

    def test_decorator_preserves_docstring(self):
        @profile_numerical()
        def documented():
            """My docstring."""
            pass

        assert documented.__doc__ == "My docstring."

    def test_decorator_exception_propagates(self):
        @profile_numerical()
        def broken():
            raise TypeError("bad type")

        with pytest.raises(TypeError, match="bad type"):
            broken()

    def test_decorator_with_args_and_kwargs(self):
        @profile_numerical("matrix_op")
        def multiply(a, b, *, scale=1.0):
            return a * b * scale

        result = multiply(3, 4, scale=2.0)
        assert result == 24.0

    def test_decorator_slow_threshold_flag(self, caplog):
        caplog.set_level(logging.INFO)

        @profile_numerical("instant_op", slow_threshold=0.001)
        def fast():
            time.sleep(0.002)

        fast()
        assert "[SLOW]" in caplog.text


# ---------------------------------------------------------------------------
# ProfilingCollector
# ---------------------------------------------------------------------------


class TestProfilingCollector:
    def test_track_stores_record(self):
        collector = ProfilingCollector("test_sim")
        with collector.track("step_1"):
            pass
        assert len(collector.records) == 1
        assert collector.records[0].label == "step_1"

    def test_multiple_tracks_stored_in_order(self):
        collector = ProfilingCollector("sim")
        for label in ("alpha", "beta", "gamma"):
            with collector.track(label):
                pass
        labels = [r.label for r in collector.records]
        assert labels == ["alpha", "beta", "gamma"]

    def test_total_elapsed_sums_records(self):
        collector = ProfilingCollector("sum_test")
        with collector.track("a"):
            time.sleep(0.005)
        with collector.track("b"):
            time.sleep(0.005)
        assert collector.total_elapsed >= 0.01

    def test_total_elapsed_zero_when_empty(self):
        collector = ProfilingCollector("empty")
        assert collector.total_elapsed == 0.0

    def test_log_report_no_records(self, caplog):
        caplog.set_level(logging.INFO)
        collector = ProfilingCollector("empty_sim")
        collector.log_report()
        assert "no records" in caplog.text

    def test_log_report_with_records(self, caplog):
        caplog.set_level(logging.INFO)
        collector = ProfilingCollector("ddp")
        with collector.track("forward"):
            pass
        with collector.track("backward"):
            pass
        collector.log_report()
        assert "ddp" in caplog.text
        assert "forward" in caplog.text
        assert "backward" in caplog.text
        assert "slowest" in caplog.text

    def test_log_report_includes_percentage(self, caplog):
        caplog.set_level(logging.INFO)
        collector = ProfilingCollector("pct_test")
        with collector.track("step"):
            pass
        collector.log_report()
        # Percentage should appear in the report
        assert "%" in caplog.text

    def test_track_metadata_passed_to_record(self):
        collector = ProfilingCollector("meta_test")
        with collector.track("op", metadata={"n": 10}):
            pass
        assert collector.records[0].metadata == {"n": 10}

    def test_track_yields_profiler(self):
        collector = ProfilingCollector("yield_test")
        with collector.track("op") as prof:
            assert isinstance(prof, NumericalProfiler)

    def test_invalid_name_raises(self):
        with pytest.raises(ValueError, match="name"):
            ProfilingCollector("")

    def test_records_returns_copy(self):
        collector = ProfilingCollector("copy_test")
        with collector.track("x"):
            pass
        records_a = collector.records
        records_b = collector.records
        assert records_a is not records_b  # different list objects

    def test_exception_in_track_propagates(self):
        collector = ProfilingCollector("err_test")
        with pytest.raises(ZeroDivisionError):
            with collector.track("divide"):
                _ = 1 / 0

    def test_slow_threshold_flag_in_track(self, caplog):
        caplog.set_level(logging.INFO)
        collector = ProfilingCollector("slow_test")
        with collector.track("op", slow_threshold=0.001):
            time.sleep(0.002)
        assert "[SLOW]" in caplog.text


# ---------------------------------------------------------------------------
# Integration: profile_numerical used on simulation-like functions
# ---------------------------------------------------------------------------


class TestIntegrationWithSimulationCode:
    """Verify that profiling integrates cleanly with simulation-style logic."""

    def test_profile_rk4_like_function(self, caplog):
        """Confirm profiling works on a function mimicking an RK4 step."""
        import numpy as np

        caplog.set_level(logging.INFO)

        @profile_numerical("rk4_step")
        def mock_rk4(state, dt):
            # Simulate minimal computation
            return state + dt * np.ones_like(state)

        state = np.zeros(9)
        result = mock_rk4(state, 0.001)
        assert result.shape == (9,)
        assert "rk4_step" in caplog.text

    def test_collector_profiles_simulation_loop(self, caplog):
        """Confirm ProfilingCollector works across a multi-step simulation loop."""
        import numpy as np

        caplog.set_level(logging.INFO)

        collector = ProfilingCollector("trajectory_sim")

        state = np.zeros(4)
        for _i in range(3):
            with collector.track("dynamics_eval"):
                state = state + 0.01 * np.ones(4)

        collector.log_report()

        assert len(collector.records) == 3
        assert all(r.label == "dynamics_eval" for r in collector.records)
        assert "trajectory_sim" in caplog.text
        assert collector.total_elapsed >= 0.0
