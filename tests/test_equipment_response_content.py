"""Publication and digest-bound review contracts for issue #4040."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "models" / "equipment-individual-response.qmd"
MODELS_HUB = ROOT / "models" / "models.qmd"
BIBLIOGRAPHY = ROOT / "data" / "bibliography.json"
AUDIT_INVENTORY = ROOT / "data" / "trust" / "claim_audit_inventory.json"
REVIEW_COMMIT = "2ab784c58b5d58e40ed40bd04ed3c0284fd901cc"


@pytest.mark.content_lint
def test_public_equipment_response_program_is_complete_and_bounded() -> None:
    article = " ".join(ARTICLE.read_text(encoding="utf-8").split())
    hub = " ".join(MODELS_HUB.read_text(encoding="utf-8").split())
    required = (
        "Equipment and Shaft Individual-Response Validation",
        "Scientific Authority Boundary",
        "Primary-Source Register",
        "Equipment Property and Metrology Contract",
        "Randomization, Blinding, and Washout",
        "Intent Control and Adaptation",
        "Preregistered Estimands",
        "Hierarchical Participant-by-Equipment Analysis",
        "Within-Person Uncertainty",
        "Responder Instability and Carryover",
        "Practical Versus Statistical Significance",
        "Flexible-Shaft Prediction Linkage",
        "Negative, Null, Indeterminate, and Unavailable Results",
        "Further-Research and Promotion Gates",
        "manufactured-synthetic",
        "no product or fitting recommendation",
        "no coaching, clinical, design, causal, or population authority",
    )

    for phrase in required:
        assert phrase in article
    assert "equipment-individual-response.html" in hub
    assert "model-ladder.html" in article
    assert "hybrid-impact-contact.html" in article
    assert "technology-club-fitting.html" in article


@pytest.mark.content_lint
def test_equipment_response_sources_are_registered_with_exact_metadata() -> None:
    records = json.loads(BIBLIOGRAPHY.read_text(encoding="utf-8"))
    by_id = {record["id"]: record for record in records}
    expected = {
        "worobets2012effects": ("10.1080/14763141.2012.674154", "11", "2", "239--248"),
        "mackenzie2017shaft": ("10.1080/02640414.2016.1157262", "35", "2", "105--111"),
        "betzler2012shaft": ("10.1080/14763141.2012.681796", "11", "2", "223--238"),
        "jones2019shaft": ("10.1007/s12283-019-0308-3", "22", "2", "14"),
        "lacy2012driver": ("10.1016/j.proeng.2012.04.065", "34", "", "379--384"),
        "cheong2006shaft": ("10.1016/j.engfailanal.2004.12.035", "13", "3", "464--473"),
    }
    for source_id, (doi, volume, number, pages) in expected.items():
        record = by_id[source_id]
        assert record["doi"] == doi
        assert record["volume"] == volume
        assert record.get("number", "") == number
        assert record["pages"] == pages
        assert record["type"] == "paper"
        assert record["note"]


@pytest.mark.content_lint
def test_equipment_response_route_has_digest_bound_review_evidence() -> None:
    inventory = json.loads(AUDIT_INVENTORY.read_text(encoding="utf-8"))
    records = [
        record
        for record in inventory["routes"]
        if record["route"] == "/models/equipment-individual-response.html"
    ]

    assert len(records) == 1
    record = records[0]
    assert record["status"] == "reviewed"
    assert record["findings"] == []
    review = record["review"]
    assert review["review_commit"] == REVIEW_COMMIT
    assert review["source_path"] == "models/equipment-individual-response.qmd"
    assert set(review["dimensions"]) == {
        "evidence",
        "uncertainty",
        "falsifiers",
        "audience_framing",
    }
    assert set(review["evidence_paths"]) == {
        "models/equipment-individual-response.qmd",
        "src/affine_control/equipment_response_analysis.py",
        "src/affine_control/equipment_response_fixtures.py",
        "src/affine_control/equipment_response_protocol.py",
        "tests/test_equipment_response_content.py",
        "tests/test_equipment_response_protocol.py",
    }
    assert set(review["evidence_sha256"]) == set(review["evidence_paths"])
