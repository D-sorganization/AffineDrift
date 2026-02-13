#!/usr/bin/env python3
"""Enforce JavaScript dependency direction rules for website modules."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from src.tools.utils.budget_check_utils import load_config, report_results

IMPORT_RE = re.compile(r"""import\s+(?:[^"']+?\s+from\s+)?["']([^"']+)["']""")
DYNAMIC_IMPORT_RE = re.compile(r"""import\(\s*["']([^"']+)["']\s*\)""")


def _extract_imports(path: Path) -> list[tuple[int, str]]:
    """Extract JS import specifiers and their line numbers from a file."""
    imports: list[tuple[int, str]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        for match in IMPORT_RE.finditer(line):
            imports.append((line_no, match.group(1)))
        for match in DYNAMIC_IMPORT_RE.finditer(line):
            imports.append((line_no, match.group(1)))
    return imports


def _resolve_import_target(repo_root: Path, source_rel: str, specifier: str) -> str | None:
    """Resolve a JS import specifier to a repo-relative path when possible."""
    if specifier.startswith("."):
        resolved = (repo_root / Path(source_rel).parent / specifier).resolve()
        return resolved.as_posix()
    if specifier.startswith("/"):
        return specifier.lstrip("/")
    return None


def _to_repo_relative(repo_root: Path, candidate: str) -> str | None:
    """Convert an absolute or relative path to repo-relative POSIX form."""
    candidate_path = Path(candidate)
    if candidate_path.is_absolute():
        try:
            return candidate_path.relative_to(repo_root).as_posix()
        except ValueError:
            return None
    return candidate.replace("\\", "/")


def check_rules(repo_root: Path) -> list[str]:
    """Check all JS dependency boundary rules from config."""
    config = load_config(repo_root, "js_dependency_boundaries.json")
    rules = config["rules"]
    excludes = config["exclude_substrings"]

    violations: list[str] = []
    for file_path in repo_root.rglob("*.js"):
        rel = file_path.relative_to(repo_root).as_posix()
        if not file_path.is_file():
            continue
        if "node_modules/" in rel:
            continue
        if any(excl in rel for excl in excludes):
            continue

        imports = _extract_imports(file_path)
        for line_no, specifier in imports:
            candidate = _resolve_import_target(repo_root, rel, specifier)
            if not candidate:
                continue
            imported_rel = _to_repo_relative(repo_root, candidate)
            if not imported_rel:
                continue

            for rule in rules:
                source_prefix = rule["source_prefix"]
                if not rel.startswith(source_prefix):
                    continue
                for forbidden_prefix in rule["forbidden_prefixes"]:
                    if imported_rel.startswith(forbidden_prefix):
                        violations.append(
                            f"{rel}:{line_no} {source_prefix} must not import "
                            f"{forbidden_prefix} (found: {specifier})"
                        )

    return violations


def main() -> int:
    """Run the JavaScript dependency boundary check."""
    repo_root = Path(__file__).resolve().parent.parent
    violations = check_rules(repo_root)
    return report_results(
        "JavaScript dependency boundary check",
        files_scanned=0,
        details=["passed" if not violations else f"{len(violations)} violations"],
        errors=violations,
    )


if __name__ == "__main__":
    sys.exit(main())
