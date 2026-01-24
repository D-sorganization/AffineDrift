"""Shared utilities for AffineDrift tools.

This module provides common functionality used across multiple tools:
- HTML template manipulation
- YAML frontmatter parsing
- File processing utilities
"""

from .frontmatter import extract_frontmatter, extract_title_description
from .html_utils import (
    create_html_page,
    escape_html,
    replace_content_section,
    update_metadata,
    update_title_block,
)

__all__ = [
    "create_html_page",
    "escape_html",
    "extract_frontmatter",
    "extract_title_description",
    "replace_content_section",
    "update_metadata",
    "update_title_block",
]
