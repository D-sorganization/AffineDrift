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

_EVIDENCE_TIERS = (
    "effective-mechanical",
    "model-partitioned",
    "emg-proxy",
    "unavailable",
)
_OUTCOMES = ("supported", "negative", "null", "unavailable")
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

    def __post_init__(self) -> None:
        """Reject contradictory or over-authoritative result records."""
        _require_text(self.quantity, "result quantity")
        _require_text(self.unit, "result unit")
        _require_text(self.interpretation, "result interpretation")
        if self.evidence_tier not in _EVIDENCE_TIERS or self.outcome not in _OUTCOMES:
            raise ValueError("evidence tier and outcome must be declared")
        if any(phrase in self.interpretation.lower() for phrase in _AUTHORITY_PHRASES):
            raise ValueError("interpretation exceeds the authority boundary")
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


@dataclass(frozen=True)
class HumanStudyGate:
    """Governance, safety, and validation gates required before human work."""

    ethics_approval: str | None
    risk_assessment: str | None
    privacy_plan: str | None
    consent_revision: str | None
    data_license: str | None
    device_calibration: str | None
    stopping_rules_revision: str | None
    reliability_protocol: str | None
    participant_held_out: bool

    @property
    def eligible(self) -> bool:
        """Return true only when every required governed record exists."""
        records = (
            self.ethics_approval,
            self.risk_assessment,
            self.privacy_plan,
            self.consent_revision,
            self.data_license,
            self.device_calibration,
            self.stopping_rules_revision,
            self.reliability_protocol,
        )
        return self.participant_held_out and all(value and value.strip() for value in records)

    def authorize(self) -> bool:
        """Fail closed until the complete human tier is governed and validated."""
        if not self.eligible:
            raise ValueError("human tier is unavailable until every gate is satisfied")
        return True
