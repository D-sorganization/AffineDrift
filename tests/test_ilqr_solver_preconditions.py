"""Design-by-Contract precondition tests for ``ILQRSolver.optimize`` (issue #3181).

The A-O audit flagged that the public optimizer boundary had happy-path tests but
no adversarial coverage of its Design-by-Contract preconditions. ``optimize``
delegates to ``_validate_inputs`` (``require`` / ``check_finite_array`` /
``check_positive``) before iterating, raising ``ContractViolationError`` on any
violation. These negative tests pin each precondition so a regression that drops
or weakens a guard fails loudly.
"""

from __future__ import annotations

import numpy as np
import pytest
from numpy.typing import NDArray

from src.core.contracts import ContractViolationError
from src.core.optimizers.ilqr_solver import ILQRSolver


def _identity_dynamics(x: NDArray, u: NDArray) -> NDArray:
    """Minimal well-formed dynamics: state derivative equals the control."""
    return np.asarray(u, dtype=np.float64)


def _valid_kwargs() -> dict[str, object]:
    """A fully valid argument set; individual fields are overridden per test."""
    return {
        "dynamics_fn": _identity_dynamics,
        "x0": np.array([0.0], dtype=np.float64),
        "xf": np.array([1.0], dtype=np.float64),
        "u_init": np.array([[0.0]], dtype=np.float64),
        "dt": 1.0,
        "max_iters": 1,
        "tol": 1e-3,
    }


def _optimize_with(**overrides: object) -> tuple[NDArray, NDArray, NDArray]:
    kwargs = _valid_kwargs()
    kwargs.update(overrides)
    solver = ILQRSolver()
    return solver.optimize(**kwargs)  # type: ignore[arg-type]


def test_valid_inputs_do_not_raise() -> None:
    """The baseline valid argument set is accepted (guards are not over-strict)."""
    x_traj, u_traj, gains = _optimize_with()
    assert x_traj.shape[0] >= 1
    assert u_traj.shape[0] >= 1
    assert gains is not None


def test_non_callable_dynamics_is_rejected() -> None:
    with pytest.raises(ContractViolationError):
        _optimize_with(dynamics_fn="not a function")


def test_non_finite_x0_is_rejected() -> None:
    with pytest.raises(ContractViolationError):
        _optimize_with(x0=np.array([np.nan], dtype=np.float64))


def test_non_finite_xf_is_rejected() -> None:
    with pytest.raises(ContractViolationError):
        _optimize_with(xf=np.array([np.inf], dtype=np.float64))


def test_mismatched_x0_xf_shapes_are_rejected() -> None:
    with pytest.raises(ContractViolationError):
        _optimize_with(
            x0=np.array([0.0], dtype=np.float64),
            xf=np.array([1.0, 2.0], dtype=np.float64),
        )


def test_empty_u_init_is_rejected() -> None:
    with pytest.raises(ContractViolationError):
        _optimize_with(u_init=np.empty((0, 1), dtype=np.float64))


def test_non_finite_u_init_is_rejected() -> None:
    with pytest.raises(ContractViolationError):
        _optimize_with(u_init=np.array([[np.nan]], dtype=np.float64))


@pytest.mark.parametrize("bad_dt", [0.0, -1.0])
def test_non_positive_dt_is_rejected(bad_dt: float) -> None:
    with pytest.raises(ContractViolationError):
        _optimize_with(dt=bad_dt)


@pytest.mark.parametrize("bad_iters", [0, -5])
def test_max_iters_below_one_is_rejected(bad_iters: int) -> None:
    with pytest.raises(ContractViolationError):
        _optimize_with(max_iters=bad_iters)


@pytest.mark.parametrize("bad_tol", [0.0, -1e-6])
def test_non_positive_tol_is_rejected(bad_tol: float) -> None:
    with pytest.raises(ContractViolationError):
        _optimize_with(tol=bad_tol)
