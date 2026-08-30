"""Reader validation and comprehension study package."""

from __future__ import annotations

from src.affine_control.reader_validation.evaluator import (
    calculate_wilson_score_interval,
    evaluate_cohort_metrics,
    evaluate_study_metrics,
    evaluate_task_metrics,
)
from src.affine_control.reader_validation.generator import (
    build_reader_validation_study,
    generate_reader_validation_study,
    render_reader_validation_summary,
)
from src.affine_control.reader_validation.vocabulary import (
    STANDARDIZED_TASKS,
    STUDY_AUTHORITY_BOUNDARY,
    NullFinding,
    ParticipantObservation,
    RemediationIssue,
    StudyCohort,
    ValidationTask,
)

__all__ = [
    "NullFinding",
    "ParticipantObservation",
    "RemediationIssue",
    "STANDARDIZED_TASKS",
    "STUDY_AUTHORITY_BOUNDARY",
    "StudyCohort",
    "ValidationTask",
    "build_reader_validation_study",
    "calculate_wilson_score_interval",
    "evaluate_cohort_metrics",
    "evaluate_study_metrics",
    "evaluate_task_metrics",
    "generate_reader_validation_study",
    "render_reader_validation_summary",
]
