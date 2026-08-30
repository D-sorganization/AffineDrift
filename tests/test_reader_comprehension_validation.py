"""Comprehensive TDD test suite for reader findability and evidence comprehension validation."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from src.affine_control.reader_validation.evaluator import (
    calculate_wilson_score_interval,
    evaluate_study_metrics,
)
from src.affine_control.reader_validation.generator import (
    build_reader_validation_study,
    generate_reader_validation_study,
    get_authoritative_null_findings,
    get_authoritative_observations,
    get_authoritative_remediation_issues,
)
from src.affine_control.reader_validation.vocabulary import (
    STANDARDIZED_TASKS,
    STUDY_AUTHORITY_BOUNDARY,
    ParticipantObservation,
    StudyCohort,
    ValidationTask,
)


def test_task_definition_invariants() -> None:
    """Verify ValidationTask adheres to Design by Contract preconditions."""
    task = ValidationTask(
        task_id="task-1-find-monograph",
        task_number=1,
        title="Find Monograph",
        description="Find monograph path",
        expected_target="/articles/proximal_distal_energy_transfer/index.html",
        success_criterion="Lands within 90s",
    )
    assert task.task_number == 1
    assert task.to_dict()["task_id"] == "task-1-find-monograph"

    # Rejects invalid task number
    with pytest.raises(ValueError, match="task_number must be between 1 and 6"):
        ValidationTask(
            task_id="invalid",
            task_number=7,
            title="T",
            description="D",
            expected_target="E",
            success_criterion="S",
        )

    # Rejects empty title
    with pytest.raises(ValueError, match="title must not be empty"):
        ValidationTask(
            task_id="t",
            task_number=1,
            title="",
            description="D",
            expected_target="E",
            success_criterion="S",
        )


def test_standardized_task_coverage() -> None:
    """Verify all 6 required tasks exist with distinct numbers."""
    assert len(STANDARDIZED_TASKS) == 6
    task_numbers = [t.task_number for t in STANDARDIZED_TASKS]
    assert task_numbers == [1, 2, 3, 4, 5, 6]


def test_participant_observation_dbc() -> None:
    """Verify ParticipantObservation contract invariants."""
    obs = ParticipantObservation(
        participant_id="P-01",
        cohort=StudyCohort.TECHNICAL_REVIEWER.value,
        task_id="task-1-find-monograph",
        completed=True,
        duration_ms=12000.0,
        navigation_errors=0,
        comprehension_score=1.0,
        confidence_score=5,
        accessibility_barriers=(),
        reported_limitations=("Clear navigation",),
    )
    assert obs.completed is True
    assert obs.to_dict()["cohort"] == "technical_reviewer"

    # Rejects invalid cohort
    with pytest.raises(ValueError, match="Invalid cohort"):
        ParticipantObservation(
            participant_id="P-01",
            cohort="unauthorized_cohort",
            task_id="task-1",
            completed=True,
            duration_ms=100.0,
            navigation_errors=0,
            comprehension_score=1.0,
            confidence_score=5,
            accessibility_barriers=(),
            reported_limitations=(),
        )

    # Rejects negative duration
    with pytest.raises(ValueError, match="duration_ms must be non-negative"):
        ParticipantObservation(
            participant_id="P-01",
            cohort=StudyCohort.GENERAL_READER.value,
            task_id="task-1",
            completed=True,
            duration_ms=-5.0,
            navigation_errors=0,
            comprehension_score=1.0,
            confidence_score=5,
            accessibility_barriers=(),
            reported_limitations=(),
        )


def test_wilson_score_interval() -> None:
    """Verify exact Wilson score interval calculation for proportions."""
    lower, upper = calculate_wilson_score_interval(10, 10)
    assert lower > 0.69
    assert upper == 1.0

    lower, upper = calculate_wilson_score_interval(0, 10)
    assert lower == 0.0
    assert upper < 0.31

    with pytest.raises(ValueError, match="successes must be between 0 and total"):
        calculate_wilson_score_interval(15, 10)


def test_cohort_and_task_metrics_evaluation() -> None:
    """Verify metric aggregations across cohorts and tasks."""
    observations = get_authoritative_observations()
    metrics = evaluate_study_metrics(observations)

    assert metrics["total_participants"] == 24
    assert metrics["overall_completion_rate"] > 0.90
    assert metrics["overall_comprehension_rate"] > 0.85

    tr_metrics = metrics["cohort_metrics"][StudyCohort.TECHNICAL_REVIEWER.value]
    gr_metrics = metrics["cohort_metrics"][StudyCohort.GENERAL_READER.value]

    assert tr_metrics["participant_count"] == 12
    assert gr_metrics["participant_count"] == 12
    assert tr_metrics["completion_rate"] == 1.0
    assert gr_metrics["completion_rate"] >= 0.95


def test_null_findings_and_remediations() -> None:
    """Verify preservation of null findings and remediation mapping."""
    null_findings = get_authoritative_null_findings()
    assert len(null_findings) >= 2
    assert any(
        "general_reader" in f.finding_id or "general-reader" in f.finding_id for f in null_findings
    )

    remediations = get_authoritative_remediation_issues()
    assert len(remediations) >= 2
    for r in remediations:
        assert r.target_issue_url.startswith("https://github.com/D-sorganization/")


def test_full_study_generation_and_schema_validation(tmp_path: Path) -> None:
    """Verify live repository generation and schema conformance."""
    repo_root = Path(__file__).resolve().parent.parent
    study_dict, metrics = build_reader_validation_study(repo_root)

    assert study_dict["schema_version"] == "affinedrift.reader-comprehension-study/v1"
    assert study_dict["authority_boundary"] == STUDY_AUTHORITY_BOUNDARY

    schema_file = repo_root / "schemas/reader-comprehension-study-v1.schema.json"
    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    jsonschema.validate(instance=study_dict, schema=schema)

    # Test file generation
    data_path, part_path = generate_reader_validation_study(check=False, repo_root=repo_root)
    assert data_path.is_file()
    assert part_path.is_file()

    # Test check mode passes
    generate_reader_validation_study(check=True, repo_root=repo_root)
