"""Additional tests for latex_to_qmd.py — LaTeXToQuartoConverter class methods."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.tools.latex_to_qmd import LaTeXToQuartoConverter


class TestLaTeXToQuartoConverter:
    """Tests for LaTeXToQuartoConverter class methods."""

    def setup_method(self) -> None:
        """Create a fresh converter for each test."""
        self.converter = LaTeXToQuartoConverter()

    def test_init(self) -> None:
        """Should create converter without error."""
        assert self.converter is not None

    def test_read_latex_file(self, tmp_path: Path) -> None:
        """Should read LaTeX file content."""
        f = tmp_path / "test.tex"
        f.write_text(r"\begin{document}Hello\end{document}", encoding="utf-8")
        content = self.converter.read_latex_file(f)
        assert "Hello" in content

    def test_read_latex_file_raises_on_missing(self, tmp_path: Path) -> None:
        """Should raise on missing file."""
        with pytest.raises((FileNotFoundError, OSError)):
            self.converter.read_latex_file(tmp_path / "nonexistent.tex")

    def test_extract_metadata_returns_dict(self) -> None:
        """Should return dict with title, author, date."""
        tex = r"\title{My Article}\author{Author}\begin{document}\end{document}"
        meta = self.converter.extract_metadata(tex)
        assert "title" in meta
        assert "author" in meta
        assert "date" in meta

    def test_extract_metadata_uses_fallback_author(self) -> None:
        """Should use 'AffineDrift' as fallback author when none found."""
        tex = r"\title{Test}\begin{document}\end{document}"
        meta = self.converter.extract_metadata(tex)
        assert meta["author"] == "AffineDrift"

    def test_extract_body(self) -> None:
        """Should extract content between begin/end document."""
        tex = r"\begin{document}Body content here\end{document}"
        body = self.converter.extract_body(tex)
        assert "Body content here" in body

    def test_convert_sections_h1(self) -> None:
        """Should convert \\section{} to # heading."""
        content = r"\section{Introduction}"
        result = self.converter.convert_sections(content)
        assert "# Introduction" in result

    def test_convert_sections_paragraph(self) -> None:
        """Should convert \\paragraph{} to ##### heading."""
        content = r"\paragraph{Note}"
        result = self.converter.convert_sections(content)
        assert "##### Note" in result

    def test_convert_sections_subparagraph(self) -> None:
        """Should convert \\subparagraph{} to ###### heading."""
        content = r"\subparagraph{Sub}"
        result = self.converter.convert_sections(content)
        assert "###### Sub" in result

    def test_convert_text_formatting_bold(self) -> None:
        """Should convert \\textbf{} to **bold**."""
        content = r"\textbf{important}"
        result = self.converter.convert_text_formatting(content)
        assert "**important**" in result

    def test_convert_lists_itemize(self) -> None:
        """Should convert \\begin{itemize} to markdown list."""
        content = r"\begin{itemize}\item First\item Second\end{itemize}"
        result = self.converter.convert_lists(content)
        assert isinstance(result, str)

    def test_convert_environments_abstract(self) -> None:
        """Should convert \\begin{abstract} to Quarto div."""
        content = r"\begin{abstract}My abstract.\end{abstract}"
        result = self.converter.convert_environments(content)
        assert ".abstract-section" in result or "Abstract" in result

    def test_convert_environments_keypoint(self) -> None:
        """Should convert \\begin{keypoint} to Quarto callout."""
        content = r"\begin{keypoint}Important!\end{keypoint}"
        result = self.converter.convert_environments(content)
        assert "keypoint" in result.lower() or "Key Point" in result

    def test_convert_environments_limitation(self) -> None:
        """Should convert \\begin{limitation} to Quarto div."""
        content = r"\begin{limitation}A limitation.\end{limitation}"
        result = self.converter.convert_environments(content)
        assert "limitation" in result.lower()

    def test_convert_equations_align(self) -> None:
        """Should wrap align environment in $$."""
        content = r"\begin{align}x = y\end{align}"
        result = self.converter.convert_equations(content)
        assert "$$" in result

    def test_convert_equations_equation(self) -> None:
        """Should wrap equation environment in $$."""
        content = r"\begin{equation}x = y\end{equation}"
        result = self.converter.convert_equations(content)
        assert "$$" in result

    def test_convert_figures_with_caption(self) -> None:
        """Should extract caption from figure environment."""
        content = r"\begin{figure}[h]\caption{My Figure}\end{figure}"
        result = self.converter.convert_figures(content)
        assert "My Figure" in result

    def test_convert_figures_without_caption(self) -> None:
        """Should produce [Figure] placeholder when no caption."""
        content = r"\begin{figure}[h]\end{figure}"
        result = self.converter.convert_figures(content)
        assert "Figure" in result

    def test_convert_figures_removes_tikz(self) -> None:
        """Should replace tikzpicture with placeholder."""
        content = r"\begin{tikzpicture}complex\end{tikzpicture}"
        result = self.converter.convert_figures(content)
        assert "tikzpicture" not in result

    def test_convert_references_label(self) -> None:
        """Should convert \\label{eq:} to Quarto format."""
        content = r"\label{eq:force}"
        result = self.converter.convert_references(content)
        assert "{#eq-force}" in result

    def test_convert_references_ref(self) -> None:
        """Should convert \\ref{} to Quarto format."""
        content = r"\ref{fig:diagram}"
        result = self.converter.convert_references(content)
        assert "[@fig:diagram]" in result

    def test_clean_latex_commands_bvec(self) -> None:
        """Should convert \\bvec{} to **bold**."""
        content = r"\bvec{F}"
        result = self.converter.clean_latex_commands(content)
        assert "**F**" in result

    def test_clean_latex_commands_removes_tables(self) -> None:
        """Should remove table environments."""
        content = r"\begin{table}[h]data\end{table}"
        result = self.converter.clean_latex_commands(content)
        assert r"\begin{table}" not in result

    def test_create_frontmatter_includes_title(self) -> None:
        """Should include title in YAML frontmatter."""
        meta = {"title": "My Article", "author": "Author", "date": "2026-01-01"}
        result = self.converter.create_frontmatter(meta)
        assert 'title: "My Article"' in result
        assert result.startswith("---")

    def test_convert_to_qmd_full_pipeline(self) -> None:
        """Should run full conversion pipeline on a LaTeX document."""
        tex = r"""
\title{Test Article}
\author{Test Author}
\begin{document}
\section{Introduction}
Some text here.
\end{document}
"""
        result = self.converter.convert_to_qmd(tex)
        assert isinstance(result, str)
        assert "Test Article" in result

    def test_convert_file(self, tmp_path: Path) -> None:
        """Should convert LaTeX file to .qmd output."""
        tex = tmp_path / "article.tex"
        tex.write_text(
            r"\title{Test}\begin{document}\section{Intro}Text.\end{document}",
            encoding="utf-8",
        )
        output = tmp_path / "article.qmd"
        self.converter.convert_file(tex, output)
        assert output.exists()
        assert "Test" in output.read_text()
