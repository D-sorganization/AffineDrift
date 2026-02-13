#!/usr/bin/env python3
"""Ensure DRY shared content helpers are used in key scripts."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from src.tools.utils.budget_check_utils import report_results
except ModuleNotFoundError:
    repo_root = Path(__file__).resolve().parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from src.tools.utils.budget_check_utils import report_results


def _requires_token(path: Path, token: str) -> str | None:
    text = path.read_text(encoding="utf-8")
    if token not in text:
        return f"{path.as_posix()} missing token: {token}"
    return None


def main() -> int:
    """Check that targeted scripts keep using shared content utilities."""
    repo_root = Path(__file__).resolve().parent.parent

    checks: list[tuple[str, str]] = [
        ("scripts/generate_search_index.py", "collect_qmd_files"),
        ("scripts/generate_search_index.py", "read_qmd_with_frontmatter"),
        ("scripts/add_meta_descriptions.py", "read_qmd_with_frontmatter"),
    ]

    errors: list[str] = []
    for rel_path, token in checks:
        path = repo_root / rel_path
        if not path.exists():
            errors.append(f"Missing required file: {rel_path}")
            continue
        maybe_error = _requires_token(path, token)
        if maybe_error:
            errors.append(maybe_error)

    return report_results(
        "DRY shared-helper adoption check",
        files_scanned=len(checks),
        details=["shared content utilities required in targeted scripts"],
        errors=errors,
    )


if __name__ == "__main__":
    sys.exit(main())
