"""Evidence and human-promotion boundaries for impedance identification."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Literal

EvidenceTier = Literal[
    "effective-mechanical",
    "model-partitioned",
    "emg-proxy",
    "unavailable",
]
Outcome = Literal["supported", "negative", "null", "unavailable"]
RecordStatus = Literal["pending-external", "approved-external"]
EvidenceOrigin = Literal["synthetic-fixture", "measured", "model-estimated", "unavailable"]
RecordType = Literal[
    "ethics-approval",
    "risk-assessment",
    "privacy-plan",
    "consent-revision",
    "data-license",
    "device-calibration",
    "stopping-rules-revision",
    "reliability-protocol",
    "independent-approval",
]

_EVIDENCE_TIERS = (
    "effective-mechanical",
    "model-partitioned",
    "emg-proxy",
    "unavailable",
)
_OUTCOMES = ("supported", "negative", "null", "unavailable")
_EVIDENCE_ORIGINS = ("synthetic-fixture", "measured", "model-estimated", "unavailable")
_RECORD_STATUSES = ("pending-external", "approved-external")
_RECORD_TYPES = (
    "ethics-approval",
    "risk-assessment",
    "privacy-plan",
    "consent-revision",
    "data-license",
    "device-calibration",
    "stopping-rules-revision",
    "reliability-protocol",
    "independent-approval",
)
_AUTHORITY_PHRASES = (
    "muscle force",
    "neural strategy",
    "coaching",
    "clinical",
    "diagnosis",
    "treatment",
)


def _require_text(value: str, label: str) -> None:
    """Reject blank evidence declarations."""
    if not value.strip():
        raise ValueError(f"{label} must be declared")


@dataclass(frozen=True)
class EvidenceProvenance:
    """Machine-readable result origin that prevents silent synthetic promotion."""

    origin: EvidenceOrigin
    record_id: str
    revision: str
    synthetic_fixture: bool

    def __post_init__(self) -> None:
        """Require a runtime origin and a consistent synthetic-fixture marker."""
        if self.origin not in _EVIDENCE_ORIGINS:
            raise ValueError("evidence origin is not declared")
        _require_text(self.record_id, "provenance record_id")
        _require_text(self.revision, "provenance revision")
        if self.origin == "synthetic-fixture" and not self.synthetic_fixture:
            raise ValueError("synthetic-fixture origin requires its explicit fixture marker")
        if self.origin != "synthetic-fixture" and self.synthetic_fixture:
            raise ValueError(f"{self.origin} origin cannot retain synthetic-fixture provenance")


@dataclass(frozen=True)
class ImpedanceResult:
    """One tiered result with uncertainty, sensitivity, and adverse outcome."""

    quantity: str
    evidence_tier: EvidenceTier
    estimate: float | None
    uncertainty_interval: tuple[float, float] | None
    unit: str
    outcome: Outcome
    sensitivity_parameters: tuple[str, ...]
    interpretation: str
    provenance: EvidenceProvenance

    def __post_init__(self) -> None:
        """Reject contradictory or over-authoritative result records."""
        _require_text(self.quantity, "result quantity")
        _require_text(self.unit, "result unit")
        _require_text(self.interpretation, "result interpretation")
        if self.evidence_tier not in _EVIDENCE_TIERS or self.outcome not in _OUTCOMES:
            raise ValueError("evidence tier and outcome must be declared")
        if any(phrase in self.interpretation.lower() for phrase in _AUTHORITY_PHRASES):
            raise ValueError("interpretation exceeds the authority boundary")
        if self.provenance.origin == "synthetic-fixture" and "synthetic" not in (
            self.interpretation.lower()
        ):
            raise ValueError("synthetic results must retain an explicit synthetic interpretation")
        if self.evidence_tier == "unavailable" or self.outcome == "unavailable":
            self._validate_unavailable()
            return
        self._validate_available()

    def _validate_unavailable(self) -> None:
        """Require the unavailable tier, outcome, and values to agree."""
        if self.evidence_tier != "unavailable" or self.outcome != "unavailable":
            raise ValueError("unavailable tier and outcome must agree")
        if self.estimate is not None or self.uncertainty_interval is not None:
            raise ValueError("unavailable results cannot contain estimates")
        if self.provenance.origin != "unavailable":
            raise ValueError("unavailable results require unavailable provenance")

    def _validate_available(self) -> None:
        """Require finite estimates, complete intervals, and sensitivity inputs."""
        if self.estimate is None or self.uncertainty_interval is None:
            raise ValueError("available results require an estimate and uncertainty")
        lower, upper = self.uncertainty_interval
        if not all(isfinite(value) for value in (self.estimate, lower, upper)):
            raise ValueError("uncertainty must be finite")
        if not lower <= self.estimate <= upper:
            raise ValueError("uncertainty must be ordered and contain the estimate")
        if not self.sensitivity_parameters or any(
            not value.strip() for value in self.sensitivity_parameters
        ):
            raise ValueError("sensitivity parameters must be declared")
        if self.provenance.origin == "unavailable":
            raise ValueError("available results cannot use unavailable provenance")


@dataclass(frozen=True)
class GovernedRecord:
    """Typed reference to a record controlled by an external human authority."""

    record_id: str
    record_type: RecordType
    authority: str
    revision: str
    status: RecordStatus

    def __post_init__(self) -> None:
        """Reject placeholders and undeclared external-review states."""
        for value, label in (
            (self.record_id, "record_id"),
            (self.authority, "record authority"),
            (self.revision, "record revision"),
        ):
            _require_text(value, label)
        if self.status not in _RECORD_STATUSES:
            raise ValueError("record status must be pending-external or approved-external")
        if self.record_type not in _RECORD_TYPES:
            raise ValueError("governed record type must be declared")

    @property
    def externally_approved(self) -> bool:
        """Return whether the external record carries its approved state."""
        return self.status == "approved-external"


@dataclass(frozen=True)
class HumanReadiness:
    """Structural review-readiness report that never authorizes collection."""

    ready_for_external_review: bool
    authorizes_participant_collection: Literal[False]
    next_gate: str


@dataclass(frozen=True)
class HumanStudyGate:
    """Typed structural prerequisites for an external human release decision."""

    ethics_approval: GovernedRecord | None
    risk_assessment: GovernedRecord | None
    privacy_plan: GovernedRecord | None
    consent_revision: GovernedRecord | None
    data_license: GovernedRecord | None
    device_calibration: GovernedRecord | None
    stopping_rules_revision: GovernedRecord | None
    reliability_protocol: GovernedRecord | None
    independent_approval: GovernedRecord | None
    participant_held_out_plan_registered: bool

    def __post_init__(self) -> None:
        """Reject arbitrary strings masquerading as governed approval records."""
        if any(
            record is not None and not isinstance(record, GovernedRecord) for record in self.records
        ):
            raise TypeError("human gates require typed governed records")
        expected_types = _RECORD_TYPES
        for record, expected_type in zip(self.records, expected_types, strict=True):
            if record is not None and record.record_type != expected_type:
                raise ValueError("human gate record types must match their exact prerequisites")
        record_ids = tuple(record.record_id for record in self.records if record is not None)
        if len(record_ids) != len(set(record_ids)):
            raise ValueError("human gate record IDs must be distinct")

    @property
    def records(self) -> tuple[GovernedRecord | None, ...]:
        """Return the exact structural record set."""
        return (
            self.ethics_approval,
            self.risk_assessment,
            self.privacy_plan,
            self.consent_revision,
            self.data_license,
            self.device_calibration,
            self.stopping_rules_revision,
            self.reliability_protocol,
            self.independent_approval,
        )

    @property
    def ready_for_external_review(self) -> bool:
        """Return structural completeness without granting participant authority."""
        approvals = all(record and record.externally_approved for record in self.records)
        return self.participant_held_out_plan_registered and bool(approvals)

    def require_external_review_readiness(self) -> HumanReadiness:
        """Fail closed or return a non-authorizing external-review handoff."""
        if not self.ready_for_external_review:
            raise ValueError("human tier is not ready for external review")
        return HumanReadiness(
            ready_for_external_review=True,
            authorizes_participant_collection=False,
            next_gate="A human release decision outside this software remains required.",
        )
