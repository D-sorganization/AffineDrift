"""Tests for the RL funnel support helpers (issue #3230)."""

from __future__ import annotations

import numpy as np
import pytest

from src.core.contracts.definitions import ContractViolationError
from src.tools.rl_funnel_support import (
    STATE_DIM,
    BenchmarkResult,
    double_pendulum_mass_matrix,
    format_results,
    validate_reference_trajectory,
    validate_state_vector,
    validate_time_span,
    validate_weight_matrix,
)


def _result(name: str, err: float) -> BenchmarkResult:
    return BenchmarkResult(
        name=name,
        tracking_error=err,
        control_effort=1.0,
        runtime_sec=0.1,
        trajectory=np.zeros((4, 3)),
        t_grid=np.linspace(0, 1, 3),
    )


def test_mass_matrix_is_symmetric_and_finite():
    m = double_pendulum_mass_matrix(0.3, -0.5)
    assert m.shape == (2, 2)
    assert np.allclose(m, m.T)
    assert np.all(np.isfinite(m))


def test_validate_state_vector_accepts_correct_shape():
    validate_state_vector(np.zeros(STATE_DIM), "x")


def test_validate_state_vector_rejects_wrong_shape():
    with pytest.raises(ContractViolationError):
        validate_state_vector(np.zeros(3), "x")


def test_validate_state_vector_rejects_nonfinite():
    with pytest.raises(ContractViolationError):
        validate_state_vector(np.array([1.0, np.nan, 0.0, 0.0]), "x")


def test_validate_time_span_accepts_increasing():
    validate_time_span((0.0, 1.0))


def test_validate_time_span_rejects_nonincreasing():
    with pytest.raises(ContractViolationError):
        validate_time_span((1.0, 1.0))


def test_validate_weight_matrix_shape_enforced():
    validate_weight_matrix(np.eye(4), (4, 4), "Q")
    with pytest.raises(ContractViolationError):
        validate_weight_matrix(np.eye(3), (4, 4), "Q")


def test_validate_reference_trajectory_ok():
    t = np.linspace(0, 1, 5)
    x = np.zeros((STATE_DIM, 5))
    validate_reference_trajectory(t, x)


def test_validate_reference_trajectory_rejects_nonmonotonic_time():
    t = np.array([0.0, 0.5, 0.4, 1.0])
    x = np.zeros((STATE_DIM, 4))
    with pytest.raises(ContractViolationError):
        validate_reference_trajectory(t, x)


def test_format_results_includes_names_and_improvement():
    results = [_result("Setpoint", 10.0), _result("Trajectory", 4.0)]
    text = format_results(results)
    assert "Setpoint" in text
    assert "Trajectory" in text
    assert "improvement" in text.lower()
