"""Tests for publish_manual_article.py — manual article publishing functions."""

from src.tools.publish_manual_article import simple_markdown_to_html, wrap_in_article_section


class TestSimpleMarkdownToHtml:
    """Tests for simple_markdown_to_html()."""

    def test_converts_h2_header(self) -> None:
        """Should convert ## headers to h2 HTML elements."""
        md = "## My Section\n"
        result = simple_markdown_to_html(md)
        assert "<h2" in result
        assert "My Section" in result

    def test_converts_list_item(self) -> None:
        """Should convert - list items to ul/li HTML."""
        md = "- First item\n- Second item\n"
        result = simple_markdown_to_html(md)
        assert "<ul>" in result
        assert "<li>First item</li>" in result
        assert "<li>Second item</li>" in result
        assert "</ul>" in result

    def test_converts_bold_text(self) -> None:
        """Should convert **bold** to <strong> tags."""
        md = "Some **bold** text\n"
        result = simple_markdown_to_html(md)
        assert "<strong>bold</strong>" in result

    def test_converts_italic_text(self) -> None:
        """Should convert *italic* to <em> tags."""
        md = "Some *italic* text\n"
        result = simple_markdown_to_html(md)
        assert "<em>italic</em>" in result

    def test_skips_yaml_frontmatter_markers(self) -> None:
        """Should skip --- yaml frontmatter markers."""
        md = "---\nSome content\n---\n"
        result = simple_markdown_to_html(md)
        assert "---" not in result
        assert "Some content" in result

    def test_empty_string(self) -> None:
        """Should return empty string for empty input."""
        result = simple_markdown_to_html("")
        assert result == ""

    def test_paragraph_wrapping(self) -> None:
        """Should wrap non-list, non-header lines in <p> tags."""
        md = "A plain paragraph.\n"
        result = simple_markdown_to_html(md)
        assert "<p>A plain paragraph.</p>" in result

    def test_list_closes_before_header(self) -> None:
        """Should close ul before rendering a header."""
        md = "- item\n## Header\n"
        result = simple_markdown_to_html(md)
        ul_pos = result.find("</ul>")
        h2_pos = result.find("<h2")
        assert ul_pos < h2_pos

    def test_bold_in_list_item(self) -> None:
        """Should convert bold text within list items."""
        md = "- **bold item**\n"
        result = simple_markdown_to_html(md)
        assert "<strong>bold item</strong>" in result

    def test_h2_anchor_id_generation(self) -> None:
        """Should generate anchor id from header text."""
        md = "## My Section Title\n"
        result = simple_markdown_to_html(md)
        assert 'id="my-section-title"' in result

    def test_list_closes_on_empty_line(self) -> None:
        """Should close ul on empty line."""
        md = "- item\n\nParagraph after.\n"
        result = simple_markdown_to_html(md)
        assert "</ul>" in result
        assert "<p>Paragraph after.</p>" in result

    def test_list_closes_on_non_list_content(self) -> None:
        """Should close ul when non-list content follows."""
        md = "- item\nNot a list item\n"
        result = simple_markdown_to_html(md)
        assert "</ul>" in result


class TestWrapInArticleSection:
    """Tests for wrap_in_article_section()."""

    def test_wraps_in_article_section(self) -> None:
        """Should wrap body HTML in article section structure."""
        body = "<p>Content</p>"
        result = wrap_in_article_section(body)
        assert 'class="article-section"' in result
        assert "<p>Content</p>" in result

    def test_contains_main_content_area(self) -> None:
        """Should include main-content-area div."""
        body = "<p>Test</p>"
        result = wrap_in_article_section(body)
        assert 'class="main-content-area"' in result

    def test_contains_right_sidebar(self) -> None:
        """Should include right-sidebar aside."""
        body = "<p>Test</p>"
        result = wrap_in_article_section(body)
        assert 'class="right-sidebar"' in result

    def test_returns_string(self) -> None:
        """Should return a string."""
        result = wrap_in_article_section("")
        assert isinstance(result, str)
