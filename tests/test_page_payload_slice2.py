"""UX slice 2 (#5165): page payload and render-blocking guardrails."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from scripts.post_render_page_performance import process_html_head_performance

ROOT = Path(__file__).resolve().parents[1]


def _head(html: str) -> str:
    return html.split("</head>", maxsplit=1)[0]


def _citation_reference_count(html: str) -> int:
    return len(re.findall(r'name="citation_reference"', html))


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
        assert "google-scholar" not in data

    def test_pages_metadata_disables_scholar_for_site_chrome(self) -> None:
        path = ROOT / "pages" / "_metadata.yml"
        assert path.is_file(), "pages/_metadata.yml must disable scholar for About and similar hubs"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data.get("google-scholar") is False


class TestPostRenderHeadPerformance:
    """Post-render HTML fixes for duplicate assets and dev-only tooling."""

    SAMPLE_HEAD = """<!DOCTYPE html><html><head>
<link href="site_libs/bootstrap/bootstrap-light.min.css" rel="stylesheet" class="quarto-color-scheme" id="quarto-bootstrap">
<link href="site_libs/bootstrap/bootstrap-dark.min.css" rel="stylesheet" class="quarto-color-scheme quarto-color-alternate" id="quarto-bootstrap-dark">
<link href="site_libs/bootstrap/bootstrap-light.min.css" rel="stylesheet" class="quarto-color-scheme-extra" id="quarto-bootstrap-extra">
<script src="site_libs/quarto-html/axe/axe-check.js"></script>
<meta name="citation_reference" content="citation_title=Noise;,citation_author=Nobody;">
</head><body><div id="refs"><div id="ref-smith2020">Smith 2020</div></div><p>Hello</p></body></html>"""

    def test_preserves_quarto_color_scheme_extra_stylesheets(self) -> None:
        """Removing quarto-color-scheme-extra breaks Quarto theme JS (#5179 review)."""
        out = process_html_head_performance(self.SAMPLE_HEAD)
        head = _head(out)
        assert "quarto-color-scheme-extra" in head
        assert head.count("bootstrap-light.min.css") == 2

    def test_dark_color_scheme_links_use_disabled_stylesheet_without_print_onload(self) -> None:
        polluted = self.SAMPLE_HEAD.replace(
            "quarto-color-alternate",
            'quarto-color-alternate" media="print" onload="this.media=\'all\'"',
            1,
        )
        head = _head(process_html_head_performance(polluted))
        for tag in re.findall(r"<link\b[^>]*quarto-color-alternate[^>]*>", head, re.I):
            low = tag.lower()
            assert (
                'rel="disabled-stylesheet"' in low and "media=" not in low and "onload=" not in low
            )

    def test_strips_axe_check_from_production_html(self) -> None:
        out = process_html_head_performance(self.SAMPLE_HEAD)
        assert "axe-check.js" not in out

    def test_prunes_citation_reference_tags_not_present_in_refs_section(self) -> None:
        out = process_html_head_performance(self.SAMPLE_HEAD)
        assert _citation_reference_count(out) == 0

    def test_keeps_citation_reference_when_title_matches_pandoc_refs_div(self) -> None:
        html = """<!DOCTYPE html><html><head>
<meta name="citation_reference" content="citation_title=Smith 2020;,citation_author=Smith;">
<meta name="citation_reference" content="citation_title=Unrelated global bib entry;,citation_author=Nobody;">
</head><body><div id="refs" class="references csl-bib-body"><div id="ref-smith2020" class="csl-entry">Smith 2020</div></div></body></html>"""
        out = process_html_head_performance(html)
        assert _citation_reference_count(out) == 1
        assert "Smith 2020" in out
        assert "Unrelated global" not in out

    def test_quarto_fixture_prunes_global_scholar_bloat_but_keeps_cited_work(self) -> None:
        """Fixture HTML is Quarto-rendered; only on-page #refs entries keep citation_reference meta."""
        html = (ROOT / "tests" / "fixtures" / "page-payload-article-scholar.html").read_text(
            encoding="utf-8"
        )
        assert '<div id="refs"' in html
        assert _citation_reference_count(html) > 1
        out = process_html_head_performance(html)
        assert _citation_reference_count(out) == 1
        assert "mathematical introduction to robotic manipulation" in out.lower()
        assert "global noise entry" not in out.lower()

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


class TestPageContainerMinHeightCLS:
    """Mobile article layout shift (CLS ~0.13) from inline min-height (#5211)."""

    def test_quarto_theme_css_neutralizes_quarto_content_min_height(self) -> None:
        css = (ROOT / "css" / "components" / "quarto-theme.css").read_text(encoding="utf-8")
        match = re.search(r"#quarto-content[^{]*\{([^}]*)\}", css, re.DOTALL)
        assert match, "Missing #quarto-content rule in css/components/quarto-theme.css"
        block = match.group(1)
        assert "min-height" in block and "!important" in block

    def test_site_head_mobile_declares_quarto_content_min_height_auto(self) -> None:
        head_html = (ROOT / "_includes" / "site-head.html").read_text(encoding="utf-8")
        assert "min-height: auto !important;" in head_html

    def test_strip_inline_page_container_min_height(self) -> None:
        from scripts.post_render_page_performance import strip_inline_page_container_min_height

        html_with_inline = '<div id="quarto-content" class="quarto-container" style="min-height: calc(100vh - 60px); color: red;"><p>Content</p></div>'
        cleaned = strip_inline_page_container_min_height(html_with_inline)
        assert "min-height" not in cleaned
        assert "color: red" in cleaned
        assert "quarto-content" in cleaned

    def test_neutralize_nav_min_height(self, tmp_path: Path) -> None:
        from scripts.post_render_page_performance import neutralize_nav_min_height

        sample_nav = """
        const mainContainer = window.document.querySelector(".quarto-container");
        if (mainContainer) {
          mainContainer.style.minHeight = "calc(100vh - " + bodyOffset + "px)";
        }
        """
        nav_file = tmp_path / "quarto-nav.js"
        nav_file.write_text(sample_nav, encoding="utf-8")
        modified = neutralize_nav_min_height(nav_file)
        assert modified is True
        result = nav_file.read_text(encoding="utf-8")
        assert 'mainContainer.style.minHeight = "calc' not in result
        assert "neutralized for CLS" in result
