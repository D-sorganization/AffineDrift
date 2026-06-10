"""Behavioral tests for ``scripts/assessment_report_builder.py`` (issue #3230).

Covers ``build_comprehensive_report``: grade header rendering, the
top-recommendations ordering (ascending by grade), the conditional
issue-creation path (only categories with grade < 5), and the
"Additional Audits" passthrough from an existing report file.

A fake ``issue_generator`` is injected so no real issue files are needed; the
working directory is redirected to ``tmp_path`` because the function creates
``docs/assessments/issues`` relative to cwd.
"""

from __future__ import annotations

from pathlib import Path

from scripts.assessment_report_builder import build_comprehensive_report


def _fake_issue_generator(**kwargs) -> Path:
    return Path(f"issue_{kwargs['category_id']}.md")


def _score(grade: float, *, rec: str = "do better", details: str = "x") -> dict:
    return {"grade": grade, "recommendation": rec, "details": details}


def test_report_header_and_grade(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    report = build_comprehensive_report(
        {"A": _score(8.0)}, 8.0, issue_generator=_fake_issue_generator
    )
    assert "# Comprehensive Repository Assessment" in report
    assert "## Overall Grade: 8.00/10" in report
    assert "| Code Structure | 8.0 |" in report


def test_low_grade_creates_issue_high_grade_does_not(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    scores = {
        "A": _score(3.0, rec="fix structure"),  # < 5 -> issue created
        "B": _score(9.0, rec="keep it up"),  # >= 5 -> no issue
    }
    report = build_comprehensive_report(scores, 6.0, issue_generator=_fake_issue_generator)
    assert "Created issue: `issue_A.md`" in report
    assert "issue_B.md" not in report


def test_recommendations_sorted_ascending_by_grade(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    scores = {
        "A": _score(9.0, rec="A rec"),
        "B": _score(2.0, rec="B rec"),
        "C": _score(5.0, rec="C rec"),
    }
    report = build_comprehensive_report(scores, 5.3, issue_generator=_fake_issue_generator)
    # Worst grade (B, 2.0) must appear as recommendation #1.
    rec_section = report.split("## Top Recommendations", 1)[1]
    assert rec_section.index("B rec") < rec_section.index("C rec") < rec_section.index("A rec")


def test_additional_audits_appended_from_existing_file(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    existing = tmp_path / "docs" / "assessments" / "Comprehensive_Assessment.md"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text(
        "# Old\n## Additional Audits\nSecurity deep-dive results.\n", encoding="utf-8"
    )
    report = build_comprehensive_report(
        {"A": _score(8.0)}, 8.0, issue_generator=_fake_issue_generator
    )
    assert "## Additional Audits" in report
    assert "Security deep-dive results." in report
