#!/usr/bin/env python3
"""Fail CI on net-new over-budget changed files."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

try:
    from scripts.check_module_size_budget import line_count
    from src.tools.utils.budget_check_utils import load_config, report_results
except ModuleNotFoundError:
    repo_root = Path(__file__).resolve().parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from scripts.check_module_size_budget import line_count
    from src.tools.utils.budget_check_utils import load_config, report_results


def _merge_base(repo_root: Path) -> str:
    """Resolve a stable merge base for changed-file comparisons."""
    candidates = ["origin/main", "main", "HEAD~1"]
    for candidate in candidates:
        try:
            result = subprocess.run(
                ["git", "merge-base", "HEAD", candidate],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
            )
            sha = result.stdout.strip()
            if sha:
                return sha
        except subprocess.CalledProcessError:
            continue
    return "HEAD~1"


def _changed_files(repo_root: Path, base_ref: str) -> list[str]:
    """Return repo-relative changed file paths."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", f"{base_ref}...HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        # In shallow CI merge checkouts, merge-base refs may be unavailable.
        # Fall back to changed files in current HEAD commit.
        result = subprocess.run(
            ["git", "show", "--name-only", "--pretty=", "--diff-filter=ACMR", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    """Check changed files against the module size budget configuration."""
    repo_root = Path(__file__).resolve().parent.parent
    config = load_config(repo_root, "module_size_budget.json")
    max_by_ext = {k.lower(): int(v) for k, v in config["max_lines_by_extension"].items()}
    explicit_limits = {k: int(v) for k, v in config["explicit_limits"].items()}
    exclude_substrings = config["exclude_substrings"]

    base_ref = _merge_base(repo_root)
    changed = _changed_files(repo_root, base_ref)

    violations: list[str] = []
    checked = 0

    for rel in changed:
        if any(excl in rel for excl in exclude_substrings):
            continue
        path = repo_root / rel
        if not path.exists() or not path.is_file():
            continue

        if rel in explicit_limits:
            max_lines = explicit_limits[rel]
        else:
            max_lines = max_by_ext.get(path.suffix.lower())
            if max_lines is None:
                continue

        checked += 1
        lines = line_count(path)
        if lines > max_lines:
            violations.append(f"{rel}: {lines} > {max_lines}")

    return report_results(
        "Changed-file module size budget check",
        files_scanned=checked,
        details=[f"base_ref={base_ref}", f"changed_candidates={len(changed)}"],
        errors=violations,
    )


if __name__ == "__main__":
    sys.exit(main())
