"""Utilities for running external shell commands and tools.

This module provides wrappers for common development tools like Ruff and Black,
returning standardized result dictionaries.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from typing import Any


def run_tool(
    command: list[str],
    tool_name: str,
    result_processor: Callable[[subprocess.CompletedProcess[str]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run an external tool and return standardized results.

    This is a factory function that reduces duplication when wrapping
    subprocess calls for different development tools.

    Args:
        command: The command to run as a list of strings.
        tool_name: Name of the tool (for error messages).
        result_processor: Optional function to process the result.
            If None, returns default dict with exit_code, output, errors.

    Returns:
        Dictionary with tool execution results.
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )
        if result_processor:
            return result_processor(result)
        return {
            "exit_code": result.returncode,
            "output": result.stdout,
            "errors": result.stderr,
        }
    except FileNotFoundError:
        return {"exit_code": -1, "output": "", "errors": f"{tool_name} not installed"}


def run_ruff_check(path: str = ".") -> dict[str, Any]:
    """Run ruff and return statistics.

    Args:
        path: Directory or file to check.

    Returns:
        Dictionary with exit_code, output, and errors.
    """
    return run_tool(
        command=["ruff", "check", path, "--statistics", "--output-format=json"],
        tool_name="ruff",
    )


def run_black_check(path: str = ".") -> dict[str, Any]:
    """Run black check and return results.

    Args:
        path: Directory or file to check.

    Returns:
        Dictionary with exit_code and files_to_format count.
    """

    def process_black_result(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
        return {
            "exit_code": result.returncode,
            "files_to_format": result.stdout.count("would reformat"),
        }

    return run_tool(
        command=["black", "--check", "--quiet", path],
        tool_name="black",
        result_processor=process_black_result,
    )
