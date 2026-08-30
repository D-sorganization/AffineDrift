"""Pure functional statistical evaluation for reader validation studies."""

from __future__ import annotations

import math
import statistics
from collections.abc import Sequence
from typing import Any

from src.affine_control.reader_validation.vocabulary import (
    STANDARDIZED_TASKS,
    ParticipantObservation,
    StudyCohort,
)


def calculate_wilson_score_interval(
    successes: int, total: int, confidence: float = 0.95
) -> tuple[float, float]:
    """Calculate Wilson score interval for a binomial proportion."""
    if total == 0:
        return (0.0, 0.0)
    if successes < 0 or successes > total:
        raise ValueError("successes must be between 0 and total")

    # z-value for confidence (default 1.96 for 95%)
    z = 1.959963984540054 if confidence == 0.95 else 1.6448536269514722
    p_hat = successes / total
    z2 = z * z
    n = total

    denominator = 1.0 + z2 / n
    center_adj = p_hat + z2 / (2.0 * n)
    spread = z * math.sqrt((p_hat * (1.0 - p_hat) + z2 / (4.0 * n)) / n)

    lower = max(0.0, (center_adj - spread) / denominator)
    upper = min(1.0, (center_adj + spread) / denominator)
    return (round(lower, 4), round(upper, 4))


def evaluate_cohort_metrics(
    observations: Sequence[ParticipantObservation], cohort: str
) -> dict[str, Any]:
    """Compute statistical summary metrics for a specific participant cohort."""
    cohort_obs = [o for o in observations if o.cohort == cohort]
    if not cohort_obs:
        return {
            "completion_ci_95": [0.0, 0.0],
            "completion_rate": 0.0,
            "error_rate_per_task": 0.0,
            "mean_comprehension_score": 0.0,
            "median_duration_ms": 0.0,
            "participant_count": 0,
        }

    total_tasks = len(cohort_obs)
    completed_tasks = sum(1 for o in cohort_obs if o.completed)
    completion_rate = round(completed_tasks / total_tasks, 4)
    completion_ci = calculate_wilson_score_interval(completed_tasks, total_tasks)

    mean_comp = round(statistics.mean(o.comprehension_score for o in cohort_obs), 4)
    durations = [o.duration_ms for o in cohort_obs]
    median_dur = round(float(statistics.median(durations)), 1)
    total_errors = sum(o.navigation_errors for o in cohort_obs)
    err_rate = round(total_errors / total_tasks, 4)

    # Distinct participants
    pids = {o.participant_id for o in cohort_obs}

    return {
        "completion_ci_95": list(completion_ci),
        "completion_rate": completion_rate,
        "error_rate_per_task": err_rate,
        "mean_comprehension_score": mean_comp,
        "median_duration_ms": median_dur,
        "participant_count": len(pids),
    }


def evaluate_task_metrics(
    observations: Sequence[ParticipantObservation], task_id: str, task_number: int
) -> dict[str, Any]:
    """Compute metrics for a single standardized task across all cohorts."""
    task_obs = [o for o in observations if o.task_id == task_id]
    if not task_obs:
        return {
            "completion_rate": 0.0,
            "mean_comprehension_score": 0.0,
            "median_duration_ms": 0.0,
            "task_number": task_number,
            "total_errors": 0,
        }

    total = len(task_obs)
    completed = sum(1 for o in task_obs if o.completed)
    comp_rate = round(completed / total, 4)
    mean_comp = round(statistics.mean(o.comprehension_score for o in task_obs), 4)
    durations = [o.duration_ms for o in task_obs]
    median_dur = round(float(statistics.median(durations)), 1)
    total_errors = sum(o.navigation_errors for o in task_obs)

    return {
        "completion_rate": comp_rate,
        "mean_comprehension_score": mean_comp,
        "median_duration_ms": median_dur,
        "task_number": task_number,
        "total_errors": total_errors,
    }


def evaluate_study_metrics(
    observations: Sequence[ParticipantObservation],
) -> dict[str, Any]:
    """Compute the full study metrics dictionary from observations."""
    if not observations:
        raise ValueError("Cannot evaluate study metrics from empty observations list")

    pids = {o.participant_id for o in observations}
    cohort_metrics: dict[str, Any] = {
        StudyCohort.TECHNICAL_REVIEWER.value: evaluate_cohort_metrics(
            observations, StudyCohort.TECHNICAL_REVIEWER.value
        ),
        StudyCohort.GENERAL_READER.value: evaluate_cohort_metrics(
            observations, StudyCohort.GENERAL_READER.value
        ),
    }

    task_metrics: dict[str, Any] = {}
    for task in STANDARDIZED_TASKS:
        task_metrics[task.task_id] = evaluate_task_metrics(
            observations, task.task_id, task.task_number
        )

    total_tasks = len(observations)
    total_completed = sum(1 for o in observations if o.completed)
    overall_completion = round(total_completed / total_tasks, 4)
    overall_comp_score = round(statistics.mean(o.comprehension_score for o in observations), 4)

    return {
        "cohort_metrics": cohort_metrics,
        "overall_completion_rate": overall_completion,
        "overall_comprehension_rate": overall_comp_score,
        "task_metrics": task_metrics,
        "total_participants": len(pids),
    }
