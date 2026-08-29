"""Contracts for the equipment and shaft individual-response program (#4040)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from src.affine_control.equipment_response_analysis import (
    analyze_equipment_response,
    qualify_observations,
)
from src.affine_control.equipment_response_fixtures import (
    adverse_carryover_observations,
    build_fixture_ledger,
    build_protocol,
    manufactured_observations,
)
from src.affine_control.equipment_response_protocol import (
    REQUIRED_PROPERTY_IDS,
    EquipmentCondition,
    EquipmentProperty,
    RandomizationPlan,
    ResponseObservation,
)


def test_protocol_freezes_sources_estimand_and_authority_boundary() -> None:
    protocol = build_protocol()

    assert protocol.revision == "affinedrift.equipment-individual-response/v1"
    assert tuple(source.source_id for source in protocol.sources) == (
        "worobets2012effects",
        "mackenzie2017shaft",
        "betzler2012shaft",
        "jones2019shaft",
        "lacy2012driver",
        "cheong2006shaft",
    )
    assert protocol.estimand == (
        "within-participant target-minus-baseline change in clubhead speed at impact"
    )
    assert protocol.outcome_unit == "m/s"
    assert protocol.practical_threshold == pytest.approx(0.5)
    assert protocol.human_gate.status == "unavailable"
    assert "independent equipment qualification" in protocol.human_gate.missing_authorities
    assert "product or fitting recommendation" in protocol.authority_limit


def test_equipment_conditions_require_complete_traceable_metrology() -> None:
    protocol = build_protocol()
    baseline = protocol.conditions[0]

    assert tuple(item.property_id for item in baseline.properties) == REQUIRED_PROPERTY_IDS
    assert all(item.origin == "manufactured-synthetic" for item in baseline.properties)
    assert all(item.standard_uncertainty > 0.0 for item in baseline.properties)
    assert all(item.calibration_revision for item in baseline.properties)
    assert protocol.chain_of_custody.condition_ids == tuple(
        condition.condition_id for condition in protocol.conditions
    )
    assert protocol.chain_of_custody.events

    with pytest.raises(ValueError, match="exact required equipment property set"):
        EquipmentCondition(**{**baseline.__dict__, "properties": baseline.properties[:-1]})
    with pytest.raises(ValueError, match="standard uncertainty"):
        EquipmentProperty(**{**baseline.properties[0].__dict__, "standard_uncertainty": -1.0})


def test_randomization_requires_balanced_ab_ba_sequences_and_declared_washout() -> None:
    plan = build_protocol().randomization

    assert plan.algorithm == "seeded-blocked-permutation-v1"
    assert plan.sequence_counts == {"AB": 4, "BA": 4}
    assert plan.cycles_per_participant == 3
    assert plan.trials_per_condition_per_cycle == 5
    assert plan.blinding == "participant-and-analyst-condition-codes"

    all_ab = tuple((participant, "AB") for participant, _ in plan.assignments)
    with pytest.raises(ValueError, match="counterbalanced"):
        RandomizationPlan(**{**plan.__dict__, "assignments": all_ab})
    with pytest.raises(ValueError, match="washout"):
        RandomizationPlan(**{**plan.__dict__, "washout_minutes": 0.0})


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("outcome_value", float("nan"), "finite"),
        ("measurement_standard_uncertainty", 0.0, "uncertainty"),
        ("intent_error", -0.1, "intent error"),
        ("carryover_residual", -0.1, "carryover residual"),
        ("origin", "measured", "manufactured-synthetic"),
    ),
)
def test_observations_reject_invalid_or_promoted_values(
    field: str, value: object, message: str
) -> None:
    observation = manufactured_observations()[0]

    with pytest.raises(ValueError, match=message):
        ResponseObservation(**{**observation.__dict__, field: value})


def test_qualification_requires_complete_cells_and_retains_failed_records() -> None:
    protocol = build_protocol()
    observations = manufactured_observations()
    qualified = qualify_observations(protocol, observations)

    assert qualified.complete is True
    assert qualified.retained_observation_count == len(observations)
    assert qualified.unavailable_participant_ids == ()

    with pytest.raises(ValueError, match="duplicate observation ID"):
        qualify_observations(protocol, observations + (observations[0],))
    with pytest.raises(ValueError, match="complete participant-cycle-condition cells"):
        qualify_observations(protocol, observations[:-1])

    adverse = adverse_carryover_observations()
    failed = qualify_observations(protocol, adverse)
    assert failed.retained_observation_count == len(adverse)
    assert failed.unavailable_participant_ids == ("P08",)
    assert failed.participant_records[-1].status == "unavailable"
    assert "carryover" in failed.participant_records[-1].reason


def test_hierarchical_analysis_preserves_individual_directions_and_instability() -> None:
    analysis = analyze_equipment_response(build_protocol(), manufactured_observations())
    statuses = {result.status for result in analysis.participants}

    assert statuses == {"positive", "negative", "null", "indeterminate"}
    assert abs(analysis.group.mean_effect) < build_protocol().practical_threshold
    assert analysis.group.between_participant_variance > 0.0
    assert analysis.global_recommendation is None
    assert any(not result.stable_across_cycles for result in analysis.participants)
    assert all(result.origin == "manufactured-synthetic" for result in analysis.participants)
    assert all(result.authorized_guidance == "unavailable" for result in analysis.participants)


def test_measurement_uncertainty_widens_the_individual_interval() -> None:
    protocol = build_protocol()
    observations = manufactured_observations()
    baseline = analyze_equipment_response(protocol, observations)
    noisy = tuple(
        (
            replace(item, measurement_standard_uncertainty=0.8)
            if item.participant_id == "P01"
            else item
        )
        for item in observations
    )
    widened = analyze_equipment_response(protocol, noisy)
    baseline_result = next(item for item in baseline.participants if item.participant_id == "P01")
    noisy_result = next(item for item in widened.participants if item.participant_id == "P01")

    assert noisy_result.interval_width > baseline_result.interval_width
    assert noisy_result.raw_effect == pytest.approx(baseline_result.raw_effect)


def test_failed_carryover_is_unavailable_not_imputed_or_recommended() -> None:
    analysis = analyze_equipment_response(build_protocol(), adverse_carryover_observations())
    failed = next(item for item in analysis.participants if item.participant_id == "P08")

    assert failed.status == "unavailable"
    assert failed.raw_effect is None
    assert failed.authorized_guidance == "unavailable"
    assert analysis.global_recommendation is None


def test_fixture_ledger_keeps_negative_null_unstable_and_unavailable_outcomes() -> None:
    ledger = build_fixture_ledger()

    assert tuple(record.status for record in ledger) == (
        "positive",
        "negative",
        "null",
        "indeterminate",
        "unavailable",
    )
    assert all(record.authorized_guidance == "unavailable" for record in ledger)
    assert all(
        record.evidence_origin in {"manufactured-synthetic", "unavailable"} for record in ledger
    )
