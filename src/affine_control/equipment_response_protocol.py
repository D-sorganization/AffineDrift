"""Contracts for equipment and shaft individual-response studies.

The declarations in this module are deliberately narrower than a fitting
system.  They preserve metrology, randomization, qualification, provenance,
and authority boundaries for manufactured protocol fixtures.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import isfinite
from typing import Literal

SequenceId = Literal["AB", "BA"]
ResultStatus = Literal["positive", "negative", "null", "indeterminate", "unavailable"]

REQUIRED_PROPERTY_IDS = (
    "shaft-flexural-rigidity-profile",
    "shaft-torsional-rigidity-profile",
    "shaft-mass",
    "club-length",
    "total-mass",
    "balance-point",
    "head-mass",
    "head-inertia",
    "grip-mass",
    "static-loft",
    "static-lie",
    "face-angle",
)


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must be declared")


@dataclass(frozen=True)
class EvidenceSource:
    """Primary source used to constrain the protocol or interpretation."""

    source_id: str
    contribution: str

    def __post_init__(self) -> None:
        _require_text(self.source_id, "source ID")
        _require_text(self.contribution, "source contribution")


@dataclass(frozen=True)
class EquipmentProperty:
    """One calibrated property in an equipment-condition record."""

    property_id: str
    values: tuple[float, ...]
    unit: str
    standard_uncertainty: float
    method: str
    calibration_revision: str
    origin: str

    def __post_init__(self) -> None:
        if self.property_id not in REQUIRED_PROPERTY_IDS:
            raise ValueError("property ID is outside the required equipment property set")
        if not self.values or not all(isfinite(value) for value in self.values):
            raise ValueError("equipment property values must be finite and nonempty")
        if not isfinite(self.standard_uncertainty) or self.standard_uncertainty <= 0.0:
            raise ValueError("equipment property standard uncertainty must be positive")
        for value, label in (
            (self.unit, "property unit"),
            (self.method, "measurement method"),
            (self.calibration_revision, "calibration revision"),
        ):
            _require_text(value, label)
        if self.origin != "manufactured-synthetic":
            raise ValueError("equipment property origin must be manufactured-synthetic")


@dataclass(frozen=True)
class EquipmentCondition:
    """Coded intervention with a complete, ordered property manifest."""

    condition_id: str
    analyst_code: str
    properties: tuple[EquipmentProperty, ...]

    def __post_init__(self) -> None:
        _require_text(self.condition_id, "condition ID")
        _require_text(self.analyst_code, "analyst code")
        if tuple(item.property_id for item in self.properties) != REQUIRED_PROPERTY_IDS:
            raise ValueError("condition must contain the exact required equipment property set")


@dataclass(frozen=True)
class CustodyEvent:
    """One immutable metrology or custody transition."""

    event_id: str
    action: str
    custodian_role: str
    condition_ids: tuple[str, ...]


@dataclass(frozen=True)
class ChainOfCustody:
    """Ordered custody record for all coded equipment conditions."""

    condition_ids: tuple[str, ...]
    events: tuple[CustodyEvent, ...]

    def __post_init__(self) -> None:
        if not self.condition_ids or not self.events:
            raise ValueError("chain of custody must name conditions and events")
        if any(event.condition_ids != self.condition_ids for event in self.events):
            raise ValueError("every custody event must cover the declared conditions")


@dataclass(frozen=True)
class RandomizationPlan:
    """Counterbalanced repeated-crossover allocation contract."""

    algorithm: str
    seed: int
    assignments: tuple[tuple[str, SequenceId], ...]
    cycles_per_participant: int
    trials_per_condition_per_cycle: int
    washout_minutes: float
    blinding: str

    @property
    def sequence_counts(self) -> dict[str, int]:
        return dict(Counter(sequence for _, sequence in self.assignments))

    def __post_init__(self) -> None:
        participant_ids = tuple(participant for participant, _ in self.assignments)
        if not participant_ids or len(set(participant_ids)) != len(participant_ids):
            raise ValueError("randomization requires unique participant IDs")
        counts = Counter(sequence for _, sequence in self.assignments)
        if set(counts) != {"AB", "BA"} or counts["AB"] != counts["BA"]:
            raise ValueError("randomization must be counterbalanced across AB and BA")
        if self.cycles_per_participant < 2 or self.trials_per_condition_per_cycle < 2:
            raise ValueError("repeated crossover requires multiple cycles and trials")
        if not isfinite(self.washout_minutes) or self.washout_minutes <= 0.0:
            raise ValueError("washout duration must be finite and positive")
        _require_text(self.algorithm, "randomization algorithm")
        _require_text(self.blinding, "blinding declaration")


@dataclass(frozen=True)
class HumanEvidenceGate:
    """Availability and missing authority for human-facing interpretation."""

    status: Literal["unavailable"]
    missing_authorities: tuple[str, ...]


@dataclass(frozen=True)
class EquipmentResponseProtocol:
    """Versioned individual-response study contract."""

    revision: str
    sources: tuple[EvidenceSource, ...]
    estimand: str
    outcome_unit: str
    practical_threshold: float
    conditions: tuple[EquipmentCondition, ...]
    chain_of_custody: ChainOfCustody
    randomization: RandomizationPlan
    carryover_limit: float
    intent_error_limit: float
    human_gate: HumanEvidenceGate
    authority_limit: str

    def __post_init__(self) -> None:
        if len(self.conditions) != 2 or len({row.condition_id for row in self.conditions}) != 2:
            raise ValueError("protocol requires exactly two unique equipment conditions")
        if self.chain_of_custody.condition_ids != tuple(
            row.condition_id for row in self.conditions
        ):
            raise ValueError("condition and custody identifiers must align")
        if not isfinite(self.practical_threshold) or self.practical_threshold <= 0.0:
            raise ValueError("practical threshold must be positive")
        if self.carryover_limit <= 0.0 or self.intent_error_limit <= 0.0:
            raise ValueError("qualification limits must be positive")


@dataclass(frozen=True)
class ResponseObservation:
    """One retained manufactured trial with uncertainty and quality signals."""

    observation_id: str
    participant_id: str
    cycle: int
    condition_id: str
    trial: int
    outcome_value: float
    measurement_standard_uncertainty: float
    intent_error: float
    carryover_residual: float
    origin: str

    def __post_init__(self) -> None:
        for value, label in (
            (self.observation_id, "observation ID"),
            (self.participant_id, "participant ID"),
            (self.condition_id, "condition ID"),
        ):
            _require_text(value, label)
        if not isfinite(self.outcome_value):
            raise ValueError("outcome value must be finite")
        if (
            not isfinite(self.measurement_standard_uncertainty)
            or self.measurement_standard_uncertainty <= 0.0
        ):
            raise ValueError("measurement uncertainty must be finite and positive")
        if not isfinite(self.intent_error) or self.intent_error < 0.0:
            raise ValueError("intent error must be finite and nonnegative")
        if not isfinite(self.carryover_residual) or self.carryover_residual < 0.0:
            raise ValueError("carryover residual must be finite and nonnegative")
        if self.cycle < 1 or self.trial < 1:
            raise ValueError("cycle and trial indices must be positive")
        if self.origin != "manufactured-synthetic":
            raise ValueError("observation origin must be manufactured-synthetic")


@dataclass(frozen=True)
class FixtureLedgerRecord:
    """Compact, non-authoritative expected result for regression review."""

    record_id: str
    status: ResultStatus
    evidence_origin: Literal["manufactured-synthetic", "unavailable"]
    authorized_guidance: Literal["unavailable"] = "unavailable"
