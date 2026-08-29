"""Contracts for phase-dependent impedance and co-contraction identification."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from src.affine_control.impedance_emg import co_contraction_proxy
from src.affine_control.impedance_evidence import GovernedRecord, HumanStudyGate
from src.affine_control.impedance_fixtures import (
    manufactured_confounded_case,
    manufactured_emg_pair,
    manufactured_emg_pair_declaration,
    manufactured_full_rank_case,
    manufactured_human_gate,
    manufactured_protocol,
    manufactured_results,
)
from src.affine_control.impedance_protocol import (
    assess_identifiability,
    fit_impedance,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTICLE = REPO_ROOT / "models" / "active-impedance-identification.qmd"
MODELS_HUB = REPO_ROOT / "models" / "models.qmd"
AUDIT_INVENTORY = REPO_ROOT / "data" / "trust" / "claim_audit_inventory.json"
REVIEW_COMMIT = "c6c2e37505526afbf849ae9bf2e58399f6f3af11"


def test_preregistration_freezes_sources_safety_phases_models_and_hypotheses() -> None:
    protocol = manufactured_protocol()

    assert protocol.protocol_id == "affinedrift.active-impedance/v1"
    assert {source.source_id for source in protocol.sources} == {
        "westwick-perreault-2012",
        "lipps-et-al-2020",
        "vant-veld-et-al-2021",
        "li-et-al-2021",
        "carey-et-al-2026",
        "hermens-et-al-2000",
    }
    hermens = next(
        source for source in protocol.sources if source.source_id == "hermens-et-al-2000"
    )
    assert hermens.source_type == "method-recommendation"
    assert len(protocol.safety.stopping_rules) >= 3
    assert {phase.phase_id for phase in protocol.phases} == {
        "transition",
        "pre-impact",
    }
    assert {model.output_quantity for model in protocol.models} == {
        "endpoint-wrench",
        "joint-torque",
    }
    assert {pair.side for pair in protocol.emg_pairs} == {"lead", "trail"}
    assert protocol.uncertainty_method
    assert protocol.reliability_metric
    assert protocol.human_gate.ready_for_external_review is False
    assert {hypothesis.outcome_if_not_supported for hypothesis in protocol.hypotheses} >= {
        "negative",
        "null",
        "unavailable",
    }


def test_runtime_domains_and_preregistration_joins_fail_closed() -> None:
    protocol = manufactured_protocol()

    with pytest.raises(ValueError, match="source type"):
        replace(protocol.sources[0], source_type="review")
    with pytest.raises(ValueError, match="side"):
        replace(protocol.emg_channels[0], side="center")
    with pytest.raises(ValueError, match="output quantity"):
        replace(protocol.models[0], output_quantity="muscle-force")
    with pytest.raises(ValueError, match="adverse outcome"):
        replace(protocol.hypotheses[0], outcome_if_not_supported="supported")

    duplicate_channel = replace(
        protocol.emg_channels[1], channel_id=protocol.emg_channels[0].channel_id
    )
    with pytest.raises(ValueError, match="EMG channel IDs"):
        replace(protocol, emg_channels=(protocol.emg_channels[0], duplicate_channel))

    duplicate_output = replace(
        protocol.models[1], output_quantity=protocol.models[0].output_quantity
    )
    with pytest.raises(ValueError, match="endpoint and joint"):
        replace(protocol, models=(protocol.models[0], duplicate_output))
    extra_endpoint = replace(protocol.models[0], model_id="extra-endpoint-model")
    with pytest.raises(ValueError, match="exactly one endpoint and joint"):
        replace(protocol, models=(*protocol.models, extra_endpoint))

    duplicate_phase = replace(protocol.phases[1], phase_id=protocol.phases[0].phase_id)
    with pytest.raises(ValueError, match="phase IDs"):
        replace(protocol, phases=(protocol.phases[0], duplicate_phase))

    pair = protocol.emg_pairs[0]
    with pytest.raises(ValueError, match="distinct"):
        replace(pair, antagonist_channel_id=pair.agonist_channel_id)
    unknown_channel = replace(pair, agonist_channel_id="unknown-channel")
    with pytest.raises(ValueError, match="registered EMG channels"):
        replace(protocol, emg_pairs=(unknown_channel, protocol.emg_pairs[1]))
    wrong_side = replace(pair, side="trail")
    with pytest.raises(ValueError, match="same declared side"):
        replace(protocol, emg_pairs=(wrong_side, protocol.emg_pairs[1]))


def test_safety_envelope_and_operational_windows_are_complete_and_ordered() -> None:
    protocol = manufactured_protocol()
    phase = protocol.phases[0]

    assert tuple(window.window_type for window in phase.windows) == (
        "baseline",
        "early-response",
        "late-response",
    )
    assert all(
        earlier.end_ms <= later.start_ms
        for earlier, later in zip(phase.windows, phase.windows[1:], strict=False)
    )
    with pytest.raises(ValueError, match="safety limits"):
        replace(protocol.safety, maximum_torque_nm=0.0)
    with pytest.raises(ValueError, match="stopping rules"):
        replace(protocol.safety, stopping_rules=())
    overlapping = replace(phase.windows[1], start_ms=-5.0)
    with pytest.raises(ValueError, match="ordered and nonoverlapping"):
        replace(phase, windows=(phase.windows[0], overlapping, phase.windows[2]))
    shifted_zero = replace(phase.windows[0], end_ms=1.0)
    shifted_early = replace(phase.windows[1], start_ms=1.0)
    with pytest.raises(ValueError, match="perturbation zero"):
        replace(phase, windows=(shifted_zero, shifted_early, phase.windows[2]))


@pytest.mark.parametrize("phase_id", ["transition", "pre-impact"])
def test_full_rank_synthetic_fixture_recovers_phase_specific_effective_parameters(
    phase_id: str,
) -> None:
    model, design, response, truth = manufactured_full_rank_case(phase_id)
    report = assess_identifiability(
        design,
        model.rank_tolerance,
        model.maximum_condition_number,
    )
    fit = fit_impedance(model, design, response)

    assert report.rank == len(model.parameter_names)
    assert report.nullity == 0
    assert report.identifiable is True
    assert np.allclose(fit.estimates, truth, atol=1.0e-10)
    assert fit.residual_rms < 1.0e-12
    assert fit.output_quantity == "joint-torque"
    assert fit.evidence_tier == "model-partitioned"


def test_confounded_stiffness_and_voluntary_basis_remain_unidentifiable() -> None:
    model, design, response = manufactured_confounded_case()
    report = assess_identifiability(
        design,
        model.rank_tolerance,
        model.maximum_condition_number,
    )

    assert report.rank == len(model.parameter_names) - 1
    assert report.nullity == 1
    assert report.identifiable is False
    with pytest.raises(ValueError, match="identifiable"):
        fit_impedance(model, design, response)


def test_near_singular_design_uses_the_same_relative_tolerance_for_rank_and_fit() -> None:
    model, _, _, _ = manufactured_full_rank_case("transition")
    tolerant_model = replace(
        model,
        rank_tolerance=1.0e-6,
        maximum_condition_number=1.0e12,
    )
    design = np.diag((1.0, 1.0, 1.0, 1.0, 1.0e-8))
    response = design @ np.ones(5)
    report = assess_identifiability(
        design,
        tolerant_model.rank_tolerance,
        tolerant_model.maximum_condition_number,
    )

    assert report.rank == 4
    assert report.nullity == 1
    assert report.identifiable is False
    with pytest.raises(ValueError, match="identifiable"):
        fit_impedance(tolerant_model, design, response)


def test_rank_and_condition_domains_reject_nonsensical_numerical_gates() -> None:
    model, design, _, _ = manufactured_full_rank_case("transition")

    with pytest.raises(ValueError, match="rank tolerance"):
        replace(model, rank_tolerance=1.0)
    with pytest.raises(ValueError, match="condition number"):
        replace(model, maximum_condition_number=0.99)
    with pytest.raises(ValueError, match="rank tolerance"):
        assess_identifiability(design, 1.0, model.maximum_condition_number)
    with pytest.raises(ValueError, match="condition number"):
        assess_identifiability(design, model.rank_tolerance, 0.99)


def test_endpoint_and_joint_impedance_are_distinct_model_conditioned_outputs() -> None:
    protocol = manufactured_protocol()
    endpoint, joint = protocol.models

    assert endpoint.coordinate_frame != joint.coordinate_frame
    assert endpoint.response_unit == "N,Nm"
    assert joint.response_unit == "Nm"
    assert endpoint.jacobian_assumption
    assert "geometric" in endpoint.jacobian_assumption.lower()
    assert all("muscle" not in parameter.lower() for parameter in endpoint.parameter_names)
    assert all("muscle" not in parameter.lower() for parameter in joint.parameter_names)


def test_emg_co_contraction_is_a_normalization_sensitive_proxy_not_stiffness() -> None:
    declaration = manufactured_emg_pair_declaration()
    envelopes = manufactured_emg_pair()
    baseline_proxy = co_contraction_proxy(declaration, envelopes)
    rescaled_proxy = co_contraction_proxy(
        declaration,
        replace(envelopes, antagonist=0.5 * envelopes.antagonist),
    )

    assert 0.0 <= baseline_proxy <= 1.0
    assert not np.isclose(baseline_proxy, rescaled_proxy)
    assert declaration.cci_family == "amplitude-driven"
    assert declaration.comparison_scope == "within-formula-relative-trends-only"
    with pytest.raises(ValueError, match="aligned"):
        co_contraction_proxy(
            declaration,
            replace(envelopes, agonist=envelopes.agonist[:-1]),
        )
    with pytest.raises(ValueError, match="nonnegative"):
        co_contraction_proxy(
            declaration,
            replace(envelopes, antagonist=-envelopes.antagonist),
        )
    with pytest.raises(ValueError, match="channel IDs"):
        co_contraction_proxy(
            declaration,
            replace(
                envelopes,
                agonist_channel_id=envelopes.antagonist_channel_id,
                antagonist_channel_id=envelopes.agonist_channel_id,
            ),
        )


def test_result_ledger_preserves_mechanical_model_proxy_and_unavailable_tiers() -> None:
    results = manufactured_results()

    assert {result.evidence_tier for result in results} == {
        "effective-mechanical",
        "model-partitioned",
        "emg-proxy",
        "unavailable",
    }
    assert {result.outcome for result in results} == {
        "supported",
        "negative",
        "null",
        "unavailable",
    }
    assert {result.provenance.origin for result in results} == {
        "synthetic-fixture",
        "unavailable",
    }
    assert all(result.provenance.record_id for result in results)
    assert all(
        result.uncertainty_interval is not None for result in results if result.estimate is not None
    )
    sensitivities = {item for result in results for item in result.sensitivity_parameters}
    assert any("electrode" in item for item in sensitivities)
    assert any("reflex" in item for item in sensitivities)
    assert any("passive" in item for item in sensitivities)

    with pytest.raises(ValueError, match="unavailable"):
        replace(results[0], evidence_tier="unavailable")
    with pytest.raises(ValueError, match="authority"):
        replace(results[0], interpretation="This identifies muscle force for coaching.")
    with pytest.raises(ValueError, match="measured origin"):
        replace(
            results[0],
            provenance=replace(results[0].provenance, origin="measured"),
        )
    with pytest.raises(ValueError, match="unavailable"):
        replace(
            results[0],
            provenance=replace(results[0].provenance, origin="unavailable"),
        )


def test_human_tier_requires_every_governance_safety_and_validation_gate() -> None:
    gate = manufactured_human_gate()

    assert gate.ready_for_external_review is False
    assert gate.participant_held_out_plan_registered is False
    with pytest.raises(ValueError, match="external review"):
        gate.require_external_review_readiness()

    with pytest.raises(TypeError, match="governed records"):
        HumanStudyGate(
            ethics_approval="future-approved-record",
            risk_assessment="future-approved-record",
            privacy_plan="future-approved-record",
            consent_revision="future-approved-record",
            data_license="future-approved-record",
            device_calibration="future-approved-record",
            stopping_rules_revision="future-approved-record",
            reliability_protocol="future-approved-record",
            independent_approval="future-approved-record",
            participant_held_out_plan_registered=True,
        )

    record_types = (
        "ethics-approval",
        "risk-assessment",
        "privacy-plan",
        "consent-revision",
        "data-license",
        "device-calibration",
        "stopping-rules-revision",
        "reliability-protocol",
        "independent-approval",
    )
    records = tuple(
        GovernedRecord(
            record_id=f"external-record-{record_type}",
            record_type=record_type,
            authority="independent human authority",
            revision="approved-revision",
            status="approved-external",
        )
        for record_type in record_types
    )
    complete = HumanStudyGate(
        ethics_approval=records[0],
        risk_assessment=records[1],
        privacy_plan=records[2],
        consent_revision=records[3],
        data_license=records[4],
        device_calibration=records[5],
        stopping_rules_revision=records[6],
        reliability_protocol=records[7],
        independent_approval=records[8],
        participant_held_out_plan_registered=True,
    )
    readiness = complete.require_external_review_readiness()
    assert readiness.ready_for_external_review is True
    assert readiness.authorizes_participant_collection is False
    assert "outside this software" in readiness.next_gate

    with pytest.raises(ValueError, match="exact prerequisites"):
        replace(complete, ethics_approval=records[1])
    with pytest.raises(ValueError, match="distinct"):
        replace(complete, risk_assessment=replace(records[0], record_type="risk-assessment"))


@pytest.mark.content_lint
def test_public_protocol_is_source_bounded_and_non_authoritative() -> None:
    article = " ".join(ARTICLE.read_text(encoding="utf-8").split())
    hub = " ".join(MODELS_HUB.read_text(encoding="utf-8").split())
    required = (
        "Active Impedance and Co-Contraction Identification",
        "Primary-Source Register",
        "journal method-recommendation article, not a formal measurement standard",
        "Perturbation Device and Safety Envelope",
        "Phase and Response-Window Contract",
        "Endpoint and Joint Impedance",
        "EMG Processing and Electrode Uncertainty",
        "Amplitude-Driven",
        "Direct cross-index value comparison is prohibited",
        "Excitation and Identifiability",
        "Synthetic Recovery and Confounding Fixtures",
        "machine-readable evidence origin",
        "Effective Mechanical",
        "Model Partitioned",
        "EMG Proxy",
        "Negative, Null, and Unavailable Results",
        "participant-held-out analysis plan is registered",
        "no muscle-force identification",
        "no coaching or clinical authority",
    )

    for phrase in required:
        assert phrase in article
    assert "active-impedance-identification.html" in hub


@pytest.mark.content_lint
def test_public_protocol_has_exact_reviewed_claim_audit_evidence() -> None:
    inventory = json.loads(AUDIT_INVENTORY.read_text(encoding="utf-8"))
    records = [
        record
        for record in inventory["routes"]
        if record["route"] == "/models/active-impedance-identification.html"
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
        "src/affine_control/impedance_evidence.py",
        "src/affine_control/impedance_emg.py",
        "src/affine_control/impedance_fixtures.py",
        "src/affine_control/impedance_protocol.py",
        "src/affine_control/impedance_sources.py",
        "tests/test_active_impedance_protocol.py",
    }
