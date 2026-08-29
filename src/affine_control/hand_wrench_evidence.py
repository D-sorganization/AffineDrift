"""Evidence and promotion boundaries for bilateral hand-wrench results."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Literal

Outcome = Literal["supported", "negative", "null", "unavailable"]
LoadTier = Literal[
    "total-measured",
    "bilateral-measured",
    "model-estimated",
    "unavailable",
]

_OUTCOMES = ("supported", "negative", "null", "unavailable")
_LOAD_TIERS = ("total-measured", "bilateral-measured", "model-estimated", "unavailable")
_AUTHORITY_PHRASES = ("muscle", "coaching", "clinical", "diagnosis", "treatment")


def _require_text(value: str, label: str) -> None:
    """Reject a blank declaration."""
    if not value.strip():
        raise ValueError(f"{label} must be declared")


@dataclass(frozen=True)
class LoadResult:
    """One source-labeled result with uncertainty and sensitivity provenance."""

    quantity: str
    load_tier: LoadTier
    estimate: float | None
    uncertainty_interval: tuple[float, float] | None
    unit: str
    outcome: Outcome
    sensitivity_parameters: tuple[str, ...]
    interpretation: str

    def __post_init__(self) -> None:
        """Keep unavailable and adverse results explicit and non-authoritative."""
        _require_text(self.quantity, "result quantity")
        _require_text(self.unit, "result unit")
        _require_text(self.interpretation, "result interpretation")
        if self.load_tier not in _LOAD_TIERS or self.outcome not in _OUTCOMES:
            raise ValueError("load tier and outcome must be declared")
        if any(phrase in self.interpretation.lower() for phrase in _AUTHORITY_PHRASES):
            raise ValueError("interpretation exceeds the authority boundary")
        if self.load_tier == "unavailable" or self.outcome == "unavailable":
            self._validate_unavailable()
            return
        self._validate_available()

    def _validate_unavailable(self) -> None:
        """Require unavailable tier, outcome, and missing values to agree."""
        if self.load_tier != "unavailable" or self.outcome != "unavailable":
            raise ValueError("unavailable tier and outcome must agree")
        if self.estimate is not None or self.uncertainty_interval is not None:
            raise ValueError("unavailable results cannot contain estimates")

    def _validate_available(self) -> None:
        """Require finite estimates, complete uncertainty, and sensitivities."""
        if self.estimate is None or self.uncertainty_interval is None:
            raise ValueError("available results require an estimate and uncertainty")
        lower, upper = self.uncertainty_interval
        values = (self.estimate, lower, upper)
        if not all(isfinite(value) for value in values) or not lower <= self.estimate <= upper:
            raise ValueError("uncertainty must be finite, ordered, and contain the estimate")
        if not self.sensitivity_parameters or any(
            not value.strip() for value in self.sensitivity_parameters
        ):
            raise ValueError("sensitivity parameters must be declared")


@dataclass(frozen=True)
class HumanTierGate:
    """Governance gates required before participant data may be analyzed."""

    ethics_approval: str | None
    privacy_plan: str | None
    consent_revision: str | None
    data_license: str | None
    participant_held_out: bool

    @property
    def eligible(self) -> bool:
        """Return true only when every human-governance declaration exists."""
        records = (
            self.ethics_approval,
            self.privacy_plan,
            self.consent_revision,
            self.data_license,
        )
        return self.participant_held_out and all(value and value.strip() for value in records)

    def authorize(self) -> bool:
        """Fail closed when any human-governance record is absent."""
        if not self.eligible:
            raise ValueError("human tier is unavailable until every governance gate is satisfied")
        return True
