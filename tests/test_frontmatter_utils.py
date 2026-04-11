"""Tests for YAML frontmatter parsing utilities."""

from __future__ import annotations

from src.tools.utils.frontmatter import (
    extract_frontmatter,
    extract_title_description,
    parse_frontmatter_dict,
)

# ---------------------------------------------------------------------------
# extract_frontmatter tests
# ---------------------------------------------------------------------------


def test_extract_frontmatter_returns_yaml_and_body() -> None:
    """extract_frontmatter should split YAML block from body content."""
    content = "---\ntitle: My Article\n---\nBody content here.\n"
    yaml, body = extract_frontmatter(content)
    assert yaml == "title: My Article"
    assert "Body content here." in body


def test_extract_frontmatter_returns_none_when_no_frontmatter() -> None:
    """extract_frontmatter should return None yaml for content without frontmatter."""
    content = "Just a plain text document.\n"
    yaml, body = extract_frontmatter(content)
    assert yaml is None
    assert body == content


def test_extract_frontmatter_body_excludes_yaml_delimiters() -> None:
    """Body returned by extract_frontmatter should not include the --- delimiters."""
    content = "---\ntitle: Test\n---\nActual body.\n"
    yaml, body = extract_frontmatter(content)
    assert "---" not in body
    assert "Actual body." in body


def test_extract_frontmatter_handles_multiline_yaml() -> None:
    """extract_frontmatter should capture multiline YAML correctly."""
    content = "---\ntitle: Test\nauthor: Alice\ndate: 2026-01-01\n---\nContent.\n"
    yaml, body = extract_frontmatter(content)
    assert yaml is not None
    assert "author: Alice" in yaml
    assert "date: 2026-01-01" in yaml


# ---------------------------------------------------------------------------
# extract_title_description tests
# ---------------------------------------------------------------------------


def test_extract_title_description_returns_title_and_description() -> None:
    """extract_title_description should parse title and description from YAML."""
    yaml = 'title: "My Article"\ndescription: "A great piece"'
    title, desc = extract_title_description(yaml)
    assert title == "My Article"
    assert desc == "A great piece"


def test_extract_title_description_returns_defaults_when_yaml_is_none() -> None:
    """extract_title_description should return defaults when yaml_content is None."""
    title, desc = extract_title_description(None, default_title="Default", default_description="D")
    assert title == "Default"
    assert desc == "D"


def test_extract_title_description_returns_empty_defaults_by_default() -> None:
    """extract_title_description defaults should be empty strings."""
    title, desc = extract_title_description(None)
    assert title == ""
    assert desc == ""


def test_extract_title_description_returns_default_when_title_missing() -> None:
    """extract_title_description should use default_title when title not in YAML."""
    yaml = 'description: "Has no title"'
    title, desc = extract_title_description(yaml, default_title="Fallback")
    assert title == "Fallback"
    assert desc == "Has no title"


def test_extract_title_description_returns_default_when_description_missing() -> None:
    """extract_title_description should use default_description when desc not in YAML."""
    yaml = 'title: "Has no description"'
    title, desc = extract_title_description(yaml, default_description="No desc")
    assert title == "Has no description"
    assert desc == "No desc"


def test_extract_title_description_supports_unquoted_yaml_values() -> None:
    """extract_title_description should parse standard unquoted YAML scalars."""
    yaml = "title: Research Notes\ndescription: See https://example.com:8443/path"
    title, desc = extract_title_description(yaml)
    assert title == "Research Notes"
    assert desc == "See https://example.com:8443/path"


def test_parse_frontmatter_dict_uses_yaml_scalar_parsing() -> None:
    """parse_frontmatter_dict should preserve valid YAML scalar values."""
    content = """---
title: "Research: Notes"
description: See https://example.com:8443/path
toc: true
format:
  html:
    toc: true
---
Body.
"""
    frontmatter = parse_frontmatter_dict(content)

    assert frontmatter["title"] == "Research: Notes"
    assert frontmatter["description"] == "See https://example.com:8443/path"
    assert frontmatter["toc"] == "true"
    assert "format" not in frontmatter
