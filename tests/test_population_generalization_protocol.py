"""Executable contracts for population generalization issue #4039."""

from __future__ import annotations

from dataclasses import replace

import pytest

from src.affine_control.population_generalization import (
    DatasetCard,
    EvidenceOrigin,
    LockedSplit,
    PopulationPromotionEvidence,
    evaluate_population_prediction,
    population_claim_authorized,
    validate_split_integrity,
)
from src.affine_control.population_generalization_fixtures import (
    build_manufactured_protocol,
    manufactured_observations,
    manufactured_split,
)


def test_protocol_freezes_population_hierarchy_estimands_and_authority() -> None:
    protocol = build_manufactured_protocol()

    assert protocol.revision == "affinedrift.population-generalization/v1"
    assert protocol.dataset_card.target_population
    assert protocol.dataset_card.sampling_frame == "manufactured balanced fixture only"
    assert protocol.dataset_card.evidence_origin is EvidenceOrigin.MANUFACTURED_SYNTHETIC
    assert protocol.dataset_card.hierarchy == (
        "site",
        "participant",
        "session",
        "equipment",
        "trial",
    )
    assert protocol.estimands == (
        "within-person explanation",
        "between-person association",
        "prediction",
        "causal inference",
    )
    assert protocol.preregistration.status == "template-only"
    assert protocol.external_validation_status == "unavailable"
    assert protocol.authority_limit.endswith("population authority.")


def test_dataset_card_rejects_missing_governance_and_convenience_promotion() -> None:
    card = build_manufactured_protocol().dataset_card

    with pytest.raises(ValueError, match="privacy"):
        replace(card, privacy_plan="")
    with pytest.raises(ValueError, match="strata"):
        replace(card, cohort_strata=())
    with pytest.raises(ValueError, match="sampling frame"):
        DatasetCard(**{**card.__dict__, "sampling_frame": "population representative"})


def test_locked_split_is_group_disjoint_and_rejects_every_leakage_level() -> None:
    observations = manufactured_observations()
    split = manufactured_split()

    validate_split_integrity(observations, split)
    assert split.locked_test_set is True
    assert split.lock_revision

    leaked_participant = replace(
        split,
        assignments=split.assignments + (replace(split.assignments[0], partition="test"),),
    )
    with pytest.raises(ValueError, match="participant leakage"):
        validate_split_integrity(observations, leaked_participant)

    with pytest.raises(ValueError, match="locked test set"):
        validate_split_integrity(observations, replace(split, locked_test_set=False))


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("participant_id", "p1", "participant leakage"),
        ("session_id", "s1", "session leakage"),
        ("equipment_id", "driver-a", "equipment leakage"),
        ("trial_id", "t1", "trial leakage"),
        ("site_id", "site-a", "site leakage"),
    ),
)
def test_test_partition_rejects_nested_group_leakage(field: str, value: str, message: str) -> None:
    observations = list(manufactured_observations())
    observations[-2] = replace(observations[-2], **{field: value})

    with pytest.raises(ValueError, match=message):
        validate_split_integrity(tuple(observations), manufactured_split())


def test_prediction_report_is_deterministic_hierarchical_and_keeps_adverse_results() -> None:
    observations = manufactured_observations()
    split = manufactured_split()

    first = evaluate_population_prediction(observations, split, minimum_subgroup_size=2)
    second = evaluate_population_prediction(observations, split, minimum_subgroup_size=2)

    assert first == second
    assert (
        first.participant_weighted_interval.lower
        <= first.mean_error
        <= first.participant_weighted_interval.upper
    )
    assert first.calibration.slope == pytest.approx(0.5)
    assert first.calibration.intercept == pytest.approx(5.0)
    assert {row.status for row in first.outcomes} == {"negative", "null", "unavailable"}
    assert any(row.status == "unavailable" for row in first.subgroup_performance)
    assert first.external_validation_status == "unavailable"
    assert first.authorizes_population_claim is False


def test_population_promotion_fails_closed_without_measured_external_authority() -> None:
    evidence = PopulationPromotionEvidence.manufactured_fixture()

    assert population_claim_authorized(evidence) is False
    assert (
        population_claim_authorized(
            replace(evidence, human_approval=True, external_site_validation=True)
        )
        is False
    )

    with pytest.raises(ValueError, match="measured evidence"):
        replace(evidence, evidence_origin=EvidenceOrigin.MEASURED)


def test_split_contract_rejects_blank_lock_revision() -> None:
    split = manufactured_split()

    with pytest.raises(ValueError, match="lock revision"):
        LockedSplit(**{**split.__dict__, "lock_revision": ""})
