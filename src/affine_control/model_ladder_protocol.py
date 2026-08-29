"""Bounded declarations and manufactured fixtures for a nested model ladder.

This module validates comparison contracts; it is not a dynamics engine. The
fixtures are analytic, synthetic records for testing projection, convergence,
and model-selection behavior without implying validation on participant data.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Literal

LevelId = Literal[
    "planar-rigid",
    "spatial-open-chain",
    "spatial-closed-chain",
    "flexible-shaft",
]
EvidenceStatus = Literal["measured", "estimated", "modeled", "assumed", "unavailable"]
ResultOutcome = Literal["supported", "null", "negative", "unavailable"]

LEVEL_IDS: tuple[LevelId, ...] = (
    "planar-rigid",
    "spatial-open-chain",
    "spatial-closed-chain",
    "flexible-shaft",
)
COMPARISON_CATEGORIES = (
    "conserved-quantity-residuals",
    "kinematics",
    "generalized-loads",
    "club-face-and-path",
    "impact-state",
    "runtime",
    "conditioning",
    "parameter-sensitivity",
)
_EVIDENCE_STATUSES = ("measured", "estimated", "modeled", "assumed", "unavailable")
_OUTCOMES = ("supported", "null", "negative", "unavailable")
_AUTHORITY_PHRASES = (
    "coaching prescription",
    "clinical authority",
    "all golfers",
    "causes better",
)


def _require_text(value: str, label: str) -> None:
    """Reject an empty declaration field."""
    if not value.strip():
        raise ValueError(f"{label} must be declared")


def _require_text_tuple(values: tuple[str, ...], label: str) -> None:
    """Reject an empty tuple or any blank member."""
    if not values or any(not value.strip() for value in values):
        raise ValueError(f"{label} must be declared")


@dataclass(frozen=True)
class ModelLevel:
    """One level with shared coordinates and explicit interpretation limits."""

    level_id: LevelId
    parent_id: LevelId | None
    coordinates: tuple[str, ...]
    units: tuple[str, ...]
    frame: str
    included_physics: tuple[str, ...]
    omitted_physics: tuple[str, ...]
    intended_uses: tuple[str, ...]
    parameter_revision: str
    initialization: str
    event_definition: str
    projection_to_parent: tuple[int, ...]

    def __post_init__(self) -> None:
        """Validate coordinate alignment and scientific declarations."""
        if self.level_id not in LEVEL_IDS:
            raise ValueError("level_id is not part of the declared ladder")
        if not self.coordinates or len(self.coordinates) != len(self.units):
            raise ValueError("coordinates and units must be nonempty and aligned")
        _require_text_tuple(self.coordinates, "coordinates")
        _require_text_tuple(self.units, "coordinate units")
        _require_text(self.frame, "coordinate frame")
        _require_text_tuple(self.included_physics, "included physics")
        _require_text_tuple(self.omitted_physics, "omitted physics")
        _require_text_tuple(self.intended_uses, "intended uses")
        _require_text(self.parameter_revision, "parameter revision")
        _require_text(self.initialization, "initialization")
        _require_text(self.event_definition, "event definition")


@dataclass(frozen=True)
class ModelLadderProtocol:
    """Versioned comparison contract for all four nested levels."""

    protocol_id: str
    source_revision: str
    levels: tuple[ModelLevel, ...]
    comparison_categories: tuple[str, ...]
    uncertainty_method: str
    data_classification: str
    license: str

    def __post_init__(self) -> None:
        """Fail closed unless nesting and adjacent maps are exact prefixes."""
        for value, label in (
            (self.protocol_id, "protocol_id"),
            (self.source_revision, "source revision"),
            (self.uncertainty_method, "uncertainty method"),
            (self.data_classification, "data classification"),
            (self.license, "license"),
        ):
            _require_text(value, label)
        if tuple(level.level_id for level in self.levels) != LEVEL_IDS:
            raise ValueError("model levels must follow the frozen nested order")
        if self.comparison_categories != COMPARISON_CATEGORIES:
            raise ValueError("all task-specific comparison categories must be declared")
        for index, level in enumerate(self.levels):
            expected_parent = None if index == 0 else self.levels[index - 1]
            parent_id = None if expected_parent is None else expected_parent.level_id
            if level.parent_id != parent_id:
                raise ValueError("each non-root level must name its adjacent parent")
            if expected_parent is None:
                if level.projection_to_parent:
                    raise ValueError("the root level cannot declare a parent projection")
                continue
            expected_map = tuple(range(len(expected_parent.coordinates)))
            if level.projection_to_parent != expected_map:
                raise ValueError("adjacent projection must preserve shared coordinate order")
            projected_names = tuple(level.coordinates[item] for item in expected_map)
            projected_units = tuple(level.units[item] for item in expected_map)
            names_changed = projected_names != expected_parent.coordinates
            units_changed = projected_units != expected_parent.units
            if names_changed or units_changed:
                raise ValueError("adjacent levels must preserve shared names and units")


@dataclass(frozen=True)
class ComparisonObservation:
    """One task-specific comparison with provenance and uncertainty."""

    level_id: LevelId
    category: str
    metric_name: str
    unit: str
    estimate: float | None
    uncertainty_interval: tuple[float, float] | None
    evidence_status: EvidenceStatus
    outcome: ResultOutcome

    def __post_init__(self) -> None:
        """Validate numerical and provenance consistency."""
        if self.level_id not in LEVEL_IDS or self.category not in COMPARISON_CATEGORIES:
            raise ValueError("comparison must name a declared level and category")
        _require_text(self.metric_name, "metric name")
        _require_text(self.unit, "metric unit")
        _validate_result_fields(
            self.estimate,
            self.uncertainty_interval,
            self.evidence_status,
            self.outcome,
        )


@dataclass(frozen=True)
class TaskAssessment:
    """Evidence-bounded sufficiency assessment for one task and level."""

    task_id: str
    level_id: LevelId
    metric_name: str
    unit: str
    estimate: float | None
    uncertainty_interval: tuple[float, float] | None
    tolerance: float
    evidence_status: EvidenceStatus
    outcome: ResultOutcome
    sufficient: bool | None
    interpretation: str

    def __post_init__(self) -> None:
        """Validate sufficiency fields and block authority promotion."""
        for value, label in (
            (self.task_id, "task_id"),
            (self.metric_name, "metric name"),
            (self.unit, "metric unit"),
            (self.interpretation, "interpretation"),
        ):
            _require_text(value, label)
        if self.level_id not in LEVEL_IDS:
            raise ValueError("task assessment must name a declared level")
        if not isfinite(self.tolerance) or self.tolerance < 0.0:
            raise ValueError("task tolerance must be finite and nonnegative")
        lowered = self.interpretation.lower()
        if "global fidelity" in lowered or self.unit == "%":
            raise ValueError("global fidelity percentages are outside this contract")
        if any(phrase in lowered for phrase in _AUTHORITY_PHRASES):
            raise ValueError("interpretation exceeds the scientific authority boundary")
        _validate_result_fields(
            self.estimate,
            self.uncertainty_interval,
            self.evidence_status,
            self.outcome,
        )


def _validate_result_fields(
    estimate: float | None,
    interval: tuple[float, float] | None,
    evidence_status: EvidenceStatus,
    outcome: ResultOutcome,
) -> None:
    """Require consistent estimates, intervals, status, and outcomes."""
    if evidence_status not in _EVIDENCE_STATUSES or outcome not in _OUTCOMES:
        raise ValueError("result provenance and outcome must be declared")
    if estimate is None:
        if interval is not None:
            raise ValueError("an unavailable estimate cannot have an interval")
        if evidence_status != "unavailable" or outcome != "unavailable":
            raise ValueError("missing estimates must be marked unavailable")
        return
    if not isfinite(estimate) or interval is None:
        raise ValueError("available estimates require finite values and uncertainty")
    lower, upper = interval
    if not all(isfinite(value) for value in interval) or lower > estimate or estimate > upper:
        raise ValueError("uncertainty must be finite, ordered, and contain the estimate")


def build_model_ladder_protocol() -> ModelLadderProtocol:
    """Build the frozen four-level comparison protocol."""
    shared = ("club_path_angle", "club_path_rate")
    shared_units = ("rad", "rad/s")
    additions = (
        ((), ()),
        (("out_of_plane_angle", "out_of_plane_rate"), ("rad", "rad/s")),
        (("closure_x", "closure_y"), ("m", "m")),
        (("shaft_mode_1", "shaft_mode_rate_1"), ("m", "m/s")),
    )
    included = (
        ("planar rigid-link kinematics", "planar inertial and generalized loads"),
        ("three-dimensional rigid-body kinematics", "out-of-plane face orientation"),
        ("bilateral closure constraints", "closed-chain reaction loads"),
        ("first flexible-shaft bending coordinate", "shaft strain energy"),
    )
    omitted = (
        ("out-of-plane motion", "bilateral closure", "shaft flexibility"),
        ("bilateral closure", "hand-contact reaction split", "shaft flexibility"),
        ("shaft flexibility", "participant-specific tissue dynamics"),
        ("higher shaft modes", "aerodynamics", "participant-specific tissue dynamics"),
    )
    uses = (
        ("planar path and energy-accounting checks",),
        ("three-dimensional face and path checks",),
        ("bilateral load-share and closure-residual checks",),
        ("shaft deflection and impact-state sensitivity checks",),
    )
    levels: list[ModelLevel] = []
    coordinates: tuple[str, ...] = shared
    units: tuple[str, ...] = shared_units
    for index, level_id in enumerate(LEVEL_IDS):
        extra_coordinates, extra_units = additions[index]
        coordinates += extra_coordinates
        units += extra_units
        parent = None if index == 0 else LEVEL_IDS[index - 1]
        parent_size = 0 if index == 0 else len(levels[-1].coordinates)
        levels.append(
            ModelLevel(
                level_id=level_id,
                parent_id=parent,
                coordinates=coordinates,
                units=units,
                frame="right-handed pelvis-fixed frame; SI units",
                included_physics=included[index],
                omitted_physics=omitted[index],
                intended_uses=uses[index],
                parameter_revision="manufactured-analytic-parameters/v1",
                initialization="shared coordinates equal; added coordinates initialized to zero",
                event_definition="first descending crossing of club_path_angle = 0 rad",
                projection_to_parent=tuple(range(parent_size)),
            )
        )
    return ModelLadderProtocol(
        protocol_id="affinedrift.model-ladder-protocol/v1",
        source_revision="affinedrift.model-ladder/v1",
        levels=tuple(levels),
        comparison_categories=COMPARISON_CATEGORIES,
        uncertainty_method="deterministic analytic interval around each manufactured value",
        data_classification="synthetic; no participant data",
        license="MIT",
    )


def minimum_sufficient_level(
    protocol: ModelLadderProtocol,
    assessments: tuple[TaskAssessment, ...],
    task_id: str,
) -> LevelId | None:
    """Return the least complex level meeting its declared task tolerance."""
    _require_text(task_id, "task_id")
    by_level = {row.level_id: row for row in assessments if row.task_id == task_id}
    for level in protocol.levels:
        assessment = by_level.get(level.level_id)
        if assessment is None or assessment.sufficient is not True:
            continue
        if assessment.uncertainty_interval is None or assessment.outcome != "supported":
            continue
        if max(abs(value) for value in assessment.uncertainty_interval) <= assessment.tolerance:
            return level.level_id
    return None
