from __future__ import annotations

import numpy as np
import pytest

from src.core.optimizers.ilqr_solver import ILQRSolver


def test_ilqr_line_search_reduces_alpha_until_cost_decreases(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    solver = ILQRSolver()

    def dynamics(x: np.ndarray, u: np.ndarray) -> np.ndarray:
        return np.array([u[0]], dtype=np.float64)

    def backward_pass(*_args: object) -> tuple[np.ndarray, np.ndarray, float]:
        k_traj = np.array([[4.0]], dtype=np.float64)
        k_feedback = np.zeros((1, 1, 1), dtype=np.float64)
        return k_traj, k_feedback, 4.0

    monkeypatch.setattr(solver, "_backward_pass", backward_pass)

    x_traj, u_traj, _ = solver.optimize(
        dynamics,
        np.array([0.0], dtype=np.float64),
        np.array([1.0], dtype=np.float64),
        np.array([[0.0]], dtype=np.float64),
        dt=1.0,
        max_iters=1,
    )

    assert u_traj[0, 0] == pytest.approx(1.0)
    assert x_traj[-1, 0] == pytest.approx(1.0)
