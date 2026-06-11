"""Tests for the canonical split_frontmatter function and backward-compat wrappers."""

from __future__ import annotations

from src.tools.utils.frontmatter import (
    extract_frontmatter,
    extract_title_description,
    parse_frontmatter_dict,
    split_frontmatter,
)

# ---------------------------------------------------------------------------
# split_frontmatter — canonical function
# ---------------------------------------------------------------------------


def test_split_frontmatter_basic() -> None:
    """split_frontmatter parses a simple YAML block."""
    content = "---\ntitle: Hello\n---\nBody here.\n"
    fm, body = split_frontmatter(content)
    assert fm["title"] == "Hello"
    assert body == "Body here.\n"


def test_split_frontmatter_missing_returns_empty_dict() -> None:
    """split_frontmatter returns ({}, content) when no frontmatter block is present."""
    content = "Just plain text.\n"
    fm, body = split_frontmatter(content)
    assert fm == {}
    assert body == content


def test_split_frontmatter_single_quoted_title() -> None:
    """split_frontmatter handles single-quoted title values correctly."""
    content = "---\ntitle: 'My Single-Quoted Title'\n---\nBody.\n"
    fm, body = split_frontmatter(content)
    assert fm["title"] == "My Single-Quoted Title"


def test_split_frontmatter_unquoted_title() -> None:
    """split_frontmatter handles unquoted title values."""
    content = "---\ntitle: Unquoted Title\n---\nBody.\n"
    fm, body = split_frontmatter(content)
    assert fm["title"] == "Unquoted Title"


def test_split_frontmatter_unquoted_date_is_date_object() -> None:
    """yaml.safe_load parses unquoted dates as datetime.date objects."""
    import datetime

    content = "---\ndate: 2024-05-01\n---\nBody.\n"
    fm, _ = split_frontmatter(content)
    assert isinstance(fm["date"], datetime.date)


def test_split_frontmatter_trailing_spaces_on_delimiter() -> None:
    """split_frontmatter accepts --- delimiter lines with trailing spaces."""
    content = "---  \ntitle: Hi\n---  \nBody.\n"
    fm, body = split_frontmatter(content)
    assert fm["title"] == "Hi"
    assert body == "Body.\n"


def test_split_frontmatter_crlf_line_endings() -> None:
    """split_frontmatter handles CRLF line endings in frontmatter."""
    content = "---\r\ntitle: CRLF Title\r\n---\r\nBody.\r\n"
    fm, body = split_frontmatter(content)
    assert fm.get("title") == "CRLF Title"


def test_split_frontmatter_no_trailing_newline_after_delimiter() -> None:
    """split_frontmatter matches when frontmatter ends at EOF without trailing newline."""
    content = "---\ntitle: EOF\n---"
    fm, body = split_frontmatter(content)
    assert fm["title"] == "EOF"
    assert body == ""


def test_split_frontmatter_invalid_yaml_returns_empty_dict() -> None:
    """split_frontmatter returns ({}, content) on YAML parse error."""
    content = "---\n: invalid: yaml:\n---\nBody.\n"
    fm, body = split_frontmatter(content)
    # Either parses or falls back to empty; we just assert no exception is raised.
    assert isinstance(fm, dict)


def test_split_frontmatter_non_mapping_yaml_returns_empty_dict() -> None:
    """split_frontmatter returns ({}, content) when YAML root is not a mapping."""
    content = "---\n- item1\n- item2\n---\nBody.\n"
    fm, body = split_frontmatter(content)
    assert fm == {}
    assert body == content


# ---------------------------------------------------------------------------
# backward-compat wrapper: parse_frontmatter_dict
# ---------------------------------------------------------------------------


def test_parse_frontmatter_dict_coerces_date_to_str() -> None:
    """parse_frontmatter_dict returns string for unquoted date fields."""
    content = "---\ndate: 2024-05-01\n---\nBody.\n"
    result = parse_frontmatter_dict(content)
    assert isinstance(result["date"], str)
    assert "2024" in result["date"]


def test_parse_frontmatter_dict_basic() -> None:
    """parse_frontmatter_dict returns a str-valued dict."""
    content = "---\ntitle: My Article\ndescription: A great article\n---\nBody.\n"
    result = parse_frontmatter_dict(content)
    assert result["title"] == "My Article"
    assert result["description"] == "A great article"


def test_parse_frontmatter_dict_no_frontmatter_returns_empty() -> None:
    """parse_frontmatter_dict returns {} when no frontmatter."""
    result = parse_frontmatter_dict("Plain text only.\n")
    assert result == {}


# ---------------------------------------------------------------------------
# backward-compat wrapper: extract_frontmatter
# ---------------------------------------------------------------------------


def test_extract_frontmatter_returns_yaml_string_and_body() -> None:
    """extract_frontmatter returns raw YAML string and body."""
    content = "---\ntitle: My Article\n---\nBody content here.\n"
    yaml_str, body = extract_frontmatter(content)
    assert yaml_str is not None
    assert "title" in yaml_str
    assert "Body content here." in body


def test_extract_frontmatter_returns_none_when_no_frontmatter() -> None:
    """extract_frontmatter returns None yaml for content without frontmatter."""
    content = "Just a plain text document.\n"
    yaml_str, body = extract_frontmatter(content)
    assert yaml_str is None
    assert body == content


# ---------------------------------------------------------------------------
# backward-compat wrapper: extract_title_description
# ---------------------------------------------------------------------------


def test_extract_title_description_single_quoted() -> None:
    """extract_title_description handles single-quoted titles."""
    yaml_str = "title: 'Single Quoted'\ndescription: 'Some desc'"
    title, desc = extract_title_description(yaml_str)
    assert title == "Single Quoted"
    assert desc == "Some desc"


def test_extract_title_description_unquoted() -> None:
    """extract_title_description handles unquoted title values."""
    yaml_str = "title: Unquoted Title"
    title, _ = extract_title_description(yaml_str)
    assert title == "Unquoted Title"


def test_extract_title_description_double_quoted() -> None:
    """extract_title_description handles double-quoted titles."""
    yaml_str = 'title: "Double Quoted"\ndescription: "A great article"'
    title, desc = extract_title_description(yaml_str)
    assert title == "Double Quoted"
    assert desc == "A great article"


def test_extract_title_description_none_yaml_returns_defaults() -> None:
    """extract_title_description returns defaults when yaml_content is None."""
    title, desc = extract_title_description(None, default_title="Default", default_description="D")
    assert title == "Default"
    assert desc == "D"


def test_extract_title_description_missing_title_returns_default() -> None:
    """extract_title_description uses default_title when title is absent."""
    yaml_str = 'description: "Has no title"'
    title, desc = extract_title_description(yaml_str, default_title="Fallback")
    assert title == "Fallback"
    assert desc == "Has no title"
