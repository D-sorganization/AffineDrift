"""Tests for comprehensive assessment report markdown generation."""

from __future__ import annotations

from pathlib import Path

from scripts.assessment_report_builder import CATEGORIES, build_comprehensive_report


def test_build_comprehensive_report_sorts_recommendations_and_creates_issues(
    tmp_path: Path, monkeypatch
) -> None:
    """Low-scoring categories should create issue documents and lead recommendations."""
    monkeypatch.chdir(tmp_path)
    created: list[dict[str, object]] = []

    def fake_issue_generator(**kwargs) -> Path:
        created.append(kwargs)
        return Path(f"issue-{kwargs['category_id']}.md")

    scores = {
        "A": {"grade": 8.0, "recommendation": "Keep structure", "details": "ok"},
        "G": {"grade": 3.0, "recommendation": "Add tests", "details": "coverage"},
    }

    report = build_comprehensive_report(scores, 6.5, issue_generator=fake_issue_generator)

    assert "## Overall Grade: 6.50/10" in report
    assert "Add tests" in report
    assert "Created issue: `issue-G.md`" in report
    assert created == [
        {
            "category_id": "G",
            "category_name": CATEGORIES["G"],
            "grade": 3.0,
            "details": "coverage",
        }
    ]


def test_build_comprehensive_report_preserves_additional_audits(
    tmp_path: Path, monkeypatch
) -> None:
    """Existing Additional Audits content should be appended to the generated report."""
    monkeypatch.chdir(tmp_path)
    assessments = tmp_path / "docs" / "assessments"
    assessments.mkdir(parents=True)
    (assessments / "Comprehensive_Assessment.md").write_text(
        "# Existing\n\n## Additional Audits\n\nPrior audit note\n",
        encoding="utf-8",
    )

    report = build_comprehensive_report(
        {"A": {"grade": 9.0, "recommendation": "ok", "details": "ok"}},
        9.0,
        issue_generator=lambda **_kwargs: Path("unused.md"),
    )

    assert "## Additional Audits" in report
    assert "Prior audit note" in report
