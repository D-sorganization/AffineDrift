"""AST-based code quality analysis.

Provides structural checks that require parsing the full Python AST:
- Missing docstrings on public functions
- Missing return type hints
- Syntax error detection
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def check_ast_issues(content: str, filepath: Path) -> list[tuple[int, str, str]]:
    """Check AST for quality issues.

    Analyses the parsed AST of *content* for:
    - Missing docstrings on function definitions (unless in scripts/tests)
    - Relaxed return-type hint checks (delegated to MyPy)

    Args:
        content: Full source text of the file.
        filepath: Path used to decide whether docstring checks apply.

    Returns:
        List of ``(line_number, message, code_snippet)`` tuples.
    """
    issues: list[tuple[int, str, str]] = []
    # Skip checking quality check scripts for AST issues
    if filepath.name in (
        "quality_check_script.py",
        "matlab_quality_check.py",
        "code_quality_check.py",
        "quality-check.py",
    ):
        return issues

    # Exclude certain files/directories from docstring checks
    skip_docstring_checks = False
    filepath_str = str(filepath).replace("\\", "/")
    if "scripts/" in filepath_str or "tests/" in filepath_str:
        skip_docstring_checks = True
    if filepath_str.endswith("src/core/contracts.py"):
        skip_docstring_checks = True

    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.FunctionDef)
                and not skip_docstring_checks
                and not ast.get_docstring(node)
            ):
                if (
                    len(node.body) == 1
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and node.body[0].value.value == ...
                ):
                    continue

                issues.append(
                    (node.lineno, f"Function '{node.name}' missing docstring", ""),
                )
            # Return-type enforcement is delegated to MyPy.
            # To enforce here, check `node.returns` and append issue.
    except SyntaxError as e:
        issues.append((0, f"Syntax error: {e}", ""))
    return issues
