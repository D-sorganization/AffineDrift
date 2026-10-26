"""Preregistered correction-authority contract and closed-form edge-case oracles."""

from dataclasses import dataclass
from math import isfinite

from src.affine_control.reachability import (
    LinearScalarSystem,
    PlanarRankDeficientSystem,
    rank_deficient_reachable_box,
    scalar_linear_reachable_interval,
)
from src.affine_control.reachability_protocol import (
    AnalysisDeclaration,
    CoordinateDeclaration,
    EventDeclaration,
    Hypothesis,
    InputDeclaration,
    ModelDeclaration,
    ReachabilityProtocol,
    SolverDeclaration,
    StateDeclaration,
    TaskMetricDeclaration,
    UncertaintyDeclaration,
    reject_forbidden_protocol_phrases,
)


@dataclass(frozen=True)
class HorizonSweepDeclaration:
    nominal: float
    sweep_min: float
    sweep_max: float

    def __post_init__(self) -> None:
        values = (self.nominal, self.sweep_min, self.sweep_max)
        if not all(isfinite(value) for value in values):
            raise ValueError("horizon sweep values must be finite")
        if self.nominal <= 0.0 or self.sweep_min <= 0.0 or self.sweep_max <= self.sweep_min:
            raise ValueError("horizon sweep range must be positive and ordered")


@dataclass(frozen=True)
class BaselineDetectorDeclaration:
    definition: str
    tracking_error_threshold: float

    def __post_init__(self) -> None:
        if not self.definition.strip():
            raise ValueError("baseline detector definition must be declared")
        if not isfinite(self.tracking_error_threshold) or self.tracking_error_threshold <= 0.0:
            raise ValueError("tracking error threshold must be finite and positive")


@dataclass(frozen=True)
class CorrectionAuthorityDeclaration:
    failure_definition: str
    horizon: HorizonSweepDeclaration
    effort_definition: str
    baseline_detector: BaselineDetectorDeclaration
    lead_time_definition: str
    kappa_max: float

    def __post_init__(self) -> None:
        for value, label in (
            (self.failure_definition, "failure definition"),
            (self.effort_definition, "effort measure"),
            (self.lead_time_definition, "lead-time metric"),
        ):
            if not value.strip():
                raise ValueError(f"{label} must be declared")
        if not isfinite(self.kappa_max) or self.kappa_max <= 0.0:
            raise ValueError("kappa_max must be finite and positive")


@dataclass(frozen=True)
class CorrectionAuthorityProtocol:
    base: ReachabilityProtocol
    authority: CorrectionAuthorityDeclaration
    hypotheses: tuple[Hypothesis, ...]


@dataclass(frozen=True)
class CorrectionAuthorityOracleResult:
    recoverable: bool
    margin: float


def validate_correction_authority_protocol(protocol: CorrectionAuthorityProtocol) -> None:
    reject_forbidden_protocol_phrases(protocol.base.protocol_id)
    for hypothesis in protocol.hypotheses:
        reject_forbidden_protocol_phrases(hypothesis.statement)
        reject_forbidden_protocol_phrases(hypothesis.success_criterion)
    if not protocol.hypotheses:
        raise ValueError("at least one preregistered hypothesis is required")


def double_integrator_position_interval(
    position: float, velocity: float, input_bound: float, horizon: float
) -> tuple[float, float]:
    if not all(isfinite(value) for value in (position, velocity, input_bound, horizon)):
        raise ValueError("double-integrator inputs must be finite")
    if input_bound < 0.0 or horizon < 0.0:
        raise ValueError("input bound and horizon must be nonnegative")
    center = position + velocity * horizon
    radius = 0.5 * input_bound * horizon * horizon
    return (center - radius, center + radius)


def _margin_to_target(
    interval: tuple[float, float], target: float, tolerance: float, required_task_error: float
) -> float:
    lower, upper = interval
    if target < lower - tolerance or target > upper + tolerance:
        return min(target - upper, lower - target)
    clearance = min(upper - target, target - lower)
    return clearance - tolerance if required_task_error == 0.0 else clearance


def evaluate_double_integrator_correction_authority(
    required_task_error: float,
    position: float,
    velocity: float,
    input_bound: float,
    horizon: float,
    tolerance: float,
) -> CorrectionAuthorityOracleResult:
    interval = double_integrator_position_interval(position, velocity, input_bound, horizon)
    target = position - required_task_error
    margin = _margin_to_target(interval, target, tolerance, required_task_error)
    return CorrectionAuthorityOracleResult(recoverable=margin >= 0.0, margin=margin)


def evaluate_scalar_correction_authority(
    required_task_error: float,
    system: LinearScalarSystem,
    horizon: float,
    tolerance: float,
) -> CorrectionAuthorityOracleResult:
    interval = scalar_linear_reachable_interval(system, horizon)
    target = system.initial_state - required_task_error
    margin = _margin_to_target(interval, target, tolerance, required_task_error)
    return CorrectionAuthorityOracleResult(recoverable=margin >= 0.0, margin=margin)


def evaluate_planar_rank_deficient_authority(
    required_task_error: tuple[float, float],
    system: PlanarRankDeficientSystem,
    tolerance: float,
) -> CorrectionAuthorityOracleResult:
    if required_task_error[1] != 0.0:
        return CorrectionAuthorityOracleResult(recoverable=False, margin=0.0)
    box = rank_deficient_reachable_box(system)
    margin = _margin_to_target(
        (box.lower[0], box.upper[0]), system.initial_state[0], tolerance, required_task_error[0]
    )
    return CorrectionAuthorityOracleResult(recoverable=margin >= 0.0, margin=margin)


def preregistered_humanoid_correction_authority_protocol() -> CorrectionAuthorityProtocol:
    coordinates = CoordinateDeclaration(
        ("task_position", "task_velocity"), ("m", "m/s"), (1.0, 0.5), "weighted_l2"
    )
    model = ModelDeclaration(
        "mujoco-swing-and-recovery-fixture",
        "preregistered-v1",
        StateDeclaration((0.0, 0.0), coordinates),
        InputDeclaration(("recovery_torque",), ((-1.0, 1.0),), ("N m",)),
    )
    analysis = AnalysisDeclaration(
        0.35,
        EventDeclaration("task set membership", "enter", "none", "terminal horizon"),
        TaskMetricDeclaration(
            "task-space position error", "m", 0.05, "at terminal horizon under bounded input"
        ),
        UncertaintyDeclaration(
            "deterministic simulation fixture", "frozen model revision", "modeled"
        ),
    )
    base = ReachabilityProtocol(
        "affinedrift.correction-authority/humanoid-option-a/v1",
        model,
        analysis,
        SolverDeclaration("offline-ltv-gramian-evaluator", "dispatch-3-placeholder", 1e-8),
    )
    authority = CorrectionAuthorityDeclaration(
        failure_definition=(
            "Unrecoverable when terminal task-space error after horizon H exceeds "
            "tolerance under bounded input."
        ),
        horizon=HorizonSweepDeclaration(0.35, 0.15, 0.55),
        effort_definition="∫‖u‖² dt on successful trials only.",
        baseline_detector=BaselineDetectorDeclaration(
            "Tracking-error threshold detector on task-space error.", 0.05
        ),
        lead_time_definition="Correction-authority detection time minus baseline detection time.",
        kappa_max=1.0e8,
    )
    return CorrectionAuthorityProtocol(
        base=base,
        authority=authority,
        hypotheses=(
            Hypothesis(
                "H-CA-LEAD",
                "prediction",
                (
                    "On the deterministic MuJoCo swing-and-recovery fixture, correction "
                    "authority flags unrecoverable perturbations earlier than tracking error "
                    "without higher effort on successful trials."
                ),
                "Positive median lead time and non-increasing successful-trial effort.",
            ),
        ),
    )
