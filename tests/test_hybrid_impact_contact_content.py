"""Public-content and review-evidence contracts for issue #4038."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "models" / "hybrid-impact-contact.qmd"
MODELS_HUB = ROOT / "models" / "models.qmd"
BIBLIOGRAPHY = ROOT / "data" / "bibliography.json"
AUDIT_INVENTORY = ROOT / "data" / "trust" / "claim_audit_inventory.json"
REVIEW_COMMIT = "TO-BE-REPLACED-BY-CONTENT-COMMIT"


@pytest.mark.content_lint
def test_public_hybrid_impact_protocol_is_complete_and_bounded() -> None:
    article = " ".join(ARTICLE.read_text(encoding="utf-8").split())
    hub = " ".join(MODELS_HUB.read_text(encoding="utf-8").split())
    required = (
        "Hybrid Impact-Contact and Event-Time Uncertainty",
        "Scientific Authority Boundary",
        "Primary-Source Register",
        "Pre-Impact State and Frame Contract",
        "+x clubface normal from club toward ball",
        "Rigid Impulse Model",
        "Compliant Contact Model",
        "Hybrid Event Model",
        "Solver and Event-Detection Policy",
        "Balance, Convergence, and Failure Contracts",
        "Grazing",
        "Multiple Contact",
        "Event-Time and Parameter Uncertainty",
        "Outcome-Specific Model Comparison",
        "no contact model is universally correct",
        "Negative, Null, and Unavailable Results",
        "synthetic-fixture",
        "no coaching, clinical, causal, population, or equipment-design authority",
    )

    for phrase in required:
        assert phrase in article
    assert "hybrid-impact-contact.html" in hub


@pytest.mark.content_lint
def test_primary_sources_are_registered_in_canonical_bibliography() -> None:
    records = json.loads(BIBLIOGRAPHY.read_text(encoding="utf-8"))
    by_id = {record["id"]: record for record in records}

    expected_dois = {
        "roberts2001contacttime": "10.1046/j.1460-2687.2001.00084.x",
        "petersen2009clubface": "10.1007/s12283-009-0030-7",
        "mcnally2018shaftimpact": "10.3390/proceedings2060245",
        "kong2024saltation": "10.1109/JPROC.2024.3440211",
    }
    for source_id, doi in expected_dois.items():
        assert by_id[source_id]["doi"] == doi
        assert by_id[source_id]["type"] == "paper"
        assert by_id[source_id]["note"]


@pytest.mark.content_lint
def test_public_route_has_digest_bound_review_evidence() -> None:
    inventory = json.loads(AUDIT_INVENTORY.read_text(encoding="utf-8"))
    records = [
        record
        for record in inventory["routes"]
        if record["route"] == "/models/hybrid-impact-contact.html"
    ]

    assert len(records) == 1
    record = records[0]
    assert record["status"] == "reviewed"
    assert record["findings"] == []
    review = record["review"]
    assert review["review_commit"] == REVIEW_COMMIT
    assert review["source_path"] == "models/hybrid-impact-contact.qmd"
    assert set(review["dimensions"]) == {
        "evidence",
        "uncertainty",
        "falsifiers",
        "audience_framing",
    }
    assert set(review["evidence_paths"]) == {
        "models/hybrid-impact-contact.qmd",
        "src/affine_control/impact_contact_fixtures.py",
        "src/affine_control/impact_contact_models.py",
        "src/affine_control/impact_contact_protocol.py",
        "src/affine_control/impact_contact_uncertainty.py",
        "tests/test_hybrid_impact_contact_protocol.py",
    }
    assert set(review["evidence_sha256"]) == set(review["evidence_paths"])
