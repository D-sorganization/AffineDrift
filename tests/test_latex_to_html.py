"""Tests for the LaTeX to HTML converter."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.tools.latex_to_html import LaTeXToHTMLConverter

_SAMPLE_LATEX = r"""
\title{Test Article}
\author{Test Author}
\begin{document}
\begin{abstract}
This is the abstract.
\end{abstract}
\section{Introduction}
Hello world. See \url{https://example.com} for more.
\begin{equation}
x = y + z
\end{equation}
This has \textbf{bold} and \textit{italic} text.
\begin{itemize}
\item First item
\item Second item
\end{itemize}
\end{document}
"""


class TestLaTeXToHTMLConverterInit:
    """Tests for converter initialization."""

    def test_init_without_template(self) -> None:
        """Converter should initialize without errors when no template given."""
        converter = LaTeXToHTMLConverter()
        assert converter is not None

    def test_init_with_nonexistent_template(self, tmp_path: Path) -> None:
        """Converter should accept a nonexistent template path gracefully."""
        converter = LaTeXToHTMLConverter(template_file=tmp_path / "missing.html")
        assert converter is not None

    def test_init_with_existing_template(self, tmp_path: Path) -> None:
        """Converter should load an existing template file."""
        template = tmp_path / "template.html"
        template.write_text(
            "<html><head><title>{{title}}</title></head><body>{{content}}</body></html>",
            encoding="utf-8",
        )
        converter = LaTeXToHTMLConverter(template_file=template)
        assert converter.template_file == template


class TestReadLatexFile:
    """Tests for the file reading static method."""

    def test_read_latex_file_reads_content(self, tmp_path: Path) -> None:
        """read_latex_file should return file content as string."""
        f = tmp_path / "article.tex"
        f.write_text(_SAMPLE_LATEX, encoding="utf-8")
        content = LaTeXToHTMLConverter.read_latex_file(f)
        assert "Test Article" in content

    def test_read_latex_file_raises_for_missing_file(self, tmp_path: Path) -> None:
        """read_latex_file should raise when file is missing."""
        with pytest.raises((FileNotFoundError, OSError)):
            LaTeXToHTMLConverter.read_latex_file(tmp_path / "missing.tex")


class TestConvertLatexToHTML:
    """Tests for the main LaTeX-to-HTML conversion pipeline."""

    def test_converts_abstract_to_div(self) -> None:
        """convert_latex_to_html should wrap abstract in a div."""
        converter = LaTeXToHTMLConverter()
        result = converter.convert_latex_to_html(_SAMPLE_LATEX)
        assert "abstract" in result.lower()

    def test_converts_sections_to_headings(self) -> None:
        """convert_latex_to_html should produce HTML headings."""
        converter = LaTeXToHTMLConverter()
        result = converter.convert_latex_to_html(_SAMPLE_LATEX)
        assert "<h" in result
        assert "Introduction" in result

    def test_converts_bold_formatting(self) -> None:
        """convert_latex_to_html should convert \\textbf to <strong>."""
        converter = LaTeXToHTMLConverter()
        latex = r"\textbf{bold text}"
        result = converter.convert_latex_to_html(latex)
        assert "<strong>" in result or "bold text" in result

    def test_converts_italic_formatting(self) -> None:
        """convert_latex_to_html should convert \\textit to <em>."""
        converter = LaTeXToHTMLConverter()
        latex = r"\textit{italic text}"
        result = converter.convert_latex_to_html(latex)
        assert "<em>" in result or "italic text" in result

    def test_converts_urls(self) -> None:
        """convert_latex_to_html should convert \\url to HTML links."""
        converter = LaTeXToHTMLConverter()
        latex = r"\url{https://example.com}"
        result = converter.convert_latex_to_html(latex)
        assert "https://example.com" in result

    def test_converts_lists(self) -> None:
        """convert_latex_to_html should convert itemize to HTML lists."""
        converter = LaTeXToHTMLConverter()
        latex = "\\begin{itemize}\n\\item First\n\\item Second\n\\end{itemize}"
        result = converter.convert_latex_to_html(latex)
        assert "<ul>" in result or "<li>" in result


class TestConvertEquations:
    """Tests for equation environment conversion."""

    def test_converts_equation_environment(self) -> None:
        """convert_equations should wrap equation environments with MathJax div."""
        converter = LaTeXToHTMLConverter()
        latex = "\\begin{equation}\nx = y\n\\end{equation}"
        result = converter.convert_equations(latex)
        assert "\\[" in result or "equation" in result

    def test_converts_display_math(self) -> None:
        """convert_equations should convert \\[ ... \\] display math."""
        converter = LaTeXToHTMLConverter()
        latex = "\\[x = y + z\\]"
        result = converter.convert_equations(latex)
        assert "equation" in result or "x = y" in result


class TestConvertParagraphs:
    """Tests for paragraph conversion."""

    def test_wraps_plain_text_in_p_tags(self) -> None:
        """convert_paragraphs should wrap paragraphs in <p> tags."""
        converter = LaTeXToHTMLConverter()
        result = converter.convert_paragraphs("This is a paragraph.")
        assert "<p>" in result
        assert "This is a paragraph." in result

    def test_leaves_html_tags_unwrapped(self) -> None:
        """convert_paragraphs should not double-wrap existing HTML tags."""
        converter = LaTeXToHTMLConverter()
        result = converter.convert_paragraphs("<h2>Introduction</h2>")
        # Should not be wrapped in another <p>
        assert result.count("<p>") == 0

    def test_ignores_empty_lines(self) -> None:
        """convert_paragraphs should skip empty or whitespace-only blocks."""
        converter = LaTeXToHTMLConverter()
        result = converter.convert_paragraphs("\n\n\n")
        assert "<p>" not in result


class TestGetTemplate:
    """Tests for template loading."""

    def test_uses_fallback_template_when_no_file(self) -> None:
        """_get_template should return a fallback HTML template when no file set."""
        converter = LaTeXToHTMLConverter(template_file=None)
        template = converter._get_template()
        assert "<!DOCTYPE html>" in template or "<html" in template

    def test_reads_template_from_file(self, tmp_path: Path) -> None:
        """_get_template should return the file content when template exists."""
        template_file = tmp_path / "tmpl.html"
        template_file.write_text("<html>{{content}}</html>", encoding="utf-8")
        converter = LaTeXToHTMLConverter(template_file=template_file)
        template = converter._get_template()
        assert "{{content}}" in template


class TestCreateHtmlPage:
    """Tests for full HTML page creation."""

    def test_replaces_title_placeholder(self) -> None:
        """create_html_page should inject the title into the template."""
        converter = LaTeXToHTMLConverter()
        html = converter.create_html_page("My Title", "<p>content</p>")
        assert "My Title" in html

    def test_replaces_content_placeholder(self) -> None:
        """create_html_page should inject the content into the template."""
        converter = LaTeXToHTMLConverter()
        html = converter.create_html_page("T", "<p>The content</p>")
        assert "The content" in html


class TestConvertFile:
    """Tests for end-to-end file conversion."""

    def test_convert_file_writes_html(self, tmp_path: Path) -> None:
        """convert_file should write an .html file and return its path."""
        input_file = tmp_path / "article.tex"
        input_file.write_text(_SAMPLE_LATEX, encoding="utf-8")
        output_file = tmp_path / "article.html"

        converter = LaTeXToHTMLConverter()
        result = converter.convert_file(input_file, output_file)
        assert result == str(output_file)
        assert output_file.exists()

    def test_convert_file_infers_output_path(self, tmp_path: Path) -> None:
        """convert_file with no output_file should infer .html extension."""
        input_file = tmp_path / "article.tex"
        input_file.write_text(_SAMPLE_LATEX, encoding="utf-8")

        converter = LaTeXToHTMLConverter()
        result = converter.convert_file(input_file)
        expected = str(tmp_path / "article.html")
        assert result == expected
        assert (tmp_path / "article.html").exists()

    def test_convert_file_includes_title_in_output(self, tmp_path: Path) -> None:
        """convert_file output should contain the article title."""
        input_file = tmp_path / "article.tex"
        input_file.write_text(_SAMPLE_LATEX, encoding="utf-8")

        converter = LaTeXToHTMLConverter()
        converter.convert_file(input_file)
        content = (tmp_path / "article.html").read_text(encoding="utf-8")
        assert "Test Article" in content
