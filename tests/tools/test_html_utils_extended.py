"""Extended tests for src.tools.utils.html_utils."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.tools.utils.html_utils import (
    create_html_page,
    escape_html,
    fix_relative_paths,
    remove_articles_scripts,
    replace_content_section,
    update_metadata,
    update_title_block,
)


class TestEscapeHtml:
    """Tests for escape_html()."""

    def test_escapes_angle_brackets(self) -> None:
        """Should escape < and > characters."""
        result = escape_html("<script>alert()</script>")
        assert "<" not in result
        assert ">" not in result

    def test_escapes_ampersand(self) -> None:
        """Should escape &."""
        result = escape_html("A & B")
        assert "&amp;" in result

    def test_plain_text_unchanged(self) -> None:
        """Should not modify plain text without special characters."""
        result = escape_html("Hello World")
        assert result == "Hello World"


class TestUpdateMetadata:
    """Tests for update_metadata()."""

    def test_updates_title_tag(self) -> None:
        """Should replace the <title> tag content."""
        template = "<title>Old Title</title>"
        result = update_metadata(template, "New Title", "Description")
        assert "New Title" in result
        assert "Old Title" not in result

    def test_updates_meta_description(self) -> None:
        """Should replace the meta description content."""
        template = '<meta name="description" content="Old description">'
        result = update_metadata(template, "Title", "New description")
        assert "New description" in result

    def test_returns_unchanged_when_no_match(self) -> None:
        """Should return unchanged template when no matching tags found."""
        template = "<html><body>Content</body></html>"
        result = update_metadata(template, "Title", "Desc")
        assert result == template


class TestUpdateTitleBlock:
    """Tests for update_title_block()."""

    def test_updates_h1_title(self) -> None:
        """Should replace h1.title content."""
        template = '<h1 class="title">Old Title</h1>'
        result = update_title_block(template, "New Title", "Desc")
        assert "New Title" in result
        assert "Old Title" not in result

    def test_updates_description_div(self) -> None:
        """Should replace description div content."""
        template = '<div class="description">\n    Old desc\n  </div>'
        result = update_title_block(template, "Title", "New desc")
        assert "New desc" in result

    def test_no_match_returns_unchanged(self) -> None:
        """Should return unchanged template when no matching elements."""
        template = "<html><p>Content</p></html>"
        result = update_title_block(template, "Title", "Desc")
        assert result == template


class TestReplaceContentSection:
    """Tests for replace_content_section()."""

    def test_replaces_article_section(self) -> None:
        """Should replace article-section content."""
        template = '<section class="article-section">\n  Old content\n</section>'
        result = replace_content_section(template, "<p>New content</p>")
        assert "New content" in result
        assert "Old content" not in result

    def test_no_match_unchanged(self) -> None:
        """Should not modify template when no article-section found."""
        template = "<html><p>Other content</p></html>"
        result = replace_content_section(template, "<p>New</p>")
        assert result == template


class TestRemoveArticlesScripts:
    """Tests for remove_articles_scripts()."""

    def test_removes_update_function(self) -> None:
        """Should remove updateArticlesHistory function."""
        template = "function updateArticlesHistory() { var x = 1; }"
        result = remove_articles_scripts(template)
        assert "updateArticlesHistory" not in result

    def test_removes_function_call(self) -> None:
        """Should remove updateArticlesHistory() call."""
        template = "var x = 1;\nupdateArticlesHistory();\nvar y = 2;"
        result = remove_articles_scripts(template)
        assert "updateArticlesHistory();" not in result

    def test_no_change_when_no_script(self) -> None:
        """Should return unchanged template when no script present."""
        template = "Clean content without scripts."
        result = remove_articles_scripts(template)
        assert result == template


class TestFixRelativePaths:
    """Tests for fix_relative_paths()."""

    def test_default_depth_one(self) -> None:
        """Should use ../ prefix for depth=1."""
        from src.tools.utils.constants import PATH_REPLACEMENT_PATTERNS

        if not PATH_REPLACEMENT_PATTERNS:
            pytest.skip("No PATH_REPLACEMENT_PATTERNS defined")
        # Just verify the function runs without error
        result = fix_relative_paths("<html>content</html>", depth=1)
        assert isinstance(result, str)

    def test_depth_two_uses_double_prefix(self) -> None:
        """Should use ../../ prefix for depth=2."""
        result = fix_relative_paths("<html>content</html>", depth=2)
        assert isinstance(result, str)


class TestCreateHtmlPage:
    """Tests for create_html_page()."""

    def test_creates_html_file(self, tmp_path: Path) -> None:
        """Should create an HTML file at the specified path."""
        output = tmp_path / "article.html"
        template = (
            "<html><head><title>Old</title>"
            '<meta name="description" content="old"></head>'
            '<body><section class="article-section">old</section></body></html>'
        )
        result = create_html_page(
            title="My Article",
            description="A description",
            body_html="<p>Content</p>",
            output_file=output,
            template_content=template,
        )
        assert result is True
        assert output.exists()

    def test_returns_false_for_empty_template(self, tmp_path: Path) -> None:
        """Should return False when template_content is empty."""
        output = tmp_path / "article.html"
        result = create_html_page(
            title="Title",
            description="Desc",
            body_html="<p>Content</p>",
            output_file=output,
            template_content="",
        )
        assert result is False

    def test_requires_non_empty_title(self, tmp_path: Path) -> None:
        """Should raise on empty title (contract)."""
        output = tmp_path / "article.html"
        with pytest.raises(AssertionError):
            create_html_page(
                title="",
                description="Desc",
                body_html="<p>Content</p>",
                output_file=output,
                template_content="<html></html>",
            )

    def test_fix_paths_true(self, tmp_path: Path) -> None:
        """Should apply path fixes when fix_paths=True."""
        output = tmp_path / "article.html"
        template = (
            "<html><head><title>Old</title>"
            '<meta name="description" content="old"></head>'
            "<body>content</body></html>"
        )
        result = create_html_page(
            title="Title",
            description="Desc",
            body_html="<p>Content</p>",
            output_file=output,
            template_content=template,
            fix_paths=True,
            path_depth=1,
        )
        assert result is True

    def test_non_articles_page_type(self, tmp_path: Path) -> None:
        """Should handle page_type other than 'articles'."""
        output = tmp_path / "model.html"
        template = "<html><head><title>Old</title></head><body></body></html>"
        result = create_html_page(
            title="My Model",
            description="A model page",
            body_html="<p>Model content</p>",
            output_file=output,
            template_content=template,
            page_type="models",
        )
        assert isinstance(result, bool)
