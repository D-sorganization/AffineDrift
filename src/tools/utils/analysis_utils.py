"""Utilities for analyzing Python code quality and structure.

This module provides functions to extract metrics and assess various aspects
of Python source code, such as documentation coverage, type hint usage,
and code complexity.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from src.core.contracts import ensure, require


def get_python_metrics(filepath: Path) -> dict[str, int]:
    """Extract metrics from a Python file using AST analysis.

    Args:
        filepath: Path to the Python file.

    Returns:
        Dictionary containing metrics: functions, classes, docstrings,
        typed_returns, and branches.
    """
    require(filepath is not None, "filepath must not be None")
    metrics = {
        "functions": 0,
        "classes": 0,
        "docstrings": 0,
        "typed_returns": 0,
        "branches": 0,
    }
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                metrics["functions"] += 1
                if ast.get_docstring(node):
                    metrics["docstrings"] += 1
                if node.returns:
                    metrics["typed_returns"] += 1
            elif isinstance(node, ast.ClassDef):
                metrics["classes"] += 1
                if ast.get_docstring(node):
                    metrics["docstrings"] += 1
            elif isinstance(node, ast.If | ast.For | ast.While | ast.ExceptHandler):
                metrics["branches"] += 1
    except (SyntaxError, ValueError):
        # Skip files with syntax errors or other parsing issues
        pass
    except (FileNotFoundError, OSError, KeyError):
        # Fallback for other issues
        pass
    return metrics


def get_detailed_function_metrics(content: str) -> list[dict[str, Any]]:
    """Extract detailed function metrics from Python source code.

    Args:
        content: Python source code content.

    Returns:
        List of dictionaries with function details.
    """
    functions = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                functions.append(
                    {
                        "name": node.name,
                        "lineno": node.lineno,
                        "args": len(node.args.args),
                        "body_lines": (
                            (getattr(node, "end_lineno", 0) - getattr(node, "lineno", 0) + 1)
                            if (
                                isinstance(getattr(node, "end_lineno", None), int)
                                and isinstance(getattr(node, "lineno", None), int)
                            )
                            else 0
                        ),
                        "has_docstring": (ast.get_docstring(node) is not None),
                    }
                )
    except (SyntaxError, ValueError):
        pass
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
    try_count = content.count("try:")
    bare_except_count = len(re.findall(r"except\s*:", content))
    return {
        "try_count": try_count,
        "bare_except_count": bare_except_count,
    }


def assess_logging_content(content: str) -> dict[str, int]:
    """Analyze logging versus print usage in file content.

    Args:
        content: The source code content.

    Returns:
        Dictionary with 'logging_usage' and 'print_usage'.
    """
    logging_usage = 1 if ("logging." in content or "logger." in content) else 0
    print_usage = 1 if "print(" in content else 0
    return {
        "logging_usage": logging_usage,
        "print_usage": print_usage,
    }
