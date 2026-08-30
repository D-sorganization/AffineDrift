"""Standardized vocabulary and domain models for governed research artifact releases."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

RELEASE_AUTHORITY_BOUNDARY = (
    "Exploratory and computational research releases do not infer coaching, "
    "clinical, design, causal, or population authority."
)

SHA256_REGEX = re.compile(r"^[0-9a-f]{64}$")
GIT_COMMIT_REGEX = re.compile(r"^[0-9a-f]{40}$")


class ReleaseLevel(StrEnum):
    """Governed research release maturity tiers."""

    EXPLORATORY = "exploratory"
    INTERNALLY_REVIEWED = "internally_reviewed"
    INDEPENDENTLY_REVIEWED = "independently_reviewed"
    REPLICATED = "replicated"
    QUALIFIED = "qualified"


@dataclass(frozen=True)
class ReleaseArtifact:
    """An immutable, checksummed release artifact file."""

    path: str
    sha256: str
    byte_size: int
    kind: str
    description: str

    def __post_init__(self) -> None:
        """Validate Design by Contract preconditions."""
        if not self.path:
            raise ValueError("path must not be empty")
        if not SHA256_REGEX.match(self.sha256):
            raise ValueError(f"Invalid SHA-256 digest: {self.sha256}")
        if self.byte_size < 0:
            raise ValueError("byte_size must be non-negative")
        if not self.kind:
            raise ValueError("kind must not be empty")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "byte_size": self.byte_size,
            "description": self.description,
            "kind": self.kind,
            "path": self.path,
            "sha256": self.sha256,
        }


@dataclass(frozen=True)
class ExecutionReport:
    """Execution details for reproducible computational research."""

    command: str
    exit_code: int
    runtime_seconds: float
    outputs_produced: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate DbC preconditions."""
        if not self.command:
            raise ValueError("command must not be empty")
        if self.runtime_seconds < 0:
            raise ValueError("runtime_seconds must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "command": self.command,
            "exit_code": self.exit_code,
            "outputs_produced": list(self.outputs_produced),
            "runtime_seconds": self.runtime_seconds,
        }


@dataclass(frozen=True)
class UncertaintyBreakdown:
    """Explicit epistemological breakdown distinguishing measured, modeled, and assumed values."""

    measured_quantities: tuple[str, ...]
    modeled_quantities: tuple[str, ...]
    assumed_quantities: tuple[str, ...]
    unavailable_quantities: tuple[str, ...]
    known_limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "assumed_quantities": list(self.assumed_quantities),
            "known_limitations": list(self.known_limitations),
            "measured_quantities": list(self.measured_quantities),
            "modeled_quantities": list(self.modeled_quantities),
            "unavailable_quantities": list(self.unavailable_quantities),
        }


@dataclass(frozen=True)
class IndependentReviewRecord:
    """Governed independent review record with declared scope and conflict statement."""

    reviewer_id: str
    review_scope: str
    conflict_of_interest_statement: str
    disposition: str
    findings: tuple[str, ...]
    verification_commit: str

    def __post_init__(self) -> None:
        """Validate DbC preconditions."""
        if not self.reviewer_id:
            raise ValueError("reviewer_id must not be empty")
        if not self.review_scope:
            raise ValueError("review_scope must not be empty")
        if not self.conflict_of_interest_statement:
            raise ValueError("conflict_of_interest_statement must not be empty")
        valid_dispositions = ("approved", "conditional", "rejected", "pending")
        if self.disposition not in valid_dispositions:
            raise ValueError(f"Invalid disposition: {self.disposition}")
        if not GIT_COMMIT_REGEX.match(self.verification_commit):
            raise ValueError(f"Invalid verification git commit: {self.verification_commit}")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "conflict_of_interest_statement": self.conflict_of_interest_statement,
            "disposition": self.disposition,
            "findings": list(self.findings),
            "review_scope": self.review_scope,
            "reviewer_id": self.reviewer_id,
            "verification_commit": self.verification_commit,
        }


@dataclass(frozen=True)
class ResearchReleasePackage:
    """A complete governed research release package."""

    release_id: str
    release_level: str
    title: str
    protocol_id: str
    git_commit: str
    repository_url: str
    environment_pins: dict[str, str]
    license: str
    artifacts: tuple[ReleaseArtifact, ...]
    analysis_execution: ExecutionReport
    uncertainty_and_limitations: UncertaintyBreakdown
    independent_review: IndependentReviewRecord
    authority_boundary: str
    released_on: str

    def __post_init__(self) -> None:
        """Validate DbC preconditions."""
        if not self.release_id:
            raise ValueError("release_id must not be empty")
        if not self.title:
            raise ValueError("title must not be empty")
        if not self.protocol_id:
            raise ValueError("protocol_id must not be empty")
        if not GIT_COMMIT_REGEX.match(self.git_commit):
            raise ValueError(f"Invalid git commit: {self.git_commit}")
        if not self.artifacts:
            raise ValueError("artifacts must contain at least one entry")

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "analysis_execution": self.analysis_execution.to_dict(),
            "artifacts": [a.to_dict() for a in self.artifacts],
            "authority_boundary": self.authority_boundary,
            "independent_review": self.independent_review.to_dict(),
            "protocol_id": self.protocol_id,
            "provenance": {
                "environment_pins": self.environment_pins,
                "git_commit": self.git_commit,
                "license": self.license,
                "repository_url": self.repository_url,
            },
            "release_id": self.release_id,
            "release_level": self.release_level,
            "released_on": self.released_on,
            "schema_version": "affinedrift.research-artifact-release/v1",
            "title": self.title,
            "uncertainty_and_limitations": self.uncertainty_and_limitations.to_dict(),
        }
