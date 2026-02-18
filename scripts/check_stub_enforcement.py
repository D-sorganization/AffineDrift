#!/usr/bin/env python3
"""Fail CI when untracked placeholder/stub code is detected in production modules.

This guardrail prevents new stub functions (``pass`` bodies, ``raise NotImplementedError``,
``...`` ellipsis bodies) from being introduced without an associated tracking issue.

Stubs that are explicitly tracked in ``config/stub_enforcement.json`` are allowed.
Exception-handler ``pass`` statements and abstract method stubs are always allowed.
"""

from __future__ import annotations

import ast
import logging
import sys
from pathlib import Path

from src.tools.utils.budget_check_utils import (
    collect_matching_files,
    load_config,
    read_text_safe,
    report_results,
)

logger = logging.getLogger(__name__)


def _is_exception_handler_pass(node: ast.Pass, tree: ast.Module) -> bool:
    """Check if a Pass node is inside an exception handler."""
    for parent in ast.walk(tree):
        if isinstance(parent, ast.ExceptHandler):
            for child in ast.walk(parent):
                if child is node:
                    return True
    return False


def _is_abstract_method(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Check if a function is an abstract method via decorator."""
    for decorator in func_node.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id in (
            "abstractmethod",
            "abstractproperty",
        ):
            return True
        if isinstance(decorator, ast.Attribute) and decorator.attr in (
            "abstractmethod",
            "abstractproperty",
        ):
            return True
    return False


def _find_stub_functions(source: str, filepath: str) -> list[str]:
    """Find stub functions in Python source code.

    Returns list of stub descriptions (e.g. 'funcname at line N').
    """
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return []

    stubs: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue

        # Skip abstract methods
        if _is_abstract_method(node):
            continue

        body = node.body
        if not body:
            continue

        # Check for single-statement stub bodies
        if len(body) == 1:
            stmt = body[0]

            # pass statement (not in exception handler)
            if isinstance(stmt, ast.Pass):
                stubs.append(f"{node.name} at line {node.lineno}: bare `pass` body")
                continue

            # Ellipsis (...) body
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                if stmt.value.value is ...:
                    stubs.append(f"{node.name} at line {node.lineno}: ellipsis body")
                    continue

            # raise NotImplementedError
            if isinstance(stmt, ast.Raise) and stmt.exc is not None:
                if isinstance(stmt.exc, ast.Call) and isinstance(stmt.exc.func, ast.Name):
                    if stmt.exc.func.id == "NotImplementedError":
                        stubs.append(
                            f"{node.name} at line {node.lineno}: raises NotImplementedError"
                        )
                        continue

        # Check for docstring + pass/ellipsis (2-statement body)
        if len(body) == 2:
            first, second = body
            is_docstring = isinstance(first, ast.Expr) and isinstance(
                first.value, ast.Constant | ast.Str
            )
            if is_docstring:
                if isinstance(second, ast.Pass):
                    stubs.append(f"{node.name} at line {node.lineno}: docstring + pass")
                elif isinstance(second, ast.Expr) and isinstance(second.value, ast.Constant):
                    if second.value.value is ...:
                        stubs.append(f"{node.name} at line {node.lineno}: docstring + ellipsis")

    return stubs


def main() -> int:
    """Check for untracked stub/placeholder code in production modules."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    repo_root = Path(__file__).resolve().parent.parent
    config = load_config(repo_root, "stub_enforcement.json")

    allowed_exts = set(config["file_extensions"])
    max_untracked = int(config["max_untracked_stubs"])
    tracked_stubs = config.get("tracked_stubs", {})

    files = collect_matching_files(
        repo_root,
        config["include_roots"],
        config["exclude_substrings"],
        allowed_exts,
    )

    all_stubs: list[str] = []
    untracked_stubs: list[str] = []

    for path in files:
        text = read_text_safe(path)
        if text is None:
            continue

        rel_path = str(path.relative_to(repo_root)).replace("\\", "/")
        stubs = _find_stub_functions(text, rel_path)

        for stub_desc in stubs:
            full_desc = f"{rel_path}: {stub_desc}"
            all_stubs.append(full_desc)

            if rel_path not in tracked_stubs:
                untracked_stubs.append(full_desc)

    details = [
        f"total stub functions found: {len(all_stubs)}",
        f"tracked (allowed): {len(all_stubs) - len(untracked_stubs)}",
        f"untracked: {len(untracked_stubs)} (max {max_untracked})",
    ]

    errors: list[str] = []
    if len(untracked_stubs) > max_untracked:
        errors.append(f"Untracked stub budget exceeded: {len(untracked_stubs)} > {max_untracked}")
        for stub in untracked_stubs:
            errors.append(f"  - {stub}")

    return report_results("Stub enforcement check", len(files), details, errors)


if __name__ == "__main__":
    sys.exit(main())
