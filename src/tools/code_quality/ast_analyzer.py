"""AST-based code quality analysis.

Provides structural checks that require parsing the full Python AST:
- Missing docstrings on public functions
- Missing return type hints
- Syntax error detection
"""

from __future__ import annotations

import ast
from pathlib import Path

_SKIP_AST_CHECK_NAMES: frozenset[str] = frozenset(
    {
        "quality_check_script.py",
        "matlab_quality_check.py",
        "code_quality_check.py",
        "quality-check.py",
    }
)
"""File names that are excluded from AST quality checks."""


def _should_skip_docstring_checks(filepath: Path) -> bool:
    """Determine whether docstring checks should be skipped for a given file.

    Docstring checks are skipped for scripts directories, test directories,
    and the core contracts module.

    Args:
        filepath: Path to the Python source file.

    Returns:
        True if docstring checks should be skipped, False otherwise.
    """
    filepath_str = str(filepath).replace("\\", "/")
    if "scripts/" in filepath_str or "tests/" in filepath_str:
        return True
    return filepath_str.endswith("src/core/contracts.py")


def _check_function_docstrings(
    tree: ast.Module,
    issues: list[tuple[int, str, str]],
) -> None:
    """Walk the AST and append missing-docstring issues for function definitions.

    Stub functions (body is a single ``...`` expression) are exempt.

    Args:
        tree: Parsed AST module.
        issues: Mutable list to which ``(line_number, message, snippet)`` tuples
            are appended.
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if ast.get_docstring(node):
            continue
        # Exempt stub functions whose body is solely ``...``
        if (
            len(node.body) == 1
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and node.body[0].value.value == ...
        ):
            continue
        issues.append((node.lineno, f"Function '{node.name}' missing docstring", ""))


def check_ast_issues(content: str, filepath: Path) -> list[tuple[int, str, str]]:
    """Check AST for quality issues.

    Analyses the parsed AST of *content* for:
    - Missing docstrings on function definitions (unless in scripts/tests)
    - Relaxed return-type hint checks (delegated to MyPy)

    Delegates docstring scanning to ``_check_function_docstrings``.

    Args:
        content: Full source text of the file.
        filepath: Path used to decide whether docstring checks apply.

    Returns:
        List of ``(line_number, message, code_snippet)`` tuples.
    """
    issues: list[tuple[int, str, str]] = []

    if filepath.name in _SKIP_AST_CHECK_NAMES:
        return issues

    skip_docstring_checks = _should_skip_docstring_checks(filepath)

    try:
        tree = ast.parse(content)
        if not skip_docstring_checks:
            _check_function_docstrings(tree, issues)
        # Return-type enforcement is delegated to MyPy.
    except SyntaxError as e:
        issues.append((0, f"Syntax error: {e}", ""))
    return issues
