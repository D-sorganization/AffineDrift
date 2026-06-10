"""Tests for RL funnel simulation helpers."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

from src.tools import rl_funnel_simulation


def test_compute_tracking_metrics_returns_error_and_effort() -> None:
    """Tracking metrics should compute mean squared state/control norms."""

    def controller(_t: float, _x: np.ndarray) -> np.ndarray:
        return np.array([2.0, -1.0])

    t_grid = np.array([0.0, 1.0])
    x_sim = np.array(
        [
            [1.0, 2.0],
            [0.0, 1.0],
            [0.0, 0.0],
            [0.0, 0.0],
        ]
    )
    x_ref = np.zeros((4, 2))

    tracking_error, control_effort = rl_funnel_simulation._compute_tracking_metrics(
        controller, x_sim, t_grid, t_grid, x_ref
    )

    assert tracking_error == pytest.approx((1.0 + 5.0) / 2.0)
    assert control_effort == pytest.approx(5.0)


def test_validate_benchmark_inputs_rejects_bad_contracts() -> None:
    """Benchmark inputs should fail fast on non-callable or malformed data."""
    with pytest.raises(ValueError, match="controller must be callable"):
        rl_funnel_simulation._validate_benchmark_inputs(object(), np.zeros(4), (0.0, 1.0), 0.1)

    with pytest.raises(ValueError, match="shape"):
        rl_funnel_simulation._validate_benchmark_inputs(
            lambda _t, _x: np.zeros(2), np.zeros(3), (0.0, 1.0), 0.1
        )


def test_run_benchmark_uses_solver_and_returns_result(monkeypatch) -> None:
    """run_benchmark should delegate integration and package result metrics."""

    def fake_solve_ivp(closed_loop, t_span, x0, max_step, dense_output):
        assert t_span == (0.0, 0.2)
        assert max_step == 0.1
        assert dense_output is True
        closed_loop(0.0, x0)

        def sol(t_eval):
            return np.tile(x0.reshape(4, 1), (1, len(t_eval)))

        return SimpleNamespace(sol=sol)

    monkeypatch.setattr(rl_funnel_simulation, "solve_ivp", fake_solve_ivp)
    monkeypatch.setattr(
        rl_funnel_simulation,
        "double_pendulum_drift",
        lambda _t, _x: np.zeros(4),
    )
    monkeypatch.setattr(
        rl_funnel_simulation,
        "double_pendulum_B",
        lambda _x: np.zeros((4, 2)),
    )

    result = rl_funnel_simulation.run_benchmark(
        lambda _t, _x: np.array([100.0, -100.0]),
        np.ones(4),
        (0.0, 0.2),
        np.array([0.0, 0.1]),
        np.zeros((4, 2)),
        "fake",
        dt=0.1,
    )

    assert result.name == "fake"
    assert result.trajectory.shape == (4, 2)
    assert result.tracking_error == pytest.approx(4.0)
