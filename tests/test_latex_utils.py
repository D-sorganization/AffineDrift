"""Tests for the shared LaTeX parsing utilities (DRY consolidation).

Validates that the shared utilities produce correct output for all
three converter targets (HTML, Quarto .qmd, and simple Quarto).
"""

from __future__ import annotations

import pytest

from src.tools.utils.latex_utils import (
    LaTeXMetadata,
    clean_common_latex,
    convert_lists_to_html,
    convert_lists_to_markdown,
    convert_quotes,
    convert_references,
    convert_sections_to_html,
    convert_sections_to_markdown,
    convert_text_formatting_to_html,
    convert_text_formatting_to_markdown,
    convert_urls_to_html,
    convert_urls_to_markdown,
    extract_abstract,
    extract_author,
    extract_body,
    extract_metadata,
    extract_title,
    remove_comments,
    remove_labels,
    remove_spacing_commands,
)

# ─── Metadata Extraction ────────────────────────────────────────


class TestTitleExtraction:
    """Test extract_title across various LaTeX inputs."""

    def test_simple_title(self) -> None:
        assert extract_title(r"\title{My Article}") == "My Article"

    def test_title_with_textbf(self) -> None:
        result = extract_title(r"\title{\textbf{Bold Title}}")
        assert result == "Bold Title"

    def test_title_with_linebreak(self) -> None:
        result = extract_title(r"\title{First\\Second}")
        assert "First" in result and "Second" in result

    def test_fallback_when_no_title(self) -> None:
        assert extract_title("No title here", "Default") == "Default"

    def test_default_fallback(self) -> None:
        assert extract_title("") == "Untitled Article"


class TestAuthorExtraction:
    """Test extract_author."""

    def test_simple_author(self) -> None:
        assert extract_author(r"\author{John Doe}") == "John Doe"

    def test_no_author(self) -> None:
        assert extract_author("no author") == ""


class TestAbstractExtraction:
    """Test extract_abstract."""

    def test_simple_abstract(self) -> None:
        latex = r"\begin{abstract}This is the abstract.\end{abstract}"
        assert extract_abstract(latex) == "This is the abstract."

    def test_no_abstract(self) -> None:
        assert extract_abstract("no abstract") == ""


class TestBodyExtraction:
    """Test extract_body."""

    def test_extracts_between_document_markers(self) -> None:
        latex = r"\begin{document}Body content here\end{document}"
        assert extract_body(latex) == "Body content here"

    def test_full_content_when_no_markers(self) -> None:
        latex = "Just some content"
        assert extract_body(latex) == "Just some content"


class TestMetadataExtraction:
    """Test the combined extract_metadata function."""

    def test_full_metadata(self) -> None:
        latex = r"""
        \title{Test Article}
        \author{Jane Smith}
        \begin{abstract}Abstract text.\end{abstract}
        \tableofcontents
        \begin{document}Body\end{document}
        """
        meta = extract_metadata(latex)
        assert isinstance(meta, LaTeXMetadata)
        assert meta.title == "Test Article"
        assert meta.author == "Jane Smith"
        assert meta.abstract == "Abstract text."
        assert meta.has_toc is True


# ─── Section Conversion ─────────────────────────────────────────


class TestSectionConversion:
    """Test section heading conversion for both formats."""

    @pytest.mark.parametrize(
        "latex,expected_md",
        [
            (r"\section{Introduction}", "# Introduction"),
            (r"\subsection{Background}", "## Background"),
            (r"\subsubsection{Details}", "### Details"),
        ],
        ids=["section", "subsection", "subsubsection"],
    )
    def test_to_markdown(self, latex: str, expected_md: str) -> None:
        result = convert_sections_to_markdown(latex)
        assert expected_md in result

    @pytest.mark.parametrize(
        "latex,expected_html",
        [
            (r"\section{Introduction}", "<h2>Introduction</h2>"),
            (r"\subsection{Background}", "<h3>Background</h3>"),
            (r"\subsubsection{Details}", "<h4>Details</h4>"),
        ],
        ids=["section", "subsection", "subsubsection"],
    )
    def test_to_html(self, latex: str, expected_html: str) -> None:
        result = convert_sections_to_html(latex)
        assert expected_html in result


# ─── Text Formatting ────────────────────────────────────────────


class TestTextFormatting:
    """Test text formatting conversion."""

    def test_bold_to_markdown(self) -> None:
        assert convert_text_formatting_to_markdown(r"\textbf{bold}") == "**bold**"

    def test_italic_to_markdown(self) -> None:
        assert convert_text_formatting_to_markdown(r"\emph{em}") == "*em*"

    def test_code_to_markdown(self) -> None:
        assert convert_text_formatting_to_markdown(r"\texttt{code}") == "`code`"

    def test_bold_to_html(self) -> None:
        assert convert_text_formatting_to_html(r"\textbf{bold}") == "<strong>bold</strong>"

    def test_italic_to_html(self) -> None:
        assert convert_text_formatting_to_html(r"\emph{em}") == "<em>em</em>"

    def test_code_to_html(self) -> None:
        assert convert_text_formatting_to_html(r"\texttt{code}") == "<code>code</code>"


# ─── List Conversion ─────────────────────────────────────────────


class TestListConversion:
    """Test list environment conversion."""

    def test_itemize_to_markdown(self) -> None:
        latex = r"\begin{itemize}\item First\item Second\end{itemize}"
        result = convert_lists_to_markdown(latex)
        assert "- First" in result
        assert "- Second" in result

    def test_enumerate_to_markdown(self) -> None:
        latex = r"\begin{enumerate}\item First\item Second\end{enumerate}"
        result = convert_lists_to_markdown(latex)
        assert "1. " in result
        assert "2. " in result

    def test_itemize_to_html(self) -> None:
        latex = r"\begin{itemize}\item First\item Second\end{itemize}"
        result = convert_lists_to_html(latex)
        assert "<ul>" in result
        assert "<li>" in result

    def test_enumerate_to_html(self) -> None:
        latex = r"\begin{enumerate}\item First\item Second\end{enumerate}"
        result = convert_lists_to_html(latex)
        assert "<ol>" in result
        assert "<li>" in result


# ─── Cleanup Utilities ──────────────────────────────────────────


class TestCleanup:
    """Test cleanup utility functions."""

    def test_remove_comments(self) -> None:
        content = "text\n% comment line\nmore text % inline comment"
        result = remove_comments(content)
        assert "comment" not in result
        assert "text" in result

    def test_remove_labels(self) -> None:
        content = r"Text \label{eq:main} more text"
        result = remove_labels(content)
        assert r"\label" not in result
        assert "Text" in result

    def test_remove_spacing(self) -> None:
        content = r"Before \vspace{1cm} after \hspace{2em} end \small text"
        result = remove_spacing_commands(content)
        assert r"\vspace" not in result
        assert r"\hspace" not in result
        assert r"\small" not in result

    def test_clean_common(self) -> None:
        """clean_common_latex applies all cleanup in one pass."""
        content = r"""\maketitle
        \title{Test}
        \label{fig:1}
        \vspace{1cm}
        % comment
        Real content here"""
        result = clean_common_latex(content)
        assert r"\maketitle" not in result
        assert r"\label" not in result
        assert "Real content here" in result


# ─── URL / Reference Conversion ─────────────────────────────────


class TestURLConversion:
    """Test URL and reference conversion."""

    def test_url_to_markdown(self) -> None:
        result = convert_urls_to_markdown(r"\url{https://example.com}")
        assert "[https://example.com](https://example.com)" in result

    def test_href_to_markdown(self) -> None:
        result = convert_urls_to_markdown(r"\href{https://example.com}{Example}")
        assert "[Example](https://example.com)" in result

    def test_url_to_html(self) -> None:
        result = convert_urls_to_html(r"\url{https://example.com}")
        assert 'href="https://example.com"' in result

    def test_href_to_html(self) -> None:
        result = convert_urls_to_html(r"\href{https://example.com}{Example}")
        assert "Example" in result
        assert 'href="https://example.com"' in result


class TestReferences:
    """Test LaTeX reference conversion."""

    def test_ref(self) -> None:
        assert r"\ref" not in convert_references(r"\ref{eq:1}")

    def test_cref_to_figure(self) -> None:
        result = convert_references(r"\cref{fig:1}")
        assert "Figure" in result


class TestQuotes:
    """Test LaTeX quote conversion."""

    def test_double_backtick(self) -> None:
        assert convert_quotes("``hello''") == '"hello"'
