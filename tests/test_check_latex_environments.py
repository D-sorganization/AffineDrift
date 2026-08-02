"""Tests for check_latex_environments.py.

Pandoc renders maths environments in a `.qmd` and drops the rest, so the content
inside a `\\begin{tabular}` or a `\\begin{intuitionbox}` never reaches the page.
The allow-list is maths-only because an earlier probe assumed `table` and
`itemize` were safe -- they are ordinary LaTeX -- and 24 tables stayed missing
for another round as a result.
"""

from __future__ import annotations

from scripts.check_latex_environments import find


class TestMathsIsKept:
    """Maths environments render and must not be reported."""

    def test_equation(self) -> None:
        assert find("\\begin{equation}\nx = y\n\\end{equation}\n") == []

    def test_align(self) -> None:
        assert find("\\begin{align}\na &= b\n\\end{align}\n") == []

    def test_starred_form(self) -> None:
        assert find("\\begin{align*}\na &= b\n\\end{align*}\n") == []

    def test_matrix_inside_maths(self) -> None:
        assert find("$$\n\\begin{bmatrix} a \\\\ b \\end{bmatrix}\n$$\n") == []


class TestEverythingElseIsReported:
    """Each of these was found dropping real content from the site."""

    def test_tabular(self) -> None:
        found = find("\\begin{tabular}{ll}\na & b\n\\end{tabular}\n")
        assert [name for _, name in found] == ["tabular"]

    def test_table(self) -> None:
        assert [name for _, name in find("\\begin{table}[h]\nx\n\\end{table}\n")] == ["table"]

    def test_a_custom_box(self) -> None:
        found = find("\\begin{intuitionbox}\nA trajectory is a curve.\n\\end{intuitionbox}\n")
        assert [name for _, name in found] == ["intuitionbox"]

    def test_itemize_is_not_safe_just_because_it_is_standard_latex(self) -> None:
        """The assumption that cost 24 tables a round."""
        assert [name for _, name in find("\\begin{itemize}\n\\item x\n\\end{itemize}\n")] == [
            "itemize"
        ]

    def test_figure(self) -> None:
        assert [name for _, name in find("\\begin{figure}\nx\n\\end{figure}\n")] == ["figure"]

    def test_reports_the_line_number(self) -> None:
        found = find("Prose.\n\nMore prose.\n\n\\begin{tabular}{ll}\na & b\n\\end{tabular}\n")
        assert found == [(5, "tabular")]


class TestFencedCode:
    """A LaTeX example inside a code block is being shown, not rendered."""

    def test_ignores_an_environment_in_a_fence(self) -> None:
        assert find("```latex\n\\begin{tabular}{ll}\na & b\n\\end{tabular}\n```\n") == []

    def test_finds_one_after_the_fence_closes(self) -> None:
        text = (
            "```\n\\begin{table}\nx\n\\end{table}\n```\n\n\\begin{tabular}{l}\na\n\\end{tabular}\n"
        )
        assert [name for _, name in find(text)] == ["tabular"]
