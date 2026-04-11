"""Tests for src.tools.latex_to_html — LaTeX to HTML converter."""

from __future__ import annotations

from pathlib import Path

from src.tools.latex_to_html import LaTeXToHTMLConverter


class TestLaTeXToHTMLConverter:
    """Tests for LaTeXToHTMLConverter class."""

    def test_init_no_template(self) -> None:
        """Should initialise without error when no template provided."""
        converter = LaTeXToHTMLConverter()
        # template_file may be None or a path; both are valid
        assert converter is not None

    def test_init_with_nonexistent_template(self) -> None:
        """Should initialise even if template file doesn't exist."""
        converter = LaTeXToHTMLConverter(template_file="/nonexistent/template.html")
        assert converter.template_file == "/nonexistent/template.html"

    def test_read_latex_file(self, tmp_path: Path) -> None:
        """Should read LaTeX file content."""
        tex = tmp_path / "article.tex"
        tex.write_text(r"\begin{document}hello\end{document}", encoding="utf-8")
        converter = LaTeXToHTMLConverter()
        content = converter.read_latex_file(tex)
        assert "hello" in content

    def test_convert_equations_display(self) -> None:
        """Should wrap display equations in div."""
        converter = LaTeXToHTMLConverter()
        content = r"\begin{equation}x = y\end{equation}"
        result = converter.convert_equations(content)
        assert result.count('class="equation"') == 1
        assert result.count(r"\[") == 1

    def test_convert_equations_inline_display(self) -> None:
        """Should wrap \\[...\\] display equations."""
        converter = LaTeXToHTMLConverter()
        content = r"\[x + y = z\]"
        result = converter.convert_equations(content)
        assert 'class="equation"' in result

    def test_convert_equations_does_not_double_wrap_equation_env(self) -> None:
        """Should not wrap equation environments twice."""
        converter = LaTeXToHTMLConverter()
        content = r"\begin{equation}x = y\end{equation}"
        result = converter.convert_equations(content)
        assert result.count('<div class="equation">') == 1

    def test_convert_paragraphs_basic(self) -> None:
        """Should wrap plain text in <p> tags."""
        converter = LaTeXToHTMLConverter()
        content = "First paragraph.\n\nSecond paragraph."
        result = converter.convert_paragraphs(content)
        assert "<p>" in result
        assert "First paragraph." in result
        assert "Second paragraph." in result

    def test_convert_paragraphs_skips_html_tags(self) -> None:
        """Should not double-wrap lines that start with HTML tags."""
        converter = LaTeXToHTMLConverter()
        content = "<h2>Heading</h2>\n\nPlain text."
        result = converter.convert_paragraphs(content)
        # h2 should not be wrapped in extra <p>
        assert "<p>\n<h2>" not in result

    def test_convert_paragraphs_skips_div(self) -> None:
        """Should not wrap <div> lines in <p>."""
        converter = LaTeXToHTMLConverter()
        content = '<div class="equation">math</div>'
        result = converter.convert_paragraphs(content)
        assert "<p>\n<div" not in result

    def test_convert_latex_to_html_basic(self) -> None:
        """Should convert basic LaTeX to HTML."""
        converter = LaTeXToHTMLConverter()
        content = r"\begin{document}Hello world.\end{document}"
        result = converter.convert_latex_to_html(content)
        assert "Hello world" in result

    def test_convert_latex_to_html_abstract(self) -> None:
        """Should convert abstract environment to styled div."""
        converter = LaTeXToHTMLConverter()
        content = r"\begin{abstract}My abstract text.\end{abstract}"
        result = converter.convert_latex_to_html(content)
        assert "abstract-section" in result or "Abstract" in result

    def test_create_html_page_includes_title(self) -> None:
        """Should include title in output HTML."""
        converter = LaTeXToHTMLConverter()
        html = converter.create_html_page("My Article", "<p>Content</p>")
        assert "My Article" in html

    def test_create_html_page_includes_content(self) -> None:
        """Should include content in output HTML."""
        converter = LaTeXToHTMLConverter()
        html = converter.create_html_page("Title", "<p>Body content</p>")
        assert "Body content" in html

    def test_get_template_fallback(self) -> None:
        """Should return fallback template when no file configured."""
        converter = LaTeXToHTMLConverter(template_file=None)
        # Force no template by removing it
        converter.template_file = None
        template = converter._get_template()
        assert "<!DOCTYPE html>" in template or "html" in template.lower()

    def test_get_template_from_file(self, tmp_path: Path) -> None:
        """Should read template from file when provided."""
        template_file = tmp_path / "template.html"
        template_file.write_text("<!DOCTYPE html><html>{{title}}</html>")
        converter = LaTeXToHTMLConverter(template_file=template_file)
        template = converter._get_template()
        assert "{{title}}" in template

    def test_convert_file(self, tmp_path: Path) -> None:
        """Should convert a LaTeX file to HTML."""
        tex = tmp_path / "article.tex"
        tex.write_text(
            r"\title{Test Article}\begin{document}Content here.\end{document}",
            encoding="utf-8",
        )
        output = tmp_path / "output.html"
        converter = LaTeXToHTMLConverter()
        converter.convert_file(tex, output)
        assert output.exists()
        assert "Content here" in output.read_text()

    def test_convert_file_default_output_path(self, tmp_path: Path) -> None:
        """Should use .html extension when no output_file provided."""
        tex = tmp_path / "article.tex"
        tex.write_text(r"\begin{document}Text.\end{document}", encoding="utf-8")
        converter = LaTeXToHTMLConverter()
        converter.convert_file(tex)
        html_path = tmp_path / "article.html"
        assert html_path.exists()

    def test_clean_html_specific_removes_tikz(self) -> None:
        """Should replace tikzpicture environments with placeholder."""
        converter = LaTeXToHTMLConverter()
        content = r"\begin{tikzpicture}complex drawing\end{tikzpicture}"
        result = converter._clean_html_specific(content)
        assert "tikzpicture" not in result
        assert "Figure" in result

    def test_clean_html_specific_keypoint(self) -> None:
        """Should convert keypoint environment to styled div."""
        converter = LaTeXToHTMLConverter()
        content = r"\begin{keypoint}Important point.\end{keypoint}"
        result = converter._clean_html_specific(content)
        assert "keypoint-box" in result

    def test_clean_html_specific_removes_figures(self) -> None:
        """Should remove figure environments."""
        converter = LaTeXToHTMLConverter()
        content = r"\begin{figure}[h]\includegraphics{img.png}\end{figure}"
        result = converter._clean_html_specific(content)
        assert r"\begin{figure}" not in result
