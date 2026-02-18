#!/usr/bin/env python3
"""Enforce Python dependency direction rules for core packages."""

from __future__ import annotations

import ast
import logging
import sys
from pathlib import Path

from src.tools.utils.budget_check_utils import load_config, report_results

logger = logging.getLogger(__name__)


def _extract_import_prefixes(path: Path) -> tuple[list[tuple[int, str]], bool]:
    """Extract import module names from a Python file via AST."""
    text = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return ([], True)
    imports: list[tuple[int, str]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append((node.lineno, name.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append((node.lineno, node.module))

    return (imports, False)


def _matches_prefix(module_name: str, prefix: str) -> bool:
    """Check if a module name matches or is under a given prefix."""
    return module_name == prefix or module_name.startswith(f"{prefix}.")


def check_rules(repo_root: Path) -> list[str]:
    """Check all dependency boundary rules from config."""
    config = load_config(repo_root, "dependency_boundaries.json")

    root = repo_root / config["python_root"]
    rules = config["rules"]
    excludes = config["exclude_substrings"]
    violations: list[str] = []
    skipped_files = 0

    for file_path in root.rglob("*.py"):
        rel = file_path.relative_to(repo_root).as_posix()
        if any(excl in rel for excl in excludes):
            continue

        module_name = rel[:-3].replace("/", ".")
        imports, skipped = _extract_import_prefixes(file_path)
        if skipped:
            skipped_files += 1
            continue

        for rule in rules:
            source_prefix = rule["source_prefix"]
            if not _matches_prefix(module_name, source_prefix):
                continue

            for line_no, imported in imports:
                for forbidden in rule["forbidden_prefixes"]:
                    if _matches_prefix(imported, forbidden):
                        violations.append(
                            f"{rel}:{line_no} {source_prefix} must not import "
                            f"{forbidden} (found: {imported})"
                        )

    if skipped_files:
        logger.info("Dependency boundary check: skipped unparsable files=%d", skipped_files)

    return violations


def main() -> int:
    """Run the dependency boundary check."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    repo_root = Path(__file__).resolve().parent.parent
    violations = check_rules(repo_root)
    return report_results(
        "Dependency boundary check",
        files_scanned=0,
        details=["passed" if not violations else f"{len(violations)} violations"],
        errors=violations,
    )


if __name__ == "__main__":
    sys.exit(main())
