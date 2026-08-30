"""Governed research artifact releases package."""

from __future__ import annotations

from src.affine_control.research_releases.generator import (
    build_authoritative_releases,
    generate_research_releases,
    render_releases_summary,
)
from src.affine_control.research_releases.validator import (
    ReleaseIntegrityError,
    compute_file_sha256,
    validate_release_package,
)
from src.affine_control.research_releases.vocabulary import (
    RELEASE_AUTHORITY_BOUNDARY,
    ExecutionReport,
    IndependentReviewRecord,
    ReleaseArtifact,
    ReleaseLevel,
    ResearchReleasePackage,
    UncertaintyBreakdown,
)

__all__ = [
    "ExecutionReport",
    "IndependentReviewRecord",
    "RELEASE_AUTHORITY_BOUNDARY",
    "ReleaseArtifact",
    "ReleaseIntegrityError",
    "ReleaseLevel",
    "ResearchReleasePackage",
    "UncertaintyBreakdown",
    "build_authoritative_releases",
    "compute_file_sha256",
    "generate_research_releases",
    "render_releases_summary",
    "validate_release_package",
]
