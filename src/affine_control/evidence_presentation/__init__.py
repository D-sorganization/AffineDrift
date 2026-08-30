"""Reader-facing evidence state presentation package."""

from __future__ import annotations

from src.affine_control.evidence_presentation.projector import (
    project_claim,
    project_companion_entity,
    project_protocol,
)
from src.affine_control.evidence_presentation.renderer import (
    render_evidence_badge,
    render_evidence_card,
    render_evidence_table,
)
from src.affine_control.evidence_presentation.vocabulary import (
    AUTHORITY_BOUNDARY_STATEMENT,
    TIER_BADGE_CLASSES,
    TIER_DISPLAY_NAMES,
    EvidencePresentationViewModel,
    EvidenceTier,
)

__all__ = [
    "AUTHORITY_BOUNDARY_STATEMENT",
    "EvidencePresentationViewModel",
    "EvidenceTier",
    "TIER_BADGE_CLASSES",
    "TIER_DISPLAY_NAMES",
    "project_claim",
    "project_companion_entity",
    "project_protocol",
    "render_evidence_badge",
    "render_evidence_card",
    "render_evidence_table",
]
