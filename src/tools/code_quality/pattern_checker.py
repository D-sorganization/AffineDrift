"""Regex-based pattern checking for code quality.

Detects banned patterns (backlog/repair markers, template placeholders),
illegitimate pass statements, and magic numbers using regex.
"""

from __future__ import annotations

import re
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────

BANNED_PATTERNS = [
    (re.compile(r"\bTODO\b"), "TODO placeholder found"),
    (re.compile(r"\bFIXME\b"), "FIXME placeholder found"),
    # (re.compile(r"^\s*\.\.\.\s*$"), "Ellipsis placeholder"), # Allow for abstract methods
    (re.compile(r"NotImplementedError"), "NotImplementedError placeholder"),
    # (re.compile(r"<.*>"), "Angle bracket placeholder"), # Too aggressive for HTML
    (re.compile(r"your.*here", re.IGNORECASE), "Template placeholder"),
    (re.compile(r"insert.*here", re.IGNORECASE), "Template placeholder"),
]

PASS_PATTERNS = [
    (re.compile(r"^\s*pass\s*$"), "Empty pass statement"),
    (
        re.compile(r"^\s*if\s+.*:\s*$"),
        "Empty if block - consider adding logic or comment",
    ),
    (
        re.compile(r"^\s*else:\s*$"),
        "Empty else block - consider adding logic or comment",
    ),
    (
        re.compile(r"^\s*except\s+.*:\s*$"),
        "Empty except block - consider adding error handling",
    ),
]

ALLOWED_CONSTANTS = [
    re.compile(r"GRAVITY_M_S2\s*=\s*", re.IGNORECASE),
]

MAGIC_NUMBERS = [
    (re.compile(r"(?<![0-9])3\.141"), "Use math.pi instead of 3.141"),
    (re.compile(r"(?<![0-9])9\.8[0-9]?(?![0-9])"), "Define GRAVITY_M_S2 constant"),
    (re.compile(r"(?<![0-9])6\.67[0-9]?(?![0-9])"), "Define gravitational constant"),
]

# Files that define or test patterns — must be excluded to avoid self-detection
_PATTERN_SELF_CHECK_FILES = frozenset(
    {
        "quality_check_script.py",
        "matlab_quality_check.py",
        "line_checks.py",
        "code_quality_check.py",
        "quality-check.py",
        "analyze_completist_data.py",
        "generate_completist_data.py",
        "pragmatic_programmer_review.py",
        "check_tech_debt_budget.py",
        # Decomposed modules that define/reference the patterns they check for
        "pattern_checker.py",
        "ast_analyzer.py",
        # Test files that exercise pattern-checker rules with intentional violations
        "test_code_quality_extras.py",
        "test_wrist_universal_joint_visual.py",
    }
)


# ─── Public API ───────────────────────────────────────────────


def is_legitimate_pass_context(lines: list[str], line_num: int) -> bool:
    """Check if a pass statement is in a legitimate context.

    Legitimate contexts include class bodies, try/except blocks,
    and context managers.

    Args:
        lines: All lines in the file.
        line_num: 1-indexed line number of the ``pass`` statement.

    Returns:
        ``True`` if the pass is in a context where it is valid boilerplate.
    """
    if line_num <= 0 or line_num > len(lines):
        return False

    line = lines[line_num - 1].strip()
    if line != "pass":
        return False

    # Check if this is in a class definition (legitimate)
    for i in range(line_num - 1, max(0, line_num - 10), -1):
        prev_line = lines[i - 1].strip()
        if prev_line.startswith("class "):
            return True
        if prev_line.startswith("def "):
            return False
        if prev_line.endswith(":") and any(
            keyword in prev_line
            for keyword in ["try:", "except", "finally:", "with ", "if __name__"]
        ):
            return True

    # Check if this is in a try/except block (legitimate)
    for i in range(line_num - 1, max(0, line_num - 5), -1):
        prev_line = lines[i - 1].strip()
        if "try:" in prev_line or "except" in prev_line:
            return True

    # Check if this is in a context manager (legitimate)
    for i in range(line_num - 1, max(0, line_num - 3), -1):
        prev_line = lines[i - 1].strip()
        if prev_line.startswith("with "):
            return True

    return False


def check_banned_patterns(
    lines: list[str],
    filepath: Path,
) -> list[tuple[int, str, str]]:
    """Check for banned patterns in *lines*.

    Scans every line for backlog/repair markers, template placeholders,
    and illegitimate pass statements.

    Args:
        lines: Source lines of the file.
        filepath: Used to skip self-check files.

    Returns:
        List of ``(line_number, message, code_snippet)`` tuples.
    """
    issues: list[tuple[int, str, str]] = []
    if filepath.name in _PATTERN_SELF_CHECK_FILES:
        return issues

    for line_num, line in enumerate(lines, 1):
        # Check for basic banned patterns
        for pattern, message in BANNED_PATTERNS:
            if pattern.search(line):
                # Ignore NotImplementedError in comments
                if "NotImplementedError" in message and "#" in line:
                    continue
                issues.append((line_num, message, line.strip()))

        # Special handling for pass statements
        if re.match(r"^\s*pass\s*$", line) and not is_legitimate_pass_context(
            lines,
            line_num,
        ):
            issues.append(
                (
                    line_num,
                    "Empty pass statement - consider adding logic or comment",
                    line.strip(),
                ),
            )

    return issues


def check_magic_numbers(lines: list[str], filepath: Path) -> list[tuple[int, str, str]]:
    """Check for magic numbers in *lines*.

    Looks for common physical constants used as raw literals
    instead of named constants.

    Args:
        lines: Source lines of the file.
        filepath: Used to skip self-check files.

    Returns:
        List of ``(line_number, message, code_snippet)`` tuples.
    """
    issues: list[tuple[int, str, str]] = []
    if filepath.name in _PATTERN_SELF_CHECK_FILES:
        return issues
    for line_num, line in enumerate(lines, 1):
        line_content = line[: line.index("#")] if "#" in line else line
        # Skip lines that are already defining constants
        if any(pattern.search(line_content) for pattern in ALLOWED_CONSTANTS):
            continue
        for pattern, message in MAGIC_NUMBERS:
            if pattern.search(line_content):
                issues.append((line_num, message, line.strip()))
    return issues
