"""YAML frontmatter parsing utilities.

This module provides functions for extracting YAML frontmatter from
Quarto (.qmd) and Markdown files.

Example:
    from src.tools.utils import extract_frontmatter, extract_title_description

    content = Path("article.qmd").read_text()
    yaml_content, body = extract_frontmatter(content)
    title, description = extract_title_description(yaml_content)
"""

from __future__ import annotations

import logging
import re
from typing import Any

import yaml

from src.core.contracts import require

logger = logging.getLogger(__name__)


def _safe_load_frontmatter(yaml_content: str) -> dict[str, Any]:
    """Parse YAML frontmatter into a mapping, returning empty data on bad YAML."""
    try:
        parsed = yaml.safe_load(yaml_content)
    except yaml.YAMLError as exc:
        logger.debug("Could not parse YAML frontmatter: %s", exc)
        return {}

    return parsed if isinstance(parsed, dict) else {}


def _stringify_scalar(value: Any) -> str | None:
    """Return a stable string for scalar YAML values; skip nested data."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str | int | float):
        return str(value)
    return None


def extract_frontmatter(content: str) -> tuple[str | None, str]:
    """Extract YAML frontmatter from content.

    Args:
        content: The full file content with optional YAML frontmatter.

    Returns:
        Tuple of (yaml_content, body_content). yaml_content is None if
        no frontmatter is found.

    Example:
        >>> content = '''---
        ... title: "My Article"
        ... ---
        ... Body content here.'''
        >>> yaml, body = extract_frontmatter(content)
        >>> yaml
        'title: "My Article"'
        >>> body
        'Body content here.'
    """
    yaml_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not yaml_match:
        return None, content

    yaml_content = yaml_match.group(1)
    body_content = content[yaml_match.end() :]
    return yaml_content, body_content


def extract_title_description(
    yaml_content: str | None,
    default_title: str = "",
    default_description: str = "",
) -> tuple[str, str]:
    """Extract title and description from YAML frontmatter.

    Args:
        yaml_content: The YAML frontmatter string.
        default_title: Default title if not found in YAML.
        default_description: Default description if not found in YAML.

    Returns:
        Tuple of (title, description).

    Example:
        >>> yaml = 'title: "My Article"\\ndescription: "A great article"'
        >>> title, desc = extract_title_description(yaml)
        >>> title
        'My Article'
        >>> desc
        'A great article'
    """
    if yaml_content is None:
        return default_title, default_description

    frontmatter = _safe_load_frontmatter(yaml_content)
    title = _stringify_scalar(frontmatter.get("title")) or default_title
    description = _stringify_scalar(frontmatter.get("description")) or default_description

    return title, description


def parse_frontmatter_dict(content: str) -> dict[str, str]:
    """Parse YAML frontmatter into a dictionary.

    This is a convenience function that extracts frontmatter and parses
    it into a simple key-value dictionary. Nested values are skipped.

    Args:
        content: The full file content with optional YAML frontmatter.

    Returns:
        Dictionary of frontmatter key-value pairs. Empty dict if no frontmatter.

    Example:
        >>> content = '''---
        ... title: "My Article"
        ... description: "A great article"
        ... ---
        ... Body content here.'''
        >>> parse_frontmatter_dict(content)
        {'title': 'My Article', 'description': 'A great article'}
    """
    require(content is not None, "content must not be None")
    yaml_content, _ = extract_frontmatter(content)
    if yaml_content is None:
        return {}

    frontmatter: dict[str, str] = {}
    for key, value in _safe_load_frontmatter(yaml_content).items():
        scalar_value = _stringify_scalar(value)
        if scalar_value is not None:
            frontmatter[str(key)] = scalar_value

    return frontmatter
