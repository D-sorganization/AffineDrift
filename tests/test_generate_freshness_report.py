"""Contracts for the content freshness report (#4520, extends #4027)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from scripts.generate_freshness_report import (
    STALE_MONTHS,
    FreshnessReportError,
    generate_report,
    months_since,
    render_report,
    scan_pages,
)

REFERENCE = dt.date(2026, 9, 29)


def _write_page(root: Path, rel: str, front_matter: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{front_matter}\n---\n\n# Body\n", encoding="utf-8")
    return path


class TestMonthsSince:
    def test_same_day_is_zero_months(self) -> None:
        assert months_since(REFERENCE, REFERENCE) == 0

    def test_exactly_twelve_months_ago(self) -> None:
        assert months_since(REFERENCE, dt.date(2025, 9, 29)) == 12

    def test_day_of_month_not_yet_reached_rounds_down(self) -> None:
        # One day short of a full 12th month.
        assert months_since(REFERENCE, dt.date(2025, 9, 30)) == 11

    def test_never_negative(self) -> None:
        assert months_since(REFERENCE, dt.date(2027, 1, 1)) == 0


class TestScanPages:
    def test_recently_reviewed_page_is_not_stale(self, tmp_path: Path) -> None:
        _write_page(tmp_path, "pages/fresh.qmd", 'title: "Fresh"\nlast-reviewed: "2026-08-01"')
        entries = scan_pages(tmp_path, REFERENCE)
        assert len(entries) == 1
        assert entries[0].is_stale is False
        assert entries[0].last_reviewed == dt.date(2026, 8, 1)

    def test_page_reviewed_over_a_year_ago_is_stale(self, tmp_path: Path) -> None:
        _write_page(tmp_path, "pages/stale.qmd", 'title: "Stale"\nlast-reviewed: "2025-01-01"')
        entries = scan_pages(tmp_path, REFERENCE)
        assert entries[0].is_stale is True
        assert entries[0].months_since_review >= STALE_MONTHS

    def test_page_with_no_review_date_is_flagged_never_reviewed(self, tmp_path: Path) -> None:
        _write_page(tmp_path, "pages/unreviewed.qmd", 'title: "No Review Date"')
        entries = scan_pages(tmp_path, REFERENCE)
        assert entries[0].is_stale is True
        assert entries[0].last_reviewed is None
        assert entries[0].months_since_review is None

    def test_publish_date_is_never_used_as_a_review_date(self, tmp_path: Path) -> None:
        # A page with an old `date:` (publish/build date) but no `last-reviewed`
        # must be reported as never-reviewed, not as reviewed on that old date.
        _write_page(tmp_path, "pages/old.qmd", 'title: "Old"\ndate: "2020-01-01"')
        entries = scan_pages(tmp_path, REFERENCE)
        assert entries[0].last_reviewed is None

    def test_invalid_review_date_raises(self, tmp_path: Path) -> None:
        _write_page(tmp_path, "pages/bad.qmd", 'title: "Bad"\nlast-reviewed: "not-a-date"')
        with pytest.raises(FreshnessReportError):
            scan_pages(tmp_path, REFERENCE)

    def test_entries_sorted_by_source_path(self, tmp_path: Path) -> None:
        _write_page(tmp_path, "pages/b.qmd", 'title: "B"')
        _write_page(tmp_path, "pages/a.qmd", 'title: "A"')
        entries = scan_pages(tmp_path, REFERENCE)
        assert [e.source_path for e in entries] == ["pages/a.qmd", "pages/b.qmd"]


class TestRenderReport:
    def test_lists_stale_and_never_reviewed_sections(self, tmp_path: Path) -> None:
        _write_page(tmp_path, "pages/stale.qmd", 'title: "Stale"\nlast-reviewed: "2025-01-01"')
        _write_page(tmp_path, "pages/unreviewed.qmd", 'title: "None"')
        _write_page(tmp_path, "pages/fresh.qmd", 'title: "Fresh"\nlast-reviewed: "2026-09-01"')
        entries = scan_pages(tmp_path, REFERENCE)
        report = render_report(entries, REFERENCE)
        assert "pages/stale.qmd" in report
        assert "pages/unreviewed.qmd" in report
        assert "pages/fresh.qmd" not in report
        assert "Pages scanned: 3" in report
        assert "Stale (reviewed 12+ months ago): 1" in report
        assert "Never reviewed: 1" in report

    def test_report_is_deterministic(self, tmp_path: Path) -> None:
        _write_page(tmp_path, "pages/a.qmd", 'title: "A"\nlast-reviewed: "2025-01-01"')
        entries = scan_pages(tmp_path, REFERENCE)
        assert render_report(entries, REFERENCE) == render_report(entries, REFERENCE)


class TestGenerateReport:
    def test_writes_report_file(self, tmp_path: Path) -> None:
        _write_page(tmp_path, "pages/a.qmd", 'title: "A"')
        output = tmp_path / "reports/content-freshness.md"
        exit_code = generate_report(tmp_path, output, REFERENCE, check=False)
        assert exit_code == 0
        assert output.is_file()
        assert "pages/a.qmd" in output.read_text(encoding="utf-8")

    def test_check_fails_when_report_is_stale(self, tmp_path: Path) -> None:
        _write_page(tmp_path, "pages/a.qmd", 'title: "A"')
        output = tmp_path / "reports/content-freshness.md"
        assert generate_report(tmp_path, output, REFERENCE, check=True) == 1

    def test_check_passes_when_report_is_current(self, tmp_path: Path) -> None:
        _write_page(tmp_path, "pages/a.qmd", 'title: "A"')
        output = tmp_path / "reports/content-freshness.md"
        generate_report(tmp_path, output, REFERENCE, check=False)
        assert generate_report(tmp_path, output, REFERENCE, check=True) == 0
