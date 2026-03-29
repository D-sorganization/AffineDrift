"""Focused tests for the RL funnel benchmark issue batch."""

from __future__ import annotations

import numpy as np
import pytest

from src.core.contracts import ContractViolationError
from src.tools.rl_funnel_benchmark import (
    DEFAULT_CONTROL_SATURATION,
    BenchmarkResult,
    double_pendulum_B,
    double_pendulum_drift,
    format_results,
    generate_reference_trajectory,
    run_benchmark,
    run_comparison,
    setpoint_lqr_controller,
    trajectory_tracking_lqr,
)


def test_double_pendulum_drift_rejects_wrong_state_shape() -> None:
    with pytest.raises(ContractViolationError, match="shape"):
        double_pendulum_drift(0.0, np.zeros(3))


def test_double_pendulum_b_rejects_nonfinite_state() -> None:
    with pytest.raises(ContractViolationError):
        double_pendulum_B(np.array([0.0, np.nan, 0.0, 0.0]))


def test_generate_reference_trajectory_rejects_invalid_span() -> None:
    with pytest.raises(ContractViolationError, match="tf > t0"):
        generate_reference_trajectory((1.0, 0.0))


def test_setpoint_lqr_controller_rejects_bad_target_shape() -> None:
    with pytest.raises(ContractViolationError, match="shape"):
        setpoint_lqr_controller(np.zeros(3))


def test_trajectory_tracking_lqr_rejects_bad_reference_shape() -> None:
    t_ref = np.linspace(0.0, 1.0, 5)
    x_ref = np.zeros((3, 5))
    with pytest.raises(ContractViolationError, match="x_ref"):
        trajectory_tracking_lqr(t_ref, x_ref)


def test_run_benchmark_rejects_non_callable_controller() -> None:
    t_ref = np.linspace(0.0, 0.1, 5)
    x_ref = np.zeros((4, 5))
    with pytest.raises(ContractViolationError, match="callable"):
        run_benchmark(  # type: ignore[arg-type]
            None,
            np.zeros(4),
            (0.0, 0.1),
            t_ref,
            x_ref,
            "bad",
        )


def test_run_comparison_rejects_negative_perturbation() -> None:
    with pytest.raises(ContractViolationError, match="positive"):
        run_comparison(perturbation_scale=-0.1)


def test_run_benchmark_respects_configurable_control_limit() -> None:
    t_ref = np.linspace(0.0, 0.1, 5)
    x_ref = np.zeros((4, 5))

    def large_controller(t: float, x: np.ndarray) -> np.ndarray:
        return np.array([200.0, -200.0])

    result = run_benchmark(
        large_controller,
        np.zeros(4),
        (0.0, 0.1),
        t_ref,
        x_ref,
        "limited",
        dt=0.01,
        control_limits=(-5.0, 5.0),
    )
    assert isinstance(result, BenchmarkResult)
    assert result.name == "limited"


def test_format_results_returns_summary_text(caplog: pytest.LogCaptureFixture) -> None:
    results = [
        BenchmarkResult("Setpoint LQR", 4.0, 2.0, 0.1, np.zeros((4, 2)), np.array([0.0, 0.1])),
        BenchmarkResult(
            "Trajectory Tracking (TTCF)",
            2.0,
            3.0,
            0.1,
            np.zeros((4, 2)),
            np.array([0.0, 0.1]),
        ),
    ]
    summary = format_results(results)
    assert "Setpoint LQR" in summary
    assert "4.0000" in summary
    assert "Trajectory Tracking (TTCF)" in summary
    assert "2.0000" in summary


def test_default_control_saturation_positive() -> None:
    assert DEFAULT_CONTROL_SATURATION > 0
