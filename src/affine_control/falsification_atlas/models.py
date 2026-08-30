"""Typed view models for the governed falsification atlas."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AtlasPaths:
    """Locate every canonical authority and generated atlas artifact."""

    root: Path
    mapping: Path
    schema: Path
    claims: Path
    critiques: Path
    source_manifest: Path
    readiness: Path
    output: Path


@dataclass(frozen=True)
class AtlasRecord:
    """Expose one editorial question with authority-derived scientific state."""

    atlas_id: str
    theme: str
    title: str
    claim_id: str
    claim: str
    evidence_state: str
    uncertainty: str
    falsifier: str
    model_domain: str
    critique_id: str
    critique_state: str
    critique_source_path: str
    readiness_protocol_id: str
    readiness_title: str
    readiness_state: str
    readiness_evidence_origin: str
    validation_release_state: str
    validation_release_next_gate: str
    critique_question: str
    alternative_mechanism: str
    discriminating_measurement: str
    chapter_path: str
    chapter_anchor: str
    workflow_state: str
    workflow_reason: str
    provider_record_url: str | None
    evidence_artifacts: tuple[str, ...]


@dataclass(frozen=True)
class AtlasIndexes:
    """Hold identifier indexes for all joined scientific authorities."""

    claims: dict[str, dict[str, Any]]
    critiques: dict[str, dict[str, Any]]
    readiness: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class AtlasDocument:
    """Collect the exact source authority and ordered public atlas records."""

    schema_version: str
    provider_state: str
    provider_reason: str
    provider_tracking_issue: str
    source_repository: str
    source_commit: str
    source_root: str
    records: tuple[AtlasRecord, ...]
