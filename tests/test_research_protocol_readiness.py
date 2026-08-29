"""Executable contracts for the governed research-readiness library (#4041)."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from src.affine_control.research_readiness import (
    ResearchReadinessError,
    build_public_summary,
    load_library,
    protocol_revision,
    record_revision,
    transition_allowed,
    validate_library,
)

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "data" / "research_protocols" / "library.json"
SCHEMA = ROOT / "schemas" / "research-protocol-readiness-v1.schema.json"
CLAIMS = ROOT / "data" / "trust" / "claim_registry.json"
CRITIQUES = ROOT / "data" / "trust" / "claim_critique_ledger.json"


def _canonical() -> dict[str, object]:
    return load_library(LIBRARY, SCHEMA, CLAIMS, CRITIQUES, ROOT)


def _protocol(
    library: dict[str, object],
    protocol_id: str = "ad-protocol-dcr-perturbation-001",
) -> dict[str, object]:
    protocols = library["protocols"]
    assert isinstance(protocols, list)
    matches = [row for row in protocols if row["protocol_id"] == protocol_id]
    assert len(matches) == 1
    protocol = matches[0]
    assert isinstance(protocol, dict)
    return protocol


def test_library_is_strict_versioned_and_revision_pinned() -> None:
    library = _canonical()
    protocol = _protocol(library)

    assert library["schema_version"] == "affinedrift.research-protocol-readiness/v1"
    assert protocol["protocol_id"] == "ad-protocol-dcr-perturbation-001"
    assert protocol["state"] == "simulation-ready"
    assert protocol["protocol_revision"] == protocol_revision(protocol)
    assert protocol["record_revision"] == record_revision(protocol)

    invalid = copy.deepcopy(library)
    invalid["undeclared"] = True
    with pytest.raises(ResearchReadinessError, match="Additional properties"):
        validate_library(invalid, SCHEMA, CLAIMS, CRITIQUES, ROOT)


def test_unknown_and_skipped_states_fail_closed() -> None:
    unknown = copy.deepcopy(_canonical())
    _protocol(unknown)["state"] = "almost-ready"
    with pytest.raises(ResearchReadinessError, match="almost-ready"):
        validate_library(unknown, SCHEMA, CLAIMS, CRITIQUES, ROOT)

    skipped = copy.deepcopy(_canonical())
    history = _protocol(skipped)["history"]
    assert isinstance(history, list)
    history[0]["to"] = "simulation-ready"
    with pytest.raises(ResearchReadinessError, match="invalid transition"):
        validate_library(skipped, SCHEMA, CLAIMS, CRITIQUES, ROOT)


def test_participant_scope_controls_ethics_applicability() -> None:
    assert transition_allowed("pilot-ready", "data-ready", "none") is True
    assert transition_allowed("pilot-ready", "data-ready", "human") is False
    assert transition_allowed("pilot-ready", "ethics-approved", "human") is True
    assert transition_allowed("pilot-ready", "ethics-approved", "none") is False
    assert transition_allowed("analysis-locked", "superseded", "human") is True
    assert transition_allowed("published", "validated", "human") is False


def test_state_history_must_be_contiguous_and_end_at_declared_state() -> None:
    disconnected = copy.deepcopy(_canonical())
    history = _protocol(disconnected)["history"]
    assert isinstance(history, list)
    history[1]["from"] = "concept"
    with pytest.raises(ResearchReadinessError, match="non-contiguous"):
        validate_library(disconnected, SCHEMA, CLAIMS, CRITIQUES, ROOT)

    stale = copy.deepcopy(_canonical())
    _protocol(stale)["state"] = "evidence-reviewed"
    with pytest.raises(ResearchReadinessError, match="does not end at state"):
        validate_library(stale, SCHEMA, CLAIMS, CRITIQUES, ROOT)


def test_transition_requires_exact_gate_evidence() -> None:
    library = copy.deepcopy(_canonical())
    protocol = _protocol(library)
    evidence = protocol["evidence"]
    assert isinstance(evidence, list)
    protocol["evidence"] = [
        item for item in evidence if isinstance(item, dict) and item["kind"] != "synthetic-dry-run"
    ]

    with pytest.raises(ResearchReadinessError, match="simulation-ready.*synthetic-dry-run"):
        validate_library(library, SCHEMA, CLAIMS, CRITIQUES, ROOT)


def test_evidence_paths_and_digests_are_repository_bounded() -> None:
    traversal = copy.deepcopy(_canonical())
    evidence = _protocol(traversal)["evidence"]
    assert isinstance(evidence, list) and isinstance(evidence[0], dict)
    evidence[0]["path"] = "data/../SPEC.md"
    with pytest.raises(ResearchReadinessError, match="traversal"):
        validate_library(traversal, SCHEMA, CLAIMS, CRITIQUES, ROOT)

    stale = copy.deepcopy(_canonical())
    stale_evidence = _protocol(stale)["evidence"]
    assert isinstance(stale_evidence, list) and isinstance(stale_evidence[0], dict)
    stale_evidence[0]["sha256"] = "0" * 64
    with pytest.raises(ResearchReadinessError, match="digest mismatch"):
        validate_library(stale, SCHEMA, CLAIMS, CRITIQUES, ROOT)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("claim_ids", ["ad-missing-999"], "claim ID"),
        ("critique_ids", ["crit-missing"], "critique ID"),
        (
            "workflow_artifacts",
            [
                {
                    "path": "scripts/missing.py",
                    "sha256": "0" * 64,
                    "source_revision": "0" * 40,
                }
            ],
            "workflow artifact",
        ),
    ),
)
def test_authority_links_must_resolve(field: str, value: list[object], message: str) -> None:
    library = copy.deepcopy(_canonical())
    links = _protocol(library)["links"]
    assert isinstance(links, dict)
    links[field] = value

    with pytest.raises(ResearchReadinessError, match=message):
        validate_library(library, SCHEMA, CLAIMS, CRITIQUES, ROOT)


def test_analysis_contract_mutation_invalidates_revision() -> None:
    library = copy.deepcopy(_canonical())
    protocol = _protocol(library)
    specification = protocol["specification"]
    assert isinstance(specification, dict)
    specification["question"] = "A silently changed research question."

    with pytest.raises(ResearchReadinessError, match="protocol revision mismatch"):
        validate_library(library, SCHEMA, CLAIMS, CRITIQUES, ROOT)


def test_lifecycle_mutation_invalidates_record_revision() -> None:
    library = copy.deepcopy(_canonical())
    protocol = _protocol(library)
    protocol["authority_boundary"] = "A silently changed authority boundary."

    with pytest.raises(ResearchReadinessError, match="record revision mismatch"):
        validate_library(library, SCHEMA, CLAIMS, CRITIQUES, ROOT)


def test_catalog_indexes_every_completed_e1_through_e8_program() -> None:
    protocols = _canonical()["protocols"]
    assert isinstance(protocols, list)

    assert len(protocols) == 8
    assert {row["companion_issue"] for row in protocols} == {
        4033,
        4034,
        4035,
        4036,
        4037,
        4038,
        4039,
        4040,
    }
    assert {row["state"] for row in protocols} == {"simulation-ready"}
    assert {row["evidence_origin"] for row in protocols} <= {
        "analytical",
        "manufactured-synthetic",
        "modeled",
    }


def test_duplicate_json_keys_are_rejected(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text(
        '{"schema_version":"first","schema_version":"second","protocols":[]}',
        encoding="utf-8",
    )

    with pytest.raises(ResearchReadinessError, match="Duplicate JSON key"):
        load_library(duplicate, SCHEMA, CLAIMS, CRITIQUES, ROOT)


def test_artifact_and_route_audit_links_are_exact_byte_joined() -> None:
    library = copy.deepcopy(_canonical())
    protocol = _protocol(library)
    links = protocol["links"]
    assert isinstance(links, dict)
    artifacts = links["workflow_artifacts"]
    assert isinstance(artifacts, list) and isinstance(artifacts[0], dict)
    artifacts[0]["sha256"] = "0" * 64

    with pytest.raises(ResearchReadinessError, match="artifact digest mismatch"):
        validate_library(library, SCHEMA, CLAIMS, CRITIQUES, ROOT)

    dangling = copy.deepcopy(_canonical())
    dangling_links = _protocol(dangling)["links"]
    assert isinstance(dangling_links, dict)
    dangling_links["route_audit_ids"] = ["ad-route-000000000000"]
    with pytest.raises(ResearchReadinessError, match="route audit ID"):
        validate_library(dangling, SCHEMA, CLAIMS, CRITIQUES, ROOT)


def test_public_summary_preserves_readiness_and_authority_boundaries() -> None:
    summary = build_public_summary(_canonical())
    protocol = summary["protocols"][0]

    assert protocol["state"] == "simulation-ready"
    assert protocol["next_gate"] == "pilot-ready"
    assert protocol["authorizes_data_collection"] is False
    assert protocol["authorizes_claim_promotion"] is False
    assert protocol["evidence_origin"] == "manufactured-synthetic"
    assert protocol["unavailable_boundaries"]
    assert "evidence" not in json.dumps(summary)
    assert "custodian" not in json.dumps(summary)
    assert json.dumps(summary, sort_keys=True) == json.dumps(summary, sort_keys=True)
