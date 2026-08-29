"""Manufactured equipment and individual-response fixtures for #4040."""

from __future__ import annotations

from dataclasses import replace

from src.affine_control.equipment_response_analysis import analyze_equipment_response
from src.affine_control.equipment_response_protocol import (
    REQUIRED_PROPERTY_IDS,
    ChainOfCustody,
    CustodyEvent,
    EquipmentCondition,
    EquipmentProperty,
    EquipmentResponseProtocol,
    EvidenceSource,
    FixtureLedgerRecord,
    HumanEvidenceGate,
    RandomizationPlan,
    ResponseObservation,
)

_PARTICIPANT_EFFECTS = {
    "P01": (1.4, 1.4, 1.4),
    "P02": (0.9, 0.9, 0.9),
    "P03": (-1.4, -1.4, -1.4),
    "P04": (-0.9, -0.9, -0.9),
    "P05": (0.0, 0.0, 0.0),
    "P06": (0.1, 0.1, 0.1),
    "P07": (1.0, -1.0, 0.6),
    "P08": (-0.3, -0.3, -0.3),
}


def build_protocol() -> EquipmentResponseProtocol:
    """Build the frozen manufactured crossover protocol."""
    conditions = (_condition("condition-a", "C01", 0.0), _condition("condition-b", "C02", 1.0))
    condition_ids = tuple(row.condition_id for row in conditions)
    return EquipmentResponseProtocol(
        revision="affinedrift.equipment-individual-response/v1",
        sources=tuple(
            EvidenceSource(source_id, contribution)
            for source_id, contribution in (
                ("worobets2012effects", "subject-dependent club-property response"),
                ("mackenzie2017shaft", "within-golfer shaft-stiffness response"),
                ("betzler2012shaft", "repeated shaft-strain and kinematic trials"),
                ("jones2019shaft", "within- and between-golfer strain variability"),
                ("lacy2012driver", "designed driver mass and length experiment"),
                ("cheong2006shaft", "mechanical shaft metrology and model comparison"),
            )
        ),
        estimand="within-participant target-minus-baseline change in clubhead speed at impact",
        outcome_unit="m/s",
        practical_threshold=0.5,
        conditions=conditions,
        chain_of_custody=ChainOfCustody(
            condition_ids,
            (
                CustodyEvent("E01", "calibrated and sealed", "metrology lead", condition_ids),
                CustodyEvent("E02", "coded and released", "independent custodian", condition_ids),
            ),
        ),
        randomization=RandomizationPlan(
            algorithm="seeded-blocked-permutation-v1",
            seed=4040,
            assignments=tuple(
                (participant, "AB" if index < 4 else "BA")
                for index, participant in enumerate(_PARTICIPANT_EFFECTS)
            ),
            cycles_per_participant=3,
            trials_per_condition_per_cycle=5,
            washout_minutes=10.0,
            blinding="participant-and-analyst-condition-codes",
        ),
        carryover_limit=0.2,
        intent_error_limit=0.2,
        human_gate=HumanEvidenceGate(
            "unavailable",
            (
                "independent equipment qualification",
                "preregistered human crossover data",
                "independent statistical review",
            ),
        ),
        authority_limit=(
            "No product or fitting recommendation, coaching prescription, clinical claim, "
            "causal claim, design authority, or population transport is authorized."
        ),
    )


def _condition(condition_id: str, analyst_code: str, offset: float) -> EquipmentCondition:
    values = {
        "shaft-flexural-rigidity-profile": (31.0 + offset, 27.0 + offset, 22.0 + offset),
        "shaft-torsional-rigidity-profile": (8.0 + offset, 7.0 + offset, 6.0 + offset),
        "shaft-mass": (0.065 + offset * 0.002,),
        "club-length": (1.143,),
        "total-mass": (0.315 + offset * 0.002,),
        "balance-point": (0.735 - offset * 0.004,),
        "head-mass": (0.198,),
        "head-inertia": (0.0029,),
        "grip-mass": (0.052,),
        "static-loft": (0.183,),
        "static-lie": (1.012,),
        "face-angle": (0.0,),
    }
    units = {
        "shaft-flexural-rigidity-profile": "N m^2",
        "shaft-torsional-rigidity-profile": "N m^2",
        "shaft-mass": "kg",
        "club-length": "m",
        "total-mass": "kg",
        "balance-point": "m from butt",
        "head-mass": "kg",
        "head-inertia": "kg m^2",
        "grip-mass": "kg",
        "static-loft": "rad",
        "static-lie": "rad",
        "face-angle": "rad",
    }
    properties = tuple(
        EquipmentProperty(
            property_id,
            values[property_id],
            units[property_id],
            0.001,
            "manufactured calibrated fixture method",
            "calibration-fixture/v1",
            "manufactured-synthetic",
        )
        for property_id in REQUIRED_PROPERTY_IDS
    )
    return EquipmentCondition(condition_id, analyst_code, properties)


def manufactured_observations() -> tuple[ResponseObservation, ...]:
    """Return balanced manufactured trials with mixed individual effects."""
    protocol = build_protocol()
    observations: list[ResponseObservation] = []
    trial_offsets = (-0.08, -0.04, 0.0, 0.04, 0.08)
    for participant_index, (participant, _) in enumerate(protocol.randomization.assignments):
        for cycle, effect in enumerate(_PARTICIPANT_EFFECTS[participant], start=1):
            baseline = 39.0 + participant_index * 0.25 + cycle * 0.05
            for condition_index, condition in enumerate(protocol.conditions):
                for trial, trial_offset in enumerate(trial_offsets, start=1):
                    observations.append(
                        ResponseObservation(
                            observation_id=(
                                f"{participant}-C{cycle}-{condition.condition_id}-T{trial}"
                            ),
                            participant_id=participant,
                            cycle=cycle,
                            condition_id=condition.condition_id,
                            trial=trial,
                            outcome_value=baseline + condition_index * effect + trial_offset,
                            measurement_standard_uncertainty=0.08,
                            intent_error=0.04,
                            carryover_residual=0.03,
                            origin="manufactured-synthetic",
                        )
                    )
    return tuple(observations)


def adverse_carryover_observations() -> tuple[ResponseObservation, ...]:
    """Retain all trials while making P08 unavailable for carryover."""
    return tuple(
        replace(row, carryover_residual=0.5) if row.participant_id == "P08" else row
        for row in manufactured_observations()
    )


def build_fixture_ledger() -> tuple[FixtureLedgerRecord, ...]:
    """Expose representative positive, negative, null, unstable, and failed results."""
    ordinary = analyze_equipment_response(build_protocol(), manufactured_observations())
    adverse = analyze_equipment_response(build_protocol(), adverse_carryover_observations())
    by_participant = {row.participant_id: row for row in ordinary.participants}
    failed = next(row for row in adverse.participants if row.participant_id == "P08")
    selected = (
        by_participant["P01"],
        by_participant["P03"],
        by_participant["P05"],
        by_participant["P07"],
        failed,
    )
    return tuple(
        FixtureLedgerRecord(
            record_id=row.participant_id,
            status=row.status,
            evidence_origin=row.origin,
        )
        for row in selected
    )
