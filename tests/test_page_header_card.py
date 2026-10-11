"""Tests for the Page Header Card component (WEB-03.2 #4507).

Enforces:
1. Rendered purely from front matter (`maturity`/`status`, `audience`, `reading-time`,
   `prerequisites`, `date`/`published`, `last-reviewed`/`date-modified`, `citation`/`cite-link`).
2. Accessible markup: a `<dl>` with `<dt>` and `<dd>` pairs, with badges carrying text (not colour alone).
3. Estimated reading time is explicitly labelled "estimate".
4. Printed cleanly in the print stylesheet (`css/print.css`).
5. Reading-time policy conflict is resolved and recorded in `books/roadmap.qmd`.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FILTER = ROOT / "scripts/filters/page-header-card.lua"
PRINT_CSS = ROOT / "css/print.css"
ROADMAP = ROOT / "books/roadmap.qmd"
ACCESSIBILITY_JS = ROOT / "js/accessibility.js"


def _render_html(frontmatter_extra: str, body: str = "Body paragraph.") -> str:
    """Render a synthetic page through Quarto/Pandoc with the page-header-card Lua filter."""
    quarto = shutil.which("quarto")
    if quarto is None:
        pytest.skip("Quarto is required for the page-header-card integration check")
    with tempfile.TemporaryDirectory() as tmp_dir:
        qmd = Path(tmp_dir) / "test.qmd"
        content = (
            "---\n"
            "title: Test Article\n"
            "description: Test article description\n"
            f"{frontmatter_extra}\n"
            f"filters:\n  - {FILTER.resolve().as_posix()}\n"
            "format: html\n"
            "---\n\n"
            f"{body}\n"
        )
        qmd.write_text(content, encoding="utf-8")
        result = subprocess.run(
            [quarto, "render", str(qmd), "--to", "html"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert result.returncode == 0, f"quarto render failed:\n{result.stderr}\n{result.stdout}"
        html_file = qmd.with_suffix(".html")
        assert html_file.exists()
        return html_file.read_text(encoding="utf-8")


@pytest.mark.integration
def test_page_without_header_frontmatter_is_unchanged() -> None:
    html = _render_html("categories: [test]")
    assert "page-header-card" not in html
    assert "page-header-metadata" not in html


@pytest.mark.integration
def test_page_with_maturity_renders_badge_with_text() -> None:
    html = _render_html('status: "Canonical"')
    assert "page-header-card" in html
    assert "<dl" in html
    assert "<dt" in html
    assert "<dd" in html
    assert "badge--maturity" in html
    assert "Canonical" in html


@pytest.mark.integration
def test_page_with_audience_renders_badge_with_text() -> None:
    html = _render_html('audience: "Intermediate"')
    assert "page-header-card" in html
    assert "badge--audience" in html
    assert "Intermediate" in html


@pytest.mark.integration
def test_page_with_reading_time_renders_labelled_estimate() -> None:
    html = _render_html('reading-time: "15 min (estimate)"')
    assert "page-header-card" in html
    assert "15 min" in html
    assert "estimate" in html.lower()


@pytest.mark.integration
def test_page_with_prerequisites_renders_list() -> None:
    frontmatter = (
        "prerequisites:\n"
        '  - "Introduction to Controllable Systems"\n'
        '  - "Basic Differential Geometry"\n'
    )
    html = _render_html(frontmatter)
    assert "page-header-card" in html
    assert "Prerequisites" in html
    assert "Introduction to Controllable Systems" in html
    assert "Basic Differential Geometry" in html


@pytest.mark.integration
def test_page_with_dates_renders_published_and_reviewed() -> None:
    frontmatter = 'date: "2026-04-15"\n' 'last-reviewed: "2026-09-20"\n'
    html = _render_html(frontmatter)
    assert "page-header-card" in html
    assert "Published" in html
    assert "2026-04-15" in html
    assert "Last Reviewed" in html
    assert "2026-09-20" in html


@pytest.mark.integration
def test_page_with_citation_renders_cite_link() -> None:
    html = _render_html("citation: true")
    assert "page-header-card" not in html
    assert "Cite this page" in html
    assert 'href="#citation"' in html


@pytest.mark.integration
def test_full_header_card_accessible_dl_structure() -> None:
    frontmatter = (
        'status: "Reviewed"\n'
        'audience: "Advanced"\n'
        'reading-time: "20 min (estimate)"\n'
        'date: "2026-03-01"\n'
        'last-reviewed: "2026-09-25"\n'
        "prerequisites:\n"
        '  - "Vector Field Geometry"\n'
        "citation: true\n"
    )
    html = _render_html(frontmatter)
    assert "page-header-card" in html
    assert '<dl class="page-header-metadata"' in html
    # Check that text is associated with labels
    assert "Reviewed" in html
    assert "Advanced" in html
    assert "20 min" in html
    assert "estimate" in html.lower()
    assert "Vector Field Geometry" in html
    assert "Cite this page" in html


def test_print_stylesheet_includes_page_header_card_rules() -> None:
    assert PRINT_CSS.exists()
    content = PRINT_CSS.read_text(encoding="utf-8")
    assert ".page-header-card" in content
    assert "break-inside: avoid" in content


def test_reading_time_policy_conflict_resolved_in_roadmap() -> None:
    assert ROADMAP.exists()
    content = ROADMAP.read_text(encoding="utf-8")
    # Must record that reading-time estimates are qualified as estimates
    assert "reading-time" in content.lower() or "reading time" in content.lower()
    assert "estimate" in content.lower()


def test_accessibility_js_reading_time_labels_estimate() -> None:
    assert ACCESSIBILITY_JS.exists()
    content = ACCESSIBILITY_JS.read_text(encoding="utf-8")
    assert "estimate" in content.lower()
