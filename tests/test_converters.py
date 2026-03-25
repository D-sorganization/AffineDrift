"""Tests for converter tool modules: latex_to_quarto, verify_images, wrap_sidebars."""

from __future__ import annotations

import tempfile
from pathlib import Path

from src.tools.latex_to_quarto import _build_yaml_frontmatter, latex_to_quarto_md
from src.tools.verify_images import extract_image_urls
from src.tools.wrap_sidebars import wrap_file

# ---------------------------------------------------------------------------
# latex_to_quarto module tests
# ---------------------------------------------------------------------------


class TestBuildYamlFrontmatter:
    """Tests for _build_yaml_frontmatter helper."""

    def test_title_included_in_output(self) -> None:
        """Title string appears in frontmatter output."""
        result = _build_yaml_frontmatter("My Title", toc=False, abstract=None)
        assert "My Title" in result

    def test_toc_true_adds_toc_directive(self) -> None:
        """toc=True adds 'toc: true' directive to frontmatter."""
        result = _build_yaml_frontmatter("T", toc=True, abstract=None)
        assert "toc: true" in result

    def test_toc_false_omits_toc_directive(self) -> None:
        """toc=False does not include 'toc: true' in frontmatter."""
        result = _build_yaml_frontmatter("T", toc=False, abstract=None)
        assert "toc: true" not in result

    def test_abstract_text_appears_when_provided(self) -> None:
        """Abstract text is embedded in frontmatter when provided."""
        result = _build_yaml_frontmatter("T", toc=False, abstract="Short abstract.")
        assert "Short abstract." in result

    def test_no_abstract_block_when_none(self) -> None:
        """No 'abstract' key in frontmatter when abstract is None."""
        result = _build_yaml_frontmatter("T", toc=False, abstract=None)
        assert "abstract" not in result

    def test_output_starts_with_yaml_delimiter(self) -> None:
        """Frontmatter block opens with the '---' YAML delimiter."""
        result = _build_yaml_frontmatter("T", toc=False, abstract=None)
        assert result.startswith("---")

    def test_output_ends_with_double_newline(self) -> None:
        """Frontmatter block ends with two newlines after closing '---'."""
        result = _build_yaml_frontmatter("T", toc=False, abstract=None)
        assert result.endswith("\n\n")


class TestLatexToQuartoMd:
    """Tests for the latex_to_quarto_md conversion function."""

    def test_returns_three_tuple(self) -> None:
        """latex_to_quarto_md returns a 3-tuple of (str, int, int)."""
        tex = r"\begin{document}Hello world.\end{document}"
        result = latex_to_quarto_md(tex, "fallback")
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_body_text_preserved_in_output(self) -> None:
        """Body text from the LaTeX source appears in the Quarto output."""
        tex = r"\begin{document}Important body content.\end{document}"
        md, _, _ = latex_to_quarto_md(tex, "fallback")
        assert "Important body content." in md

    def test_section_becomes_h1_heading(self) -> None:
        r"""LaTeX \section{} converts to a Markdown # heading."""
        tex = r"\begin{document}\section{Introduction}Body.\end{document}"
        md, _, _ = latex_to_quarto_md(tex, "fallback")
        assert "# Introduction" in md

    def test_subsection_becomes_h2_heading(self) -> None:
        r"""LaTeX \subsection{} converts to a Markdown ## heading."""
        tex = r"\begin{document}\subsection{Background}Body.\end{document}"
        md, _, _ = latex_to_quarto_md(tex, "fallback")
        assert "## Background" in md

    def test_fallback_title_used_without_title_command(self) -> None:
        r"""Fallback title is used when LaTeX source has no \title command."""
        tex = r"\begin{document}Content.\end{document}"
        md, _, _ = latex_to_quarto_md(tex, "My Fallback")
        assert "My Fallback" in md

    def test_explicit_title_overrides_fallback(self) -> None:
        r"""Explicit \title{} in the source takes priority over fallback."""
        tex = r"\title{Explicit Title}\begin{document}Content.\end{document}"
        md, _, _ = latex_to_quarto_md(tex, "Fallback")
        assert "Explicit Title" in md

    def test_word_counts_are_non_negative_integers(self) -> None:
        """Both word count return values are non-negative integers."""
        tex = r"\begin{document}Some words here.\end{document}"
        _, before_wc, after_wc = latex_to_quarto_md(tex, "title")
        assert isinstance(before_wc, int)
        assert isinstance(after_wc, int)
        assert before_wc >= 0
        assert after_wc >= 0

    def test_tableofcontents_removed_from_body(self) -> None:
        r"""\\tableofcontents directive is stripped from the converted body."""
        tex = r"\begin{document}\tableofcontents Content.\end{document}"
        md, _, _ = latex_to_quarto_md(tex, "title")
        assert "\\tableofcontents" not in md

    def test_tableofcontents_triggers_toc_in_frontmatter(self) -> None:
        r"""\\tableofcontents in source adds 'toc: true' to YAML frontmatter."""
        tex = r"\begin{document}\tableofcontents Content.\end{document}"
        md, _, _ = latex_to_quarto_md(tex, "title")
        assert "toc: true" in md

    def test_abstract_extracted_and_in_output(self) -> None:
        """Abstract block content appears in the converted output."""
        tex = (
            r"\begin{document}"
            r"\begin{abstract}Key abstract text.\end{abstract}"
            r"Body text.\end{document}"
        )
        md, _, _ = latex_to_quarto_md(tex, "title")
        assert "Key abstract text." in md
        assert r"\begin{abstract}" not in md


# ---------------------------------------------------------------------------
# verify_images module tests
# ---------------------------------------------------------------------------


class TestExtractImageUrls:
    """Tests for extract_image_urls function in verify_images."""

    def test_extracts_html_img_src_double_quotes(self) -> None:
        """Extracts src URL from HTML <img> tag with double-quote attribute."""
        content = '<img src="images/photo.png" alt="photo">'
        urls = extract_image_urls(content)
        assert "images/photo.png" in urls

    def test_extracts_html_img_src_single_quotes(self) -> None:
        """Extracts src URL from HTML <img> tag with single-quote attribute."""
        content = "<img src='assets/figure.jpg' alt='fig'>"
        urls = extract_image_urls(content)
        assert "assets/figure.jpg" in urls

    def test_extracts_markdown_image_url(self) -> None:
        """Extracts URL from a Markdown image reference."""
        content = "![Alt text](path/to/image.svg)"
        urls = extract_image_urls(content)
        assert "path/to/image.svg" in urls

    def test_returns_empty_list_for_content_with_no_images(self) -> None:
        """Returns empty list when content has no image references."""
        content = "Plain text with no images."
        urls = extract_image_urls(content)
        assert urls == []

    def test_returns_all_urls_when_multiple_images(self) -> None:
        """Returns all URLs when content contains multiple image references."""
        content = '![A](a.png) ![B](b.jpg) <img src="c.gif">'
        urls = extract_image_urls(content)
        assert "a.png" in urls
        assert "b.jpg" in urls
        assert "c.gif" in urls


# ---------------------------------------------------------------------------
# wrap_sidebars module tests
# ---------------------------------------------------------------------------


class TestWrapFile:
    """Tests for wrap_file function in wrap_sidebars."""

    def test_left_sidebar_wrapped_in_sticky_div(self) -> None:
        """Left sidebar content is wrapped in a sidebar-sticky-content div."""
        content = '<aside class="left-sidebar">Nav content</aside>Rest of page.'
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".qmd", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            tmp_path = Path(f.name)
        try:
            wrap_file(tmp_path)
            result = tmp_path.read_text(encoding="utf-8")
            assert "sidebar-sticky-content" in result
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_already_wrapped_sidebar_not_double_wrapped(self) -> None:
        """A file already containing sidebar-sticky-content is not re-wrapped."""
        content = (
            '<aside class="left-sidebar">'
            '<div class="sidebar-sticky-content">Nav</div>'
            "</aside>"
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".qmd", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            tmp_path = Path(f.name)
        try:
            wrap_file(tmp_path)
            result = tmp_path.read_text(encoding="utf-8")
            # Should remain exactly one occurrence — no double-wrapping
            assert result.count("sidebar-sticky-content") == 1
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_file_without_sidebar_unchanged(self) -> None:
        """Files without any aside sidebar tag are left unchanged."""
        content = "<div>No sidebars here.</div>"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".qmd", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            tmp_path = Path(f.name)
        try:
            wrap_file(tmp_path)
            result = tmp_path.read_text(encoding="utf-8")
            assert result == content
        finally:
            tmp_path.unlink(missing_ok=True)
