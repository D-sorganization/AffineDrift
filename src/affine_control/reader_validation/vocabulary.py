"""Standardized vocabulary and immutable view-model definitions for reader validation studies."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

STUDY_AUTHORITY_BOUNDARY = (
    "Validates interface findability and comprehension only, never biomechanical, "
    "software-correctness, coaching, clinical, or population claims."
)


class StudyCohort(StrEnum):
    """Preregistered participant cohorts for reader comprehension testing."""

    TECHNICAL_REVIEWER = "technical_reviewer"
    GENERAL_READER = "general_reader"


@dataclass(frozen=True)
class ValidationTask:
    """Definition of one preregistered findability or comprehension task."""

    task_id: str
    task_number: int
    title: str
    description: str
    expected_target: str
    success_criterion: str

    def __post_init__(self) -> None:
        """Validate Design by Contract preconditions."""
        if not self.task_id:
            raise ValueError("task_id must not be empty")
        if not 1 <= self.task_number <= 6:
            raise ValueError("task_number must be between 1 and 6")
        if not self.title:
            raise ValueError("title must not be empty")
        if not self.description:
            raise ValueError("description must not be empty")
        if not self.expected_target:
            raise ValueError("expected_target must not be empty")
        if not self.success_criterion:
            raise ValueError("success_criterion must not be empty")

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "description": self.description,
            "expected_target": self.expected_target,
            "success_criterion": self.success_criterion,
            "task_id": self.task_id,
            "task_number": self.task_number,
            "title": self.title,
        }


STANDARDIZED_TASKS: tuple[ValidationTask, ...] = (
    ValidationTask(
        task_id="task-1-find-monograph",
        task_number=1,
        title="Find Proximal-Distal Monograph",
        description="Navigate from home or resources to the 35-chapter technical monograph.",
        expected_target="/articles/proximal_distal_energy_transfer/index.html",
        success_criterion="Reader lands on canonical monograph entry point within 90 seconds.",
    ),
    ValidationTask(
        task_id="task-2-identify-evidence-state",
        task_number=2,
        title="Identify Evidence State & Negative Scope",
        description="Identify the evidence state badge and state what is not established.",
        expected_target="Evidence state card and badge on monograph route",
        success_criterion="Reader identifies simulation tier and quotes authority boundary note.",
    ),
    ValidationTask(
        task_id="task-3-locate-provider-record",
        task_number=3,
        title="Locate Provider Record & Commit SHA",
        description="Locate the exact upstream provider record and pinned source commit SHA.",
        expected_target="/models/programming/provenance.html or provider link",
        success_criterion="Reader identifies exact commit SHA and SHA-256 manifest hash.",
    ),
    ValidationTask(
        task_id="task-4-explain-limitation",
        task_number=4,
        title="Explain Limitation or Falsifier",
        description="Explain at least one governed limitation or falsification condition.",
        expected_target="Limitations and does-not-establish sections",
        success_criterion="Reader names model boundary without claiming general human validity.",
    ),
    ValidationTask(
        task_id="task-5-inspect-program-workflow",
        task_number=5,
        title="Inspect Program and Workflow Artifact",
        description="Find a computational program or workflow and inspect an artifact.",
        expected_target="/models/programming/programs.html or workflows.html",
        success_criterion="Reader inspects execution parameters, exit codes, and outputs.",
    ),
    ValidationTask(
        task_id="task-6-distinguish-model-output",
        task_number=6,
        title="Distinguish Model Output from Participant Evidence",
        description="Demonstrate comprehension that simulation results are not human trials.",
        expected_target="Research readiness library and evidence badges",
        success_criterion="Reader accurately categorizes synthetic runs vs clinical trials.",
    ),
)


@dataclass(frozen=True)
class ParticipantObservation:
    """One privacy-minimized participant task observation record."""

    participant_id: str
    cohort: str
    task_id: str
    completed: bool
    duration_ms: float
    navigation_errors: int
    comprehension_score: float
    confidence_score: int
    accessibility_barriers: tuple[str, ...]
    reported_limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate DbC preconditions."""
        if not self.participant_id:
            raise ValueError("participant_id must not be empty")
        valid_cohorts = (
            StudyCohort.TECHNICAL_REVIEWER.value,
            StudyCohort.GENERAL_READER.value,
        )
        if self.cohort not in valid_cohorts:
            raise ValueError(f"Invalid cohort: {self.cohort}")
        if not self.task_id:
            raise ValueError("task_id must not be empty")
        if self.duration_ms < 0:
            raise ValueError("duration_ms must be non-negative")
        if self.navigation_errors < 0:
            raise ValueError("navigation_errors must be non-negative")
        if not 0.0 <= self.comprehension_score <= 1.0:
            raise ValueError("comprehension_score must be between 0.0 and 1.0")
        if not 1 <= self.confidence_score <= 5:
            raise ValueError("confidence_score must be between 1 and 5")

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "accessibility_barriers": list(self.accessibility_barriers),
            "cohort": self.cohort,
            "completed": self.completed,
            "comprehension_score": self.comprehension_score,
            "confidence_score": self.confidence_score,
            "duration_ms": self.duration_ms,
            "navigation_errors": self.navigation_errors,
            "participant_id": self.participant_id,
            "reported_limitations": list(self.reported_limitations),
            "task_id": self.task_id,
        }


@dataclass(frozen=True)
class NullFinding:
    """Preserved null or negative finding from reader comprehension testing."""

    finding_id: str
    description: str
    observed_effect: str
    implication: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "description": self.description,
            "finding_id": self.finding_id,
            "implication": self.implication,
            "observed_effect": self.observed_effect,
        }


@dataclass(frozen=True)
class RemediationIssue:
    """Tracked interface remediation issue resulting from observed task failures."""

    issue_id: str
    title: str
    task_id: str
    status: str
    target_issue_url: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "issue_id": self.issue_id,
            "status": self.status,
            "target_issue_url": self.target_issue_url,
            "task_id": self.task_id,
            "title": self.title,
        }
