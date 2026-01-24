"""Shared utilities for AffineDrift tools.

This module provides common functionality used across multiple tools:
- HTML template manipulation
- YAML frontmatter parsing
- File discovery utilities
- Logging configuration
"""

from .file_utils import (
    find_files_by_extension,
    find_html_files,
    find_markdown_files,
    find_qmd_files,
    process_file_content,
)
from .frontmatter import extract_frontmatter, extract_title_description
from .html_utils import (
    create_html_page,
    escape_html,
    replace_content_section,
    update_metadata,
    update_title_block,
)
from .logging_utils import setup_logging, setup_logging_with_timestamp

__all__ = [
    "create_html_page",
    "escape_html",
    "extract_frontmatter",
    "extract_title_description",
    "find_files_by_extension",
    "find_html_files",
    "find_markdown_files",
    "find_qmd_files",
    "process_file_content",
    "replace_content_section",
    "setup_logging",
    "setup_logging_with_timestamp",
    "update_metadata",
    "update_title_block",
]
