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
    ErrorHandlingMetrics,
    FunctionDetail,
    LoggingMetrics,
    PythonFileMetrics,
    assess_error_handling_content,
    assess_logging_content,
    calculate_complexity,
    collect_error_handling_metrics,
    collect_function_details,
    collect_logging_metrics,
    collect_python_file_metrics,
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
from .async_utils import run_async_task, run_sync_in_thread
from .constants import (
    EXCLUDE_DIRS,
    EXCLUDE_DIRS_CONTENT,
    EXCLUDE_DIRS_PYTHON,
    EXCLUDE_FILES,
    HTML_FIX_PATTERNS,
    PATH_REPLACEMENT_PATTERNS,
)
from .conversion_utils import batch_convert
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
from .profiling_utils import (
    BenchmarkResult,
    MemoryResult,
    ProfilingReport,
    TimingResult,
    benchmark,
    memory_tracking,
    profile_execution_time,
    profile_memory,
)
from .report_utils import (
    AssessmentFinding,
    generate_issue_document,
    generate_markdown_report,
    generate_report_from_finding,
)
from .shell_utils import ToolResult
from .validation_utils import BaseValidator

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
    "collect_python_file_metrics",
    "PythonFileMetrics",
    "calculate_complexity",
    "get_detailed_function_metrics",
    "collect_function_details",
    "FunctionDetail",
    "assess_error_handling_content",
    "collect_error_handling_metrics",
    "ErrorHandlingMetrics",
    "assess_logging_content",
    "collect_logging_metrics",
    "LoggingMetrics",
    # Assessment utilities
    "ASSESSMENT_DEFINITIONS",
    "CATEGORIES",
    "GROUP_WEIGHTS",
    "GROUP_MAPPING",
    "PRAGMATIC_PRINCIPLES",
    "classify_assessment_category",
    # Report utilities
    "AssessmentFinding",
    "generate_markdown_report",
    "generate_issue_document",
    "generate_report_from_finding",
    "format_issue_body",
    "get_repo_short_name",
    # Shell utilities
    "ToolResult",
    # Conversion utilities
    "batch_convert",
    # Async utilities
    "run_async_task",
    "run_sync_in_thread",
    # Profiling utilities
    "BenchmarkResult",
    "MemoryResult",
    "ProfilingReport",
    "TimingResult",
    "benchmark",
    "memory_tracking",
    "profile_execution_time",
    "profile_memory",
    # Validation utilities
    "BaseValidator",
]
