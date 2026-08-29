"""Typed path and option bundles for scientific claim-audit tooling."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AuditSources:
    """Paths to the schema and upstream authority documents."""

    schema: Path
    claims: Path
    ledger: Path
    root: Path


@dataclass(frozen=True)
class ReportTargets:
    """Paths for deterministic generated reports."""

    json: Path
    markdown: Path


@dataclass(frozen=True)
class GenerationOptions:
    """Optional generation and publication-validation controls."""

    manifest: Path | None = None
    check: bool = False
    enforce: bool = False
