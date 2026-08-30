"""Standardized presentation vocabulary and view-model types for reader-facing evidence states."""

from __future__ import annotations

import html
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

AUTHORITY_BOUNDARY_STATEMENT = (
    "Presentation cannot promote a claim or infer human, coaching, clinical, "
    "equipment, design, causal, or population authority."
)


class EvidenceTier(StrEnum):
    """Deterministic hierarchy of evidence presentation tiers."""

    MATHEMATICAL_IDENTITY = "mathematical_identity"
    MANUFACTURED_SYNTHETIC = "manufactured_synthetic"
    QUALIFIED_SIMULATION = "qualified_simulation"
    PILOT_BOUNDED = "pilot_bounded"
    GOVERNED_DATASET = "governed_dataset"
    COLLECTING_LOCKED = "collecting_locked"
    VALIDATED_EVIDENCE = "validated_evidence"
    PUBLISHED_CLAIM = "published_claim"
    SUPERSEDED_REVOKED = "superseded_revoked"


TIER_DISPLAY_NAMES: dict[EvidenceTier, str] = {
    EvidenceTier.MATHEMATICAL_IDENTITY: "Mathematical Identity",
    EvidenceTier.MANUFACTURED_SYNTHETIC: "Manufactured Synthetic",
    EvidenceTier.QUALIFIED_SIMULATION: "Qualified Simulation",
    EvidenceTier.PILOT_BOUNDED: "Pilot-Bounded Readiness",
    EvidenceTier.GOVERNED_DATASET: "Governed Dataset / Protocol",
    EvidenceTier.COLLECTING_LOCKED: "Collection / Analysis Locked",
    EvidenceTier.VALIDATED_EVIDENCE: "Validated Empirical Evidence",
    EvidenceTier.PUBLISHED_CLAIM: "Published Governed Claim",
    EvidenceTier.SUPERSEDED_REVOKED: "Superseded / Revoked",
}

TIER_BADGE_CLASSES: dict[EvidenceTier, str] = {
    EvidenceTier.MATHEMATICAL_IDENTITY: "badge-math-identity",
    EvidenceTier.MANUFACTURED_SYNTHETIC: "badge-manufactured-synthetic",
    EvidenceTier.QUALIFIED_SIMULATION: "badge-qualified-simulation",
    EvidenceTier.PILOT_BOUNDED: "badge-pilot-bounded",
    EvidenceTier.GOVERNED_DATASET: "badge-governed-dataset",
    EvidenceTier.COLLECTING_LOCKED: "badge-collecting-locked",
    EvidenceTier.VALIDATED_EVIDENCE: "badge-validated-evidence",
    EvidenceTier.PUBLISHED_CLAIM: "badge-published-claim",
    EvidenceTier.SUPERSEDED_REVOKED: "badge-superseded-revoked",
}


@dataclass(frozen=True)
class EvidencePresentationViewModel:
    """Immutable view-model consumed by reader-facing templates and UI components.

    Enforces the Law of Demeter: templates consume only these flat, strongly-typed
    fields and cannot query or mutate nested internal registry state.
    """

    entity_id: str
    title: str
    kind: str
    tier: str
    state_label: str
    state_badge_class: str
    establishes: tuple[str, ...]
    does_not_establish: tuple[str, ...]
    limitations: tuple[str, ...]
    next_gate: str
    source_revision: str
    evidence_origin: str
    authority_boundary: str
    accessible_label: str
    source_url: str = ""

    def __post_init__(self) -> None:
        """Validate DbC invariants."""
        if not self.entity_id:
            raise ValueError("entity_id must not be empty")
        if not self.title:
            raise ValueError("title must not be empty")
        if not self.establishes:
            raise ValueError("establishes must contain at least one item")
        if not self.does_not_establish:
            raise ValueError("does_not_establish must contain at least one item")
        if not self.limitations:
            raise ValueError("limitations must contain at least one item")
        if not self.next_gate:
            raise ValueError("next_gate must not be empty")
        if not self.source_revision:
            raise ValueError("source_revision must not be empty")
        if not self.authority_boundary:
            raise ValueError("authority_boundary must not be empty")
        if not self.accessible_label:
            raise ValueError("accessible_label must not be empty")

    def to_dict(self) -> dict[str, Any]:
        """Convert view model to a JSON-serializable dictionary."""
        data: dict[str, Any] = {
            "accessible_label": self.accessible_label,
            "authority_boundary": self.authority_boundary,
            "does_not_establish": list(self.does_not_establish),
            "entity_id": self.entity_id,
            "establishes": list(self.establishes),
            "evidence_origin": self.evidence_origin,
            "kind": self.kind,
            "limitations": list(self.limitations),
            "next_gate": self.next_gate,
            "source_revision": self.source_revision,
            "state_badge_class": self.state_badge_class,
            "state_label": self.state_label,
            "tier": self.tier,
            "title": self.title,
        }
        if self.source_url:
            data["source_url"] = self.source_url
        return data

    @property
    def escaped_title(self) -> str:
        """HTML-escaped title for safe template rendering."""
        return html.escape(self.title, quote=True)

    @property
    def escaped_state_label(self) -> str:
        """HTML-escaped state label."""
        return html.escape(self.state_label, quote=True)
