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


def get_python_metrics(filepath: Path) -> dict[str, int]:
    """Extract metrics from a Python file using AST analysis.

    Args:
        filepath: Path to the Python file.

    Returns:
        Dictionary containing metrics: functions, classes, docstrings,
        typed_returns, and branches.
    """
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
    except Exception:
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
    funcs = metrics.get("functions", 0)
    branches = metrics.get("branches", 0)
    return branches / funcs if funcs > 0 else 0.0


def assess_error_handling_content(content: str) -> dict[str, int]:
    """Analyze error handling patterns in file content using AST.

    Args:
        content: The source code content.

    Returns:
        Dictionary with 'try_count' and 'bare_except_count'.
    """
    try_count = 0
    bare_except_count = 0
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                try_count += 1
                for handler in node.handlers:
                    if handler.type is None:
                        bare_except_count += 1
    except (SyntaxError, ValueError):
        # Fallback for parsing issues
        pass

    return {
        "try_count": try_count,
        "bare_except_count": bare_except_count,
    }


def assess_logging_content(content: str) -> dict[str, int]:
    """Analyze logging versus print usage in file content using AST.

    Args:
        content: The source code content.

    Returns:
        Dictionary with 'logging_usage' and 'print_usage'.
    """
    logging_usage = 0
    print_usage = 0
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for print()
                if isinstance(node.func, ast.Name) and node.func.id == "print":
                    print_usage = 1
                # Check for logging usage (logging.info, logger.error, etc.)
                elif isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id in ("logging", "logger"):
                            logging_usage = 1
    except (SyntaxError, ValueError):
        # Fallback for parsing issues
        pass

    return {
        "logging_usage": logging_usage,
        "print_usage": print_usage,
    }
