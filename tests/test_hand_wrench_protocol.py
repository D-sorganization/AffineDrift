"""Contracts for bilateral hand-wrench identification and grip qualification."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from src.affine_control.hand_wrench_evidence import HumanTierGate
from src.affine_control.hand_wrench_fixtures import (
    manufactured_bandwidth_samples,
    manufactured_benchtop_results,
    manufactured_calibration_case,
    manufactured_frames,
    manufactured_human_gate,
    manufactured_preregistration,
    manufactured_wrench_pair,
)
from src.affine_control.hand_wrench_protocol import (
    assess_identifiability,
    bilateral_sensor_map,
    calibrate_wrench,
    compatible_bilateral_allocations,
    inertial_compensate,
    point_force_wrench_map,
    qualify_bandwidth,
    total_wrench_map,
    transform_wrench,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTICLE = REPO_ROOT / "models" / "bilateral-hand-wrench-validation.qmd"
MODELS_HUB = REPO_ROOT / "models" / "models.qmd"
AUDIT_INVENTORY = REPO_ROOT / "data" / "trust" / "claim_audit_inventory.json"
REVIEW_COMMIT = "ae1577ccfb2001d191e5a329d61a0551cfa06583"


def test_preregistration_freezes_sources_measurement_and_analysis_contracts() -> None:
    protocol = manufactured_preregistration()

    assert protocol.protocol_id == "affinedrift.bilateral-hand-wrench/v1"
    assert {source.source_id for source in protocol.sources} == {
        "koike-2016",
        "choi-park-2020",
        "upstream-identifiability-2026",
        "upstream-sensor-qualification-2026",
    }
    assert {sensor.hand for sensor in protocol.sensors} == {"lead", "trail"}
    assert protocol.analysis.participant_split == "participant-held-out"
    assert protocol.analysis.inertial_compensation
    assert protocol.analysis.contact_assumptions
    assert protocol.analysis.exclusion_rules
    assert {hypothesis.outcome_if_not_supported for hypothesis in protocol.hypotheses} >= {
        "negative",
        "null",
        "unavailable",
    }


def test_net_wrench_observability_does_not_identify_bilateral_allocation() -> None:
    total_report = assess_identifiability(total_wrench_map())
    bilateral_report = assess_identifiability(bilateral_sensor_map())

    assert (total_report.rank, total_report.nullity) == (6, 6)
    assert total_report.identifiable is False
    assert (bilateral_report.rank, bilateral_report.nullity) == (12, 0)
    assert bilateral_report.identifiable is True

    lead, trail = manufactured_wrench_pair()
    total = lead + trail
    first, second = compatible_bilateral_allocations(total)
    assert np.allclose(first[0] + first[1], total)
    assert np.allclose(second[0] + second[1], total)
    assert not np.allclose(first[0], second[0])


def test_point_force_map_preserves_the_axial_internal_null_mode() -> None:
    lead_position = np.array([-0.1, 0.0, 0.0])
    trail_position = np.array([0.1, 0.0, 0.0])
    mapping = point_force_wrench_map(lead_position, trail_position)
    report = assess_identifiability(mapping)
    axial_mode = np.array([1.0, 0.0, 0.0, -1.0, 0.0, 0.0])

    assert (report.rank, report.nullity) == (5, 1)
    assert np.allclose(mapping @ axial_mode, np.zeros(6))


def test_cross_talk_calibration_recovers_only_the_declared_sensor_wrench() -> None:
    calibration, applied, raw = manufactured_calibration_case()
    recovered = calibrate_wrench(raw, calibration)

    assert np.allclose(recovered, applied, atol=1.0e-12)
    assert calibration.matrix_rank == 6
    assert calibration.condition_number < calibration.maximum_condition_number

    singular = tuple(tuple(0.0 for _ in range(6)) for _ in range(6))
    with pytest.raises(ValueError, match="full rank"):
        replace(calibration, calibration_matrix=singular)


def test_bandwidth_qualification_requires_nyquist_and_complete_passband_evidence() -> None:
    calibration, _, _ = manufactured_calibration_case()
    samples = manufactured_bandwidth_samples()

    assert qualify_bandwidth(calibration, samples) is True
    with pytest.raises(ValueError, match="Nyquist"):
        replace(calibration, sample_rate_hz=2.0 * calibration.bandwidth_hz)
    with pytest.raises(ValueError, match="bandwidth boundary"):
        qualify_bandwidth(calibration, samples[:-1])
    failed = (*samples[:-1], replace(samples[-1], gain_ratio=0.8))
    assert qualify_bandwidth(calibration, failed) is False


def test_lead_and_trail_frames_transport_wrenches_to_one_club_frame() -> None:
    lead_transform, trail_transform = manufactured_frames()
    lead, trail = manufactured_wrench_pair()
    lead_club = transform_wrench(lead, lead_transform)
    trail_club = transform_wrench(trail, trail_transform)

    assert np.allclose(lead_club[:3], np.array([12.0, -5.0, 30.0]))
    assert np.allclose(trail_club[:3], np.array([-2.0, 8.0, 20.0]))
    assert np.allclose(lead_club + trail_club, np.array([10.0, 3.0, 50.0, -0.2, 2.4, 1.2]))


def test_synchronization_inertial_compensation_and_contact_assumptions_fail_closed() -> None:
    protocol = manufactured_preregistration()
    measured = np.array([10.0, 3.0, 50.0, 1.6, 3.4, -0.7])
    inertial = np.array([1.0, -1.0, 4.0, 0.1, 0.2, -0.1])

    assert protocol.analysis.qualifies_sync_offset(0.0002) is True
    assert protocol.analysis.qualifies_sync_offset(0.0012) is False
    assert np.allclose(
        inertial_compensate(measured, inertial),
        np.array([9.0, 4.0, 46.0, 1.5, 3.2, -0.6]),
    )
    with pytest.raises(ValueError, match="inertial wrench"):
        inertial_compensate(measured, None)


def test_result_ledger_separates_load_tiers_uncertainty_and_adverse_outcomes() -> None:
    results = manufactured_benchtop_results()

    assert {row.load_tier for row in results} == {
        "total-measured",
        "bilateral-measured",
        "model-estimated",
        "unavailable",
    }
    assert {row.outcome for row in results} == {
        "supported",
        "negative",
        "null",
        "unavailable",
    }
    assert all(row.uncertainty_interval is not None for row in results if row.estimate is not None)
    parameters = {parameter for row in results for parameter in row.sensitivity_parameters}
    assert any("shaft" in parameter for parameter in parameters)
    assert any("grip" in parameter for parameter in parameters)

    available = results[0]
    with pytest.raises(ValueError, match="unavailable"):
        replace(available, load_tier="unavailable")
    with pytest.raises(ValueError, match="authority"):
        replace(available, interpretation="This identifies a muscle and is coaching advice.")


def test_human_tier_remains_ineligible_without_every_governance_gate() -> None:
    gate = manufactured_human_gate()

    assert gate.eligible is False
    with pytest.raises(ValueError, match="human tier"):
        gate.authorize()

    eligible = HumanTierGate(
        ethics_approval="future-approved-record",
        privacy_plan="future-approved-record",
        consent_revision="future-approved-record",
        data_license="future-approved-record",
        participant_held_out=True,
    )
    assert eligible.authorize() is True


@pytest.mark.content_lint
def test_public_protocol_is_source_bounded_and_non_authoritative() -> None:
    article = " ".join(ARTICLE.read_text(encoding="utf-8").split())
    hub = " ".join(MODELS_HUB.read_text(encoding="utf-8").split())
    required = (
        "Bilateral Hand-Wrench Identifiability",
        "Primary-Source Register",
        "Lead, Trail, and Club Frames",
        "Calibration, Cross-Talk, and Bandwidth",
        "Synchronization and Inertial Compensation",
        "Rank and Observability",
        "Total Measured",
        "Bilateral Measured",
        "Model Estimated",
        "Negative, Null, and Unavailable Results",
        "participant-held-out",
        "no muscle-force attribution",
        "no coaching or clinical authority",
    )

    for phrase in required:
        assert phrase in article
    assert "bilateral-hand-wrench-validation.html" in hub


@pytest.mark.content_lint
def test_public_protocol_has_exact_reviewed_claim_audit_evidence() -> None:
    inventory = json.loads(AUDIT_INVENTORY.read_text(encoding="utf-8"))
    records = [
        record
        for record in inventory["routes"]
        if record["route"] == "/models/bilateral-hand-wrench-validation.html"
    ]

    assert len(records) == 1
    record = records[0]
    assert record["status"] == "reviewed"
    assert record["findings"] == []
    assert record["review"]["review_commit"] == REVIEW_COMMIT
    assert set(record["review"]["dimensions"]) == {
        "evidence",
        "uncertainty",
        "falsifiers",
        "audience_framing",
    }
    assert set(record["review"]["evidence_paths"]) == {
        "src/affine_control/hand_wrench_evidence.py",
        "src/affine_control/hand_wrench_fixtures.py",
        "src/affine_control/hand_wrench_protocol.py",
        "tests/test_hand_wrench_protocol.py",
    }
