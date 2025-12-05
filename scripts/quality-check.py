#!/usr/bin/env python3
"""Quality check script to verify AI-generated code meets standards."""

import ast
import re
import sys
from pathlib import Path

# Configuration
BANNED_PATTERNS = [
    (re.compile(r"\bTODO\b"), "TODO placeholder found"),
    (re.compile(r"\bFIXME\b"), "FIXME placeholder found"),
    (re.compile(r"^\s*\.\.\.\s*$"), "Ellipsis placeholder"),
    (re.compile(r"NotImplementedError"), "NotImplementedError placeholder"),
    (re.compile(r"<.*>"), "Angle bracket placeholder"),
    (re.compile(r"your.*here", re.IGNORECASE), "Template placeholder"),
    (re.compile(r"insert.*here", re.IGNORECASE), "Template placeholder"),
]

# More intelligent pass statement detection
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

MAGIC_NUMBERS = [
    (re.compile(r"(?<![0-9])3\.141"), "Use math.pi instead of 3.141"),
    (re.compile(r"(?<![0-9])9\.8[0-9]?(?![0-9])"), "Define GRAVITY_M_S2 constant"),
    (re.compile(r"(?<![0-9])6\.67[0-9]?(?![0-9])"), "Define gravitational constant"),
]


def _is_in_class_definition(lines: list[str], line_num: int) -> bool:
    """Check if pass is in a class definition context."""
    result = False
    for i in range(line_num - 1, max(0, line_num - 10), -1):
        prev_line = lines[i - 1].strip()
        if prev_line.startswith("class "):
            result = True
            break
        if prev_line.startswith("def "):
            result = False
            break
        if prev_line.endswith(":") and any(
            keyword in prev_line
            for keyword in ["try:", "except", "finally:", "with ", "if __name__"]
        ):
            result = True
            break
    return result


def _is_in_try_except_block(lines: list[str], line_num: int) -> bool:
    """Check if pass is in a try/except block context."""
    for i in range(line_num - 1, max(0, line_num - 5), -1):
        prev_line = lines[i - 1].strip()
        if "try:" in prev_line or "except" in prev_line:
            return True
    return False


def _is_in_context_manager(lines: list[str], line_num: int) -> bool:
    """Check if pass is in a context manager context."""
    for i in range(line_num - 1, max(0, line_num - 3), -1):
        prev_line = lines[i - 1].strip()
        if prev_line.startswith("with "):
            return True
    return False


def is_legitimate_pass_context(lines: list[str], line_num: int) -> bool:
    """Check if a pass statement is in a legitimate context."""
    if line_num <= 0 or line_num > len(lines):
        return False

    line = lines[line_num - 1].strip()
    if line != "pass":
        return False

    return (
        _is_in_class_definition(lines, line_num)
        or _is_in_try_except_block(lines, line_num)
        or _is_in_context_manager(lines, line_num)
    )


def check_banned_patterns(
    lines: list[str],
    filepath: Path,
) -> list[tuple[int, str, str]]:
    """Check for banned patterns in lines."""
    issues: list[tuple[int, str, str]] = []
    # Skip checking this file for its own patterns
    excluded_names = [
        "quality_check_script.py",
        "quality_check.py",
        "quality-check.py",
        "quality-check-script.py",
    ]
    if filepath.name in excluded_names:
        return issues

    # Check if this is a test file - exclude angle bracket check for test files
    is_test_file = "test" in filepath.name.lower() or "test" in str(filepath.parts)

    # Check if this is a file that generates HTML/uses HTML strings (GUI, Streamlit, HTML conversion tools)
    is_html_generating_file = False
    if filepath.suffix == ".py":
        # Check if it's a Streamlit file
        if "streamlit" in filepath.name.lower() or "Streamlit" in str(filepath.parts):
            is_html_generating_file = True
        # Check if it's an HTML conversion tool or navigation update tool
        elif any(
            tool_name in filepath.name.lower()
            for tool_name in ["latex_to_html", "html", "convert", "update_navigation"]
        ):
            is_html_generating_file = True
        # Check if it's a GUI file (PyQt/Qt applications)
        else:
            try:
                content = filepath.read_text(encoding="utf-8")
                # Check for GUI framework imports and HTML usage
                if any(
                    import_name in content
                    for import_name in [
                        "PyQt",
                        "QtWidgets",
                        "QApplication",
                        "QLabel",
                        "setText",
                        "streamlit",
                        "st.",
                    ]
                ):
                    if (
                        "<b>" in content
                        or "<br>" in content
                        or "setText" in content
                        or "st." in content
                    ):
                        is_html_generating_file = True
            except (OSError, UnicodeDecodeError):
                pass

    # Exclude quality check scripts and MATLAB quality check from certain checks
    is_quality_check_script = (
        "quality_check" in filepath.name.lower() or "matlab_quality_check" in filepath.name.lower()
    )

    for line_num, line in enumerate(lines, 1):
        # Check for basic banned patterns
        for pattern, message in BANNED_PATTERNS:
            # Skip angle bracket placeholder check for test files and HTML-generating files (HTML strings are valid)
            if (is_test_file or is_html_generating_file) and "Angle bracket placeholder" in message:
                continue
            # Skip TODO/FIXME/Angle bracket checks in quality check scripts (they're part of the pattern definitions)
            if is_quality_check_script and (
                "TODO placeholder" in message
                or "FIXME placeholder" in message
                or "Angle bracket placeholder" in message
            ):
                continue
            # Skip angle bracket patterns in regex strings (r"<...") and usage messages
            if "Angle bracket placeholder" in message and (
                'r"' in line
                or "r'" in line
                or "re.compile" in line
                or "Usage:" in line
                or "print(" in line
            ):
                continue
            if pattern.search(line):
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
    """Check for magic numbers in lines."""
    issues: list[tuple[int, str, str]] = []
    # Skip checking this file for magic numbers
    excluded_names = [
        "quality_check_script.py",
        "quality_check.py",
        "quality-check.py",
        "quality-check-script.py",
        "matlab_quality_check.py",
    ]
    if filepath.name in excluded_names:
        return issues
    # Skip magic number checks in quality check scripts (they contain pattern definitions)
    if "quality_check" in filepath.name.lower() or "matlab_quality_check" in filepath.name.lower():
        return issues
    for line_num, line in enumerate(lines, 1):
        line_content = line[: line.index("#")] if "#" in line else line
        # Skip lines that are already defining constants (e.g., GRAVITY_M_S2 = 9.81)
        if re.search(r"GRAVITY_M_S2\s*=\s*", line_content, re.IGNORECASE):
            continue
        # Skip magic numbers in string literals (like in matlab_quality_check.py)
        if '"' in line_content or "'" in line_content:
            # Check if the magic number is inside quotes
            if re.search(r'["\'].*9\.8[0-9]?.*["\']', line_content) or re.search(
                r'["\'].*3\.141.*["\']', line_content
            ):
                continue
        for pattern, message in MAGIC_NUMBERS:
            if pattern.search(line_content):
                issues.append((line_num, message, line.strip()))
    return issues


def check_ast_issues(content: str, filepath: Path) -> list[tuple[int, str, str]]:
    """Check AST for quality issues."""
    issues: list[tuple[int, str, str]] = []
    try:
        tree = ast.parse(content)
        # Track function hierarchy to skip nested functions
        function_stack: list[ast.FunctionDef] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if this is a nested function (has a parent function)
                is_nested = len(function_stack) > 0
                function_stack.append(node)

                # Skip docstring check for nested functions (they're usually helper functions)
                if not is_nested:
                    if not ast.get_docstring(node):
                        # Skip private nested functions in update_navigation.py
                        if not (
                            filepath.name == "update_navigation.py" and node.name.startswith("_")
                        ):
                            issues.append(
                                (
                                    node.lineno,
                                    f"Function '{node.name}' missing docstring",
                                    "",
                                ),
                            )

                if not node.returns and node.name != "__init__":
                    issues.append(
                        (
                            node.lineno,
                            f"Function '{node.name}' missing return type hint",
                            "",
                        ),
                    )

                # Pop when done with this function's children
                if function_stack and function_stack[-1] == node:
                    function_stack.pop()
    except SyntaxError as e:
        issues.append((0, f"Syntax error: {e}", ""))
    return issues


def check_file(filepath: Path) -> list[tuple[int, str, str]]:
    """Check a Python file for quality issues."""
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.splitlines()

        issues = []
        issues.extend(check_banned_patterns(lines, filepath))
        issues.extend(check_magic_numbers(lines, filepath))
        issues.extend(check_ast_issues(content, filepath))
    except (OSError, UnicodeDecodeError) as e:
        return [(0, f"Error reading file: {e}", "")]
    else:
        return issues


def main() -> None:
    """Run quality checks on Python files."""
    python_files = list(Path().rglob("*.py"))

    # Exclude certain directories (AffineDrift-specific)
    exclude_dirs = {
        "archive",
        "Archive",
        "legacy",
        "experimental",
        ".git",
        "__pycache__",
        ".ruff_cache",
        ".mypy_cache",
        "_site",
        "docs",
        ".quarto",
        "Drafts",
        "output",
        ".ipynb_checkpoints",
        ".Trash",
    }
    python_files = [f for f in python_files if not any(part in exclude_dirs for part in f.parts)]

    # Exclude quality check scripts themselves
    excluded_script_names = [
        "quality_check.py",
        "quality_check_script.py",
        "quality-check.py",
        "quality-check-script.py",
    ]
    python_files = [f for f in python_files if f.name not in excluded_script_names]

    all_issues = []
    for filepath in python_files:
        issues = check_file(filepath)
        if issues:
            all_issues.append((filepath, issues))

    # Report
    if all_issues:
        sys.stderr.write("❌ Quality check FAILED\n\n")
        for filepath, issues in all_issues:
            sys.stderr.write(f"\n{filepath}:\n")
            for line_num, message, code in issues:
                if line_num > 0:
                    sys.stderr.write(f"  Line {line_num}: {message}\n")
                    if code:
                        sys.stderr.write(f"    > {code}\n")
                else:
                    sys.stderr.write(f"  {message}\n")

        sys.stderr.write(
            f"\nTotal issues: {sum(len(issues) for _, issues in all_issues)}\n",
        )
        sys.exit(1)
    else:
        sys.stderr.write("✅ Quality check PASSED\n")
        sys.stderr.write(f"Checked {len(python_files)} Python files\n")
        sys.exit(0)


if __name__ == "__main__":
    main()



