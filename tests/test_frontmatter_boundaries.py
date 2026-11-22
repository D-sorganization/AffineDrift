"""Canonical YAML and legacy flat-frontmatter fallback boundaries."""

from __future__ import annotations

import pytest

from src.tools.utils.frontmatter import (
    extract_frontmatter,
    extract_title_description,
    parse_frontmatter_dict,
    split_frontmatter,
)

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("raw", ["title: [unfinished", "[", "title: {broken"])
def test_invalid_yaml_preserves_canonical_input_and_uses_title_defaults(raw: str) -> None:
    content = f"---\n{raw}\n---\nBody stays intact.\n"
    assert split_frontmatter(content) == ({}, content)
    assert extract_title_description(raw, "Fallback Title", "Fallback Description") == (
        "Fallback Title",
        "Fallback Description",
    )


@pytest.mark.parametrize("raw", ["", "null", "42", "plain text", "- first\n- second"])
def test_non_object_yaml_is_not_promoted_to_metadata(raw: str) -> None:
    content = f"---\n{raw}\n---\nBody.\n"
    assert split_frontmatter(content) == ({}, content)
    assert extract_title_description(raw, "Title", "Description") == ("Title", "Description")
    assert parse_frontmatter_dict(content) == {}


def test_legacy_flat_fallback_ignores_nested_empty_and_non_field_lines() -> None:
    raw = (
        "title: Example: With a Colon\n"
        "\n"
        "  nested: ignored\n"
        ": missing key\n"
        "empty:\n"
        "not a field\n"
        "category: 'reference'\n"
        'description: "A Raw: Description"'
    )
    content = f"---\n{raw}\n---\nBody.\n"
    assert split_frontmatter(content) == ({}, content)
    assert parse_frontmatter_dict(content) == {
        "title": "Example: With a Colon",
        "category": "reference",
        "description": "A Raw: Description",
    }
    assert extract_frontmatter(content) == (raw, "Body.\n")


def test_canonical_types_and_legacy_string_values_remain_distinct() -> None:
    content = "---\ncount: 3\nenabled: true\ndate: 2026-01-02\n---\nBody.\n"
    canonical, body = split_frontmatter(content)
    assert canonical["count"] == 3
    assert canonical["enabled"] is True
    assert body == "Body.\n"
    assert parse_frontmatter_dict(content) == {
        "count": "3",
        "enabled": "True",
        "date": "2026-01-02",
    }


@pytest.mark.parametrize(
    "content",
    [
        "\ufeff---\ntitle: Header\n---\nBody.",
        "\n---\ntitle: Header\n---\nBody.",
        "---\ntitle: Unclosed Header\nBody.",
        "----\ntitle: Extra Dash\n----\nBody.",
        "Text before metadata\n---\ntitle: Later\n---\nBody.",
    ],
)
def test_unrecognized_header_boundaries_leave_content_untouched(content: str) -> None:
    assert split_frontmatter(content) == ({}, content)
    assert extract_frontmatter(content) == (None, content)


def test_only_leading_metadata_is_removed_and_body_is_preserved_exactly() -> None:
    body = "Body café.\n---\ntitle: Body Data\n---\nEnd.\n"
    content = f"---\ntitle: Leading Header\n---\n{body}"
    assert split_frontmatter(content) == ({"title": "Leading Header"}, body)
    assert extract_frontmatter(content) == ("title: Leading Header", body)
