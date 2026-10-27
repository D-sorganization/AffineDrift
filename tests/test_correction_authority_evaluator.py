"""Offline LTV correction-authority evaluator tests (#5208)."""

from math import exp

import numpy as np
import pytest

from src.affine_control.correction_authority_contract import (
    evaluate_double_integrator_correction_authority,
    evaluate_planar_rank_deficient_authority,
    evaluate_scalar_correction_authority,
    preregistered_humanoid_correction_authority_protocol,
)
from src.affine_control.correction_authority_evaluator import (
    Indeterminate,
    LTVLinearizationStep,
    backward_gramian_operation_count,
    evaluate_correction_authority_along_trajectory,
    horizon_authority_sweep,
    instantaneous_step_dcr,
)
from src.affine_control.reachability import LinearScalarSystem, PlanarRankDeficientSystem
from src.affine_control.reachability_protocol import ReachabilityIllConditionedError

_KAPPA = preregistered_humanoid_correction_authority_protocol().authority.kappa_max


def _scalar_step(system: LinearScalarSystem, horizon: float) -> LTVLinearizationStep:
    if system.drift_gradient == 0.0:
        transition, input_factor = 1.0, horizon
    else:
        transition = exp(system.drift_gradient * horizon)
        input_factor = (transition - 1.0) / system.drift_gradient
    return LTVLinearizationStep(
        state_matrix=np.array([[transition]]),
        input_matrix=np.array([[input_factor]]),
        drift=np.array([input_factor * system.drift_offset]),
    )


def _double_integrator_steps(horizon: float, steps: int) -> tuple[LTVLinearizationStep, ...]:
    dt = horizon / steps
    a = np.array([[1.0, dt], [0.0, 1.0]])
    b = np.array([[0.0], [dt]])
    return tuple(LTVLinearizationStep(a, b, np.zeros(2)) for _ in range(steps))


def _evaluate(
    steps: tuple[LTVLinearizationStep, ...],
    initial_state: np.ndarray,
    input_bound: float,
    required_task_error: float,
    tolerance: float,
    task_direction: np.ndarray | None = None,
    **kwargs: object,
) -> tuple[object, ...]:
    direction = (
        task_direction if task_direction is not None else np.array([1.0, 0.0])[: len(initial_state)]
    )
    return evaluate_correction_authority_along_trajectory(
        steps=steps,
        initial_state=initial_state,
        input_bound=input_bound,
        required_task_error=required_task_error,
        task_direction=direction,
        tolerance=tolerance,
        kappa_max=_KAPPA,
        **kwargs,
    )


@pytest.mark.parametrize(
    "steps,input_bound,required,tol,oracle,tol_margin",
    [
        (
            _double_integrator_steps(1.0, 32),
            1.0,
            0.3,
            0.05,
            evaluate_double_integrator_correction_authority(0.3, 0, 0, 1, 1, 0.05),
            0.08,
        ),
        (
            (_scalar_step(LinearScalarSystem(0, 0, 0, 2), 0.5),),
            2.0,
            0.0,
            0.25,
            evaluate_scalar_correction_authority(0, LinearScalarSystem(0, 0, 0, 2), 0.5, 0.25),
            1e-9,
        ),
        (
            (_scalar_step(LinearScalarSystem(0, 0, 50, 1), 1.0),),
            1.0,
            0.0,
            0.1,
            evaluate_scalar_correction_authority(0, LinearScalarSystem(0, 0, 50, 1), 1, 0.1),
            1e-9,
        ),
    ],
)
def test_evaluator_matches_dispatch1_oracles(
    steps, input_bound, required, tol, oracle, tol_margin
) -> None:
    initial = np.zeros(steps[0].state_matrix.shape[0])
    result = _evaluate(steps, initial, input_bound, required, tol)[0]
    assert not isinstance(result, Indeterminate)
    assert result.recoverable is oracle.recoverable
    if oracle.margin is not None:
        assert result.margin == pytest.approx(oracle.margin, abs=tol_margin)


def test_rank_deficient_and_dcr_helpers() -> None:
    oracle = evaluate_planar_rank_deficient_authority(
        (0, -1), PlanarRankDeficientSystem((0, 0), (0, 2), 1, 1), 0.1
    )
    steps = (LTVLinearizationStep(np.eye(2), np.array([[1.0], [0.0]]), np.array([0.0, 2.0])),)
    result = _evaluate(steps, np.zeros(2), 1.0, 1.0, 0.1, np.array([0.0, 1.0]))[0]
    assert not isinstance(result, Indeterminate) and result.recoverable is oracle.recoverable
    assert instantaneous_step_dcr(
        _scalar_step(LinearScalarSystem(0, 0, 50, 1), 1.0), 1.0
    ) == pytest.approx(50.0)


def test_singular_and_kappa_gates() -> None:
    singular = (LTVLinearizationStep(np.array([[0, 1], [0, 0]]), np.zeros((2, 1)), np.zeros(2)),)
    assert isinstance(_evaluate(singular, np.zeros(2), 1.0, 0.1, 0.01)[-1], Indeterminate)
    steps = _double_integrator_steps(1.0, 16)
    params = dict(
        steps=steps,
        initial_state=np.zeros(2),
        input_bound=1.0,
        required_task_error=0.1,
        task_direction=np.array([1.0, 0.0]),
        tolerance=0.01,
        kappa_max=1.0,
    )
    with pytest.raises(ReachabilityIllConditionedError, match="kappa_max"):
        evaluate_correction_authority_along_trajectory(**params, ill_conditioned_mode="raise")
    out = evaluate_correction_authority_along_trajectory(
        **params, ill_conditioned_mode="indeterminate"
    )
    assert isinstance(out[0], Indeterminate)


def test_monte_carlo_containment_and_scaling() -> None:
    steps = _double_integrator_steps(1.0, 16)
    terminal = _evaluate(steps, np.zeros(2), 1.0, 0.0, 0.0, return_gramians=True)[0]
    assert not isinstance(terminal, Indeterminate) and terminal.gramian is not None
    rng, worst = np.random.default_rng(5208), 0.0
    for _ in range(200):
        state = np.zeros(2)
        for step, control in zip(steps, rng.uniform(-1, 1, len(steps)), strict=True):
            state = step.state_matrix @ state + step.input_matrix[:, 0] * control + step.drift
        worst = max(worst, float(state @ np.linalg.solve(terminal.gramian, state)) - len(steps))
    assert worst <= 0.05
    assert backward_gramian_operation_count(20, 3) == pytest.approx(
        2 * backward_gramian_operation_count(10, 3)
    )


def test_horizon_sensitivity_reports_monotonicity() -> None:
    sweep = horizon_authority_sweep(
        step_builder=lambda horizon: _double_integrator_steps(horizon, 16),
        horizons=(0.2, 0.35, 0.5),
        initial_state=np.zeros(2),
        input_bound=1.0,
        required_task_error=0.02,
        task_direction=np.array([1.0, 0.0]),
        tolerance=0.01,
        kappa_max=_KAPPA,
    )
    assert sweep.monotone_nondecreasing_margin and sweep.violations == ()
