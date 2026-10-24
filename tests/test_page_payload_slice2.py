"""UX slice 2 (#5165): page payload and render-blocking guardrails."""

from __future__ import annotations

from pathlib import Path

import yaml

from scripts.post_render_page_performance import process_html_head_performance

ROOT = Path(__file__).resolve().parents[1]


def _head(html: str) -> str:
    return html.split("</head>", maxsplit=1)[0]


class TestQuartoScholarScope:
    def test_post_render_page_performance_is_registered(self) -> None:
        data = yaml.safe_load((ROOT / "_quarto.yml").read_text(encoding="utf-8"))
        steps = data.get("project", {}).get("post-render", [])
        assert any("post_render_page_performance" in step for step in steps)

    """Google Scholar exports belong on research articles, not every route."""

    def test_project_default_disables_global_scholar_bibliography_export(self) -> None:
        data = yaml.safe_load((ROOT / "_quarto.yml").read_text(encoding="utf-8"))
        assert data["format"]["html"].get("google-scholar") is False

    def test_articles_metadata_enables_scholar_for_research_pages(self) -> None:
        data = yaml.safe_load((ROOT / "articles" / "_metadata.yml").read_text(encoding="utf-8"))
        assert data["format"]["html"].get("google-scholar") is True

    def test_pages_metadata_disables_scholar_for_site_chrome(self) -> None:
        path = ROOT / "pages" / "_metadata.yml"
        assert path.is_file(), "pages/_metadata.yml must disable scholar for About and similar hubs"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data.get("google-scholar") is False


class TestPostRenderHeadPerformance:
    """Post-render HTML fixes for duplicate assets and dev-only tooling."""

    SAMPLE_HEAD = """<!DOCTYPE html><html><head>
<link href="site_libs/bootstrap/bootstrap-light.min.css" rel="stylesheet" class="quarto-color-scheme" id="quarto-bootstrap">
<link href="site_libs/bootstrap/bootstrap-dark.min.css" rel="stylesheet" class="quarto-color-scheme quarto-color-alternate" id="quarto-bootstrap">
<link href="site_libs/bootstrap/bootstrap-light.min.css" rel="stylesheet" class="quarto-color-scheme-extra" id="quarto-bootstrap">
<script src="site_libs/quarto-html/axe/axe-check.js"></script>
<meta name="citation_reference" content="citation_title=Noise;,citation_author=Nobody;">
<section id="refs"><div id="ref-smith2020">Smith 2020</div></section>
</head><body><p>Hello</p></body></html>"""

    def test_removes_duplicate_quarto_color_scheme_extra_stylesheets(self) -> None:
        out = process_html_head_performance(self.SAMPLE_HEAD)
        head = _head(out)
        assert head.count("bootstrap-light.min.css") == 1

    def test_strips_axe_check_from_production_html(self) -> None:
        out = process_html_head_performance(self.SAMPLE_HEAD)
        assert "axe-check.js" not in out

    def test_prunes_citation_reference_tags_not_present_in_refs_section(self) -> None:
        out = process_html_head_performance(self.SAMPLE_HEAD)
        assert 'name="citation_reference"' not in out

    def test_keeps_citation_reference_when_title_matches_refs_section(self) -> None:
        html = """<!DOCTYPE html><html><head>
<meta name="citation_reference" content="citation_title=Smith 2020;,citation_author=Smith;">
</head><body><section id="refs"><div id="ref-smith2020">Smith 2020</div></section></body></html>"""
        out = process_html_head_performance(html)
        assert 'name="citation_reference"' in out

    def test_non_research_fixture_stays_under_citation_meta_byte_budget(self) -> None:
        """Navigation-style pages must not ship the full 995-entry scholar bibliography."""
        html = (ROOT / "tests" / "fixtures" / "page-payload-about-head.html").read_text(
            encoding="utf-8"
        )
        out = process_html_head_performance(html)
        meta_bytes = sum(
            len(line) for line in _head(out).splitlines() if 'name="citation_reference"' in line
        )
        assert meta_bytes < 5000
