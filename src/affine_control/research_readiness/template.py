"""Neutral concept-template construction for the readiness library."""

from __future__ import annotations

from copy import deepcopy
from typing import cast

from .states import protocol_revision, record_revision


def concept_template(library: dict[str, object]) -> dict[str, object]:
    """Return a neutral schema-valid concept template with no live authority joins."""
    protocols = cast(list[dict[str, object]], library["protocols"])
    source_specification = cast(dict[str, object], protocols[0]["specification"])
    dictionary = deepcopy(source_specification["data_dictionary"])
    protocol: dict[str, object] = {
        "protocol_id": "ad-protocol-template-example-000",
        "title": "New Research Protocol Concept Template",
        "companion_issue": 4041,
        "owner": "Replace with the accountable protocol owner before registration",
        "protocol_revision": "0" * 64,
        "record_revision": "0" * 64,
        "state": "concept",
        "participant_scope": "none",
        "evidence_origin": "unavailable",
        "authority_boundary": (
            "Uninstantiated concept template only; it carries no research, collection, "
            "or publication authority."
        ),
        "unavailable_boundaries": [
            "Protocol-specific scientific specification and accountable owner",
            "Evidence, calculation, workflow, dataset, critique, claim, and route-audit joins",
            "Every readiness gate beyond concept",
        ],
        "specification": {
            "question": "Replace with one bounded, falsifiable research question.",
            "estimands": [
                {
                    "estimand_id": "est-template-example",
                    "description": "Replace with the quantity to be estimated.",
                    "population": "Replace with the bounded target population or modeled system.",
                    "outcome": "Replace with the declared outcome.",
                    "contrast": "Replace with the declared comparison.",
                }
            ],
            "hypotheses": [
                {
                    "hypothesis_id": "hyp-template-example",
                    "statement": "Replace with a falsifiable statement.",
                    "direction": "none",
                    "falsifier": "Replace with evidence that would reject the statement.",
                    "null_handling": "Retain negative, null, and unavailable outcomes.",
                }
            ],
            "population": {
                "target_population": "Replace before promotion beyond concept.",
                "sampling_frame": "Unavailable in the neutral template.",
                "inclusion": ["Replace with explicit inclusion rules."],
                "exclusion": ["Replace with explicit exclusion rules."],
                "authority": "No population authority is present.",
            },
            "intervention_exposure": {
                "type": "none",
                "description": "Unavailable in the neutral template.",
                "comparator": "Unavailable in the neutral template.",
            },
            "measurements": [
                {
                    "name": "Replace with a declared measurement.",
                    "quantity_class": "unavailable",
                    "frame": "Replace with a declared frame.",
                    "unit": "Replace with a declared unit.",
                    "calibration_id": "cal-template-example",
                }
            ],
            "calibrations": [
                {
                    "calibration_id": "cal-template-example",
                    "status": "unavailable",
                    "plan": "Replace with traceability and acceptance criteria.",
                }
            ],
            "data_dictionary": dictionary,
            "governance": {
                "privacy": "Unavailable; define before any data-ready transition.",
                "license": "Unavailable; define before any data-ready transition.",
                "consent": "No participants are in scope for the neutral template.",
                "ethics": "No participants or private data are permitted by this template.",
                "human_approval_required": False,
                "animal_approval_required": False,
                "private_data_approval_required": False,
            },
            "analysis": {
                "workflow_path": "scripts/generate_research_readiness_library.py",
                "power_plan": "Unavailable; replace before pilot-ready promotion.",
                "exclusion_rules": ["Reject undeclared exclusions."],
                "uncertainty_plan": "Unavailable; replace with a bounded uncertainty plan.",
                "falsifiers": ["Reject promotion when declared falsifiers are absent."],
                "null_result_policy": "Retain negative, null, and unavailable outcomes.",
                "deviation_policy": "Append and review deviations before analysis.",
                "promotion_criteria": ["Satisfy every declared target-state gate."],
            },
        },
        "links": {
            "claim_ids": [],
            "claim_link_status": "unavailable",
            "claim_link_next_gate": "Register bounded claims before evidence review.",
            "critique_ids": [],
            "critique_link_status": "unavailable",
            "critique_link_next_gate": "Register applicable critiques before evidence review.",
            "calculation_artifacts": [],
            "workflow_artifacts": [],
            "datasets": [],
            "route_audits": [],
            "validation_release": {
                "status": "unavailable",
                "next_gate": "Only #4042 may supply publication authority.",
            },
        },
        "evidence": [],
        "history": [],
        "promotion_attempts": [],
    }
    protocol["protocol_revision"] = protocol_revision(protocol)
    protocol["record_revision"] = record_revision(protocol)
    return {
        "schema_version": "affinedrift.research-protocol-readiness/v1",
        "protocols": [protocol],
    }
