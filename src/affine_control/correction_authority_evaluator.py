"""Offline LTV correction-authority evaluator with backward Gramian recursion."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Literal

import numpy as np
from numpy.typing import NDArray

from src.affine_control.reachability import (
    _GRAMIAN_OPS_PER_STEP,
    LinearScalarSystem,
    instantaneous_scalar_dcr,
)
from src.affine_control.reachability_protocol import ReachabilityIllConditionedError

type Array = NDArray[np.float64]
IllConditionedMode = Literal["raise", "indeterminate"]


@dataclass(frozen=True)
class LTVLinearizationStep:
    """Single discrete-time LTV linearization step (A_k, B_k, d_k)."""

    state_matrix: Array
    input_matrix: Array
    drift: Array

    def __post_init__(self) -> None:
        """Validate matrix dimensions and finiteness."""
        a = np.asarray(self.state_matrix, dtype=np.float64)
        b = np.asarray(self.input_matrix, dtype=np.float64)
        d = np.asarray(self.drift, dtype=np.float64).reshape(-1)
        if a.ndim != 2 or b.ndim != 2 or d.ndim != 1 or a.shape[0] != a.shape[1]:
            raise ValueError("invalid LTV step shape")
        if a.shape[0] != b.shape[0] or a.shape[0] != d.shape[0]:
            raise ValueError("LTV step dimensions must align")
        if not np.all(np.isfinite(np.r_[a.ravel(), b.ravel(), d])):
            raise ValueError("LTV step values must be finite")


@dataclass(frozen=True)
class Indeterminate:
    """Returned when controllability Gramian is singular or ill-conditioned."""

    reason: str


@dataclass(frozen=True)
class CorrectionAuthorityStepResult:
    """Per-step correction-authority evaluation output."""

    recoverable: bool
    margin: float
    dcr: float
    cond_w_c: float
    gramian: Array | None = None


@dataclass(frozen=True)
class HorizonAuthoritySweep:
    """Summary of correction authority across a sequence of horizons."""

    horizons: tuple[float, ...]
    margins: tuple[float, ...]
    monotone_nondecreasing_margin: bool
    violations: tuple[str, ...]


def backward_gramian_operation_count(steps: int, state_dim: int) -> int:
    """Return O(N * n^3) matrix-multiply operation count for backward recursion."""
    if steps < 0 or state_dim < 0:
        raise ValueError("steps and state_dim must be nonnegative")
    return steps * state_dim**3 * _GRAMIAN_OPS_PER_STEP


def instantaneous_step_dcr(step: LTVLinearizationStep, input_bound: float) -> float:
    """Compute instantaneous drift-to-control ratio for one LTV step."""
    if not isfinite(input_bound) or input_bound <= 0.0:
        raise ValueError("input_bound must be finite and positive")
    if step.state_matrix.shape[0] == 1:
        scale = float(np.max(np.abs(step.input_matrix)))
        sys_1d = LinearScalarSystem(0.0, 0.0, float(step.drift[0]), input_bound * scale)
        return instantaneous_scalar_dcr(sys_1d)
    drift_norm = float(np.linalg.norm(step.drift))
    singular_values = np.linalg.svd(step.input_matrix, compute_uv=False)
    capacity = input_bound * float(singular_values[0]) if singular_values.size else 0.0
    if capacity == 0.0:
        return float("inf") if drift_norm > 0.0 else 0.0
    return drift_norm / capacity


def _margin_to_target(
    interval: tuple[float, float], target: float, tolerance: float, required_task_error: float
) -> tuple[bool, float]:
    """Return recoverability flag and signed margin to the target interval."""
    lower, upper = interval
    if target < lower - tolerance or target > upper + tolerance:
        return False, min(target - upper, lower - target)
    clearance = min(upper - target, target - lower)
    margin = clearance - tolerance if required_task_error == 0.0 else clearance
    return margin >= 0.0, margin


def _backward_controllability_gramians(
    steps: tuple[LTVLinearizationStep, ...],
) -> tuple[Array, ...]:
    """Compute finite-horizon controllability Gramians via backward recursion."""
    if not steps:
        raise ValueError("at least one LTV step is required")
    state_dim = steps[0].state_matrix.shape[0]
    gramian_next = np.zeros((state_dim, state_dim), dtype=np.float64)
    gramians_reversed: list[Array] = []
    for step in reversed(steps):
        a, b = step.state_matrix, step.input_matrix
        gramian = a @ gramian_next @ a.T + b @ b.T
        gramian_next = 0.5 * (gramian + gramian.T)
        gramians_reversed.append(gramian_next)
    return tuple(reversed(gramians_reversed))


def _condition_number_or_singular(gramian: Array) -> float:
    """Return condition number of Gramian or raise if singular."""
    if not np.any(gramian):
        raise ReachabilityIllConditionedError("singular controllability Gramian")
    condition = float(np.linalg.cond(gramian))
    if not isfinite(condition):
        raise ReachabilityIllConditionedError("singular controllability Gramian")
    return condition


def _propagate_nominal(steps: tuple[LTVLinearizationStep, ...], initial_state: Array) -> Array:
    """Propagate zero-input affine drift state across steps."""
    state = np.asarray(initial_state, dtype=np.float64).reshape(-1)
    for step in steps:
        state = step.state_matrix @ state + step.drift
    return state


def _task_output_interval(
    gramian: Array,
    task_direction: Array,
    center_state: Array,
    input_bound: float,
    horizon_steps: int,
) -> tuple[float, float]:
    """Project reachable ellipsoid onto task direction to form interval."""
    direction = np.asarray(task_direction, dtype=np.float64).reshape(-1)
    center = float(direction @ center_state)
    radius = input_bound * float(np.sqrt(float(direction @ gramian @ direction) * horizon_steps))
    return (center - radius, center + radius)


def _handle_ill_conditioned(
    error: ReachabilityIllConditionedError, mode: IllConditionedMode
) -> Indeterminate:
    """Raise or wrap ReachabilityIllConditionedError per mode."""
    if mode == "raise":
        raise error
    return Indeterminate(str(error))


def _evaluate_single_step(
    step: LTVLinearizationStep,
    remaining: tuple[LTVLinearizationStep, ...],
    gramian: Array,
    direction: Array,
    initial: Array,
    prefix: tuple[LTVLinearizationStep, ...],
    input_bound: float,
    target: float,
    tolerance: float,
    required_task_error: float,
    kappa_max: float,
    ill_conditioned_mode: IllConditionedMode,
    return_gramians: bool,
) -> CorrectionAuthorityStepResult | Indeterminate:
    """Evaluate correction authority at a single step along the trajectory."""
    form = float(direction @ gramian @ direction)
    state_at_step = _propagate_nominal(prefix, initial) if prefix else initial
    center_state = _propagate_nominal(remaining, state_at_step)
    center = float(direction @ center_state)
    if not np.any(gramian):
        err = ReachabilityIllConditionedError("singular controllability Gramian")
        return _handle_ill_conditioned(err, ill_conditioned_mode)
    if form <= 1e-15:
        interval, condition = (center, center), float("inf")
    else:
        try:
            condition = _condition_number_or_singular(gramian)
            if condition > kappa_max:
                raise ReachabilityIllConditionedError("controllability Gramian exceeds kappa_max")
        except ReachabilityIllConditionedError as error:
            return _handle_ill_conditioned(error, ill_conditioned_mode)
        interval = _task_output_interval(
            gramian, direction, center_state, input_bound, len(remaining)
        )
    recoverable, margin = _margin_to_target(interval, target, tolerance, required_task_error)
    return CorrectionAuthorityStepResult(
        recoverable=recoverable,
        margin=margin,
        dcr=instantaneous_step_dcr(step, input_bound),
        cond_w_c=condition,
        gramian=gramian if return_gramians else None,
    )


def evaluate_correction_authority_along_trajectory(
    steps: tuple[LTVLinearizationStep, ...],
    initial_state: Array,
    input_bound: float,
    required_task_error: float,
    task_direction: Array,
    tolerance: float,
    kappa_max: float,
    ill_conditioned_mode: IllConditionedMode = "indeterminate",
    return_gramians: bool = False,
) -> tuple[CorrectionAuthorityStepResult | Indeterminate, ...]:
    """Evaluate correction authority, DCR, and Gramian conditioning along a trajectory."""
    if not isfinite(kappa_max) or kappa_max <= 0.0:
        raise ValueError("kappa_max must be finite and positive")
    if not isfinite(input_bound) or input_bound < 0.0:
        raise ValueError("input_bound must be finite and nonnegative")
    if not steps:
        raise ValueError("at least one LTV step is required")
    direction = np.asarray(task_direction, dtype=np.float64).reshape(-1)
    if direction.shape[0] != steps[0].state_matrix.shape[0]:
        raise ValueError("task_direction must match the state dimension")
    initial = np.asarray(initial_state, dtype=np.float64).reshape(-1)
    if initial.shape[0] != direction.shape[0]:
        raise ValueError("initial_state must match the state dimension")

    target = float(direction @ initial) - required_task_error
    gramians = _backward_controllability_gramians(steps)
    return tuple(
        _evaluate_single_step(
            step=step,
            remaining=steps[idx:],
            gramian=gramians[idx],
            direction=direction,
            initial=initial,
            prefix=steps[:idx],
            input_bound=input_bound,
            target=target,
            tolerance=tolerance,
            required_task_error=required_task_error,
            kappa_max=kappa_max,
            ill_conditioned_mode=ill_conditioned_mode,
            return_gramians=return_gramians,
        )
        for idx, step in enumerate(steps)
    )


def horizon_authority_sweep(
    step_builder: object,
    horizons: tuple[float, ...],
    initial_state: Array,
    input_bound: float,
    required_task_error: float,
    task_direction: Array,
    tolerance: float,
    kappa_max: float,
) -> HorizonAuthoritySweep:
    """Sweep horizons and report whether terminal authority margin is monotone."""
    if not callable(step_builder):
        raise ValueError("step_builder must be callable")
    margins: list[float] = []
    violations: list[str] = []
    for horizon in horizons:
        terminal = evaluate_correction_authority_along_trajectory(
            steps=step_builder(horizon),
            initial_state=initial_state,
            input_bound=input_bound,
            required_task_error=required_task_error,
            task_direction=task_direction,
            tolerance=tolerance,
            kappa_max=kappa_max,
        )[0]
        if isinstance(terminal, Indeterminate):
            violations.append(f"horizon {horizon}: {terminal.reason}")
            margins.append(float("-inf"))
        else:
            margins.append(terminal.margin)
    monotone = True
    for idx in range(len(margins) - 1):
        left, right = margins[idx], margins[idx + 1]
        if right + 1e-12 < left:
            monotone = False
            violations.append(
                f"margin decreased from {left} to {right} between horizons "
                f"{horizons[idx]} and {horizons[idx + 1]}"
            )
    return HorizonAuthoritySweep(
        horizons=horizons,
        margins=tuple(margins),
        monotone_nondecreasing_margin=monotone and all(m != float("-inf") for m in margins),
        violations=tuple(violations),
    )
