"""Declared validation and hypothesis ledgers for the reachability authority."""

from dataclasses import dataclass
from math import isfinite
from typing import Literal, cast

import numpy as np
from numpy.typing import NDArray

NormName = Literal["l2", "linf", "weighted_l2"]
HypothesisKind = Literal["association", "prediction", "theorem"]
HypothesisOutcome = Literal["supported", "null", "negative", "unavailable"]
EvidenceStatus = Literal["measured", "estimated", "modeled", "assumed", "unavailable"]

_VALID_NORMS: tuple[NormName, ...] = ("l2", "linf", "weighted_l2")
_VALID_HYPOTHESIS_KINDS: tuple[HypothesisKind, ...] = (
    "association",
    "prediction",
    "theorem",
)
_VALID_OUTCOMES: tuple[HypothesisOutcome, ...] = (
    "supported",
    "null",
    "negative",
    "unavailable",
)
_VALID_EVIDENCE_STATUS: tuple[EvidenceStatus, ...] = (
    "measured",
    "estimated",
    "modeled",
    "assumed",
    "unavailable",
)
_FORBIDDEN_AUTHORITY_PHRASES = (
    "elite strategy",
    "coaching prescription",
    "all golfers",
    "clinical authority",
    "causes lower",
)


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must be declared")


def _require_finite(values: tuple[float, ...], label: str) -> None:
    if not all(isfinite(value) for value in values):
        raise ValueError(f"{label} must be finite")


@dataclass(frozen=True)
class CoordinateDeclaration:
    """Names, units, scaling, and norm for a declared state coordinate vector."""

    names: tuple[str, ...]
    units: tuple[str, ...]
    scaling: tuple[float, ...]
    norm: NormName

    def __post_init__(self) -> None:
        """Validate the coordinate declaration at its public boundary."""
        if not self.names or len({len(self.names), len(self.units), len(self.scaling)}) != 1:
            raise ValueError("coordinate names, units, and scaling must be nonempty and aligned")
        missing_name = any(not name.strip() for name in self.names)
        missing_unit = any(not unit.strip() for unit in self.units)
        if missing_name or missing_unit:
            raise ValueError("coordinate names and units must be declared")
        _require_finite(self.scaling, "coordinate scaling")
        if any(scale <= 0.0 for scale in self.scaling):
            raise ValueError("coordinate scaling must be positive")
        if self.norm not in _VALID_NORMS:
            raise ValueError("coordinate norm must be one of the declared norms")


@dataclass(frozen=True)
class StateDeclaration:
    """A frozen initial state bound to its coordinate declaration."""

    values: tuple[float, ...]
    coordinates: CoordinateDeclaration

    def __post_init__(self) -> None:
        """Require one finite state value per coordinate."""
        if len(self.values) != len(self.coordinates.names):
            raise ValueError("state values must align with declared coordinates")
        _require_finite(self.values, "state values")


@dataclass(frozen=True)
class InputDeclaration:
    """Named bounded inputs with explicit units."""

    names: tuple[str, ...]
    bounds: tuple[tuple[float, float], ...]
    units: tuple[str, ...]

    def __post_init__(self) -> None:
        """Require finite ordered bounds for every declared input."""
        if not self.names or len({len(self.names), len(self.bounds), len(self.units)}) != 1:
            raise ValueError("input names, bounds, and units must be nonempty and aligned")
        if any(not value.strip() for value in (*self.names, *self.units)):
            raise ValueError("input names and units must be declared")
        for lower, upper in self.bounds:
            _require_finite((lower, upper), "input bounds")
            if lower > upper:
                raise ValueError("input lower bounds cannot exceed upper bounds")


@dataclass(frozen=True)
class ModelDeclaration:
    """Revision-bound model, state, and admissible input set."""

    model_id: str
    revision: str
    state: StateDeclaration
    inputs: InputDeclaration

    def __post_init__(self) -> None:
        """Require stable model identity and revision text."""
        _require_text(self.model_id, "model_id")
        _require_text(self.revision, "model revision")


@dataclass(frozen=True)
class EventDeclaration:
    """Guard, crossing direction, reset rule, and timing convention."""

    guard: str
    direction: str
    reset: str
    timing: str

    def __post_init__(self) -> None:
        """Require every event semantic before a result can be interpreted."""
        for value, label in (
            (self.guard, "event guard"),
            (self.direction, "event direction"),
            (self.reset, "event reset"),
            (self.timing, "event timing"),
        ):
            _require_text(value, label)


@dataclass(frozen=True)
class TaskMetricDeclaration:
    """Task metric identity, unit, tolerance, and evaluation convention."""

    name: str
    unit: str
    tolerance: float
    evaluation: str

    def __post_init__(self) -> None:
        """Require a named metric and a finite nonnegative tolerance."""
        _require_text(self.name, "task metric name")
        _require_text(self.unit, "task metric unit")
        _require_text(self.evaluation, "task metric evaluation")
        if not isfinite(self.tolerance) or self.tolerance < 0.0:
            raise ValueError("task metric tolerance must be finite and nonnegative")


@dataclass(frozen=True)
class UncertaintyDeclaration:
    """Uncertainty model, varied parameters, and evidence status."""

    model: str
    parameters: str
    evidence_status: EvidenceStatus

    def __post_init__(self) -> None:
        """Require explicit uncertainty scope and evidence provenance class."""
        _require_text(self.model, "uncertainty model")
        _require_text(self.parameters, "uncertainty parameters")
        if self.evidence_status not in _VALID_EVIDENCE_STATUS:
            raise ValueError("uncertainty evidence status is not declared")


@dataclass(frozen=True)
class AnalysisDeclaration:
    """Finite horizon, event, task metric, and uncertainty records."""

    horizon: float
    event: EventDeclaration
    task_metric: TaskMetricDeclaration
    uncertainty: UncertaintyDeclaration

    def __post_init__(self) -> None:
        """Reject a nonpositive finite horizon."""
        if not isfinite(self.horizon) or self.horizon <= 0.0:
            raise ValueError("analysis horizon must be finite and positive")


@dataclass(frozen=True)
class SolverDeclaration:
    """Solver identity, revision, and numerical tolerance."""

    name: str
    revision: str
    tolerance: float

    def __post_init__(self) -> None:
        """Require a named revision and positive finite tolerance."""
        _require_text(self.name, "solver name")
        _require_text(self.revision, "solver revision")
        if not isfinite(self.tolerance) or self.tolerance <= 0.0:
            raise ValueError("solver tolerance must be finite and positive")


@dataclass(frozen=True)
class ReachabilityProtocol:
    """Complete interpretation contract for one bounded validation run."""

    protocol_id: str
    model: ModelDeclaration
    analysis: AnalysisDeclaration
    solver: SolverDeclaration

    def __post_init__(self) -> None:
        """Require a stable protocol identifier."""
        _require_text(self.protocol_id, "protocol_id")


@dataclass(frozen=True)
class Hypothesis:
    """Predeclared association, prediction, or theorem-level hypothesis."""

    hypothesis_id: str
    kind: HypothesisKind
    statement: str
    success_criterion: str

    def __post_init__(self) -> None:
        """Require identity, an allowed tier, and an explicit success criterion."""
        _require_text(self.hypothesis_id, "hypothesis_id")
        _require_text(self.statement, "hypothesis statement")
        _require_text(self.success_criterion, "hypothesis success criterion")
        if self.kind not in _VALID_HYPOTHESIS_KINDS:
            raise ValueError("hypothesis kind must be association, prediction, or theorem")


@dataclass(frozen=True)
class HypothesisResult:
    """One preserved hypothesis outcome with estimate and uncertainty."""

    hypothesis_id: str
    outcome: HypothesisOutcome
    estimate: float | None
    uncertainty_interval: tuple[float, float] | None
    interpretation: str

    def __post_init__(self) -> None:
        """Validate fields and block coaching, causal, and population promotion."""
        _require_text(self.hypothesis_id, "hypothesis_id")
        _require_text(self.interpretation, "result interpretation")
        if self.outcome not in _VALID_OUTCOMES:
            raise ValueError("hypothesis outcome is not declared")
        if self.estimate is not None and not isfinite(self.estimate):
            raise ValueError("hypothesis estimate must be finite when available")
        if self.uncertainty_interval is not None:
            _require_finite(self.uncertainty_interval, "hypothesis uncertainty")
            if self.uncertainty_interval[0] > self.uncertainty_interval[1]:
                raise ValueError("hypothesis uncertainty interval is reversed")
        lowered = self.interpretation.casefold()
        if any(phrase in lowered for phrase in _FORBIDDEN_AUTHORITY_PHRASES):
            raise ValueError("result interpretation exceeds the authority boundary")


def preserve_hypothesis_results(
    hypotheses: tuple[Hypothesis, ...], results: tuple[HypothesisResult, ...]
) -> tuple[HypothesisResult, ...]:
    """Return all results in predeclared order, including null and negative outcomes."""
    kinds = {hypothesis.kind for hypothesis in hypotheses}
    if kinds != set(_VALID_HYPOTHESIS_KINDS):
        raise ValueError("one or more required hypothesis tiers are missing")
    hypothesis_ids = tuple(hypothesis.hypothesis_id for hypothesis in hypotheses)
    if len(set(hypothesis_ids)) != len(hypothesis_ids):
        raise ValueError("hypothesis identifiers must be unique")
    result_by_id = {result.hypothesis_id: result for result in results}
    if len(result_by_id) != len(results) or set(result_by_id) != set(hypothesis_ids):
        raise ValueError("every predeclared hypothesis must have exactly one preserved result")
    return tuple(result_by_id[hypothesis_id] for hypothesis_id in hypothesis_ids)


@dataclass(frozen=True)
class CrossValidationSample:
    """Sample with baseline predictors, DCR, and a declared task error."""

    state: float
    speed: float
    control_authority: float
    dcr: float
    task_error: float

    def __post_init__(self) -> None:
        """Require finite sample values and nonnegative authority and DCR."""
        _require_finite(
            (self.state, self.speed, self.control_authority, self.dcr, self.task_error),
            "cross-validation sample",
        )
        if self.control_authority < 0.0 or self.dcr < 0.0:
            raise ValueError("control authority and DCR must be nonnegative")


@dataclass(frozen=True)
class CrossValidationResult:
    """Held-out baseline and augmented errors with a preserved outcome."""

    baseline_rmse: float
    augmented_rmse: float
    augmented_error_interval: tuple[float, float]
    outcome: HypothesisOutcome


def _design_matrix(
    samples: tuple[CrossValidationSample, ...], include_dcr: bool
) -> NDArray[np.float64]:
    rows = tuple(
        (
            (1.0, sample.state, sample.speed, sample.control_authority, sample.dcr)
            if include_dcr
            else (1.0, sample.state, sample.speed, sample.control_authority)
        )
        for sample in samples
    )
    return np.asarray(rows, dtype=np.float64)


def _leave_one_out_errors(
    samples: tuple[CrossValidationSample, ...], include_dcr: bool
) -> NDArray[np.float64]:
    design = _design_matrix(samples, include_dcr)
    target = np.asarray(tuple(sample.task_error for sample in samples), dtype=np.float64)
    errors = np.empty(len(samples), dtype=np.float64)
    for index in range(len(samples)):
        keep = np.arange(len(samples)) != index
        coefficients = cast(
            NDArray[np.float64], np.linalg.lstsq(design[keep], target[keep], rcond=None)[0]
        )
        errors[index] = target[index] - float(np.dot(design[index], coefficients))
    return errors


def assess_incremental_prediction(
    samples: tuple[CrossValidationSample, ...], minimum_rmse_improvement: float
) -> CrossValidationResult:
    """Compare baseline and DCR-augmented leave-one-out prediction errors."""
    if len(samples) < 7:
        raise ValueError("at least seven samples are required for the declared regressions")
    if not isfinite(minimum_rmse_improvement) or minimum_rmse_improvement <= 0.0:
        raise ValueError("minimum RMSE improvement must be finite and positive")
    baseline_errors = _leave_one_out_errors(samples, include_dcr=False)
    augmented_errors = _leave_one_out_errors(samples, include_dcr=True)
    baseline_rmse = float(np.sqrt(np.mean(np.square(baseline_errors))))
    augmented_rmse = float(np.sqrt(np.mean(np.square(augmented_errors))))
    improvement = baseline_rmse - augmented_rmse
    if improvement >= minimum_rmse_improvement:
        outcome: HypothesisOutcome = "supported"
    elif improvement <= -minimum_rmse_improvement:
        outcome = "negative"
    else:
        outcome = "null"
    absolute_errors = np.abs(augmented_errors)
    return CrossValidationResult(
        baseline_rmse=baseline_rmse,
        augmented_rmse=augmented_rmse,
        augmented_error_interval=(float(np.min(absolute_errors)), float(np.max(absolute_errors))),
        outcome=outcome,
    )
