"""Contracts for the #4062 books and publication-roadmap audit."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from scripts.book_publication_audit import (
    BookAuditContractError,
    build_report,
    generate_report,
    validate_audit,
)

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data/trust/book_publication_audit.json"
SCHEMA = ROOT / "schemas/book-publication-audit-v1.schema.json"
INVENTORY = ROOT / "data/trust/claim_audit_inventory.json"
REPORT = ROOT / "reports/book-publication-audit.md"
BROWSER_QA = ROOT / "reports/book-publication-browser-qa.json"

SCOPED_SOURCES = {
    "/books/biomechanics-biology-to-systems.html": "books/biomechanics-biology-to-systems.qmd",
    "/books/control-is-motion.html": "books/control-is-motion.qmd",
    "/books/human-motor-control.html": "books/human-motor-control.qmd",
    "/books/index.html": "books/index.qmd",
    "/books/roadmap.html": "books/roadmap.qmd",
    "/books/tangent-space-methods.html": "books/tangent-space-methods.qmd",
}


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _routes(document: dict[str, object]) -> dict[str, dict[str, object]]:
    records = document["routes"]
    assert isinstance(records, list)
    return {str(record["route"]): record for record in records}


def test_book_audit_is_schema_valid_exactly_scoped_and_self_contained() -> None:
    audit = _json(AUDIT)
    validate_audit(audit, SCHEMA, ROOT)
    routes = _routes(audit)
    assert routes.keys() == SCOPED_SOURCES.keys()
    assert {route: record["source_path"] for route, record in routes.items()} == SCOPED_SOURCES

    for route, record in routes.items():
        source = ROOT / str(record["source_path"])
        assert hashlib.sha256(source.read_bytes()).hexdigest() == record["source_sha256"]
        included = record["included_source_paths"]
        digests = record["included_source_sha256"]
        assert included
        assert set(included) == set(digests)
        for path in included:
            assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digests[path], route


def test_book_audit_inventory_replaces_all_six_deferments() -> None:
    audit = _routes(_json(AUDIT))
    inventory = _routes(_json(INVENTORY))
    for route, audit_record in audit.items():
        record = inventory[route]
        assert record["status"] == "reviewed"
        assert "deferment" not in record
        assert record["findings"] == audit_record["findings"]
        assert record["review"]["review_commit"] == audit_record["source_revision"]
        assert "data/trust/book_publication_audit.json" in record["review"]["evidence_paths"]


def test_blockers_are_closed_and_every_route_has_adversarial_evidence() -> None:
    allowed = {"corrected", "publication_blocked"}
    for route, record in _routes(_json(AUDIT)).items():
        assert record["claims"], route
        assert record["adversarial_review"]["counterexamples"], route
        assert record["adversarial_review"]["alternative_mechanisms"], route
        assert record["adversarial_review"]["remaining_disagreements"], route
        for finding in record["findings"]:
            if finding["priority"] in {"p0", "p1"}:
                assert finding["disposition"] in allowed
                assert finding["verification_commit"] == record["source_revision"]


def test_publication_state_chapter_coverage_and_notebook_limits_are_explicit() -> None:
    volume_sources = [
        ROOT / "books/tangent-space-methods.qmd",
        ROOT / "books/control-is-motion.qmd",
        ROOT / "books/biomechanics-biology-to-systems.qmd",
        ROOT / "books/human-motor-control.qmd",
    ]
    for source in volume_sources:
        text = source.read_text(encoding="utf-8")
        assert "Publication state:" in text
        assert "scaffolded" in text
        assert "does not establish numerical correctness" in text
        assert re.search(r"blob/[0-9a-f]{40}/articles/The_Geometry_of_Motion/Volume_", text)

    tangent = volume_sources[0].read_text(encoding="utf-8")
    human = volume_sources[3].read_text(encoding="utf-8")
    assert "Induced Acceleration Analysis" in tangent
    assert "Parallel Mechanisms" in tangent
    assert "interplay of biology and dynamics of nonlinear systems" in human.lower()


def test_every_canonical_substantive_chapter_is_linked_from_its_volume_route() -> None:
    volumes = {
        "I": (ROOT / "books/tangent-space-methods.qmd", 10),
        "II": (ROOT / "books/control-is-motion.qmd", 11),
        "III": (ROOT / "books/biomechanics-biology-to-systems.qmd", 10),
        "IV": (ROOT / "books/human-motor-control.qmd", 12),
    }
    for volume, (route_path, expected_count) in volumes.items():
        main = ROOT / f"articles/The_Geometry_of_Motion/Volume_{volume}/main.tex"
        chapter_stems = re.findall(
            r"\\include\{chapters/(ch[^}]+)\}", main.read_text(encoding="utf-8")
        )
        assert len(chapter_stems) == expected_count
        route = route_path.read_text(encoding="utf-8")
        for stem in chapter_stems:
            assert f"/{stem}.tex" in route, f"Volume {volume} omits {stem}"


def test_roadmap_rejects_unmeasured_completion_and_time_claims() -> None:
    text = (ROOT / "books/roadmap.qmd").read_text(encoding="utf-8")
    forbidden = [
        r"Estimated Time",
        r"Time to Complete",
        r"master the entire framework",
        r"no prior background required",
        r"Chapters are complete and usable",
        r"Each volume has:",
        r"\b\d+[–-]\d+ hours\b",
    ]
    for pattern in forbidden:
        assert re.search(pattern, text, re.IGNORECASE) is None, pattern
    assert "Publication-State Key" in text
    assert "10 substantive chapters" in text
    assert "11 substantive chapters" in text
    assert "12 substantive chapters" in text


def test_validator_rejects_missing_or_wrong_digest_and_weak_p1() -> None:
    audit = _json(AUDIT)
    del audit["routes"][0]["source_sha256"]
    with pytest.raises(BookAuditContractError, match="source_sha256"):
        validate_audit(audit, SCHEMA, ROOT)

    audit = _json(AUDIT)
    audit["routes"][0]["source_sha256"] = "0" * 64
    with pytest.raises(BookAuditContractError, match="digest mismatch"):
        validate_audit(audit, SCHEMA, ROOT)

    audit = _json(AUDIT)
    finding = next(
        finding
        for record in audit["routes"]
        for finding in record["findings"]
        if finding["priority"] == "p1"
    )
    finding["disposition"] = "open"
    with pytest.raises(BookAuditContractError, match="P0/P1"):
        validate_audit(audit, SCHEMA, ROOT)


def test_report_is_deterministic_and_current(tmp_path: Path) -> None:
    audit = _json(AUDIT)
    assert build_report(audit) == build_report(audit)
    output = tmp_path / "book-audit.md"
    generate_report(AUDIT, SCHEMA, output, ROOT)
    assert output.read_text(encoding="utf-8") == REPORT.read_text(encoding="utf-8")


def test_browser_qa_covers_every_route_viewport_and_theme() -> None:
    evidence = _json(BROWSER_QA)
    assert evidence["schema_version"] == "affinedrift/book-publication-browser-qa/v1"
    assert evidence["issue_url"].endswith("/issues/4062")
    assert evidence["source_revision"] == "8680f12c627c0a5ee10f57710d8316f7c433c463"
    assert evidence["routes"] == list(SCOPED_SOURCES)
    assert evidence["render"] == {
        "generated_output_committed": False,
        "quarto_version": "1.8.26",
        "source_route_count": 6,
        "status": "passed",
    }
    assert evidence["viewports"] == [
        {"height": 844, "id": "mobile", "width": 390},
        {"height": 900, "id": "desktop", "width": 1440},
    ]
    assert evidence["themes"] == ["light", "dark"]

    verification = evidence["automated_verification"]
    assert verification["evidence_items"] == 24
    assert verification["routes_verified"] == 6
    assert verification["failures"] == 0
    assert verification["isolated_route_console_errors"] == 0
    assert verification["isolated_route_console_warnings"] == 0
    assert evidence["interactive_browser_review"]["routes_reviewed"] == 6
    assert evidence["interactive_browser_review"]["temporary_screenshots_retained"] is False
