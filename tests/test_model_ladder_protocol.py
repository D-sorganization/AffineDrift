"""Contracts for the bounded planar-to-flexible-shaft model ladder."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.affine_control.model_ladder_protocol import (
    COMPARISON_CATEGORIES,
    LEVEL_IDS,
    TaskAssessment,
    adjacent_projection_residuals,
    build_model_ladder_protocol,
    manufactured_comparison_observations,
    manufactured_convergence_fixture,
    manufactured_parity_fixture,
    manufactured_task_assessments,
    minimum_sufficient_level,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTICLE = REPO_ROOT / "models" / "model-ladder.qmd"
MODELS_HUB = REPO_ROOT / "models" / "models.qmd"


def test_ladder_freezes_four_nested_levels_and_interpretation_boundaries() -> None:
    protocol = build_model_ladder_protocol()

    assert tuple(level.level_id for level in protocol.levels) == LEVEL_IDS
    assert tuple(level.parent_id for level in protocol.levels) == (
        None,
        "planar-rigid",
        "spatial-open-chain",
        "spatial-closed-chain",
    )
    assert all(level.frame and level.parameter_revision for level in protocol.levels)
    assert all(level.initialization and level.event_definition for level in protocol.levels)
    assert all(level.included_physics for level in protocol.levels)
    assert all(level.omitted_physics for level in protocol.levels)
    assert all(level.intended_uses for level in protocol.levels)
    assert protocol.data_classification == "synthetic; no participant data"
    assert protocol.source_revision == "affinedrift.model-ladder/v1"
    assert protocol.license == "MIT"


def test_adjacent_projection_maps_have_exact_manufactured_parity() -> None:
    protocol = build_model_ladder_protocol()
    fixture = manufactured_parity_fixture()

    assert adjacent_projection_residuals(protocol, fixture) == {
        "spatial-open-chain->planar-rigid": 0.0,
        "spatial-closed-chain->spatial-open-chain": 0.0,
        "flexible-shaft->spatial-closed-chain": 0.0,
    }


def test_flexible_shaft_manufactured_fixture_has_declared_convergence() -> None:
    fixture = manufactured_convergence_fixture()
    errors = tuple(sample.impact_speed_error for sample in fixture)

    assert tuple(sample.mode_count for sample in fixture) == (1, 2, 4, 8)
    assert errors == pytest.approx((0.08, 0.02, 0.005, 0.00125))
    adjacent_errors = zip(errors, errors[1:], strict=False)
    assert all(later < earlier for earlier, later in adjacent_errors)
    convergence_ratios = zip(errors, errors[1:], strict=False)
    assert all(later / earlier == pytest.approx(0.25) for earlier, later in convergence_ratios)


def test_comparison_fixture_covers_every_level_and_task_specific_output() -> None:
    observations = manufactured_comparison_observations()

    for level_id in LEVEL_IDS:
        categories = {
            observation.category for observation in observations if observation.level_id == level_id
        }
        assert categories == set(COMPARISON_CATEGORIES)

    runtime = [row for row in observations if row.category == "runtime"]
    assert all(row.estimate is None for row in runtime)
    assert all(row.evidence_status == "unavailable" for row in runtime)
    assert all(row.outcome == "unavailable" for row in runtime)
    assert all(
        row.uncertainty_interval is not None for row in observations if row.estimate is not None
    )


@pytest.mark.parametrize(
    ("task_id", "expected_level"),
    (
        ("planar-path", "planar-rigid"),
        ("three-dimensional-face", "spatial-open-chain"),
        ("bilateral-load-share", "spatial-closed-chain"),
        ("shaft-deflection-at-impact", "flexible-shaft"),
        ("participant-transfer", None),
    ),
)
def test_selection_returns_minimum_sufficient_level_or_preserves_failure(
    task_id: str,
    expected_level: str | None,
) -> None:
    protocol = build_model_ladder_protocol()
    assessments = manufactured_task_assessments()

    selected = minimum_sufficient_level(protocol, assessments, task_id)

    assert selected == expected_level


def test_task_assessment_rejects_global_percentage_and_authority_overreach() -> None:
    common = {
        "task_id": "test",
        "level_id": "planar-rigid",
        "metric_name": "path error",
        "unit": "rad",
        "estimate": 0.01,
        "uncertainty_interval": (0.0, 0.02),
        "tolerance": 0.03,
        "evidence_status": "modeled",
        "outcome": "supported",
        "sufficient": True,
    }

    with pytest.raises(ValueError, match="global fidelity"):
        TaskAssessment(**common, interpretation="A global fidelity percentage.")
    with pytest.raises(ValueError, match="authority boundary"):
        TaskAssessment(**common, interpretation="A coaching prescription for all golfers.")


def test_null_negative_and_unavailable_results_remain_in_the_ledger() -> None:
    assessments = manufactured_task_assessments()

    assert {row.outcome for row in assessments} >= {"supported", "null", "negative", "unavailable"}
    participant = [row for row in assessments if row.task_id == "participant-transfer"]
    assert participant
    assert all(row.sufficient is not True for row in participant)


@pytest.mark.content_lint
def test_public_model_ladder_declares_contract_limits_and_selection_guidance() -> None:
    article = ARTICLE.read_text(encoding="utf-8")
    hub = MODELS_HUB.read_text(encoding="utf-8")
    required = (
        "Planar-to-Spatial Model Ladder",
        "Included Physics",
        "Omitted Physics",
        "Exact Adjacent-Level Fixtures",
        "Task-Specific Metrics and Uncertainty",
        "Minimum-Sufficient-Level Guidance",
        "Negative, Null, and Unavailable Results",
        "synthetic; no participant data",
        "does not establish a global fidelity percentage",
        "wall-clock runtime is unavailable",
        "measured, estimated, modeled, assumed, or unavailable",
    )

    for phrase in required:
        assert phrase in article
    assert "90%" not in article
    assert "model-ladder.html" in hub
