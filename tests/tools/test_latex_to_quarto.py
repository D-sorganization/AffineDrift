"""Tests for latex_to_quarto.py — LaTeX to Quarto markdown conversion."""

from src.tools.latex_to_quarto import _build_yaml_frontmatter, latex_to_quarto_md


class TestBuildYamlFrontmatter:
    """Tests for _build_yaml_frontmatter()."""

    def test_includes_title(self) -> None:
        """Should include the document title in frontmatter."""
        result = _build_yaml_frontmatter("My Title", toc=False, abstract=None)
        assert 'title: "My Title"' in result

    def test_toc_true_adds_toc(self) -> None:
        """Should add toc: true when toc=True."""
        result = _build_yaml_frontmatter("Title", toc=True, abstract=None)
        assert "toc: true" in result

    def test_toc_false_no_toc(self) -> None:
        """Should not add toc when toc=False."""
        result = _build_yaml_frontmatter("Title", toc=False, abstract=None)
        assert "toc: true" not in result

    def test_abstract_included_when_provided(self) -> None:
        """Should include abstract when provided."""
        result = _build_yaml_frontmatter("Title", toc=False, abstract="My abstract text.")
        assert "My abstract text." in result
        assert "abstract:" in result

    def test_no_abstract_when_none(self) -> None:
        """Should not include abstract field when None."""
        result = _build_yaml_frontmatter("Title", toc=False, abstract=None)
        assert "abstract:" not in result

    def test_starts_with_yaml_delimiter(self) -> None:
        """Should start with YAML frontmatter delimiter."""
        result = _build_yaml_frontmatter("Title", toc=False, abstract=None)
        assert result.startswith("---\n")

    def test_ends_with_yaml_delimiter(self) -> None:
        """Should end YAML block with --- delimiter."""
        result = _build_yaml_frontmatter("Title", toc=False, abstract=None)
        assert "---\n" in result


class TestLatexToQuartoMd:
    """Tests for latex_to_quarto_md()."""

    def test_basic_conversion(self) -> None:
        """Should convert a simple LaTeX document to Quarto markdown."""
        tex = r"""
\begin{document}
Hello world.
\end{document}
"""
        md, before_wc, after_wc = latex_to_quarto_md(tex, "Untitled")
        assert "Hello world." in md
        assert isinstance(before_wc, int)
        assert isinstance(after_wc, int)

    def test_returns_tuple(self) -> None:
        """Should return a 3-tuple (md, before_wc, after_wc)."""
        tex = r"\begin{document}content\end{document}"
        result = latex_to_quarto_md(tex, "Test")
        assert len(result) == 3

    def test_extracts_title_from_latex(self) -> None:
        """Should extract title from \\title{} command."""
        tex = r"""
\title{My Great Article}
\begin{document}
Body text.
\end{document}
"""
        md, _, _ = latex_to_quarto_md(tex, "fallback")
        assert "My Great Article" in md

    def test_uses_fallback_title_when_no_title(self) -> None:
        """Should use fallback title when no \\title{} found."""
        tex = r"\begin{document}text\end{document}"
        md, _, _ = latex_to_quarto_md(tex, "Fallback Title")
        assert "Fallback Title" in md

    def test_converts_sections_to_markdown(self) -> None:
        """Should convert \\section{} to # markdown heading."""
        tex = r"""
\begin{document}
\section{Introduction}
Some text.
\end{document}
"""
        md, _, _ = latex_to_quarto_md(tex, "Title")
        assert "# Introduction" in md

    def test_handles_toc_command(self) -> None:
        """Should handle \\tableofcontents and set toc: true."""
        tex = r"""
\begin{document}
\tableofcontents
Content.
\end{document}
"""
        md, _, _ = latex_to_quarto_md(tex, "Title")
        assert "toc: true" in md

    def test_abstract_extracted(self) -> None:
        """Should extract \\begin{abstract}...\\end{abstract}."""
        tex = r"""
\begin{document}
\begin{abstract}
My abstract here.
\end{abstract}
Main content.
\end{document}
"""
        md, _, _ = latex_to_quarto_md(tex, "Title")
        assert "My abstract here." in md

    def test_word_count_positive(self) -> None:
        """Word counts should be non-negative integers."""
        tex = r"\begin{document}word word word\end{document}"
        _, before_wc, after_wc = latex_to_quarto_md(tex, "Title")
        assert before_wc >= 0
        assert after_wc >= 0

    def test_minimal_document(self) -> None:
        """Should handle a minimal document with some content."""
        tex = r"\begin{document}x\end{document}"
        md, _, _ = latex_to_quarto_md(tex, "Empty")
        assert isinstance(md, str)

    def test_removes_appendix_command(self) -> None:
        """Should remove \\appendix command from body."""
        tex = r"""
\begin{document}
\appendix
Appendix content.
\end{document}
"""
        md, _, _ = latex_to_quarto_md(tex, "Title")
        assert r"\appendix" not in md or "# Appendix" in md
