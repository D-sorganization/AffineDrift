"""Tests for check_quarto_xrefs.py.

An unresolved `@sec-foo` does not fail the render. Quarto exits 0 and prints the
raw key on the page where the link should be. The book carried 132 of these. The
cases below are the real ones, reduced to the smallest form that reproduces them.
"""

from __future__ import annotations

from pathlib import Path

from scripts.check_quarto_xrefs import scan, trim


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "ch.qmd"
    path.write_text(text, encoding="utf-8")
    return path


class TestTrim:
    """The key pattern is greedy, so sentence punctuation has to come back off."""

    def test_drops_a_trailing_period(self) -> None:
        assert trim("sec-x_factor.") == "sec-x_factor"

    def test_keeps_an_internal_period(self) -> None:
        assert trim("sec-ch11.worked") == "sec-ch11.worked"

    def test_drops_a_trailing_comma(self) -> None:
        assert trim("eq-cor_definition,") == "eq-cor_definition"


class TestDefinitions:
    """What counts as defining an anchor."""

    def test_a_heading_anchor_defines(self, tmp_path: Path) -> None:
        defined, _, _ = scan(write(tmp_path, "## Solving for the Forces {#sec-solving}\n"))
        assert "sec-solving" in defined

    def test_an_equation_anchor_defines(self, tmp_path: Path) -> None:
        defined, _, _ = scan(write(tmp_path, "$$\ne = mc^2\n$$ {#eq-energy}\n"))
        assert "eq-energy" in defined

    def test_a_figure_div_defines(self, tmp_path: Path) -> None:
        defined, _, _ = scan(write(tmp_path, "::: {#fig-swing}\n![](a.png)\n:::\n"))
        assert "fig-swing" in defined


class TestCalloutTitles:
    """The trap: a callout is a div, so its `##` is a title, not a section.

    Quarto ignores an id placed there. The reference stays dead while the source
    looks correct -- this is how `sec-triple_pendulum_mass_matrix` survived a
    fix that appeared to work.
    """

    def test_an_id_on_a_callout_title_does_not_define(self, tmp_path: Path) -> None:
        text = "## Real Section\n\n::: {.callout-note}\n## Callout Title {#sec-mass_matrix}\n:::\n"
        defined, _, stranded = scan(write(tmp_path, text))
        assert "sec-mass_matrix" not in defined
        assert [key for key, _ in stranded] == ["sec-mass_matrix"]

    def test_a_heading_after_the_callout_closes_still_defines(self, tmp_path: Path) -> None:
        text = "::: {.callout-note}\n## Callout Title\n:::\n\n## Real Section {#sec-real}\n"
        defined, _, stranded = scan(write(tmp_path, text))
        assert "sec-real" in defined
        assert stranded == []

    def test_a_non_callout_div_does_not_strand(self, tmp_path: Path) -> None:
        text = "::: {.panel-tabset}\n## A Tab {#sec-tab}\n:::\n"
        defined, _, stranded = scan(write(tmp_path, text))
        assert "sec-tab" in defined
        assert stranded == []


class TestReferences:
    """What counts as referencing an anchor."""

    def test_a_plain_reference_is_collected(self, tmp_path: Path) -> None:
        _, used, _ = scan(write(tmp_path, "See @sec-x_factor for the model.\n"))
        assert [key for key, _ in used] == ["sec-x_factor"]

    def test_a_citation_is_not_a_cross_reference(self, tmp_path: Path) -> None:
        """`[@nesbit2005]` is a bibliography key, checked elsewhere."""
        _, used, _ = scan(write(tmp_path, "As shown [@nesbit2005] and [@penner2003].\n"))
        assert used == []

    def test_a_reference_inside_inline_code_is_ignored(self, tmp_path: Path) -> None:
        _, used, _ = scan(write(tmp_path, "Write `@sec-example` to link.\n"))
        assert used == []

    def test_a_reference_inside_a_fence_is_ignored(self, tmp_path: Path) -> None:
        _, used, _ = scan(write(tmp_path, "```\n@sec-example\n```\n"))
        assert used == []

    def test_an_email_like_string_is_not_a_reference(self, tmp_path: Path) -> None:
        _, used, _ = scan(write(tmp_path, "Contact someone@sec-ondary.example.\n"))
        assert used == []
