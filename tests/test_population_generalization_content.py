"""Public companion and trust-evidence contracts for issue #4039."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "models" / "population-generalization.qmd"
MODELS_HUB = ROOT / "models" / "models.qmd"
AUDIT = ROOT / "data" / "trust" / "claim_audit_inventory.json"
REPORT_JSON = ROOT / "data" / "population_generalization" / "validation_report.json"
REPORT_MD = ROOT / "reports" / "population-generalization-validation.md"


@pytest.mark.content_lint
def test_public_population_protocol_is_complete_and_bounded() -> None:
    article = " ".join(ARTICLE.read_text(encoding="utf-8").split())
    hub = " ".join(MODELS_HUB.read_text(encoding="utf-8").split())
    required = (
        "Population Generalization and Participant-Held-Out Validation",
        "Scientific Authority Boundary",
        "Dataset Card",
        "Preregistered Analysis Contract",
        "Participant, Session, Site, and Equipment Leakage",
        "Hierarchical Uncertainty and Calibration",
        "Subgroup Performance and Suppression",
        "Sensitivity and Transportability",
        "Negative, Null, and Unavailable Outcomes",
        "within-person explanation",
        "between-person association",
        "causal inference",
        "manufactured-synthetic",
        "External validation: unavailable",
        "no coaching, clinical, design, causal, or population authority",
    )
    for phrase in required:
        assert phrase in article
    assert "population-generalization.html" in hub


@pytest.mark.content_lint
def test_report_generation_is_current_and_non_authorizing() -> None:
    report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    markdown = REPORT_MD.read_text(encoding="utf-8")

    assert report["schema_version"] == "affinedrift.population-generalization-report/v1"
    assert report["evidence_origin"] == "manufactured-synthetic"
    assert report["authorizes_population_claim"] is False
    assert report["external_validation_status"] == "unavailable"
    assert {row["status"] for row in report["outcomes"]} == {
        "negative",
        "null",
        "unavailable",
    }
    assert "DO NOT use as population authority" in markdown


@pytest.mark.content_lint
def test_public_route_has_exact_byte_review_evidence() -> None:
    inventory = json.loads(AUDIT.read_text(encoding="utf-8"))
    records = [
        row
        for row in inventory["routes"]
        if row["route"] == "/models/population-generalization.html"
    ]

    assert len(records) == 1
    record = records[0]
    assert record["status"] == "reviewed"
    assert record["findings"] == []
    review = record["review"]
    assert review["source_path"] == "models/population-generalization.qmd"
    assert set(review["dimensions"]) == {
        "evidence",
        "uncertainty",
        "falsifiers",
        "audience_framing",
    }
    assert set(review["evidence_sha256"]) == set(review["evidence_paths"])
    assert {
        "models/population-generalization.qmd",
        "src/affine_control/population_generalization.py",
        "src/affine_control/population_generalization_fixtures.py",
        "tests/test_population_generalization_protocol.py",
        "data/population_generalization/validation_report.json",
    }.issubset(review["evidence_paths"])
