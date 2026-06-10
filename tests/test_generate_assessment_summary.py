"""Behavioral tests for ``scripts/generate_assessment_summary.py`` (issue #3230).

Covers the pure report parsers: ``extract_score_from_report`` (pattern match,
default fallback, missing-file error path) and ``extract_issues_from_report``
(severity extraction across BLOCKER/CRITICAL/MAJOR/MINOR).
"""

from __future__ import annotations

from scripts.generate_assessment_summary import (
    extract_issues_from_report,
    extract_score_from_report,
)


def test_extract_score_from_score_pattern(tmp_path) -> None:
    report = tmp_path / "r.md"
    report.write_text("Some text\nScore: 8.5/10\n", encoding="utf-8")
    assert extract_score_from_report(report) == 8.5


def test_extract_score_from_overall_pattern(tmp_path) -> None:
    report = tmp_path / "r.md"
    report.write_text("Overall: 9.2 across categories\n", encoding="utf-8")
    assert extract_score_from_report(report) == 9.2


def test_extract_score_defaults_when_absent(tmp_path) -> None:
    report = tmp_path / "r.md"
    report.write_text("No numeric grade here at all.\n", encoding="utf-8")
    assert extract_score_from_report(report) == 7.0


def test_extract_score_missing_file_returns_default(tmp_path) -> None:
    assert extract_score_from_report(tmp_path / "missing.md") == 7.0


def test_extract_issues_captures_severities(tmp_path) -> None:
    report = tmp_path / "report.md"
    report.write_text(
        "BLOCKER: build is broken\n" "MINOR: typo in docs\n" "Some prose with no marker.\n",
        encoding="utf-8",
    )
    issues = extract_issues_from_report(report)
    severities = {i["severity"] for i in issues}
    assert "BLOCKER" in severities
    assert "MINOR" in severities
    blocker = next(i for i in issues if i["severity"] == "BLOCKER")
    assert blocker["description"] == "build is broken"
    assert blocker["source"] == "report"


def test_extract_issues_empty_when_no_markers(tmp_path) -> None:
    report = tmp_path / "clean.md"
    report.write_text("All good. Nothing to report.\n", encoding="utf-8")
    assert extract_issues_from_report(report) == []
