"""Layout contract for the AffineDrift home page (EPIC #3140, A1+A2).

The home page must be content-first: no reviewer-facing meta-commentary,
no inline styles, no hardcoded hex colors, no decorative gradient cards.
These tests are the executable spec for the rewrite.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_style_discipline import (
    StyleDisciplineConfig,
    check_repository,
    find_violations_in_text,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_QMD = REPO_ROOT / "index.qmd"


@pytest.fixture(scope="module")
def home_text() -> str:
    return INDEX_QMD.read_text(encoding="utf-8")


class TestMetaCommentaryRemoved:
    """A1: the reviewer-facing meta sections are gone."""

    @pytest.mark.parametrize(
        "forbidden_phrase",
        [
            "For Technical Reviewers",
            "How to Read AffineDrift",
            "Verification and Review Workflow",
            "For Practitioners",
            "For Laypersons",
            "For Mathematicians",
        ],
    )
    def test_phrase_absent(self, home_text: str, forbidden_phrase: str) -> None:
        assert (
            forbidden_phrase not in home_text
        ), f"Home page still contains meta-commentary phrase: {forbidden_phrase!r}"

    @pytest.mark.parametrize(
        "forbidden_class",
        ["reviewer-section", "audience-section", "audience-card", "approach-section"],
    )
    def test_class_absent(self, home_text: str, forbidden_class: str) -> None:
        assert (
            forbidden_class not in home_text
        ), f"Home page still references abandoned class: {forbidden_class!r}"


class TestContentFirstStructure:
    """A2: the new content-first sections are present."""

    def test_hero_h1_is_affinedrift(self, home_text: str) -> None:
        assert "<h1>AffineDrift</h1>" in home_text

    def test_subtitle_present(self, home_text: str) -> None:
        assert "Scientific Notes on Golf Mechanics" in home_text

    def test_core_framework_equation_present(self, home_text: str) -> None:
        # The control-affine system is the page's central artifact.
        assert "f(x) + g(x)u" in home_text

    def test_provenance_aside_present(self, home_text: str) -> None:
        assert "provenance-note" in home_text

    def test_entry_list_present(self, home_text: str) -> None:
        # The new "Latest writing" block uses the .entry-list primitive.
        assert "entry-list" in home_text

    def test_books_block_links_both_textbooks(self, home_text: str) -> None:
        assert "The_Physics_of_Golf" in home_text
        assert "The_Geometry_of_Motion" in home_text

    def test_connect_links_present(self, home_text: str) -> None:
        for href in ("pages/about.html", "pages/contact.html", "pages/collaborate.html"):
            assert href in home_text


class TestStyleDiscipline:
    """B4: zero style-discipline violations on the home page."""

    def test_no_inline_style_attribute(self, home_text: str) -> None:
        violations = [
            v for v in find_violations_in_text(home_text, suffix=".qmd") if v.rule == "inline-style"
        ]
        assert violations == [], (
            "Inline style= still present at line(s): " f"{[v.line for v in violations]}"
        )

    def test_no_linear_gradient(self, home_text: str) -> None:
        violations = [
            v for v in find_violations_in_text(home_text, suffix=".qmd") if v.rule == "gradient"
        ]
        assert violations == []

    def test_no_hardcoded_hex(self, home_text: str) -> None:
        violations = [
            v
            for v in find_violations_in_text(home_text, suffix=".qmd")
            if v.rule == "hardcoded-hex"
        ]
        assert violations == []

    def test_repository_scope_index_clean(self) -> None:
        """End-to-end: index.qmd passes the global discipline checker."""
        config = StyleDisciplineConfig(
            repo_root=REPO_ROOT,
            qmd_globs=("index.qmd",),
            css_globs=(),
        )
        violations = check_repository(config)
        assert violations == [], "\n".join(v.format() for v in violations[:20])


class TestSidebarTrimmed:
    """A2: home sidebar collapses to three sections matching D1 IA."""

    def test_three_sidebar_section_toggles(self, home_text: str) -> None:
        # Each toggle button carries class "sidebar-section-toggle".
        count = home_text.count("sidebar-section-toggle")
        assert count == 3, f"Expected 3 sidebar toggles, found {count}"

    def test_toc_anchors_match_sections(self, home_text: str) -> None:
        # Every right-rail TOC link must point to an anchor that exists.
        import re

        toc_block = re.search(
            r"<aside class=\"home-toc\">.*?</aside>",
            home_text,
            re.DOTALL,
        )
        assert toc_block is not None, "home-toc aside missing"
        href_anchors = re.findall(r'href="#([\w-]+)"', toc_block.group())
        for anchor in href_anchors:
            assert (
                f'id="{anchor}"' in home_text
            ), f"TOC links to #{anchor} but no element has that id"
