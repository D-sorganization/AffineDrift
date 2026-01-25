"""Utilities for running external shell commands and tools.

This module provides wrappers for common development tools like Ruff and Black,
returning standardized result dictionaries.
"""

from __future__ import annotations

import subprocess
from typing import Any


def run_ruff_check(path: str = ".") -> dict[str, Any]:
    """Run ruff and return statistics.

    Args:
        path: Directory or file to check.

    Returns:
        Dictionary with exit_code, output, and errors.
    """
    try:
        result = subprocess.run(
            ["ruff", "check", path, "--statistics", "--output-format=json"],
            capture_output=True,
            text=True,
        )
        return {
            "exit_code": result.returncode,
            "output": result.stdout,
            "errors": result.stderr,
        }
    except FileNotFoundError:
        return {"exit_code": -1, "output": "", "errors": "ruff not installed"}


def run_black_check(path: str = ".") -> dict[str, Any]:
    """Run black check and return results.

    Args:
        path: Directory or file to check.

    Returns:
        Dictionary with exit_code and files_to_format count.
    """
    try:
        result = subprocess.run(
            ["black", "--check", "--quiet", path],
            capture_output=True,
            text=True,
        )
        return {
            "exit_code": result.returncode,
            "files_to_format": result.stdout.count("would reformat"),
        }
    except FileNotFoundError:
        return {"exit_code": -1, "files_to_format": 0, "errors": "black not installed"}
