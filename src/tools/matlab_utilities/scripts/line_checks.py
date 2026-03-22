"""Per-line MATLAB quality checks.

This module contains the line-level static analysis checks extracted from
MATLABQualityChecker. Each check appends issues to the caller's list.

Functions:
- update_function_scope: Track function/block nesting depth
- append_function_contract_issues: Docstring and arguments block checks
- append_banned_pattern_issues: Banned placeholder comment detection
- append_anti_pattern_issues: eval, assignin, global, etc.
- append_magic_number_issues: Unexplained numeric literals
- append_function_scope_issues: clear/clc/close-all inside functions
- analyze_matlab_file: Orchestrate all checks on a single .m file
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Module-level constants for magic number detection ────────────────────────

_ACCEPTABLE_NUMBERS: frozenset[str] = frozenset(
    {
        "0",
        "0.0",
        "1",
        "1.0",
        "2",
        "2.0",
        "3",
        "3.0",
        "4",
        "4.0",
        "5",
        "5.0",
        "10",
        "10.0",
        "100",
        "100.0",
        "1000",
        "1000.0",
        "0.5",
        "0.1",
        "0.01",
        "0.001",
        "0.0001",
    }
)
"""Numeric literals that are universally acceptable without a named constant."""

_GRAVITY_DESC = "gravitational acceleration [m/s^2] - approximate standard gravity"

_KNOWN_CONSTANTS: dict[str, str] = {
    "3.14159": "pi constant [dimensionless] - mathematical constant",
    "3.1416": "pi constant [dimensionless] - mathematical constant",
    "3.14": "pi constant [dimensionless] - mathematical constant",
    "1.5708": "pi/2 constant [dimensionless] - mathematical constant",
    "1.57": "pi/2 constant [dimensionless] - mathematical constant",
    "0.7854": "pi/4 constant [dimensionless] - mathematical constant",
    "0.785": "pi/4 constant [dimensionless] - mathematical constant",
    "9.81": _GRAVITY_DESC,
    "9.8": _GRAVITY_DESC,
    "9.807": _GRAVITY_DESC,
}
"""Well-known physical and mathematical constants that require a named constant definition."""


def update_function_scope(
    line_stripped: str,
    *,
    is_comment: bool,
    in_function: bool,
    nesting_level: int,
) -> tuple[bool, int]:
    """Track whether analysis is inside a function and current nesting depth."""
    if is_comment:
        return in_function, nesting_level

    if re.match(
        (
            r"\b(function|if|for|while|switch|try|parfor|classdef|arguments|"
            r"properties|methods|events)\b"
        ),
        line_stripped,
    ):
        if line_stripped.startswith("function"):
            in_function = True
        nesting_level += 1

    if re.match(r"\bend\b", line_stripped):
        nesting_level -= 1
        if nesting_level <= 0:
            return False, 0

    return in_function, nesting_level


def append_function_contract_issues(
    *,
    lines: list[str],
    line_number: int,
    line_stripped: str,
    file_name: str,
    issues: list[str],
) -> None:
    """Check function-level contracts: docstring and arguments block."""
    if not line_stripped.startswith("function"):
        return

    line_index = line_number - 1
    has_docstring = False
    for next_line in lines[line_index + 1 : min(line_index + 5, len(lines))]:
        candidate = next_line.strip()
        if candidate and not candidate.startswith("%"):
            break
        if candidate.startswith("%") and len(candidate) > 3:
            has_docstring = True
            break
    if not has_docstring:
        issues.append(f"{file_name} (line {line_number}): Missing function docstring")

    has_arguments = False
    for next_line in lines[line_index + 1 : min(line_index + 15, len(lines))]:
        candidate = next_line.strip()
        if candidate.startswith("%"):
            continue
        if re.search(r"\barguments\b", candidate):
            has_arguments = True
            break
    if not has_arguments:
        issues.append(
            f"{file_name} (line {line_number}): Missing arguments validation block",
        )


def append_banned_pattern_issues(
    *,
    line_stripped: str,
    line_number: int,
    file_name: str,
    issues: list[str],
) -> None:
    """Flag placeholders and temporary markers."""
    banned_patterns = [
        (r"\bTODO\b", "Backlog marker placeholder found"),
        (r"\bFIXME\b", "Immediate repair marker found"),
        (r"\bHACK\b", "Temporary workaround marker found"),
        (r"\bXXX\b", "Placeholder marker found"),
        (r"<[A-Z_][A-Z0-9_]*>", "Angle bracket placeholder found"),
        (r"\{\{.*?\}\}", "Template placeholder found"),
    ]
    for pattern, message in banned_patterns:
        if re.search(pattern, line_stripped):
            issues.append(f"{file_name} (line {line_number}): {message}")


def append_anti_pattern_issues(
    *,
    line_stripped: str,
    line_number: int,
    file_name: str,
    issues: list[str],
) -> None:
    """Detect risky MATLAB anti-patterns."""
    anti_patterns = [
        (
            r"\beval\s*\(",
            "Avoid using eval() - potential security risk and performance issue",
        ),
        (r"\bassignin\s*\(", "Avoid using assignin() - violates encapsulation"),
        (r"\bevalin\s*\(", "Avoid using evalin() - violates encapsulation"),
        (
            r"\bglobal\s+\w+",
            "Global variable usage - consider passing as argument",
        ),
        (
            r"\bexist\s*\(",
            "Consider using validation or try/catch instead of exist()",
        ),
    ]
    for pattern, message in anti_patterns:
        if re.search(pattern, line_stripped):
            issues.append(f"{file_name} (line {line_number}): {message}")

    if (
        re.search(r"^\s*load\s+\w+", line_stripped)
        or re.search(r"^\s*load\s*\([^)]+\)", line_stripped)
    ) and "=" not in line_stripped:
        issues.append(
            f"{file_name} (line {line_number}): load without output variable - "
            "use 'data = load(...)' instead",
        )


def _is_number_in_code(line_original: str, number: str) -> bool:
    """Return True if *number* appears in the code portion of a MATLAB line.

    A number is considered to be in code (not in a comment) when:
    - there is no ``%`` comment delimiter on the line, OR
    - the number's first occurrence precedes the comment delimiter.

    Args:
        line_original: The original (non-stripped) source line.
        number: The numeric literal string to locate.

    Returns:
        True if the number appears before any comment delimiter, False otherwise.
    """
    comment_index = line_original.find("%")
    number_index = line_original.find(number)
    return comment_index == -1 or (number_index != -1 and number_index < comment_index)


def append_magic_number_issues(
    *,
    line_original: str,
    line_stripped: str,
    line_number: int,
    file_name: str,
    issues: list[str],
) -> None:
    """Flag unexplained numeric literals in a MATLAB source line.

    Uses ``_ACCEPTABLE_NUMBERS`` and ``_KNOWN_CONSTANTS`` module-level sets
    to classify each literal found on the line.

    Args:
        line_original: The original (non-stripped) source line (used for comment detection).
        line_stripped: The stripped source line (used for pattern matching).
        line_number: 1-based line number for issue messages.
        file_name: File name for issue messages.
        issues: Mutable list to which new issue strings are appended.
    """
    magic_number_pattern = r"(?<![.\w])(?:\d+\.\d+|\d+)(?![.\w])"
    for number in re.findall(magic_number_pattern, line_stripped):
        if number in _KNOWN_CONSTANTS:
            issues.append(
                f"{file_name} (line {line_number}): Magic number {number} "
                f"({_KNOWN_CONSTANTS[number]}) - define as named constant",
            )
            continue
        if number in _ACCEPTABLE_NUMBERS:
            continue
        if _is_number_in_code(line_original, number):
            issues.append(
                f"{file_name} (line {line_number}): Magic number {number} "
                "should be defined as constant with units and source",
            )


def append_function_scope_issues(
    *,
    in_function: bool,
    line_stripped: str,
    line_number: int,
    file_name: str,
    issues: list[str],
) -> None:
    """Flag commands that alter global MATLAB session state from within functions."""
    if not in_function:
        return

    if re.search(r"\bclear\s+(all|global)\b", line_stripped, re.IGNORECASE):
        issues.append(
            f"{file_name} (line {line_number}): Avoid 'clear all' or 'clear global' "
            "in functions - clears all variables, functions, and MEX links",
        )
    elif re.search(r"\bclear\b(?!\s+\w+)", line_stripped):
        issues.append(
            f"{file_name} (line {line_number}): Avoid 'clear' in functions - "
            "can clear function variables",
        )

    if re.search(r"\bclc\b", line_stripped):
        issues.append(
            f"{file_name} (line {line_number}): Avoid 'clc' in functions - "
            "affects user's workspace",
        )
    if re.search(r"\bclose\s+all\b", line_stripped):
        issues.append(
            f"{file_name} (line {line_number}): Avoid 'close all' in functions - "
            "closes user's figures",
        )
    if re.search(r"\baddpath\s*\(", line_stripped):
        issues.append(
            f"{file_name} (line {line_number}): Avoid addpath in functions - "
            "manage paths externally",
        )


def _dispatch_line_checks(
    lines: list[str],
    line_number: int,
    line: str,
    is_comment: bool,
    in_function: bool,
    file_name: str,
    issues: list[str],
) -> None:
    """Run all per-line quality checks and append findings to issues."""
    line_stripped = line.strip()
    line_original = line
    append_function_contract_issues(
        lines=lines,
        line_number=line_number,
        line_stripped=line_stripped,
        file_name=file_name,
        issues=issues,
    )
    append_banned_pattern_issues(
        line_stripped=line_stripped,
        line_number=line_number,
        file_name=file_name,
        issues=issues,
    )
    if is_comment:
        return
    append_anti_pattern_issues(
        line_stripped=line_stripped,
        line_number=line_number,
        file_name=file_name,
        issues=issues,
    )
    append_magic_number_issues(
        line_original=line_original,
        line_stripped=line_stripped,
        line_number=line_number,
        file_name=file_name,
        issues=issues,
    )
    append_function_scope_issues(
        in_function=in_function,
        line_stripped=line_stripped,
        line_number=line_number,
        file_name=file_name,
        issues=issues,
    )


def analyze_matlab_file(file_path: Path) -> list[str]:
    """Analyze a single MATLAB file for quality issues.

    Args:
        file_path: Path to the MATLAB file

    Returns:
        List of quality issues found
    """
    issues: list[str] = []

    try:
        with file_path.open(encoding="utf-8", errors="ignore") as f:
            lines = f.read().split("\n")

        in_function = False
        nesting_level = 0

        for line_number, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if not line_stripped:
                continue
            is_comment = line_stripped.startswith("%")
            in_function, nesting_level = update_function_scope(
                line_stripped,
                is_comment=is_comment,
                in_function=in_function,
                nesting_level=nesting_level,
            )
            _dispatch_line_checks(
                lines, line_number, line, is_comment, in_function, file_path.name, issues
            )

    except (FileNotFoundError, PermissionError, OSError) as e:
        issues.append(f"{file_path.name}: Could not analyze file - {e!s}")

    return issues
