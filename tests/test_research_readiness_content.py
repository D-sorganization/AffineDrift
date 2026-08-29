"""Public content and exact-evidence contracts for research readiness (#4041)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from src.affine_control.research_readiness import load_library

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "models/research-protocol-readiness.qmd"
HUB = ROOT / "models/models.qmd"
SITEMAP = ROOT / "sitemap.xml"
AUDIT = ROOT / "data/trust/claim_audit_inventory.json"
TEMPLATE = ROOT / "data/research_protocols/protocol-template.json"
SCHEMA = ROOT / "schemas/research-protocol-readiness-v1.schema.json"
CLAIMS = ROOT / "data/trust/claim_registry.json"
CRITIQUES = ROOT / "data/trust/claim_critique_ledger.json"


@pytest.mark.content_lint
def test_public_route_explains_contract_gates_and_use() -> None:
    article = " ".join(ARTICLE.read_text(encoding="utf-8").split())
    required = (
        "Research Protocol and Data-Readiness Library",
        "Scientific Authority Boundary",
        "What a Readiness State Means",
        "The Complete State and Evidence Ladder",
        "Current E1–E8 Program Catalog",
        "Worked Example: DCR and Finite-Horizon Reachability",
        "Frames, Units, Calibration, and Data Dictionary",
        "Negative, Null, Unavailable, and Rejected Outcomes",
        "Private and Unavailable Evidence",
        "Add or Revise a Protocol",
        "software never authorizes participant collection",
        "no coaching, clinical, design, causal, or population authority",
        "simulation-ready",
        "pilot-ready",
        "ethics-approved",
        "analysis-locked",
        "superseded",
        "#4042",
    )
    for phrase in required:
        assert phrase in article


@pytest.mark.content_lint
def test_catalog_and_machine_readable_resources_are_linked() -> None:
    article = ARTICLE.read_text(encoding="utf-8")
    hub = HUB.read_text(encoding="utf-8")
    sitemap = SITEMAP.read_text(encoding="utf-8")

    assert "research-readiness-library.qmd" in article
    assert "../schemas/research-protocol-readiness-v1.schema.json" in article
    assert "../data/research_protocols/library.json" in article
    assert "../data/research_protocols/protocol-template.json" in article
    assert "research-protocol-readiness.html" in hub
    assert "https://affinedrift.com/models/research-protocol-readiness.html" in sitemap


def test_schema_valid_concept_template_is_safe_to_copy() -> None:
    template = load_library(TEMPLATE, SCHEMA, CLAIMS, CRITIQUES, ROOT)
    canonical = load_library(
        ROOT / "data/research_protocols/library.json", SCHEMA, CLAIMS, CRITIQUES, ROOT
    )
    protocols = template["protocols"]
    assert isinstance(protocols, list) and len(protocols) == 1
    protocol = protocols[0]
    assert protocol["state"] == "concept"
    assert protocol["companion_issue"] == 4041
    assert protocol["history"] == []
    assert protocol["promotion_attempts"] == []
    assert protocol["evidence"] == []
    assert protocol["links"]["claim_ids"] == []
    assert protocol["links"]["critique_ids"] == []
    assert protocol["links"]["route_audits"] == []
    assert protocol["links"]["calculation_artifacts"] == []
    assert protocol["links"]["workflow_artifacts"] == []
    canonical_ids = {record["protocol_id"] for record in canonical["protocols"]}
    assert protocol["protocol_id"] not in canonical_ids


def test_generator_uses_module_imports_without_a_sys_path_bootstrap() -> None:
    generator = (ROOT / "scripts/generate_research_readiness_library.py").read_text(
        encoding="utf-8"
    )
    article = ARTICLE.read_text(encoding="utf-8")

    assert "sys.path" not in generator
    assert "python -m scripts.generate_research_readiness_library --check" in article
    assert "python scripts/generate_research_readiness_library.py" not in article


def test_generated_readiness_library_has_no_trailing_whitespace() -> None:
    generated = (ROOT / "_includes/generated/research-readiness-library.qmd").read_text(
        encoding="utf-8"
    )

    assert all(line == line.rstrip() for line in generated.splitlines())


@pytest.mark.content_lint
def test_generated_public_summary_is_non_authorizing_and_complete() -> None:
    summary = json.loads(
        (ROOT / "data/research_protocols/public_summary.json").read_text(encoding="utf-8")
    )
    assert summary["authorizes_data_collection"] is False
    assert summary["authorizes_claim_promotion"] is False
    assert len(summary["protocols"]) == 8
    assert {record["state"] for record in summary["protocols"]} == {"simulation-ready"}


@pytest.mark.content_lint
def test_public_route_has_recursive_exact_byte_review_evidence() -> None:
    inventory = json.loads(AUDIT.read_text(encoding="utf-8"))
    records = [
        row
        for row in inventory["routes"]
        if row["route"] == "/models/research-protocol-readiness.html"
    ]
    assert len(records) == 1
    record = records[0]
    assert record["status"] == "reviewed"
    assert record["findings"] == []
    review = record["review"]
    expected = {
        "models/research-protocol-readiness.qmd",
        "schemas/research-protocol-readiness-v1.schema.json",
        "scripts/generate_research_readiness_library.py",
        "src/affine_control/research_readiness/authority.py",
        "src/affine_control/research_readiness/dry_runs.py",
        "src/affine_control/research_readiness/files.py",
        "src/affine_control/research_readiness/states.py",
        "src/affine_control/research_readiness/validation.py",
        "tests/research_readiness_test_support.py",
        "tests/test_research_readiness_authority_red.py",
        "tests/test_research_readiness_lifecycle_red.py",
        "tests/test_research_readiness_projection_red.py",
        "tests/test_research_protocol_readiness.py",
        "tests/test_research_readiness_content.py",
        "data/research_protocols/library.json",
        "data/research_protocols/public_summary.json",
    }
    assert expected.issubset(review["evidence_paths"])
    for path in review["evidence_paths"]:
        assert (
            review["evidence_sha256"][path]
            == hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        )
