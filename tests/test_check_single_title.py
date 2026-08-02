"""Tests for check_single_title.py.

Two ways a page's title goes wrong, both invisible in the source and both
shipped at some point:

  * a YAML `title:` alongside a body H1 renders the title twice, numbered
    separately, which inflates every chapter number after it (#3700, #3705);
  * a blank line after the opening `---` stops Pandoc reading the block as
    frontmatter at all, so the metadata keys print as page content -- ch01
    shipped `description: "If you've ever taken a golf lesson..."` as a
    chapter heading.

The cases below are the real ones, reduced to the smallest form that
reproduces them.
"""

from __future__ import annotations

from pathlib import Path

from scripts.check_single_title import (
    blank_first_line,
    body_h1,
    fragments,
    frontmatter_title,
    same_heading,
)


def lines(text: str) -> list[str]:
    return text.splitlines()


class TestFrontmatterTitle:
    """Finding a `title:` key, and not finding one past the closing fence."""

    def test_finds_a_title(self) -> None:
        assert frontmatter_title(lines('---\ntitle: "A"\ndescription: "d"\n---\n'))

    def test_ignores_a_title_after_the_block_closes(self) -> None:
        """A `title:` in the body is prose, not metadata."""
        assert not frontmatter_title(lines('---\ndescription: "d"\n---\n\ntitle: not metadata\n'))

    def test_absent_when_only_description(self) -> None:
        assert not frontmatter_title(lines('---\ndescription: "d"\n---\n'))

    def test_absent_when_there_is_no_frontmatter(self) -> None:
        assert not frontmatter_title(lines("# Just A Heading\n"))


class TestBodyH1:
    """Only a real H1 counts."""

    def test_finds_a_heading_with_an_anchor(self) -> None:
        found = body_h1(lines('---\ndescription: "d"\n---\n\n# A Chapter {#sec-a}\n'))
        assert found == "# A Chapter {#sec-a}"

    def test_ignores_a_hash_inside_fenced_code(self) -> None:
        assert body_h1(lines("```{python}\n# not a heading\n```\n")) is None

    def test_ignores_a_level_two_heading(self) -> None:
        assert body_h1(lines("## A Section\n")) is None


class TestBlankFirstLine:
    """The failure that looks like nothing at all in the source."""

    def test_detects_the_blank_line(self) -> None:
        assert blank_first_line(lines('---\n\ntitle: "A"\ndescription: "d"\n---\n'))

    def test_accepts_a_well_formed_block(self) -> None:
        assert not blank_first_line(lines('---\ntitle: "A"\n---\n'))

    def test_ignores_a_file_with_no_frontmatter(self) -> None:
        assert not blank_first_line(lines("\n# A Heading\n"))

    def test_ignores_a_single_line_file(self) -> None:
        assert not blank_first_line(lines("---\n"))


class TestSameHeading:
    """The defect is one heading rendered twice, not merely having a title.

    Every standalone article on this site has a document `title:` and a first
    H1 that is a section -- "Abstract", "Introduction", "Part 1: ...". Those are
    two different headings and are correct. Comparing only "does a title exist"
    flagged all eleven of them.
    """

    def test_identical_text_is_the_defect(self) -> None:
        assert same_heading("Critique: Hybrid Tangent Spaces", "# Critique: Hybrid Tangent Spaces")

    def test_a_document_title_and_an_abstract_are_not(self) -> None:
        assert not same_heading("A Control-Theoretic Analysis of Drift", "# Abstract")

    def test_a_document_title_and_an_introduction_are_not(self) -> None:
        assert not same_heading("Secondary Axis Stability in Golf Clubs", "# Introduction")

    def test_a_book_title_and_a_preface_are_not(self) -> None:
        assert not same_heading("The Physics of Golf", "# Preface")

    def test_an_anchor_on_the_heading_is_ignored(self) -> None:
        assert same_heading("The Language of Motion", "# The Language of Motion {#sec-02_lang}")

    def test_a_chapter_number_prefix_is_ignored(self) -> None:
        """#3705's restored titles carried one; Quarto numbers chapters itself."""
        assert same_heading("Chapter 1: A Primer on Linear Algebra", "# A Primer on Linear Algebra")


class TestFragments:
    """A `{{< include >}}`d file is not a page and must not be checked as one.

    Quarto discards the frontmatter of an included file, so a `title:` there is
    dead metadata. 23 of the 27 files in the Geometry of Motion mirror are
    fragments; checking them as pages reports a dozen duplicate titles that do
    not exist, and an earlier pass "fixed" all twelve before the `<title>` tag
    gave it away.
    """

    def test_finds_an_included_file(self, tmp_path: Path) -> None:
        (tmp_path / "volume0.qmd").write_text(
            "# Volume 0\n\n{{< include vol0_ch01.qmd >}}\n", encoding="utf-8"
        )
        (tmp_path / "vol0_ch01.qmd").write_text("# Chapter\n", encoding="utf-8")
        assert fragments(tmp_path) == {"vol0_ch01.qmd"}

    def test_ignores_a_file_nothing_includes(self, tmp_path: Path) -> None:
        (tmp_path / "page.qmd").write_text("# A Page\n", encoding="utf-8")
        assert fragments(tmp_path) == set()

    def test_handles_a_path_prefixed_include(self, tmp_path: Path) -> None:
        (tmp_path / "book.qmd").write_text("{{< include parts/intro.qmd >}}\n", encoding="utf-8")
        assert fragments(tmp_path) == {"intro.qmd"}


class TestTheBrokenStates:
    """Each state the book actually shipped."""

    def test_3705_state_is_rejected(self) -> None:
        """Blank line plus restored title: the frontmatter does not parse."""
        text = '---\n\ntitle: "The Triple Pendulum"\ndescription: "d"\n---\n\n# The Triple Pendulum: Adding the Wrists {#sec-triple_pendulum}\n'
        assert blank_first_line(lines(text))

    def test_3700_state_is_rejected(self) -> None:
        """Title and body heading together: two numbered <h1>."""
        text = '---\ntitle: "The Language of Motion"\n---\n\n# The Language of Motion {#sec-02_language_of_motion}\n'
        assert not blank_first_line(lines(text))
        assert frontmatter_title(lines(text))
        assert body_h1(lines(text)) is not None

    def test_the_fixed_state_is_accepted(self) -> None:
        text = (
            '---\ndescription: "d"\n---\n\n# The Language of Motion {#sec-02_language_of_motion}\n'
        )
        assert not blank_first_line(lines(text))
        assert not frontmatter_title(lines(text))
        assert body_h1(lines(text)) is not None
