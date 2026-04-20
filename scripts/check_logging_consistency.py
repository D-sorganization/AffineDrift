#!/usr/bin/env python3
"""Fail CI when actual print() calls are found in src/.

The codebase standardises on structured logging for all long-lived modules
under ``src/``.  Intentional CLI UX output in ``scripts/`` may retain
``print()``, but ``src/`` must use ``logging.*`` only.

Detection uses AST analysis rather than text search so that string literals
such as ``"print("`` (e.g. pattern-matchers that look for print usage) are
**not** flagged as violations.

Exit codes:
    0 — no violations found (CI pass)
    1 — one or more violations found (CI fail)
"""

from __future__ import annotations

import ast
import logging
import sys
from pathlib import Path

from src.tools.utils.budget_check_utils import report_results

logger = logging.getLogger(__name__)

# Only src/ is enforced; scripts/ is intentional CLI UX territory.
_ENFORCE_ROOTS = ("src",)
_EXCLUDE_SUBSTRINGS = (
    "__pycache__",
    ".git",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "venv",
    ".venv",
)


def _collect_src_files(repo_root: Path) -> list[Path]:
    """Return all .py files under src/ that are not excluded."""
    files: list[Path] = []
    for root in _ENFORCE_ROOTS:
        src_dir = repo_root / root
        if not src_dir.is_dir():
            continue
        for path in sorted(src_dir.rglob("*.py")):
            rel = path.relative_to(repo_root).as_posix()
            if any(excl in rel for excl in _EXCLUDE_SUBSTRINGS):
                continue
            files.append(path)
    return files


def _has_print_call(node: ast.expr) -> bool:
    """Return True if *node* is a bare ``print(...)`` call expression."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Name) and func.id == "print":
        return True
    # Covers unlikely but possible `builtins.print(...)` form
    if isinstance(func, ast.Attribute) and func.attr == "print":
        if isinstance(func.value, ast.Name) and func.value.id == "builtins":
            return True
    return False


def find_print_calls(source: str) -> list[int]:
    """Return line numbers of actual print() calls in *source*.

    String literals containing ``print(`` are **not** reported.

    Args:
        source: Python source code text.

    Returns:
        Sorted list of 1-based line numbers where print() calls occur.
        Empty list if the source cannot be parsed.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    hits: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and _has_print_call(node.value):
            hits.append(node.lineno)
    return sorted(hits)


def check_file(path: Path) -> list[str]:
    """Check *path* for print() violations.

    Args:
        path: Absolute path to a Python file.

    Returns:
        List of human-readable violation strings (empty if clean).
    """
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        logger.warning("Cannot read %s: %s", path, exc)
        return []

    violations: list[str] = []
    for lineno in find_print_calls(source):
        violations.append(f"{path}: line {lineno}: print() call found — use logging instead")
    return violations


def main() -> int:
    """Check all src/ Python files for print() calls.

    Returns:
        Exit code — 0 for clean, 1 for violations found.
    """
    repo_root = Path(__file__).resolve().parent.parent
    files = _collect_src_files(repo_root)

    all_violations: list[str] = []
    for path in files:
        all_violations.extend(check_file(path))

    details = [f"scanned {len(files)} file(s) under src/"]
    if all_violations:
        details.extend(all_violations)

    errors = all_violations  # report_results treats non-empty as failure
    return report_results(
        "Logging consistency check (no print() in src/)",
        files_scanned=len(files),
        details=details,
        errors=errors,
    )


if __name__ == "__main__":
    sys.exit(main())
