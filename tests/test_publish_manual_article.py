"""Tests for manual article publishing helpers."""

from __future__ import annotations

from src.tools.publish_manual_article import (
    simple_markdown_to_html,
    wrap_in_article_section,
)


def test_simple_markdown_to_html_converts_headers_lists_and_inline_markup() -> None:
    """Basic Markdown constructs should map into the expected HTML structure."""
    html = simple_markdown_to_html(
        "\n".join(
            [
                "---",
                "## Section Title",
                "- **Bold** item",
                "",
                "A *paragraph*.",
            ]
        )
    )

    assert '<h2 id="section-title"' in html
    assert "<ul>" in html
    assert "<strong>Bold</strong>" in html
    assert "<em>paragraph</em>" in html


def test_wrap_in_article_section_embeds_body_html() -> None:
    """Wrapped article HTML should include the standard layout container."""
    wrapped = wrap_in_article_section("<p>Body</p>")

    assert '<section class="article-section">' in wrapped
    assert '<div class="article-content">' in wrapped
    assert "<p>Body</p>" in wrapped
