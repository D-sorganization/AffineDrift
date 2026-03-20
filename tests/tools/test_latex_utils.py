"""Tests for src.tools.utils.latex_utils — shared LaTeX parsing utilities."""

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
    remove_document_structure,
    remove_labels,
    remove_spacing_commands,
)


class TestExtractTitle:
    """Tests for extract_title()."""

    def test_extracts_simple_title(self) -> None:
        r"""Should extract title from \title{...}."""
        result = extract_title(r"\title{My Article}")
        assert result == "My Article"

    def test_returns_fallback_when_no_title(self) -> None:
        """Should return fallback when no title found."""
        result = extract_title("No title here.", fallback="Default")
        assert result == "Default"

    def test_strips_textbf_formatting(self) -> None:
        r"""Should remove \textbf{} formatting from title."""
        result = extract_title(r"\title{\textbf{Bold Title}}")
        assert result == "Bold Title"

    def test_strips_line_breaks(self) -> None:
        r"""Should remove \\ from title."""
        result = extract_title(r"\title{Line\\Break}")
        assert "Line" in result


class TestExtractAuthor:
    """Tests for extract_author()."""

    def test_extracts_author(self) -> None:
        r"""Should extract author from \author{...}."""
        result = extract_author(r"\author{Jane Doe}")
        assert result == "Jane Doe"

    def test_returns_empty_when_no_author(self) -> None:
        """Should return empty string when no author found."""
        result = extract_author("No author here.")
        assert result == ""


class TestExtractAbstract:
    """Tests for extract_abstract()."""

    def test_extracts_abstract(self) -> None:
        r"""Should extract content from \begin{abstract}...\end{abstract}."""
        tex = r"\begin{abstract}This is the abstract.\end{abstract}"
        result = extract_abstract(tex)
        assert result == "This is the abstract."

    def test_returns_empty_when_no_abstract(self) -> None:
        """Should return empty string when no abstract found."""
        result = extract_abstract("No abstract here.")
        assert result == ""


class TestExtractBody:
    """Tests for extract_body()."""

    def test_extracts_document_body(self) -> None:
        r"""Should extract content between \begin{document} and \end{document}."""
        tex = r"\begin{document}Body content here\end{document}"
        result = extract_body(tex)
        assert "Body content here" in result

    def test_returns_full_content_without_markers(self) -> None:
        """Should return full content when no document markers found."""
        result = extract_body("No document markers.")
        assert "No document markers." in result


class TestExtractMetadata:
    """Tests for extract_metadata()."""

    def test_returns_latex_metadata_object(self) -> None:
        r"""Should return LaTeXMetadata with parsed fields."""
        tex = r"\title{Test}\author{Author}\begin{document}\end{document}"
        meta = extract_metadata(tex)
        assert isinstance(meta, LaTeXMetadata)
        assert meta.title == "Test"
        assert meta.author == "Author"

    def test_detects_toc(self) -> None:
        r"""Should set has_toc=True when \tableofcontents is present."""
        tex = r"\title{T}\tableofcontents\begin{document}\end{document}"
        meta = extract_metadata(tex)
        assert meta.has_toc is True

    def test_raises_on_empty_content(self) -> None:
        """Should raise on empty latex_content (contract)."""
        with pytest.raises(AssertionError):
            extract_metadata("")


class TestConvertSectionsToMarkdown:
    """Tests for convert_sections_to_markdown()."""

    def test_converts_section_to_h1(self) -> None:
        r"""Should convert \section{} to # heading."""
        result = convert_sections_to_markdown(r"\section{Introduction}")
        assert "# Introduction" in result

    def test_converts_subsection_to_h2(self) -> None:
        r"""Should convert \subsection{} to ## heading."""
        result = convert_sections_to_markdown(r"\subsection{Background}")
        assert "## Background" in result

    def test_converts_subsubsection_to_h3(self) -> None:
        r"""Should convert \subsubsection{} to ### heading."""
        result = convert_sections_to_markdown(r"\subsubsection{Details}")
        assert "### Details" in result


class TestConvertSectionsToHtml:
    """Tests for convert_sections_to_html()."""

    def test_converts_section_to_h2(self) -> None:
        r"""Should convert \section{} to <h2>."""
        result = convert_sections_to_html(r"\section{Introduction}")
        assert "<h2>Introduction</h2>" in result

    def test_converts_subsection_to_h3(self) -> None:
        r"""Should convert \subsection{} to <h3>."""
        result = convert_sections_to_html(r"\subsection{Background}")
        assert "<h3>Background</h3>" in result


class TestConvertTextFormattingToMarkdown:
    """Tests for convert_text_formatting_to_markdown()."""

    def test_converts_textbf_to_bold(self) -> None:
        r"""Should convert \textbf{} to **bold**."""
        result = convert_text_formatting_to_markdown(r"\textbf{important}")
        assert "**important**" in result

    def test_converts_textit_to_italic(self) -> None:
        r"""Should convert \textit{} to *italic*."""
        result = convert_text_formatting_to_markdown(r"\textit{emphasis}")
        assert "*emphasis*" in result

    def test_converts_texttt_to_code(self) -> None:
        r"""Should convert \texttt{} to code."""
        result = convert_text_formatting_to_markdown(r"\texttt{code}")
        assert "`code`" in result

    def test_converts_emph_to_italic(self) -> None:
        r"""Should convert \emph{} to *italic*."""
        result = convert_text_formatting_to_markdown(r"\emph{emphasized}")
        assert "*emphasized*" in result


class TestConvertTextFormattingToHtml:
    """Tests for convert_text_formatting_to_html()."""

    def test_converts_textbf_to_strong(self) -> None:
        r"""Should convert \textbf{} to <strong>."""
        result = convert_text_formatting_to_html(r"\textbf{bold}")
        assert "<strong>bold</strong>" in result

    def test_converts_textit_to_em(self) -> None:
        r"""Should convert \textit{} to <em>."""
        result = convert_text_formatting_to_html(r"\textit{italic}")
        assert "<em>italic</em>" in result


class TestConvertListsToMarkdown:
    """Tests for convert_lists_to_markdown()."""

    def test_converts_itemize_to_bullets(self) -> None:
        r"""Should convert \begin{itemize} to markdown list."""
        tex = r"\begin{itemize}\item First\item Second\end{itemize}"
        result = convert_lists_to_markdown(tex)
        assert "- " in result

    def test_converts_enumerate_to_numbered(self) -> None:
        r"""Should convert \begin{enumerate} to numbered list."""
        tex = r"\begin{enumerate}\item First\item Second\end{enumerate}"
        result = convert_lists_to_markdown(tex)
        assert "1." in result or "2." in result


class TestConvertListsToHtml:
    """Tests for convert_lists_to_html()."""

    def test_converts_itemize_to_ul(self) -> None:
        r"""Should convert \begin{itemize} to <ul>."""
        tex = r"\begin{itemize}\item First\end{itemize}"
        result = convert_lists_to_html(tex)
        assert "<ul>" in result

    def test_converts_enumerate_to_ol(self) -> None:
        r"""Should convert \begin{enumerate} to <ol>."""
        tex = r"\begin{enumerate}\item First\end{enumerate}"
        result = convert_lists_to_html(tex)
        assert "<ol>" in result


class TestRemoveComments:
    """Tests for remove_comments()."""

    def test_removes_full_line_comments(self) -> None:
        """Should remove lines starting with %."""
        result = remove_comments("% This is a comment\nActual content")
        assert "comment" not in result
        assert "Actual content" in result

    def test_removes_inline_comments(self) -> None:
        """Should remove inline % comments."""
        result = remove_comments("content % inline comment")
        assert "inline comment" not in result


class TestRemoveDocumentStructure:
    """Tests for remove_document_structure()."""

    def test_removes_maketitle(self) -> None:
        r"""Should remove \maketitle."""
        result = remove_document_structure(r"Before \maketitle After")
        assert r"\maketitle" not in result

    def test_removes_title_command(self) -> None:
        r"""Should remove \title{}."""
        result = remove_document_structure(r"\title{My Article}")
        assert r"\title" not in result


class TestRemoveLabels:
    """Tests for remove_labels()."""

    def test_removes_label_command(self) -> None:
        r"""Should remove \label{} commands."""
        result = remove_labels(r"text \label{eq:force} more text")
        assert r"\label" not in result
        assert "text" in result
        assert "more text" in result


class TestRemoveSpacingCommands:
    """Tests for remove_spacing_commands()."""

    def test_removes_vspace(self) -> None:
        r"""Should remove \vspace{} commands."""
        result = remove_spacing_commands(r"text \vspace{2cm} more")
        assert r"\vspace" not in result

    def test_removes_hspace(self) -> None:
        r"""Should remove \hspace{} commands."""
        result = remove_spacing_commands(r"text \hspace{1cm} more")
        assert r"\hspace" not in result

    def test_removes_size_commands(self) -> None:
        r"""Should remove font size commands like \small, \large."""
        result = remove_spacing_commands(r"\small text \large other")
        assert r"\small" not in result
        assert r"\large" not in result


class TestCleanCommonLatex:
    """Tests for clean_common_latex()."""

    def test_applies_all_cleanups(self) -> None:
        r"""Should apply all common cleanup operations."""
        tex = "% comment\n\\maketitle\n\\label{eq:x}\nReal content"
        result = clean_common_latex(tex)
        assert "comment" not in result
        assert r"\maketitle" not in result
        assert r"\label" not in result
        assert "Real content" in result

    def test_raises_on_empty_content(self) -> None:
        """Should raise on empty content (contract)."""
        with pytest.raises(AssertionError):
            clean_common_latex("")


class TestConvertUrlsToMarkdown:
    """Tests for convert_urls_to_markdown()."""

    def test_converts_url(self) -> None:
        r"""Should convert \url{} to markdown link."""
        result = convert_urls_to_markdown(r"\url{https://example.com}")
        assert "[https://example.com]" in result

    def test_converts_href(self) -> None:
        r"""Should convert \href{}{} to markdown link."""
        result = convert_urls_to_markdown(r"\href{https://example.com}{Click here}")
        assert "[Click here](https://example.com)" in result


class TestConvertUrlsToHtml:
    """Tests for convert_urls_to_html()."""

    def test_converts_url_to_anchor(self) -> None:
        r"""Should convert \url{} to <a> element."""
        result = convert_urls_to_html(r"\url{https://example.com}")
        assert "<a href=" in result
        assert "https://example.com" in result

    def test_converts_href_to_anchor(self) -> None:
        r"""Should convert \href{}{} to <a> element."""
        result = convert_urls_to_html(r"\href{https://example.com}{Click here}")
        assert "Click here" in result
        assert "https://example.com" in result


class TestConvertReferences:
    """Tests for convert_references()."""

    def test_converts_ref_command(self) -> None:
        r"""Should convert \ref{} to plain text."""
        result = convert_references(r"\ref{fig:diagram}")
        assert r"\ref" not in result

    def test_converts_cref_command(self) -> None:
        r"""Should convert \cref{} to 'Figure ...'."""
        result = convert_references(r"\cref{fig:diagram}")
        assert "Figure" in result


class TestConvertQuotes:
    """Tests for convert_quotes()."""

    def test_converts_open_quotes(self) -> None:
        """Should convert `` to double quote."""
        result = convert_quotes("``quoted''")
        assert '""' in result or '"' in result

    def test_converts_close_quotes(self) -> None:
        """Should convert '' to double quote."""
        result = convert_quotes("hello '' world")
        assert "''" not in result
