"""Tests for the repository-root HTML normalization script."""

from __future__ import annotations

from pathlib import Path

import fix_html


def test_remove_paragraph_wrappers_before_lists() -> None:
    """Paragraph wrappers should be removed before list blocks."""
    assert fix_html.remove_paragraph_wrappers_before_lists("<p>\n\n<ul>") == "<ul>"
    assert fix_html.remove_paragraph_wrappers_before_lists("<p>\n<ol>") == "<ol>"


def test_normalize_list_item_spacing() -> None:
    """Repeated list item closers should collapse into one separator."""
    assert fix_html.normalize_list_item_spacing("</li></li></li><li>") == "</li>\n<li>"


def test_normalize_list_block_openers() -> None:
    """Malformed list openers should be rewritten to a clean newline layout."""
    assert fix_html.normalize_list_block_openers("<ul></li>\n<li>") == "<ul>\n<li>"
    assert fix_html.normalize_list_block_openers("<ol>\n</li>\n<li>") == "<ol>\n<li>"


def test_unwrap_math_block_paragraphs() -> None:
    """Math and quote blocks should not be wrapped in stray paragraphs."""
    assert fix_html.unwrap_math_block_paragraphs("<p>\\begin{align}x\\end{align}</p>") == (
        "\\begin{align}x\\end{align}"
    )
    assert fix_html.unwrap_math_block_paragraphs("<p>\\begin{quote}") == "\\begin{quote}"


def test_resolve_repo_relative_path_uses_repo_root(tmp_path: Path) -> None:
    """Relative paths should resolve against the provided repository root."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    resolved = fix_html.resolve_repo_relative_path(
        repo_root,
        Path("content/page.html"),
    )

    assert resolved == repo_root / "content/page.html"
