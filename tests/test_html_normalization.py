"""Unit tests for HTML normalization helpers — relocated from fix_html.py (#3234).

The pure str->str rules formerly lived in the root-level fix_html.py post-render
patcher; they now live in src/tools/utils/html_utils.py so the generation path
can emit clean artifacts instead of repairing them after the fact.
"""

from src.tools.utils.html_utils import (
    normalize_html_content,
    normalize_list_block_openers,
    normalize_list_item_spacing,
    remove_paragraph_wrappers_before_lists,
    unwrap_math_block_paragraphs,
)


def test_remove_paragraph_wrappers_before_lists():
    assert remove_paragraph_wrappers_before_lists("<p>\n<ul>") == "<ul>"
    assert remove_paragraph_wrappers_before_lists("<p>\n<ol>") == "<ol>"


def test_normalize_list_item_spacing():
    assert normalize_list_item_spacing("</li></li>") == "</li>"
    assert normalize_list_item_spacing("</li><li>") == "</li>\n<li>"


def test_normalize_list_block_openers():
    assert normalize_list_block_openers("<ul></li>\n<li>") == "<ul>\n<li>"
    assert normalize_list_block_openers("<ol></li>\n<li>") == "<ol>\n<li>"


def test_unwrap_math_block_paragraphs():
    assert unwrap_math_block_paragraphs("<p>\\begin{align}") == "\\begin{align}"
    assert unwrap_math_block_paragraphs("\\end{align}</p>") == "\\end{align}"


def test_normalize_html_content_is_idempotent():
    dirty = "<p>\n<ul></li>\n<li>a</li></li>\n<li>b</li>\n</ul>"
    once = normalize_html_content(dirty)
    twice = normalize_html_content(once)
    # Idempotent: a second pass changes nothing (born-clean property).
    assert once == twice
    assert "</li></li>" not in once


def test_normalize_html_content_no_op_on_clean_input():
    clean = "<h1>Title</h1>\n<p>Body text.</p>\n"
    assert normalize_html_content(clean) == clean
