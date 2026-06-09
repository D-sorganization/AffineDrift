from __future__ import annotations

import numpy as np
import pytest

from src.core.contracts.definitions import ContractViolationError
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
    assert solver.last_diagnostics.status == "max_iterations"
    assert solver.last_diagnostics.iterations == 1


def test_ilqr_reports_convergence_when_gain_below_tolerance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    solver = ILQRSolver()

    def dynamics(x: np.ndarray, u: np.ndarray) -> np.ndarray:
        return np.array([u[0]], dtype=np.float64)

    def backward_pass(*_args: object) -> tuple[np.ndarray, np.ndarray, float]:
        return (
            np.array([[0.0]], dtype=np.float64),
            np.zeros((1, 1, 1), dtype=np.float64),
            0.0,
        )

    monkeypatch.setattr(solver, "_backward_pass", backward_pass)
    solver.optimize(
        dynamics,
        np.array([0.0], dtype=np.float64),
        np.array([1.0], dtype=np.float64),
        np.array([[0.0]], dtype=np.float64),
        dt=1.0,
        max_iters=5,
        tol=1e-3,
    )

    assert solver.last_diagnostics.converged is True
    assert solver.last_diagnostics.status == "converged"
    assert solver.last_diagnostics.reason == "feedforward gain below tolerance"


def test_ilqr_reports_line_search_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    solver = ILQRSolver()

    def dynamics(x: np.ndarray, u: np.ndarray) -> np.ndarray:
        return np.array([u[0]], dtype=np.float64)

    def backward_pass(*_args: object) -> tuple[np.ndarray, np.ndarray, float]:
        return (
            np.array([[10.0]], dtype=np.float64),
            np.zeros((1, 1, 1), dtype=np.float64),
            10.0,
        )

    monkeypatch.setattr(solver, "_backward_pass", backward_pass)
    solver.optimize(
        dynamics,
        np.array([0.0], dtype=np.float64),
        np.array([0.0], dtype=np.float64),
        np.array([[0.0]], dtype=np.float64),
        dt=1.0,
        max_iters=3,
    )

    assert solver.last_diagnostics.converged is False
    assert solver.last_diagnostics.status == "line_search_failed"


def test_ilqr_rejects_wrong_shape_dynamics_output() -> None:
    solver = ILQRSolver()

    def bad_dynamics(_x: np.ndarray, _u: np.ndarray) -> np.ndarray:
        return np.array([0.0, 1.0], dtype=np.float64)

    with pytest.raises(Exception, match="dynamics_fn output"):
        solver.optimize(
            bad_dynamics,
            np.array([0.0], dtype=np.float64),
            np.array([1.0], dtype=np.float64),
            np.array([[0.0]], dtype=np.float64),
        )


def test_ilqr_rejects_non_finite_dynamics_output() -> None:
    solver = ILQRSolver()

    def bad_dynamics(_x: np.ndarray, _u: np.ndarray) -> np.ndarray:
        return np.array([np.nan], dtype=np.float64)

    with pytest.raises(Exception, match="finite"):
        solver.optimize(
            bad_dynamics,
            np.array([0.0], dtype=np.float64),
            np.array([1.0], dtype=np.float64),
            np.array([[0.0]], dtype=np.float64),
        )


@pytest.mark.parametrize(
    ("x0", "xf", "u_init", "message"),
    [
        (
            np.array([[0.0]], dtype=np.float64),
            np.array([[1.0]], dtype=np.float64),
            np.zeros((2, 1), dtype=np.float64),
            "x0 must be one-dimensional",
        ),
        (
            np.array([0.0], dtype=np.float64),
            np.array([[1.0]], dtype=np.float64),
            np.zeros((2, 1), dtype=np.float64),
            "xf must be one-dimensional",
        ),
        (
            np.array([], dtype=np.float64),
            np.array([], dtype=np.float64),
            np.zeros((2, 1), dtype=np.float64),
            "x0 must not be empty",
        ),
        (
            np.array([0.0], dtype=np.float64),
            np.array([1.0], dtype=np.float64),
            np.zeros((2, 1, 1), dtype=np.float64),
            "u_init must be one- or two-dimensional",
        ),
        (
            np.array([0.0], dtype=np.float64),
            np.array([1.0], dtype=np.float64),
            np.zeros((2, 0), dtype=np.float64),
            "u_init must include at least one control",
        ),
    ],
)
def test_ilqr_rejects_unsupported_input_ranks(
    x0: np.ndarray,
    xf: np.ndarray,
    u_init: np.ndarray,
    message: str,
) -> None:
    solver = ILQRSolver()

    def dynamics(_x: np.ndarray, u: np.ndarray) -> np.ndarray:
        return np.array([u[0]], dtype=np.float64)

    with pytest.raises(ContractViolationError, match=message):
        solver.optimize(dynamics, x0, xf, u_init)
