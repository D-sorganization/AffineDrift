"""Tests for HTML template manipulation utilities."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.tools.utils import html_utils


def test_imports():
    assert html_utils


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("<script>", "&lt;script&gt;"),
        ("&", "&amp;"),
        ('"quoted"', "&quot;quoted&quot;"),
        ("'single'", "&#x27;single&#x27;"),
        ("plain text", "plain text"),
        ("", ""),
        ("<div class='x'>", "&lt;div class=&#x27;x&#x27;&gt;"),
    ],
)
def test_escape_html(text: str, expected: str):
    assert html_utils.escape_html(text) == expected


def test_update_metadata_replaces_title() -> None:
    """update_metadata should inject the new title into the <title> tag."""
    template = "<title>Old Title</title>"
    result = html_utils.update_metadata(template, "New Title", "desc")
    assert "New Title – AffineDrift" in result
    assert "Old Title" not in result


def test_update_metadata_replaces_description() -> None:
    """update_metadata should update the meta description tag."""
    template = '<meta name="description" content="old desc">'
    result = html_utils.update_metadata(template, "title", "new desc")
    assert 'content="new desc"' in result
    assert "old desc" not in result


def test_update_metadata_escapes_html_in_title() -> None:
    """update_metadata should escape HTML special chars in title."""
    template = "<title>Old</title>"
    result = html_utils.update_metadata(template, "<b>Bold</b>", "desc")
    assert "&lt;b&gt;" in result


def test_update_title_block_replaces_h1() -> None:
    """update_title_block should replace the h1.title element."""
    template = '<h1 class="title">Old Heading</h1>'
    result = html_utils.update_title_block(template, "New Heading", "desc")
    assert "New Heading" in result
    assert "Old Heading" not in result


def test_update_title_block_replaces_description_div() -> None:
    """update_title_block should replace the description div."""
    template = '<div class="description">\n    Old description\n  </div>'
    result = html_utils.update_title_block(template, "title", "New description")
    assert "New description" in result
    assert "Old description" not in result


def test_replace_content_section_swaps_body() -> None:
    """replace_content_section should replace article-section content."""
    template = '<section class="article-section main">Original content</section>'
    result = html_utils.replace_content_section(template, "<p>New content</p>")
    assert "<p>New content</p>" in result
    assert "Original content" not in result


def test_replace_content_section_handles_no_match() -> None:
    """replace_content_section should return template unchanged if no match."""
    template = "<div>No article section here</div>"
    result = html_utils.replace_content_section(template, "<p>body</p>")
    assert result == template


def test_remove_articles_scripts_removes_function() -> None:
    """remove_articles_scripts should strip updateArticlesHistory function."""
    template = "before\n function updateArticlesHistory() { var x = 1; }\nafter"
    result = html_utils.remove_articles_scripts(template)
    assert "updateArticlesHistory" not in result
    assert "before" in result
    assert "after" in result


def test_remove_articles_scripts_removes_call() -> None:
    """remove_articles_scripts should also strip updateArticlesHistory() calls."""
    template = "setup(); updateArticlesHistory(); teardown();"
    result = html_utils.remove_articles_scripts(template)
    assert "updateArticlesHistory" not in result


def test_fix_relative_paths_depth_1() -> None:
    """fix_relative_paths should prefix paths with ../ at depth 1."""
    template = 'href="./style.css" href="index.html"'
    result = html_utils.fix_relative_paths(template, depth=1)
    assert "../" in result


def test_fix_relative_paths_depth_2() -> None:
    """fix_relative_paths should use ../../ prefix at depth 2."""
    template = 'href="./style.css"'
    result = html_utils.fix_relative_paths(template, depth=2)
    assert "../../" in result


def test_create_html_page_returns_false_for_empty_template(tmp_path: Path) -> None:
    """create_html_page should return False when template_content is empty."""
    out = tmp_path / "out.html"
    result = html_utils.create_html_page(
        title="Test",
        description="desc",
        body_html="<p>body</p>",
        output_file=out,
        template_content="",
    )
    assert result is False
    assert not out.exists()


def test_create_html_page_returns_true_and_writes_file(tmp_path: Path) -> None:
    """create_html_page should write the output file and return True."""
    template = (
        "<title>PLACEHOLDER</title>"
        '<meta name="description" content="PLACEHOLDER">'
        '<h1 class="title">PLACEHOLDER</h1>'
        '<div class="description">\n    PLACEHOLDER\n  </div>'
        '<section class="article-section main">PLACEHOLDER</section>'
    )
    out = tmp_path / "out.html"
    result = html_utils.create_html_page(
        title="My Title",
        description="My desc",
        body_html="<p>content</p>",
        output_file=out,
        template_content=template,
    )
    assert result is True
    assert out.exists()
    content = out.read_text()
    assert "My Title" in content


def test_create_html_page_removes_scripts_for_non_articles(tmp_path: Path) -> None:
    """create_html_page should strip articles scripts for non-articles pages."""
    template = (
        "<title>X</title>"
        '<meta name="description" content="X">'
        '<h1 class="title">X</h1>'
        '<div class="description">\n    X\n  </div>'
        '<section class="article-section main">X</section>'
        " function updateArticlesHistory() { } updateArticlesHistory();"
    )
    out = tmp_path / "out.html"
    html_utils.create_html_page(
        title="T",
        description="D",
        body_html="<p>b</p>",
        output_file=out,
        template_content=template,
        page_type="models",
    )
    assert "updateArticlesHistory" not in out.read_text()


def test_create_html_page_with_fix_paths(tmp_path: Path) -> None:
    """create_html_page with fix_paths=True applies path prefix."""
    template = (
        "<title>X</title>"
        '<meta name="description" content="X">'
        '<h1 class="title">X</h1>'
        '<div class="description">\n    X\n  </div>'
        '<section class="article-section main">X</section>'
        'href="./style.css"'
    )
    out = tmp_path / "sub" / "out.html"
    html_utils.create_html_page(
        title="T",
        description="D",
        body_html="<p>b</p>",
        output_file=out,
        template_content=template,
        fix_paths=True,
        path_depth=1,
    )
    content = out.read_text()
    assert "../" in content
