"""Contracts for the bounded neural-timing perturbation protocol."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from scripts.claim_audit_evidence import included_sources, validate_review_evidence
from src.affine_control.neural_timing_analysis import (
    EvidenceProvenance,
    IntervalDecision,
    classify_interval,
    detect_first_crossing,
    holm_step_down,
)
from src.affine_control.neural_timing_fixtures import (
    build_neural_timing_protocol,
    synthetic_layer_observations,
    synthetic_onset_trace,
    synthetic_result_ledger,
)
from src.affine_control.neural_timing_protocol import (
    EvidenceSource,
    HumanStudyBoundary,
    NeuralTimingProtocol,
    PerturbationDeclaration,
    ResponseWindow,
    SynchronizationContract,
)

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_PAGE = ROOT / "models" / "neural-timing-feedback.qmd"
MODEL_HUB = ROOT / "models" / "models.qmd"
AUDIT_INVENTORY = ROOT / "data" / "trust" / "claim_audit_inventory.json"
PUBLIC_ROUTE = "/models/neural-timing-feedback.html"


def test_protocol_separates_general_evidence_from_golf_specific_evidence() -> None:
    protocol = build_neural_timing_protocol()

    scopes = {source.evidence_scope for source in protocol.sources}
    dois = {source.doi for source in protocol.sources}

    assert scopes == {"general-upper-limb", "golf-specific"}
    assert {
        "10.1152/jn.00453.2009",
        "10.1007/s00221-003-1525-2",
        "10.1007/s00221-020-05770-6",
        "10.1007/s10339-016-0783-4",
        "10.3389/fnhum.2024.1423821",
    } <= dois
    assert all(source.does_not_authorize for source in protocol.sources)


def test_protocol_declares_each_modality_and_each_observation_layer() -> None:
    protocol = build_neural_timing_protocol()
    modalities = {item.modality for item in protocol.perturbations}
    window_pairs = {(item.modality, item.layer) for item in protocol.windows}

    assert modalities == {"mechanical", "visual", "auditory"}
    assert window_pairs == {
        (modality, layer)
        for modality in modalities
        for layer in {
            "perturbation-detection",
            "muscle-response",
            "mechanical-effect",
            "task-correction",
        }
    }
    assert all(item.start_ms >= 0.0 and item.end_ms > item.start_ms for item in protocol.windows)


def test_protocol_joins_phases_shams_channels_hypotheses_and_power_families() -> None:
    protocol = build_neural_timing_protocol()

    phase_ids = {phase.phase_id for phase in protocol.phases}
    sham_ids = {sham.sham_id for sham in protocol.shams}
    channel_ids = {channel.channel_id for channel in protocol.channels}
    window_ids = {window.window_id for window in protocol.windows}
    family_ids = {plan.family_id for plan in protocol.power_plans}

    assert all(
        item.phase_id in phase_ids and item.sham_id in sham_ids for item in protocol.perturbations
    )
    assert set(protocol.synchronization.required_channel_ids) == channel_ids
    assert all(
        item.phase_id in phase_ids and item.window_id in window_ids for item in protocol.hypotheses
    )
    assert all(item.family_id in family_ids for item in protocol.hypotheses)
    assert {item.hierarchy for item in protocol.hypotheses} == {
        "primary",
        "secondary",
        "exploratory",
    }
    assert all(plan.participant_count is None for plan in protocol.power_plans)


@pytest.mark.parametrize(
    ("field", "invalid"),
    (
        ("evidence_scope", "golf-universal"),
        ("modality", "vestibular"),
        ("source_type", "review"),
    ),
)
def test_evidence_source_rejects_runtime_literal_violations(field: str, invalid: str) -> None:
    source = build_neural_timing_protocol().sources[0]

    with pytest.raises(ValueError):
        EvidenceSource(**{**source.__dict__, field: invalid})


def test_protocol_fails_closed_on_duplicate_ids_and_cross_modality_sham_join() -> None:
    protocol = build_neural_timing_protocol()
    duplicate = (*protocol.perturbations, protocol.perturbations[0])
    with pytest.raises(ValueError, match="perturbation IDs"):
        replace(protocol, perturbations=duplicate)

    mechanical = protocol.perturbations[0]
    auditory_sham = next(sham for sham in protocol.shams if sham.modality == "auditory")
    invalid_join = replace(mechanical, sham_id=auditory_sham.sham_id)
    with pytest.raises(ValueError, match="same modality"):
        replace(protocol, perturbations=(invalid_join, *protocol.perturbations[1:]))


def test_protocol_fails_closed_on_missing_layer_and_duplicate_modality_layer() -> None:
    protocol = build_neural_timing_protocol()
    with pytest.raises(ValueError, match="exactly one window"):
        replace(protocol, windows=protocol.windows[:-1])

    duplicated_pair = replace(protocol.windows[-1], window_id="duplicate-window")
    with pytest.raises(ValueError, match="exactly one window"):
        replace(protocol, windows=(*protocol.windows, duplicated_pair))


def test_perturbation_and_window_domains_fail_closed() -> None:
    protocol = build_neural_timing_protocol()
    perturbation = protocol.perturbations[0]
    window = protocol.windows[0]

    with pytest.raises(ValueError):
        PerturbationDeclaration(**{**perturbation.__dict__, "expectation": "known-afterward"})
    with pytest.raises(ValueError):
        replace(perturbation, magnitude=0.0)
    with pytest.raises(ValueError):
        ResponseWindow(**{**window.__dict__, "layer": "neural-cause"})
    with pytest.raises(ValueError):
        replace(window, start_ms=-1.0)


def test_synchronization_contract_requires_calibration_and_bounded_timing() -> None:
    synchronization = build_neural_timing_protocol().synchronization

    assert synchronization.photodiode_required
    assert synchronization.microphone_loopback_required
    assert synchronization.force_onset_required
    with pytest.raises(ValueError):
        replace(synchronization, calibration_record_id="")
    with pytest.raises(ValueError):
        replace(synchronization, maximum_channel_skew_ms=-0.1)
    with pytest.raises(ValueError):
        SynchronizationContract(**{**synchronization.__dict__, "clock_source": ""})


def test_threshold_onset_recovery_is_exact_and_rejects_ambiguous_traces() -> None:
    times_ms, signal = synthetic_onset_trace()
    onset = detect_first_crossing(times_ms, signal, threshold=0.5, persistence_samples=3)

    assert onset.sample_index == 12
    assert onset.latency_ms == pytest.approx(12.0)
    with pytest.raises(ValueError, match="strictly increasing"):
        detect_first_crossing(times_ms[::-1], signal, threshold=0.5, persistence_samples=3)
    with pytest.raises(ValueError, match="no persistent crossing"):
        detect_first_crossing(times_ms, np.zeros_like(signal), threshold=0.5, persistence_samples=3)


def test_parallel_layer_fixture_does_not_create_a_serial_latency_sum() -> None:
    observations = synthetic_layer_observations()
    mechanical = {item.layer: item for item in observations if item.modality == "mechanical"}

    assert mechanical["mechanical-effect"].latency_ms < mechanical["muscle-response"].latency_ms
    assert all(item.provenance.origin == "synthetic-fixture" for item in observations)
    assert all(item.provenance.synthetic for item in observations)


def test_holm_step_down_preserves_original_order_and_controls_one_family() -> None:
    decisions = holm_step_down((0.010, 0.060, 0.015), family_alpha=0.05)

    assert decisions == (True, False, True)
    with pytest.raises(ValueError):
        holm_step_down((0.01, 1.2), family_alpha=0.05)
    with pytest.raises(ValueError):
        holm_step_down((0.01,), family_alpha=0.0)


def test_interval_decisions_preserve_supported_negative_null_and_unavailable() -> None:
    provenance = EvidenceProvenance("synthetic-fixture", "timing-ledger", "v1", True)

    assert classify_interval(2.0, 3.0, 1.0, provenance).outcome == "supported"
    assert classify_interval(-0.5, 0.5, 1.0, provenance).outcome == "negative"
    assert classify_interval(0.5, 1.5, 1.0, provenance).outcome == "null"
    unavailable = classify_interval(None, None, 1.0, EvidenceProvenance.unavailable("missing"))
    assert unavailable.outcome == "unavailable"
    assert unavailable.estimate is None


def test_interval_decision_rejects_labels_that_contradict_its_bounds() -> None:
    provenance = EvidenceProvenance("synthetic-fixture", "timing-ledger", "v1", True)
    supported = classify_interval(2.0, 3.0, 1.0, provenance)

    with pytest.raises(ValueError, match="outcome contradicts"):
        replace(supported, outcome="negative")


def test_result_provenance_prevents_synthetic_promotion() -> None:
    ledger = synthetic_result_ledger()

    assert {item.outcome for item in ledger} == {"supported", "negative", "null", "unavailable"}
    supported = next(item for item in ledger if item.outcome == "supported")
    with pytest.raises(ValueError, match="synthetic"):
        IntervalDecision(
            **{**supported.__dict__, "provenance": replace(supported.provenance, synthetic=False)}
        )


def test_human_boundary_is_permanently_non_authorizing() -> None:
    boundary = build_neural_timing_protocol().human_boundary

    assert boundary.status == "unavailable"
    assert not boundary.participant_data_present
    assert not boundary.authorizes_participant_collection
    with pytest.raises(ValueError):
        HumanStudyBoundary(
            status="ready",
            participant_data_present=True,
            authorizes_participant_collection=True,
        )


def test_protocol_type_is_complete_and_source_bounded() -> None:
    protocol = build_neural_timing_protocol()

    assert isinstance(protocol, NeuralTimingProtocol)
    assert protocol.protocol_id == "affinedrift.neural-timing-feedback/v1"
    assert protocol.analysis_revision == "synthetic-feasibility-only/v1"
    assert protocol.human_boundary.status == "unavailable"


@pytest.mark.content_lint
def test_public_route_states_required_scientific_boundaries() -> None:
    source_paths = (
        PUBLIC_PAGE,
        *(ROOT / path for path in included_sources(ROOT, PUBLIC_PAGE.relative_to(ROOT).as_posix())),
    )
    page = "\n".join(path.read_text(encoding="utf-8") for path in source_paths)
    hub = MODEL_HUB.read_text(encoding="utf-8")
    required = (
        "General Upper-Limb Evidence",
        "Golf-Specific Evidence",
        "Perturbation Detection",
        "Muscle Response",
        "Mechanical Effect",
        "Task Correction",
        "parallel pathways",
        "Holm",
        "sham",
        "blinded",
        "Negative, Null, and Unavailable Results",
        "synthetic-fixture",
        "no unique neural-pathway attribution",
        "no coaching or clinical authority",
    )
    for phrase in required:
        assert phrase in page
    assert "neural-timing-feedback.html" in hub


@pytest.mark.content_lint
def test_public_route_has_recursive_digest_bound_review_evidence() -> None:
    inventory = json.loads(AUDIT_INVENTORY.read_text(encoding="utf-8"))
    records = [record for record in inventory["routes"] if record["route"] == PUBLIC_ROUTE]

    assert len(records) == 1
    record = records[0]
    assert record["status"] == "reviewed"
    assert len(record["findings"]) == 1
    finding = record["findings"][0]
    assert finding["finding_id"] == "ad-finding-neural-timing-outcome-consistency"
    assert finding["disposition"] == "corrected"
    assert set(finding["evidence_paths"]) == {
        "src/affine_control/neural_timing_analysis.py",
        "tests/test_neural_timing_protocol.py",
    }
    review = record["review"]
    assert review["source_path"] == "models/neural-timing-feedback.qmd"
    assert set(review["dimensions"]) == {
        "evidence",
        "uncertainty",
        "falsifiers",
        "audience_framing",
    }
    recursive = included_sources(ROOT, review["source_path"])
    assert recursive == {
        "_includes/neural-timing-authority-boundary.qmd",
        "_includes/neural-timing-human-boundary.qmd",
    }
    assert recursive <= set(review["evidence_paths"])
    assert set(review["evidence_sha256"]) == set(review["evidence_paths"])
    validate_review_evidence(record, ROOT)
