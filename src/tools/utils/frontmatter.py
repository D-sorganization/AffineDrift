"""YAML frontmatter parsing utilities.

This module provides a canonical ``split_frontmatter`` function that parses YAML
frontmatter using the yaml library, together with thin backward-compat wrappers
for the historical string-based API.

Example:
    from src.tools.utils.frontmatter import split_frontmatter

    fm, body = split_frontmatter(Path("article.qmd").read_text())
    title = fm.get("title", "")
"""

from __future__ import annotations

import logging
import re
from typing import Any

import yaml

from src.core.contracts import require

logger = logging.getLogger(__name__)

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(\n|\Z)", re.DOTALL)


def split_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Split YAML frontmatter from content.

    Parses the leading ``--- ... ---`` block (if present) with ``yaml.safe_load``
    and returns a ``(frontmatter_dict, body)`` pair.  When no valid frontmatter
    block is found the dictionary is empty and ``body`` equals the full
    ``content``.

    Args:
        content: Full file content with optional YAML frontmatter.

    Returns:
        Tuple of (frontmatter_dict, body_content).

    Example:
        >>> fm, body = split_frontmatter("---\ntitle: Hello\n---\nBody.\n")
        >>> fm["title"]
        'Hello'
        >>> body
        'Body.\n'
    """
    require(content is not None, "content must not be None")
    m = _FRONTMATTER_RE.match(content)
    if not m:
        return {}, content
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return {}, content
    if not isinstance(fm, dict):
        return {}, content
    body = content[m.end() :]
    return fm, body


# ---------------------------------------------------------------------------
# Backward-compat wrappers
# ---------------------------------------------------------------------------


def extract_frontmatter(content: str) -> tuple[str | None, str]:
    """Extract YAML frontmatter from content (legacy string-based API).

    Args:
        content: The full file content with optional YAML frontmatter.

    Returns:
        Tuple of (yaml_string, body_content). yaml_string is None if no
        frontmatter is found.

    Example:
        >>> yaml_str, body = extract_frontmatter("---\ntitle: Hi\n---\nBody.\n")
        >>> "title" in yaml_str
        True
    """
    m = _FRONTMATTER_RE.match(content)
    if not m:
        return None, content
    yaml_content = m.group(1)
    body_content = content[m.end() :]
    return yaml_content, body_content


def extract_title_description(
    yaml_content: str | None,
    default_title: str = "",
    default_description: str = "",
) -> tuple[str, str]:
    """Extract title and description from YAML frontmatter.

    Accepts either a raw YAML string (legacy) or ``None`` (no frontmatter).
    Both single-quoted and unquoted YAML title values are handled correctly
    because the value is parsed by ``yaml.safe_load``.

    Args:
        yaml_content: The YAML frontmatter string, or None.
        default_title: Default title if not found in YAML.
        default_description: Default description if not found in YAML.

    Returns:
        Tuple of (title, description).

    Example:
        >>> title, desc = extract_title_description("title: 'My Article'")
        >>> title
        'My Article'
    """
    if yaml_content is None:
        return default_title, default_description

    try:
        fm = yaml.safe_load(yaml_content)
    except yaml.YAMLError:
        return default_title, default_description

    if not isinstance(fm, dict):
        return default_title, default_description

    title = str(fm["title"]) if "title" in fm else default_title
    description = str(fm["description"]) if "description" in fm else default_description
    return title, description


def _parse_legacy_flat_frontmatter(yaml_content: str | None) -> dict[str, str]:
    """Parse historical flat frontmatter where values may contain raw colons."""
    if yaml_content is None:
        return {}

    result: dict[str, str] = {}
    for line in yaml_content.splitlines():
        if not line or line[:1].isspace() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            continue
        result[key] = value.strip("\"'")
    return result


def parse_frontmatter_dict(content: str) -> dict[str, str]:
    """Parse YAML frontmatter into a string-valued dictionary (legacy API).

    All values are coerced to ``str`` so that callers performing string
    operations on fields such as ``date`` continue to work even when
    ``yaml.safe_load`` returns a typed value (e.g. ``datetime.date``).

    Args:
        content: The full file content with optional YAML frontmatter.

    Returns:
        Dictionary of frontmatter key-value pairs as strings. Empty dict if
        no frontmatter is present or YAML parsing fails.

    Example:
        >>> d = parse_frontmatter_dict("---\ntitle: My Article\n---\nBody.\n")
        >>> d["title"]
        'My Article'
    """
    require(content is not None, "content must not be None")
    fm, _ = split_frontmatter(content)
    if fm:
        return {k: str(v) for k, v in fm.items()}
    yaml_content, _body = extract_frontmatter(content)
    return _parse_legacy_flat_frontmatter(yaml_content)
