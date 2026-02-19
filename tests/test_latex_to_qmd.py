"""Tests for LaTeX to Quarto Markdown converter."""

from __future__ import annotations

import pytest

from src.tools.latex_to_html import LaTeXToHTMLConverter
from src.tools.latex_to_qmd import LaTeXToQuartoConverter
from src.tools.utils.latex_utils import ConversionPipeline


class TestLaTeXToQuartoConverter:
    """Test suite for LaTeXToQuartoConverter."""

    def test_init(self) -> None:
        """Test converter initialization."""
        converter = LaTeXToQuartoConverter()
        assert converter is not None

    def test_extract_metadata_with_title_and_author(self) -> None:
        """Test metadata extraction with title and author."""
        converter = LaTeXToQuartoConverter()
        latex = r"""
\title{Test Article Title}
\author{Test Author}
\begin{document}
Content here
\end{document}
"""
        metadata = converter.extract_metadata(latex)
        assert metadata["title"] == "Test Article Title"
        assert metadata["author"] == "Test Author"
        assert "date" in metadata

    def test_extract_metadata_defaults(self) -> None:
        """Test metadata extraction with defaults."""
        converter = LaTeXToQuartoConverter()
        latex = r"\begin{document}Content\end{document}"
        metadata = converter.extract_metadata(latex)
        assert metadata["title"] == "Untitled"
        assert metadata["author"] == "AffineDrift"
        assert "date" in metadata

    def test_extract_body(self) -> None:
        """Test body extraction."""
        converter = LaTeXToQuartoConverter()
        latex = r"""
\title{Test}
\begin{document}
This is the body content.
\end{document}
"""
        body = converter.extract_body(latex)
        assert "This is the body content." in body
        assert "\\begin{document}" not in body
        assert "\\end{document}" not in body

    def test_convert_sections(self) -> None:
        """Test section conversion."""
        converter = LaTeXToQuartoConverter()
        content = r"\section{Introduction}\subsection{Background}"
        result = converter.convert_sections(content)
        assert "# Introduction" in result
        assert "## Background" in result

    def test_convert_text_formatting(self) -> None:
        """Test text formatting conversion."""
        converter = LaTeXToQuartoConverter()
        content = r"\textbf{bold} \textit{italic} \texttt{code}"
        result = converter.convert_text_formatting(content)
        assert "**bold**" in result
        assert "*italic*" in result
        assert "`code`" in result

    def test_convert_lists_itemize(self) -> None:
        """Test itemize list conversion."""
        converter = LaTeXToQuartoConverter()
        content = r"""
\begin{itemize}
\item First item
\item Second item
\end{itemize}
"""
        result = converter.convert_lists(content)
        assert "- First item" in result
        assert "- Second item" in result

    def test_convert_environments_keypoint(self) -> None:
        """Test keypoint environment conversion."""
        converter = LaTeXToQuartoConverter()
        content = r"\begin{keypoint}Important point\end{keypoint}"
        result = converter.convert_environments(content)
        assert "::: {.keypoint-box}" in result
        assert "**Key Point:**" in result
        assert "Important point" in result

    def test_convert_references(self) -> None:
        """Test reference conversion."""
        converter = LaTeXToQuartoConverter()
        content = r"\ref{eq:test} \cref{fig:example}"
        result = converter.convert_references(content)
        assert "[@eq:test]" in result or "[@fig:example]" in result

    def test_convert_links(self) -> None:
        """Test link conversion."""
        converter = LaTeXToQuartoConverter()
        content = r"\url{https://example.com} \href{https://test.com}{Link Text}"
        result = converter.convert_links(content)
        assert "[https://example.com](https://example.com)" in result
        assert "[Link Text](https://test.com)" in result

    def test_clean_latex_commands(self) -> None:
        """Test LaTeX command cleaning."""
        converter = LaTeXToQuartoConverter()
        content = "Some text % comment\n\\vspace{1cm}\\bvec{vector}"
        result = converter.clean_latex_commands(content)
        assert "% comment" not in result
        assert "\\vspace" not in result
        assert "**vector**" in result

    def test_create_frontmatter(self) -> None:
        """Test frontmatter creation."""
        converter = LaTeXToQuartoConverter()
        metadata = {"title": "Test", "author": "Author", "date": "2024-01-01"}
        frontmatter = converter.create_frontmatter(metadata)
        assert 'title: "Test"' in frontmatter
        assert 'author: "Author"' in frontmatter
        assert 'date: "2024-01-01"' in frontmatter
        assert "---" in frontmatter


# ─── ConversionPipeline Protocol Conformance (Issue #1250) ────


class TestConversionPipelineProtocol:
    """Verify that all LaTeX converters conform to the ConversionPipeline protocol."""

    def test_quarto_converter_is_conversion_pipeline(self) -> None:
        """LaTeXToQuartoConverter satisfies ConversionPipeline at runtime."""
        converter = LaTeXToQuartoConverter()
        assert isinstance(converter, ConversionPipeline)

    def test_html_converter_is_conversion_pipeline(self) -> None:
        """LaTeXToHTMLConverter satisfies ConversionPipeline at runtime."""
        converter = LaTeXToHTMLConverter()
        assert isinstance(converter, ConversionPipeline)

    @pytest.mark.integration
    def test_converters_share_read_interface(self) -> None:
        """Both converters expose the same pipeline methods."""
        html_conv = LaTeXToHTMLConverter()
        qmd_conv = LaTeXToQuartoConverter()

        # Both should expose read_latex_file and convert_file per the protocol.
        assert hasattr(html_conv, "read_latex_file")
        assert hasattr(qmd_conv, "read_latex_file")
        assert hasattr(html_conv, "convert_file")
        assert hasattr(qmd_conv, "convert_file")
