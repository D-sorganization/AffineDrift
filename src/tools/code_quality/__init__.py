"""Code quality check package.

Decomposed from the monolithic ``code_quality_check.py`` (Phase 3.1):

- ``ast_analyzer``      — AST-based analysis (docstring checks, type hints)
- ``pattern_checker``   — Regex-based pattern matching (banned, magic numbers)
- ``report_generator``  — Terminal report formatting (colors, output)
- ``check``             — Orchestration (file walking, aggregation, CLI)
"""

from src.tools.code_quality.ast_analyzer import check_ast_issues
from src.tools.code_quality.check import check_file, main
from src.tools.code_quality.pattern_checker import (
    check_banned_patterns,
    check_magic_numbers,
    is_legitimate_pass_context,
)
from src.tools.code_quality.report_generator import Colors

__all__ = [
    "Colors",
    "check_ast_issues",
    "check_banned_patterns",
    "check_file",
    "check_magic_numbers",
    "is_legitimate_pass_context",
    "main",
]
