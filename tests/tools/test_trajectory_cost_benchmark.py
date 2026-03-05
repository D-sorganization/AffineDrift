"""Tests for trajectory_cost_benchmark.py"""

from __future__ import annotations

import numpy as np
import pytest

from src.core.contracts import ContractViolationError
from src.tools.trajectory_cost_benchmark import (
    _as_2d,
    benchmark_cost_gap,
    setpoint_cost,
    trajectory_tracking_cost,
)


def test_as_2d():
    arr1d = np.array([1.0, 2.0])
    arr2d = _as_2d(arr1d)
    assert arr2d.ndim == 2
    assert arr2d.shape == (2, 1)

    arr2d_orig = np.array([[1.0], [2.0]])
    arr2d_new = _as_2d(arr2d_orig)
    assert arr2d_new.shape == (2, 1)

    # Empty array should trigger precondition
    with pytest.raises(ContractViolationError):
        _as_2d(np.array([], dtype=np.float64))


def test_setpoint_cost():
    state_traj = np.array([[0.0], [1.0], [2.5]], dtype=np.float64)
    target_state = np.array([3.0], dtype=np.float64)

    # Terminal error = 2.5 - 3.0 = -0.5
    # Cost = (-0.5)^2 = 0.25
    cost = setpoint_cost(state_traj, target_state)
    assert np.isclose(cost, 0.25)

    # Target state not single vector
    bad_target = np.array([[3.0], [4.0]], dtype=np.float64)
    with pytest.raises(ContractViolationError):
        setpoint_cost(state_traj, bad_target)


def test_trajectory_tracking_cost():
    state_traj = np.array([0.0, 1.0, 2.0])
    ref_traj = np.array([0.0, 2.0, 2.0])

    # Residual = [0, -1, 0] -> Cost = 1
    cost = trajectory_tracking_cost(state_traj, ref_traj)
    assert np.isclose(cost, 1.0)

    # Mismatched shapes
    bad_ref = np.array([0.0, 2.0])
    with pytest.raises(ContractViolationError):
        trajectory_tracking_cost(state_traj, bad_ref)


def test_benchmark_cost_gap():
    results = benchmark_cost_gap()
    assert "setpoint_gap" in results
    assert "tracking_advantage" in results
    assert np.isclose(results["setpoint_gap"], 0.0)  # Both arrive at 3.0
    assert (
        results["tracking_advantage"] > 0.0
    )  # Shortcut deviates a lot, so tracking cost is higher for shortcut
