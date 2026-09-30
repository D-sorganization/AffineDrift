"""Tests for the website/UX problem GitHub issue template.

Covers acceptance criteria for issue #4608: a template capturing page URL,
viewport, theme, browser, and expected versus actual behaviour.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from src.tools.utils.frontmatter import extract_frontmatter

TEMPLATE_PATH = (
    Path(__file__).resolve().parent.parent / ".github" / "ISSUE_TEMPLATE" / "website-ux-problem.md"
)


def test_website_ux_template_exists() -> None:
    """The website/UX issue template file should exist."""
    assert TEMPLATE_PATH.is_file()


def test_website_ux_template_has_required_frontmatter() -> None:
    """Frontmatter should declare name, about, title, labels, and assignees."""
    content = TEMPLATE_PATH.read_text(encoding="utf-8")
    raw_yaml, _ = extract_frontmatter(content)
    assert raw_yaml is not None
    data = yaml.safe_load(raw_yaml)

    assert data["name"]
    assert data["about"]
    assert data["title"]
    assert "website" in data["labels"]
    assert "assignees" in data


def test_website_ux_template_covers_acceptance_criteria_fields() -> None:
    """Body must prompt for page URL, viewport, theme, browser, and expected vs actual behaviour."""
    content = TEMPLATE_PATH.read_text(encoding="utf-8")
    _, body = extract_frontmatter(content)
    assert body is not None
    lowered = body.lower()

    for required in (
        "page url",
        "viewport",
        "theme",
        "browser",
        "expected",
        "actual",
    ):
        assert required in lowered, f"missing required field: {required}"
