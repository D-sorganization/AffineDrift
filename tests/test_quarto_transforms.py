"""Tests for reusable Quarto transformation helpers."""

from __future__ import annotations

from src.tools.utils.quarto_transforms import (
    clean_quarto_latex_commands,
    convert_quarto_environments,
    convert_quarto_equations,
    convert_quarto_figures,
    convert_quarto_references,
    convert_quarto_sections,
    create_quarto_frontmatter,
)


def test_convert_quarto_environments_rewrites_callouts_and_quotes() -> None:
    """LaTeX prose environments should become Quarto-friendly blocks."""
    content = (
        r"\begin{abstract}Summary\end{abstract}"
        "\n"
        r"\begin{keypoint}[x]Important\end{keypoint}"
        "\n"
        r"\begin{quote}Quoted text\end{quote}"
    )

    converted = convert_quarto_environments(content)

    assert "## Abstract" in converted
    assert "**Key Point:** Important" in converted
    assert "> Quoted text" in converted


def test_convert_quarto_equations_wraps_equation_and_align_blocks() -> None:
    """Equation and align environments should be converted to dollar blocks."""
    content = r"\begin{equation}x=1\end{equation}" "\n" r"\begin{align}a&=b\end{align}"

    converted = convert_quarto_equations(content)

    assert "$$x=1$$" in converted
    assert r"\begin{align}" in converted
    assert r"\end{align}" in converted
    assert converted.count("$$") >= 4


def test_convert_quarto_figures_uses_caption_or_placeholder() -> None:
    """Figure captions are retained and TikZ blocks become placeholders."""
    content = (
        r"\begin{figure}\caption{A diagram}\end{figure}"
        "\n"
        r"\begin{tikzpicture}draw;\end{tikzpicture}"
    )

    converted = convert_quarto_figures(content)

    assert "[Figure: A diagram]" in converted
    assert "[Figure: TikZ diagram - see PDF version]" in converted


def test_convert_quarto_references_uses_quarto_ids() -> None:
    """LaTeX refs and labels should become Quarto reference syntax."""
    content = (
        r"See \cref{sec:intro} and \ref{eq:main}. "
        r"\label{eq:main}\label{fig:plot}\label{sec:intro}\label{custom}"
    )

    converted = convert_quarto_references(content)

    assert "[@sec:intro]" in converted
    assert "[@eq:main]" in converted
    assert "{#eq-main}" in converted
    assert "{#fig-plot}" in converted
    assert "{#sec-intro}" in converted
    assert "{#custom}" in converted


def test_clean_quarto_latex_commands_replaces_tables_and_theorems() -> None:
    """Custom commands and structural blocks should become Markdown placeholders."""
    content = (
        r"\bvec{x} \Feq " r"\begin{table}tabular\end{table} " r"\begin{theorem}Result\end{theorem}"
    )

    converted = clean_quarto_latex_commands(content)

    assert "**x**" in converted
    assert "**Feq**" in converted
    assert "[Table]" in converted
    assert "**theorem:** Result" in converted


def test_create_frontmatter_and_section_conversion() -> None:
    """Frontmatter and paragraph headings should use Quarto/Markdown syntax."""
    frontmatter = create_quarto_frontmatter(
        {"title": "Title", "author": "Author", "date": "2026-06-10"}
    )
    sections = convert_quarto_sections(r"\paragraph{Small}\subparagraph{Tiny}")

    assert 'title: "Title"' in frontmatter
    assert "toc-depth: 3" in frontmatter
    assert "##### Small" in sections
    assert "###### Tiny" in sections
