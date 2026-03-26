"""Tests for src.tools.latex_to_quarto — main() and additional paths."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from src.tools.latex_to_quarto import _build_yaml_frontmatter, latex_to_quarto_md


class TestBuildYamlFrontmatter:
    """Tests for _build_yaml_frontmatter()."""

    def test_includes_title(self) -> None:
        """Should include the title in the YAML block."""
        result = _build_yaml_frontmatter("My Article", toc=False, abstract=None)
        assert '"My Article"' in result

    def test_toc_true_adds_toc_field(self) -> None:
        """Should add toc: true when toc=True."""
        result = _build_yaml_frontmatter("Title", toc=True, abstract=None)
        assert "toc: true" in result

    def test_toc_false_no_toc_field(self) -> None:
        """Should not include toc field when toc=False."""
        result = _build_yaml_frontmatter("Title", toc=False, abstract=None)
        assert "toc: true" not in result

    def test_abstract_included_when_provided(self) -> None:
        """Should include abstract in YAML when provided."""
        result = _build_yaml_frontmatter("Title", toc=False, abstract="My abstract text.")
        assert "My abstract text." in result
        assert "abstract:" in result

    def test_no_abstract_when_none(self) -> None:
        """Should not include abstract section when abstract is None."""
        result = _build_yaml_frontmatter("Title", toc=False, abstract=None)
        assert "abstract:" not in result

    def test_starts_with_yaml_delimiter(self) -> None:
        """Should start with ---."""
        result = _build_yaml_frontmatter("Title", toc=False, abstract=None)
        assert result.startswith("---")


class TestLatexToQuartoMd:
    """Tests for latex_to_quarto_md()."""

    def test_includes_title_from_latex(self) -> None:
        r"""Should extract title from \title{} command."""
        tex = r"\title{Test Article}\begin{document}Body content.\end{document}"
        result, _, _ = latex_to_quarto_md(tex, "Fallback Title")
        assert "Test Article" in result

    def test_uses_fallback_title_when_no_title(self) -> None:
        """Should use fallback title when no \\title{} found."""
        tex = r"\begin{document}Body content.\end{document}"
        result, _, _ = latex_to_quarto_md(tex, "Fallback Title")
        assert "Fallback Title" in result

    def test_returns_word_counts(self) -> None:
        """Should return original and markdown word counts as ints."""
        tex = r"\begin{document}Body content.\end{document}"
        _, orig_wc, md_wc = latex_to_quarto_md(tex, "Title")
        assert isinstance(orig_wc, int)
        assert isinstance(md_wc, int)

    def test_toc_extracted(self) -> None:
        r"""Should detect \tableofcontents and add toc: true to YAML."""
        tex = r"\begin{document}\tableofcontents\nSection text.\end{document}"
        result, _, _ = latex_to_quarto_md(tex, "Title")
        assert "toc: true" in result

    def test_abstract_extracted(self) -> None:
        r"""Should extract abstract and include in YAML frontmatter."""
        tex = (
            r"\begin{abstract}This is the abstract.\end{abstract}"
            r"\begin{document}Body.\end{document}"
        )
        result, _, _ = latex_to_quarto_md(tex, "Title")
        assert "abstract:" in result


class TestMain:
    """Tests for main() function."""

    def test_main_exits_1_when_no_tex_files_found(self, tmp_path: Path) -> None:
        """main() should exit 1 when --argv points to non-tex files."""
        non_tex = tmp_path / "document.md"
        non_tex.write_text("content", encoding="utf-8")
        with patch.object(sys, "argv", ["latex_to_quarto.py", str(non_tex)]):
            with pytest.raises(SystemExit) as exc:
                from src.tools.latex_to_quarto import main

                main()
        assert exc.value.code == 1

    def test_main_converts_tex_file(self, tmp_path: Path) -> None:
        """main() should convert a .tex file and write .qmd output."""
        tex_file = tmp_path / "article.tex"
        tex_file.write_text(
            r"\title{Test}\begin{document}Section text.\end{document}",
            encoding="utf-8",
        )
        with patch.object(sys, "argv", ["latex_to_quarto.py", str(tex_file)]):
            from src.tools import latex_to_quarto as m

            if hasattr(m, "main"):
                m.main()
        qmd_file = tmp_path / "article.qmd"
        assert qmd_file.exists()
        assert "Test" in qmd_file.read_text()
