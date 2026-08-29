"""Fail-closed population-generalization and held-out-validation contracts.

This module validates protocol structure and deterministic manufactured data.
It does not authorize participant collection or a population claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .population_generalization_evidence import ValidationReport

Partition = Literal["train", "validation", "test"]
Estimand = Literal[
    "within-person explanation",
    "between-person association",
    "prediction",
    "causal inference",
]


class EvidenceOrigin(StrEnum):
    """Allowed evidence origins without silent promotion."""

    MEASURED = "measured"
    ESTIMATED = "estimated"
    MODELED = "modeled"
    ASSUMED = "assumed"
    MANUFACTURED_SYNTHETIC = "manufactured-synthetic"
    UNAVAILABLE = "unavailable"


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must be declared")


def _require_texts(values: tuple[str, ...], label: str) -> None:
    if not values or any(not value.strip() for value in values):
        raise ValueError(f"{label} must be declared")


@dataclass(frozen=True)
class DatasetCard:
    """Population, sampling, hierarchy, governance, and exclusion record."""

    dataset_id: str
    target_population: str
    sampling_frame: str
    cohort_strata: tuple[str, ...]
    hierarchy: tuple[str, ...]
    repeated_measure_unit: str
    missingness_plan: str
    exclusion_rules: tuple[str, ...]
    privacy_plan: str
    consent_plan: str
    ethics_review: str
    license: str
    source_revision: str
    evidence_origin: EvidenceOrigin

    def __post_init__(self) -> None:
        for value, label in (
            (self.dataset_id, "dataset ID"),
            (self.target_population, "target population"),
            (self.sampling_frame, "sampling frame"),
            (self.repeated_measure_unit, "repeated-measure unit"),
            (self.missingness_plan, "missingness plan"),
            (self.privacy_plan, "privacy plan"),
            (self.consent_plan, "consent plan"),
            (self.ethics_review, "ethics review"),
            (self.license, "license"),
            (self.source_revision, "source revision"),
        ):
            _require_text(value, label)
        _require_texts(self.cohort_strata, "cohort strata")
        _require_texts(self.exclusion_rules, "exclusion rules")
        expected = ("site", "participant", "session", "equipment", "trial")
        if self.hierarchy != expected:
            raise ValueError("hierarchy must freeze site, participant, session, equipment, trial")
        if (
            self.evidence_origin is EvidenceOrigin.MANUFACTURED_SYNTHETIC
            and "representative" in self.sampling_frame.lower()
        ):
            raise ValueError(
                "sampling frame cannot promote manufactured evidence as representative"
            )


@dataclass(frozen=True)
class Preregistration:
    """Analysis declarations that must exist before a locked test is exposed."""

    status: Literal["template-only", "preregistered"]
    estimand: str
    predictors: tuple[str, ...]
    outcome: str
    metric: str
    subgroup_plan: str
    sensitivity_plan: str
    falsifiers: tuple[str, ...]

    def __post_init__(self) -> None:
        for value, label in (
            (self.estimand, "estimand"),
            (self.outcome, "outcome"),
            (self.metric, "metric"),
            (self.subgroup_plan, "subgroup plan"),
            (self.sensitivity_plan, "sensitivity plan"),
        ):
            _require_text(value, label)
        _require_texts(self.predictors, "predictors")
        _require_texts(self.falsifiers, "falsifiers")


@dataclass(frozen=True)
class Observation:
    """One manufactured trial with explicit nested identifiers and strata."""

    record_id: str
    site_id: str
    participant_id: str
    session_id: str
    equipment_id: str
    trial_id: str
    skill_stratum: str
    sex_stratum: str
    age_stratum: str
    handedness: str
    anthropometry_stratum: str
    observed: float
    predicted: float

    def __post_init__(self) -> None:
        values = (
            self.record_id,
            self.site_id,
            self.participant_id,
            self.session_id,
            self.equipment_id,
            self.trial_id,
            self.skill_stratum,
            self.sex_stratum,
            self.age_stratum,
            self.handedness,
            self.anthropometry_stratum,
        )
        _require_texts(values, "observation fields")
        if not isfinite(self.observed) or not isfinite(self.predicted):
            raise ValueError("observed and predicted values must be finite")


@dataclass(frozen=True)
class SplitAssignment:
    """A predeclared record partition."""

    record_id: str
    partition: Partition

    def __post_init__(self) -> None:
        _require_text(self.record_id, "record ID")
        if self.partition not in ("train", "validation", "test"):
            raise ValueError("partition must be train, validation, or test")


@dataclass(frozen=True)
class LockedSplit:
    """Immutable group-aware partition record."""

    split_id: str
    strategies: tuple[str, ...]
    assignments: tuple[SplitAssignment, ...]
    locked_test_set: bool
    lock_revision: str
    tuning_partitions: tuple[Partition, ...]

    def __post_init__(self) -> None:
        _require_text(self.split_id, "split ID")
        _require_texts(self.strategies, "split strategies")
        _require_text(self.lock_revision, "lock revision")
        if not self.assignments:
            raise ValueError("split assignments must be declared")
        if self.tuning_partitions != ("train", "validation"):
            raise ValueError("test partition must not be available for tuning")


def _partition_groups(
    by_record: dict[str, Observation], assignments: tuple[SplitAssignment, ...]
) -> tuple[dict[str, set[Partition]], list[str]]:
    """Collect group partitions while validating referenced record IDs."""
    partitions: dict[str, set[Partition]] = {}
    assigned_ids: list[str] = []
    for assignment in assignments:
        if assignment.record_id not in by_record:
            raise ValueError("split references an unknown observation")
        assigned_ids.append(assignment.record_id)
        row = by_record[assignment.record_id]
        for label, key in (
            ("participant", row.participant_id),
            ("session", row.session_id),
            ("equipment", row.equipment_id),
            ("trial", row.trial_id),
        ):
            partitions.setdefault(f"{label}:{key}", set()).add(assignment.partition)
    return partitions, assigned_ids


def validate_split_integrity(observations: tuple[Observation, ...], split: LockedSplit) -> None:
    """Reject participant, session, site, equipment, trial, and tuning leakage."""
    if not split.locked_test_set:
        raise ValueError("locked test set is required")
    by_record = {row.record_id: row for row in observations}
    if len(by_record) != len(observations):
        raise ValueError("observation record IDs must be unique")
    partitions, assigned_ids = _partition_groups(by_record, split.assignments)
    for key, values in partitions.items():
        if len(values) > 1:
            raise ValueError(f"{key.split(':', 1)[0]} leakage across partitions")
    if len(assigned_ids) != len(set(assigned_ids)):
        raise ValueError("record assignment must be unique")
    if set(assigned_ids) != set(by_record):
        raise ValueError("every observation must be assigned exactly once")
    test_sites = {
        by_record[row.record_id].site_id for row in split.assignments if row.partition == "test"
    }
    development_sites = {
        by_record[row.record_id].site_id
        for row in split.assignments
        if row.partition in split.tuning_partitions
    }
    if test_sites & development_sites:
        raise ValueError("site leakage across development and test partitions")


def evaluate_population_prediction(
    observations: tuple[Observation, ...],
    split: LockedSplit,
    minimum_subgroup_size: int,
) -> ValidationReport:
    """Delegate deterministic analysis to the evidence module."""
    from .population_generalization_evidence import evaluate_population_prediction as evaluate

    return evaluate(observations, split, minimum_subgroup_size)


@dataclass(frozen=True)
class PopulationPromotionEvidence:
    """Governance evidence required before a population claim can be reviewed."""

    evidence_origin: EvidenceOrigin
    measured_dataset_record: str | None
    ethics_approval: bool
    privacy_review: bool
    consent_verified: bool
    license_verified: bool
    preregistration_frozen: bool
    locked_test_verified: bool
    external_site_validation: bool
    subgroup_limits_reported: bool
    negative_results_retained: bool
    human_approval: bool

    def __post_init__(self) -> None:
        if self.evidence_origin is EvidenceOrigin.MEASURED and not self.measured_dataset_record:
            raise ValueError("measured evidence requires a governed dataset record")
        if self.evidence_origin is not EvidenceOrigin.MEASURED and self.measured_dataset_record:
            raise ValueError("non-measured evidence cannot carry a measured dataset record")

    @classmethod
    def manufactured_fixture(cls) -> PopulationPromotionEvidence:
        return cls(
            evidence_origin=EvidenceOrigin.MANUFACTURED_SYNTHETIC,
            measured_dataset_record=None,
            ethics_approval=False,
            privacy_review=False,
            consent_verified=False,
            license_verified=False,
            preregistration_frozen=False,
            locked_test_verified=True,
            external_site_validation=False,
            subgroup_limits_reported=True,
            negative_results_retained=True,
            human_approval=False,
        )


def population_claim_authorized(evidence: PopulationPromotionEvidence) -> bool:
    """Return true only for a complete measured package and human approval."""
    gates = (
        evidence.evidence_origin is EvidenceOrigin.MEASURED,
        evidence.measured_dataset_record is not None,
        evidence.ethics_approval,
        evidence.privacy_review,
        evidence.consent_verified,
        evidence.license_verified,
        evidence.preregistration_frozen,
        evidence.locked_test_verified,
        evidence.external_site_validation,
        evidence.subgroup_limits_reported,
        evidence.negative_results_retained,
        evidence.human_approval,
    )
    return all(gates)


@dataclass(frozen=True)
class PopulationProtocol:
    revision: str
    dataset_card: DatasetCard
    preregistration: Preregistration
    split: LockedSplit
    estimands: tuple[Estimand, ...]
    external_validation_status: Literal["unavailable"]
    authority_limit: str

    def __post_init__(self) -> None:
        _require_text(self.revision, "protocol revision")
        expected: tuple[Estimand, ...] = (
            "within-person explanation",
            "between-person association",
            "prediction",
            "causal inference",
        )
        if self.estimands != expected:
            raise ValueError("all four estimand classes must remain distinct")
        _require_text(self.authority_limit, "authority limit")
