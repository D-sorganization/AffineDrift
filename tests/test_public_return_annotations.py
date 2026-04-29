"""Regression tests for public return-annotation coverage in Python modules."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest


def _collect_missing_return_annotations(path: Path, repo_root: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:  # pragma: no cover - defensive failure path
        raise AssertionError(f"Failed to parse {path}: {exc}") from exc

    missing = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        if node.name.startswith("_"):
            continue
        if node.returns is None:
            missing.append(f"{path.relative_to(repo_root)}:{node.lineno}:{node.name}")
    return missing


def test_public_functions_in_src_and_scripts_have_return_annotations() -> None:
    """Public Python functions in src/ and scripts/ should declare return types."""
    if sys.version_info < (3, 12):  # noqa: UP036
        pytest.skip("Repository source uses Python 3.12 syntax; run this check on Python 3.12+.")

    repo_root = Path(__file__).resolve().parents[1]
    missing: list[str] = []

    for relative_dir in ("src", "scripts"):
        for path in (repo_root / relative_dir).rglob("*.py"):
            missing.extend(_collect_missing_return_annotations(path, repo_root))

    assert missing == []
