"""Minimal benchmark utilities for setpoint vs trajectory tracking costs."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from src.core.contracts import require

FloatArray = NDArray[np.float64]


def _as_2d(array: FloatArray) -> FloatArray:
    """Normalize vectors to 2D state trajectory layout."""
    require(array.size > 0, "array must not be empty")
    return array.reshape(-1, 1) if array.ndim == 1 else array


def setpoint_cost(state_traj: FloatArray, target_state: FloatArray) -> float:
    """Compute terminal setpoint error cost."""
    traj_2d = _as_2d(state_traj)
    target_2d = _as_2d(target_state)
    require(target_2d.shape[0] == 1, "target_state must represent a single state vector")
    terminal_error = traj_2d[-1] - target_2d[0]
    return float(np.dot(terminal_error, terminal_error))


def trajectory_tracking_cost(state_traj: FloatArray, reference_traj: FloatArray) -> float:
    """Compute cumulative trajectory tracking error cost."""
    traj_2d = _as_2d(state_traj)
    ref_2d = _as_2d(reference_traj)
    require(traj_2d.shape == ref_2d.shape, "state_traj and reference_traj must have same shape")
    residual = traj_2d - ref_2d
    return float(np.sum(residual * residual))


def benchmark_cost_gap() -> dict[str, float]:
    """Return benchmark showing trajectory-objective advantage on path fidelity."""
    reference = np.array([[0.0], [1.0], [2.0], [3.0]], dtype=np.float64)
    on_path = np.array([[0.0], [1.0], [2.0], [3.0]], dtype=np.float64)
    shortcut = np.array([[0.0], [3.0], [3.0], [3.0]], dtype=np.float64)
    target = np.array([3.0], dtype=np.float64)
    setpoint_gap = setpoint_cost(shortcut, target) - setpoint_cost(on_path, target)
    tracking_gap = trajectory_tracking_cost(shortcut, reference) - trajectory_tracking_cost(
        on_path, reference
    )
    return {"setpoint_gap": setpoint_gap, "tracking_advantage": tracking_gap}
