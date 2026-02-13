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

import re

from src.core.contracts import require


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

    title_match = re.search(r'^title:\s*"([^"]+)"', yaml_content, re.MULTILINE)
    desc_match = re.search(r'^description:\s*"([^"]+)"', yaml_content, re.MULTILINE)

    title = title_match.group(1) if title_match else default_title
    description = desc_match.group(1) if desc_match else default_description

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
    frontmatter: dict[str, str] = {}

    if not content.startswith("---"):
        return frontmatter

    parts = content.split("---", 2)
    if len(parts) < 3:
        return frontmatter

    yaml_content = parts[1].strip()
    current_key: str | None = None

    for line in yaml_content.split("\n"):
        # Skip nested/indented content
        if line.startswith("  ") and current_key is not None:
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            frontmatter[key] = value
            current_key = key

    return frontmatter
