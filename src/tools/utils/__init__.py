"""Shared utilities for AffineDrift tools.

This module provides common functionality used across multiple tools:
- HTML template manipulation
- YAML frontmatter parsing
- File discovery utilities
- Logging configuration
- Code analysis and metrics
- Assessment and reporting
- Centralized constants
"""

from .analysis_utils import (
    assess_error_handling_content,
    assess_logging_content,
    calculate_complexity,
    get_detailed_function_metrics,
    get_python_metrics,
)
from .assessment_utils import (
    ASSESSMENT_DEFINITIONS,
    CATEGORIES,
    GROUP_MAPPING,
    GROUP_WEIGHTS,
    PRAGMATIC_PRINCIPLES,
    classify_assessment_category,
)
from .constants import (
    EXCLUDE_DIRS,
    EXCLUDE_DIRS_CONTENT,
    EXCLUDE_DIRS_PYTHON,
    EXCLUDE_FILES,
    HTML_FIX_PATTERNS,
    PATH_REPLACEMENT_PATTERNS,
)
from .file_utils import (
    find_files_by_extension,
    find_html_files,
    find_markdown_files,
    find_qmd_files,
    get_python_files,
    process_file_content,
)
from .frontmatter import (
    extract_frontmatter,
    extract_title_description,
    parse_frontmatter_dict,
)
from .html_utils import (
    create_html_page,
    escape_html,
    replace_content_section,
    update_metadata,
    update_title_block,
)
from .issue_utils import format_issue_body, get_repo_short_name
from .logging_utils import setup_logging, setup_logging_with_timestamp
from .report_utils import generate_issue_document, generate_markdown_report

__all__ = [
    # Constants
    "EXCLUDE_DIRS",
    "EXCLUDE_DIRS_CONTENT",
    "EXCLUDE_DIRS_PYTHON",
    "EXCLUDE_FILES",
    "HTML_FIX_PATTERNS",
    "PATH_REPLACEMENT_PATTERNS",
    # HTML utilities
    "create_html_page",
    "escape_html",
    "replace_content_section",
    "update_metadata",
    "update_title_block",
    # Frontmatter utilities
    "extract_frontmatter",
    "extract_title_description",
    "parse_frontmatter_dict",
    # File utilities
    "find_files_by_extension",
    "find_html_files",
    "find_markdown_files",
    "find_qmd_files",
    "get_python_files",
    "process_file_content",
    # Logging utilities
    "setup_logging",
    "setup_logging_with_timestamp",
    # Analysis utilities
    "get_python_metrics",
    "calculate_complexity",
    "get_detailed_function_metrics",
    "assess_error_handling_content",
    "assess_logging_content",
    # Assessment utilities
    "ASSESSMENT_DEFINITIONS",
    "CATEGORIES",
    "GROUP_WEIGHTS",
    "GROUP_MAPPING",
    "PRAGMATIC_PRINCIPLES",
    "classify_assessment_category",
    # Report utilities
    "generate_markdown_report",
    "generate_issue_document",
    "format_issue_body",
    "get_repo_short_name",
]
