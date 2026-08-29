"""Contracts for the #4063 homepage and site-trust-surface audit."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from scripts.site_trust_surface_audit import (
    SiteAuditContractError,
    build_report,
    generate_report,
    validate_audit,
)

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data/trust/site_trust_surface_audit.json"
SCHEMA = ROOT / "schemas/site-trust-surface-audit-v1.schema.json"
INVENTORY = ROOT / "data/trust/claim_audit_inventory.json"
REPORT = ROOT / "reports/site-trust-surface-audit.md"

SCOPED_SOURCES = {
    "/": "index.qmd",
    "/pages/about.html": "pages/about.qmd",
    "/pages/book-reviews.html": "pages/book-reviews.qmd",
    "/pages/collaborate.html": "pages/collaborate.qmd",
    "/pages/contact.html": "pages/contact.qmd",
    "/pages/daydreams-doodles.html": "pages/daydreams-doodles.qmd",
    "/pages/development-roadmap.html": "pages/development-roadmap.qmd",
    "/pages/drifter-manifesto.html": "pages/drifter-manifesto.qmd",
    "/pages/notation.html": "pages/notation.qmd",
    "/pages/overview.html": "pages/overview.qmd",
    "/pages/tangent-hyperplanes.html": "pages/tangent-hyperplanes.qmd",
    "/pages/technology.html": "pages/technology.qmd",
    "/pages/tools.html": "pages/tools.qmd",
}


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _records(document: dict[str, object], key: str) -> list[dict[str, object]]:
    value = document[key]
    assert isinstance(value, list)
    assert all(isinstance(record, dict) for record in value)
    return value


def _route_map(document: dict[str, object]) -> dict[str, dict[str, object]]:
    return {str(record["route"]): record for record in _records(document, "routes")}


def test_site_surface_audit_is_schema_valid_and_exactly_scoped() -> None:
    audit = _json(AUDIT)

    validate_audit(audit, SCHEMA, ROOT)
    routes = _route_map(audit)

    assert routes.keys() == SCOPED_SOURCES.keys()
    assert {route: record["source_path"] for route, record in routes.items()} == SCOPED_SOURCES
    assert len({record["audit_id"] for record in routes.values()}) == 13


def test_every_route_has_substantive_claim_and_adversarial_evidence() -> None:
    audit = _json(AUDIT)
    claim_ids: list[str] = []

    for route, record in _route_map(audit).items():
        claims = record["claims"]
        assert isinstance(claims, list) and claims, f"{route} has no classified claims"
        assert sorted(record["claim_classes"]) == sorted(
            {str(item) for claim in claims for item in claim["claim_classes"]}
        )
        for claim in claims:
            claim_ids.append(str(claim["claim_id"]))
            authority = claim["authority"]
            assert authority["references"], f"{claim['claim_id']} has no source reference"
            assert authority["limits"], f"{claim['claim_id']} has no authority limit"
            assert claim["uncertainty"], f"{claim['claim_id']} has no uncertainty"
            assert claim["falsifiers"], f"{claim['claim_id']} has no falsifier"
            assert claim["audience_limits"], f"{claim['claim_id']} has no audience limit"
        adversarial = record["adversarial_review"]
        assert adversarial["counterexamples"]
        assert adversarial["alternative_mechanisms"]
        assert adversarial["remaining_disagreements"]

    assert len(claim_ids) == len(set(claim_ids))
    assert all(re.fullmatch(r"ad-surface-[a-z0-9-]+-[0-9]{3}", item) for item in claim_ids)


def test_scoped_inventory_is_reviewed_and_matches_audit_findings() -> None:
    audit = _route_map(_json(AUDIT))
    inventory = _route_map(_json(INVENTORY))

    for route, audit_record in audit.items():
        inventory_record = inventory[route]
        assert inventory_record["status"] == "reviewed"
        assert "deferment" not in inventory_record
        review = inventory_record["review"]
        assert review["review_commit"] == audit_record["source_revision"]
        assert "data/trust/site_trust_surface_audit.json" in review["evidence_paths"]
        assert inventory_record["findings"] == audit_record["findings"]


def test_p0_p1_findings_are_corrected_or_publication_blocked() -> None:
    allowed = {"corrected", "publication_blocked"}
    for record in _route_map(_json(AUDIT)).values():
        for finding in record["findings"]:
            if finding["priority"] in {"p0", "p1"}:
                assert finding["disposition"] in allowed
                assert finding["evidence_paths"]
                assert finding["verification_commit"] == record["source_revision"]


def test_review_revision_contains_the_exact_scoped_source_bytes() -> None:
    git = shutil.which("git")
    assert git is not None
    for record in _route_map(_json(AUDIT)).values():
        revision = str(record["source_revision"])
        source = str(record["source_path"])
        result = subprocess.run(
            [git, "diff", "--quiet", f"{revision}..HEAD", "--", source],
            cwd=ROOT,
            check=False,
        )
        assert result.returncode == 0, f"{source} changed after review revision {revision}"


def test_report_generation_is_deterministic_and_current(tmp_path: Path) -> None:
    audit = _json(AUDIT)
    assert build_report(audit) == build_report(audit)

    output = tmp_path / "site-audit.md"
    generate_report(AUDIT, SCHEMA, output, ROOT)
    assert output.read_text(encoding="utf-8") == REPORT.read_text(encoding="utf-8")


def test_validator_rejects_missing_routes_and_weak_p1_dispositions() -> None:
    audit = _json(AUDIT)
    routes = _records(audit, "routes")
    routes.pop()
    with pytest.raises(SiteAuditContractError, match="too short|exactly 13|route scope"):
        validate_audit(audit, SCHEMA, ROOT)

    audit = _json(AUDIT)
    finding = next(
        finding
        for record in _records(audit, "routes")
        for finding in record["findings"]
        if finding["priority"] == "p1"
    )
    finding["disposition"] = "open"
    with pytest.raises(SiteAuditContractError, match="P0/P1"):
        validate_audit(audit, SCHEMA, ROOT)


def test_public_status_and_upstream_capability_language_is_bounded() -> None:
    home = (ROOT / "index.qmd").read_text(encoding="utf-8")
    overview = (ROOT / "pages/overview.qmd").read_text(encoding="utf-8")
    roadmap = (ROOT / "pages/development-roadmap.qmd").read_text(encoding="utf-8")
    technology = (ROOT / "pages/technology.qmd").read_text(encoding="utf-8")
    tools = (ROOT / "pages/tools.qmd").read_text(encoding="utf-8")

    assert "Publication-state key" in home
    assert "Available" in home and "Validated" in home and "Experimental" in home
    assert "UpstreamDrift authority snapshot" in overview
    assert "8cc236c6879e7535bb6bd15aecbe3396fb6dbb36" in overview
    assert "python scripts/ci/verify_installation.py" in overview
    assert '"http://localhost:8000/api/v1/simulate"' in overview
    assert '"engine_type": "mujoco"' in overview
    assert '"http://localhost:8000/simulation"' not in overview
    assert '"engine": "pinocchio"' not in overview

    assert "%" not in roadmap
    assert "Estimated Duration" not in roadmap
    assert "Completion" not in roadmap
    assert "Current release:" not in roadmap
    assert "Status Authority" in roadmap
    assert "Article state:" in technology
    assert "AVAILABLE" in tools and "EXPERIMENTAL" in tools
