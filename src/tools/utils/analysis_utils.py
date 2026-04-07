"""Utilities for analyzing Python code quality and structure.

This module provides functions to extract metrics and assess various aspects
of Python source code, such as documentation coverage, type hint usage,
and code complexity.
"""

from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.contracts import ensure, require

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data containers (dataclasses for type safety)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PythonFileMetrics:
    """Structured metrics extracted from a Python source file."""

    functions: int = 0
    classes: int = 0
    docstrings: int = 0
    typed_returns: int = 0
    branches: int = 0


@dataclass(frozen=True, slots=True)
class FunctionDetail:
    """Detailed metrics for a single function definition."""

    name: str
    lineno: int
    args: int
    body_lines: int
    has_docstring: bool


@dataclass(frozen=True, slots=True)
class ErrorHandlingMetrics:
    """Error handling pattern counts for a source file."""

    try_count: int
    bare_except_count: int


@dataclass(frozen=True, slots=True)
class LoggingMetrics:
    """Logging vs. print usage indicators for a source file."""

    logging_usage: int
    print_usage: int


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_python_metrics(filepath: Path) -> dict[str, int]:
    """Extract metrics from a Python file using AST analysis.

    Args:
        filepath: Path to the Python file.

    Returns:
        Dictionary containing metrics: functions, classes, docstrings,
        typed_returns, and branches.
    """
    require(filepath is not None, "filepath must not be None")
    metrics = collect_python_file_metrics(filepath)
    # Return dict for backward compatibility
    return {
        "functions": metrics.functions,
        "classes": metrics.classes,
        "docstrings": metrics.docstrings,
        "typed_returns": metrics.typed_returns,
        "branches": metrics.branches,
    }


def collect_python_file_metrics(filepath: Path) -> PythonFileMetrics:
    """Extract structured metrics from a Python file using AST analysis.

    This is the typed alternative to ``get_python_metrics``, returning a
    frozen dataclass instead of a plain dict.

    Args:
        filepath: Path to the Python file.

    Returns:
        ``PythonFileMetrics`` instance with all counters populated.
    """
    require(filepath is not None, "filepath must not be None")
    functions = 0
    classes = 0
    docstrings = 0
    typed_returns = 0
    branches = 0

    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                functions += 1
                if ast.get_docstring(node):
                    docstrings += 1
                if node.returns:
                    typed_returns += 1
            elif isinstance(node, ast.ClassDef):
                classes += 1
                if ast.get_docstring(node):
                    docstrings += 1
            elif isinstance(node, ast.If | ast.For | ast.While | ast.ExceptHandler):
                branches += 1
    except (SyntaxError, ValueError):
        logger.debug(
            "Falling back to zeroed Python metrics for %s after parse failure.",
            filepath,
            exc_info=True,
        )
    except (FileNotFoundError, OSError, KeyError):
        logger.debug(
            "Falling back to zeroed Python metrics for %s after file read failure.",
            filepath,
            exc_info=True,
        )

    return PythonFileMetrics(
        functions=functions,
        classes=classes,
        docstrings=docstrings,
        typed_returns=typed_returns,
        branches=branches,
    )


def get_detailed_function_metrics(content: str) -> list[dict[str, Any]]:
    """Extract detailed function metrics from Python source code.

    Args:
        content: Python source code content.

    Returns:
        List of dictionaries with function details.
    """
    details = collect_function_details(content)
    # Return list of dicts for backward compatibility
    return [
        {
            "name": d.name,
            "lineno": d.lineno,
            "args": d.args,
            "body_lines": d.body_lines,
            "has_docstring": d.has_docstring,
        }
        for d in details
    ]


def collect_function_details(content: str) -> list[FunctionDetail]:
    """Extract structured function details from Python source code.

    This is the typed alternative to ``get_detailed_function_metrics``,
    returning ``FunctionDetail`` dataclass instances.

    Args:
        content: Python source code content.

    Returns:
        List of ``FunctionDetail`` instances.
    """
    functions: list[FunctionDetail] = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                body_lines = (
                    (getattr(node, "end_lineno", 0) - getattr(node, "lineno", 0) + 1)
                    if (
                        isinstance(getattr(node, "end_lineno", None), int)
                        and isinstance(getattr(node, "lineno", None), int)
                    )
                    else 0
                )
                functions.append(
                    FunctionDetail(
                        name=node.name,
                        lineno=node.lineno,
                        args=len(node.args.args),
                        body_lines=body_lines,
                        has_docstring=(ast.get_docstring(node) is not None),
                    )
                )
    except (SyntaxError, ValueError):
        logger.debug(
            "Falling back to empty function details after parse failure.",
            exc_info=True,
        )
    return functions


def calculate_complexity(metrics: dict[str, int]) -> float:
    """Calculate average cyclomatic-like complexity.

    Args:
        metrics: Dictionary of metrics from get_python_metrics.

    Returns:
        Average number of branches per function.
    """
    require(metrics is not None, "metrics dict must not be None")
    funcs = metrics.get("functions", 0)
    branches = metrics.get("branches", 0)
    result = branches / funcs if funcs > 0 else 0.0
    ensure(result >= 0, "complexity must be non-negative")
    return result


def assess_error_handling_content(content: str) -> dict[str, int]:
    """Analyze error handling patterns in file content.

    Args:
        content: The source code content.

    Returns:
        Dictionary with 'try_count' and 'bare_except_count'.
    """
    result = collect_error_handling_metrics(content)
    return {
        "try_count": result.try_count,
        "bare_except_count": result.bare_except_count,
    }


def collect_error_handling_metrics(content: str) -> ErrorHandlingMetrics:
    """Analyze error handling patterns, returning a typed dataclass.

    Args:
        content: The source code content.

    Returns:
        ``ErrorHandlingMetrics`` with try and bare-except counts.
    """
    return ErrorHandlingMetrics(
        try_count=content.count("try:"),
        bare_except_count=len(re.findall(r"except\s*:", content)),
    )


def assess_logging_content(content: str) -> dict[str, int]:
    """Analyze logging versus print usage in file content.

    Args:
        content: The source code content.

    Returns:
        Dictionary with 'logging_usage' and 'print_usage'.
    """
    result = collect_logging_metrics(content)
    return {
        "logging_usage": result.logging_usage,
        "print_usage": result.print_usage,
    }


def collect_logging_metrics(content: str) -> LoggingMetrics:
    """Analyze logging versus print usage, returning a typed dataclass.

    Args:
        content: The source code content.

    Returns:
        ``LoggingMetrics`` with usage indicators.
    """
    return LoggingMetrics(
        logging_usage=1 if ("logging." in content or "logger." in content) else 0,
        print_usage=1 if "print(" in content else 0,
    )
