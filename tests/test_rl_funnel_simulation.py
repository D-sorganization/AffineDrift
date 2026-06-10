"""Behavioral tests for ``src/tools/rl_funnel_simulation.py`` (issue #3230).

Covers the input-validation contract (``_validate_benchmark_inputs``), the pure
metrics helper (``_compute_tracking_metrics``), and an end-to-end short
``run_benchmark`` smoke (shapes, finiteness, determinism).
"""

from __future__ import annotations

import numpy as np
import pytest

from src.core.contracts.definitions import ContractViolationError
from src.tools.rl_funnel_simulation import (
    _compute_tracking_metrics,
    _validate_benchmark_inputs,
    run_benchmark,
)


def _zero_controller(_t: float, x: np.ndarray) -> np.ndarray:
    return np.zeros(2)


def test_validate_inputs_accepts_well_formed_arguments() -> None:
    # Should not raise.
    _validate_benchmark_inputs(_zero_controller, np.zeros(4), (0.0, 1.0), 0.01)


def test_validate_inputs_rejects_non_callable() -> None:
    with pytest.raises(ContractViolationError):
        _validate_benchmark_inputs("not callable", np.zeros(4), (0.0, 1.0), 0.01)


def test_validate_inputs_rejects_wrong_state_shape() -> None:
    with pytest.raises(ContractViolationError):
        _validate_benchmark_inputs(_zero_controller, np.zeros(3), (0.0, 1.0), 0.01)


def test_validate_inputs_rejects_nonincreasing_time_span() -> None:
    with pytest.raises(ContractViolationError):
        _validate_benchmark_inputs(_zero_controller, np.zeros(4), (1.0, 0.0), 0.01)


def test_validate_inputs_rejects_nonpositive_dt() -> None:
    with pytest.raises(ContractViolationError):
        _validate_benchmark_inputs(_zero_controller, np.zeros(4), (0.0, 1.0), 0.0)


def test_compute_metrics_zero_error_for_matching_trajectory() -> None:
    t_eval = np.linspace(0.0, 1.0, 5)
    x_ref = np.zeros((4, 5))
    # x_sim exactly equals the (interpolated) reference -> zero tracking error.
    x_sim = np.zeros((4, 5))
    tracking_error, control_effort = _compute_tracking_metrics(
        _zero_controller, x_sim, t_eval, t_eval, x_ref
    )
    assert tracking_error == pytest.approx(0.0, abs=1e-12)
    assert control_effort == pytest.approx(0.0, abs=1e-12)


def test_compute_metrics_positive_error_when_state_offset() -> None:
    t_eval = np.linspace(0.0, 1.0, 5)
    x_ref = np.zeros((4, 5))
    x_sim = np.ones((4, 5))  # constant offset from reference
    tracking_error, _ = _compute_tracking_metrics(_zero_controller, x_sim, t_eval, t_eval, x_ref)
    # Each column error is [1,1,1,1] -> squared-norm 4; mean over time is 4.
    assert tracking_error == pytest.approx(4.0)


def test_compute_metrics_reflects_control_effort() -> None:
    t_eval = np.linspace(0.0, 1.0, 4)
    x_ref = np.zeros((4, 4))
    x_sim = np.zeros((4, 4))

    def unit_controller(_t: float, _x: np.ndarray) -> np.ndarray:
        return np.ones(2)

    _, control_effort = _compute_tracking_metrics(unit_controller, x_sim, t_eval, t_eval, x_ref)
    # sum of squares of [1,1] = 2 at every step -> mean 2.
    assert control_effort == pytest.approx(2.0)


def test_run_benchmark_returns_finite_result_and_is_deterministic() -> None:
    x0 = np.array([0.1, 0.0, -0.1, 0.0])
    t_span = (0.0, 0.05)
    t_ref = np.linspace(0.0, 0.05, 6)
    x_ref = np.zeros((4, 6))

    res1 = run_benchmark(_zero_controller, x0.copy(), t_span, t_ref, x_ref, "Setpoint", dt=0.01)
    res2 = run_benchmark(_zero_controller, x0.copy(), t_span, t_ref, x_ref, "Setpoint", dt=0.01)

    assert res1.name == "Setpoint"
    assert np.isfinite(res1.tracking_error)
    assert np.isfinite(res1.control_effort)
    assert res1.trajectory.shape[0] == 4
    assert res1.t_grid.ndim == 1
    # Deterministic ODE integration -> identical trajectories across runs.
    assert res1.tracking_error == pytest.approx(res2.tracking_error)
