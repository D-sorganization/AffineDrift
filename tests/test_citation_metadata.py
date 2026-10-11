"""Tests for Per-Page Citation Metadata and "Cite This Page" block (WEB-07.2 #4544).

Enforces:
1. Every article emits `citation_title` and `citation_author`.
2. `citation_publication_date` is emitted ONLY for owner-verified dates.
3. Unverified pages omit `citation_publication_date` and emit no `NaN` placeholders.
4. BibTeX download works (standalone `.bib` file + accessible download link).
5. Validated with Google Scholar metadata checker on three sample pages.
6. Print stylesheet handles citation block with `break-inside: avoid`.
7. Project-wide `_quarto.yml` configuration includes citation and google-scholar.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml
from bs4 import BeautifulSoup

from scripts.check_google_scholar_metadata import (
    extract_citation_meta,
    validate_page_metadata,
)
from scripts.post_render_citations import process_html_content

ROOT = Path(__file__).resolve().parents[1]
QUARTO_YML = ROOT / "_quarto.yml"
PRINT_CSS = ROOT / "css/print.css"
ARTICLES_DIR = ROOT / "articles"


def _render_quarto_page(
    frontmatter_extra: str = "",
    body: str = "Test content.",
    title: str = "Sample Analysis of Control Affine Drift",
    author: str = "Dieter Olson",
) -> Path:
    """Render a synthetic article through Quarto to test citation and Google Scholar output."""
    quarto = shutil.which("quarto")
    if quarto is None:
        pytest.skip("Quarto CLI is required for citation metadata rendering tests")

    tmp_dir = Path(tempfile.mkdtemp(prefix="quarto_cite_test_"))
    qmd_file = tmp_dir / "sample-article.qmd"

    fm_lines = ["---"]
    if "title:" not in frontmatter_extra:
        fm_lines.append(f'title: "{title}"')
    if "author:" not in frontmatter_extra:
        fm_lines.append(f'author: "{author}"')
    fm_lines.append("citation: true")
    fm_lines.append("format:\n  html:\n    google-scholar: true")
    if frontmatter_extra.strip():
        fm_lines.append(frontmatter_extra.strip())
    fm_lines.append("---\n")
    fm_lines.append(body)

    content = "\n".join(fm_lines)
    qmd_file.write_text(content, encoding="utf-8")
    result = subprocess.run(
        [quarto, "render", str(qmd_file), "--to", "html"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, f"quarto render failed:\n{result.stderr}\n{result.stdout}"
    html_file = qmd_file.with_suffix(".html")
    assert html_file.is_file()
    return html_file


class TestCitationConfig:
    """Validate project-wide Quarto configuration."""

    def test_quarto_yml_enables_citation_and_scholar(self) -> None:
        assert QUARTO_YML.is_file()
        data = yaml.safe_load(QUARTO_YML.read_text(encoding="utf-8"))

        assert (
            data.get("citation") is True
        ), "citation: true must be set project-wide in _quarto.yml"
        format_html = data.get("format", {}).get("html", {})
        assert (
            format_html.get("google-scholar") is True
        ), "google-scholar: true must be set under format.html in _quarto.yml"

    def test_quarto_yml_registers_post_render_citations(self) -> None:
        assert QUARTO_YML.is_file()
        data = yaml.safe_load(QUARTO_YML.read_text(encoding="utf-8"))
        post_render = data.get("project", {}).get("post-render", [])
        assert any(
            "post_render_citations" in step for step in post_render
        ), "scripts/post_render_citations.py must be registered in project.post-render"

    def test_print_stylesheet_includes_citation_rules(self) -> None:
        assert PRINT_CSS.is_file()
        content = PRINT_CSS.read_text(encoding="utf-8")
        assert "#quarto-citation" in content
        assert "break-inside: avoid" in content
        assert ".quarto-citation-bibtex-download" in content


class TestArticleFrontmatterCompliance:
    """Ensure all tracked article sources satisfy citation prerequisites."""

    def test_every_article_has_title_and_author(self) -> None:
        assert ARTICLES_DIR.is_dir()
        articles = list(ARTICLES_DIR.glob("*.qmd"))
        assert len(articles) >= 30, f"Expected at least 30 articles, found {len(articles)}"

        missing_title: list[str] = []
        missing_author: list[str] = []
        for path in articles:
            text = path.read_text(encoding="utf-8")
            if not text.startswith("---"):
                continue
            parts = text.split("---", 2)
            if len(parts) < 3:
                continue
            try:
                fm = yaml.safe_load(parts[1])
            except yaml.YAMLError as err:
                pytest.fail(f"Failed to parse frontmatter in {path}: {err}")
            if not isinstance(fm, dict):
                continue

            if not fm.get("title"):
                missing_title.append(path.name)
            if not fm.get("author"):
                missing_author.append(path.name)

        assert not missing_title, f"Articles missing title: {missing_title}"
        assert not missing_author, f"Articles missing author: {missing_author}"


class TestGoogleScholarAndCitationRendering:
    """Integration checks on rendered HTML output."""

    @pytest.mark.integration
    def test_verified_article_emits_full_metadata_and_bibtex_download(self) -> None:
        html_file = _render_quarto_page(
            'date: "2026-03-10"\n' 'date-source: "initial-publication-record"\n'
        )
        content = html_file.read_text(encoding="utf-8")
        updated_content, bibtex_str = process_html_content(content, html_file)

        assert bibtex_str is not None
        assert "@online{" in bibtex_str
        assert "Olson, Dieter" in bibtex_str

        # Write updated content and bib file as post-render does
        html_file.write_text(updated_content, encoding="utf-8")
        bib_file = html_file.with_suffix(".bib")
        bib_file.write_text(bibtex_str, encoding="utf-8")

        # Validate with Google Scholar validator
        errors = validate_page_metadata(
            html_file,
            expected_verified_date="2026-03-10",
            is_unverified=False,
            require_citation=True,
        )
        assert not errors, f"Validation errors on verified page: {errors}"

        meta = extract_citation_meta(updated_content)
        assert meta["citation_title"] == ["Sample Analysis of Control Affine Drift"]
        assert meta["citation_author"] == ["Dieter Olson"]
        assert meta["citation_publication_date"] == ["2026-03-10"]

    @pytest.mark.integration
    def test_unverified_article_omits_publication_date_and_has_no_nan(self) -> None:
        html_file = _render_quarto_page('date: "Date unverified"\n' 'date-source: "unverified"\n')
        content = html_file.read_text(encoding="utf-8")
        updated_content, bibtex_str = process_html_content(content, html_file)

        html_file.write_text(updated_content, encoding="utf-8")
        if bibtex_str:
            html_file.with_suffix(".bib").write_text(bibtex_str, encoding="utf-8")

        # Validate with Google Scholar validator
        errors = validate_page_metadata(
            html_file,
            is_unverified=True,
            require_citation=True,
        )
        assert not errors, f"Validation errors on unverified page: {errors}"

        meta = extract_citation_meta(updated_content)
        assert meta["citation_title"] == ["Sample Analysis of Control Affine Drift"]
        assert meta["citation_author"] == ["Dieter Olson"]
        assert "citation_publication_date" not in meta
        assert "citation_cover_date" not in meta
        assert "citation_year" not in meta
        assert "citation_online_date" not in meta

        # Ensure no NaN exists anywhere in meta tags
        assert "NaN" not in updated_content[:1500]

    @pytest.mark.integration
    def test_citation_section_meets_accessibility_requirements(self) -> None:
        html_file = _render_quarto_page(
            'date: "2026-03-10"\n' 'date-source: "initial-publication-record"\n'
        )
        content = html_file.read_text(encoding="utf-8")
        updated_content, _ = process_html_content(content, html_file)

        # 1. Standalone citeas div must NOT carry role="listitem" without an enclosing role="list"
        assert 'class="csl-entry quarto-appendix-citeas" role="listitem"' not in updated_content
        assert "quarto-appendix-citeas" in updated_content

        # 2. BibTeX download button must have accessible high-contrast styles
        assert "quarto-citation-bibtex-download" in updated_content
        assert "color: var(--text-primary)" in updated_content


class TestGoogleScholarValidatorOnSamplePages:
    """Validate on 3 representative sample pages matching acceptance criteria."""

    @pytest.mark.integration
    def test_three_sample_pages_validation(self) -> None:
        # Sample 1: Standard verified article
        page1 = _render_quarto_page(
            'title: "Affine Nature of the Golf Swing"\n'
            'author: "Dieter Olson"\n'
            'date: "2025-11-28"\n'
            'date-source: "initial-publication-record"\n'
        )
        c1, b1 = process_html_content(page1.read_text(encoding="utf-8"), page1)
        page1.write_text(c1, encoding="utf-8")
        if b1:
            page1.with_suffix(".bib").write_text(b1, encoding="utf-8")

        err1 = validate_page_metadata(page1, expected_verified_date="2025-11-28")
        assert not err1, f"Sample 1 validation failed: {err1}"

        # Sample 2: Unverified article (WEB-07.3)
        page2 = _render_quarto_page(
            'title: "Zero-Torque Counterfactual Trajectories"\n'
            'author: "Dieter Olson"\n'
            'date: "Date unverified"\n'
            'date-source: "unverified"\n'
        )
        c2, b2 = process_html_content(page2.read_text(encoding="utf-8"), page2)
        page2.write_text(c2, encoding="utf-8")
        if b2:
            page2.with_suffix(".bib").write_text(b2, encoding="utf-8")

        err2 = validate_page_metadata(page2, is_unverified=True)
        assert not err2, f"Sample 2 validation failed: {err2}"

        # Sample 3: Multi-topic verified page with abstract/description
        page3 = _render_quarto_page(
            'title: "Degrees of Freedom and Dimensionality in the Swing"\n'
            'author: "Dieter Olson"\n'
            'date: "2026-03-10"\n'
            'date-source: "initial-publication-record"\n'
            'description: "Exploring the configuration space and active degrees of freedom."\n'
        )
        c3, b3 = process_html_content(page3.read_text(encoding="utf-8"), page3)
        page3.write_text(c3, encoding="utf-8")
        if b3:
            page3.with_suffix(".bib").write_text(b3, encoding="utf-8")

        err3 = validate_page_metadata(page3, expected_verified_date="2026-03-10")
        assert not err3, f"Sample 3 validation failed: {err3}"


class TestUnverifiedDatePresentation:
    """Keep uncertainty readable without inventing machine-readable dates."""

    @pytest.mark.integration
    def test_unverified_header_and_card_preserve_reviewed_date(self) -> None:
        filter_path = (ROOT / "scripts/filters/page-header-card.lua").as_posix()
        page = _render_quarto_page(
            'date: "Date unverified"\ndate-source: "unverified"\n'
            'date-modified: "2026-10-01"\n'
            f'filters: ["{filter_path}"]\n',
            body="A diagnostic may print `Invalid Date`; retain that prose.",
        )
        content, _ = process_html_content(page.read_text(encoding="utf-8"), page)
        soup = BeautifulSoup(content, "html.parser")
        title_date = soup.select_one("#title-block-header .date")
        published = soup.select_one(".page-header-item--published")
        reviewed = soup.select_one(".page-header-item--reviewed")
        assert (
            title_date is not None
            and title_date.get_text(strip=True) == "Publication date not verified"
        )
        assert published is None
        assert reviewed is not None and "2026" in reviewed.get_text()
        assert "Invalid Date" in soup.find("code").get_text()
        assert "citation_publication_date" not in extract_citation_meta(content)

    def test_cleanup_is_scoped_to_the_title_date_and_idempotent(self) -> None:
        content = (
            '<header id="title-block-header"><p class="date">Invalid Date</p></header>'
            '<article><p class="date">Invalid Date</p><code>Invalid Date</code></article>'
        )
        updated, _ = process_html_content(content, Path("sample.html"))
        assert updated == content.replace(
            '<p class="date">Invalid Date</p></header>',
            '<p class="date">Publication date not verified</p></header>',
        )
        assert process_html_content(updated, Path("sample.html"))[0] == updated

    @pytest.mark.parametrize("date_text", ["October 1, 2026", "2026-10-01", ""])
    def test_cleanup_preserves_valid_or_absent_title_dates(self, date_text: str) -> None:
        content = f'<header id="title-block-header"><p class="date">{date_text}</p></header>'
        assert process_html_content(content, Path("sample.html"))[0] == content

    @pytest.mark.integration
    @pytest.mark.parametrize("verified", [True, False])
    def test_card_preserves_verified_or_missing_publication_date(self, verified: bool) -> None:
        filter_path = (ROOT / "scripts/filters/page-header-card.lua").as_posix()
        metadata = f'filters: ["{filter_path}"]\n'
        if verified:
            metadata += 'date: "2026-03-10"\ndate-source: "initial-publication-record"\n'
        page = _render_quarto_page(metadata)
        content, _ = process_html_content(page.read_text(encoding="utf-8"), page)
        soup = BeautifulSoup(content, "html.parser")
        published = soup.select_one(".page-header-item--published")
        if verified:
            assert published is None
            assert "2026" in soup.select_one("#title-block-header .date").get_text()
            assert extract_citation_meta(content)["citation_publication_date"] == ["2026-03-10"]
        else:
            assert published is None
            assert soup.select_one("#title-block-header .date") is None
        assert "Invalid Date" not in content
