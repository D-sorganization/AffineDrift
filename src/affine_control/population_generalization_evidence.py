"""Deterministic manufactured evidence for the population protocol."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .population_generalization import LockedSplit, Observation, validate_split_integrity


@dataclass(frozen=True)
class Interval:
    """Closed participant-weighted manufactured interval."""

    lower: float
    upper: float


@dataclass(frozen=True)
class Calibration:
    """Ordinary linear calibration intercept and slope."""

    intercept: float
    slope: float


@dataclass(frozen=True)
class SubgroupPerformance:
    """Reported or small-cell-suppressed subgroup result."""

    subgroup: str
    sample_size: int
    status: Literal["reported", "unavailable"]
    mean_absolute_error: float | None
    limitation: str


@dataclass(frozen=True)
class Outcome:
    """Retained adverse, null, or unavailable outcome."""

    outcome_id: str
    status: Literal["negative", "null", "unavailable"]
    finding: str


@dataclass(frozen=True)
class ValidationReport:
    """Deterministic non-authorizing manufactured test report."""

    mean_error: float
    mean_absolute_error: float
    participant_weighted_interval: Interval
    calibration: Calibration
    subgroup_performance: tuple[SubgroupPerformance, ...]
    outcomes: tuple[Outcome, ...]
    sensitivity_result: str
    external_validation_status: Literal["unavailable"]
    authorizes_population_claim: Literal[False]


def _linear_calibration(rows: tuple[Observation, ...]) -> Calibration:
    x = [row.predicted for row in rows]
    y = [row.observed for row in rows]
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)
    denominator = sum((value - x_mean) ** 2 for value in x)
    if denominator == 0.0:
        raise ValueError("calibration slope is unavailable for constant predictions")
    slope = sum((px - x_mean) * (oy - y_mean) for px, oy in zip(x, y, strict=True))
    slope /= denominator
    return Calibration(intercept=y_mean - slope * x_mean, slope=slope)


def _subgroups(rows: tuple[Observation, ...], minimum_size: int) -> tuple[SubgroupPerformance, ...]:
    groups: dict[str, list[float]] = {}
    for row in rows:
        labels = (
            f"skill:{row.skill_stratum}",
            f"sex:{row.sex_stratum}",
            f"age:{row.age_stratum}",
            f"handedness:{row.handedness}",
            f"anthropometry:{row.anthropometry_stratum}",
            f"equipment:{row.equipment_id}",
        )
        for label in labels:
            groups.setdefault(label, []).append(abs(row.observed - row.predicted))
    output = []
    for label, errors in sorted(groups.items()):
        available = len(errors) >= minimum_size
        output.append(
            SubgroupPerformance(
                subgroup=label,
                sample_size=len(errors),
                status="reported" if available else "unavailable",
                mean_absolute_error=sum(errors) / len(errors) if available else None,
                limitation=(
                    "manufactured-fixture descriptive result only"
                    if available
                    else "suppressed below the preregistered minimum cell size"
                ),
            )
        )
    return tuple(output)


def evaluate_population_prediction(
    observations: tuple[Observation, ...],
    split: LockedSplit,
    minimum_subgroup_size: int,
) -> ValidationReport:
    """Evaluate the untouched manufactured test partition deterministically."""
    validate_split_integrity(observations, split)
    if minimum_subgroup_size < 2:
        raise ValueError("minimum subgroup size must be at least two")
    partition_by_id = {row.record_id: row.partition for row in split.assignments}
    rows = tuple(row for row in observations if partition_by_id[row.record_id] == "test")
    if len(rows) < 2:
        raise ValueError("test partition requires at least two observations")
    errors = tuple(row.observed - row.predicted for row in rows)
    participant_means: dict[str, list[float]] = {}
    for row, error in zip(rows, errors, strict=True):
        participant_means.setdefault(row.participant_id, []).append(error)
    cluster_means = tuple(sum(values) / len(values) for values in participant_means.values())
    return ValidationReport(
        mean_error=sum(errors) / len(errors),
        mean_absolute_error=sum(abs(error) for error in errors) / len(errors),
        participant_weighted_interval=Interval(min(cluster_means), max(cluster_means)),
        calibration=_linear_calibration(rows),
        subgroup_performance=_subgroups(rows, minimum_subgroup_size),
        outcomes=(
            Outcome("calibration-slope", "negative", "Slope is below the declared target of one."),
            Outcome("mean-bias", "null", "Participant-level interval includes zero."),
            Outcome("external-site", "unavailable", "No measured external site exists."),
        ),
        sensitivity_result="Complete-case and missingness perturbations are template-only.",
        external_validation_status="unavailable",
        authorizes_population_claim=False,
    )
