#!/usr/bin/env python3
"""Derive and validate publication dates and revision history metadata (WEB-07.3 #4545).

Usage:
    python -m scripts.derive_substantive_dates [--check] [--fix]
"""

from __future__ import annotations

import argparse
import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from src.tools.utils.frontmatter import split_frontmatter

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
ARTICLES_DIR = ROOT / "articles"

DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def get_latest_git_commit_date(file_path: Path) -> str | None:
    """Get the date of the most recent commit for a file."""
    git_bin = shutil.which("git") or "git"
    try:
        res = subprocess.run(
            [git_bin, "log", "-n", "1", "--format=%ad", "--date=short", "--", str(file_path)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
        date_str = res.stdout.strip()
        if DATE_REGEX.match(date_str):
            return date_str
    except (subprocess.SubprocessError, OSError) as exc:
        logger.debug("Failed to retrieve git commit date for %s: %s", file_path, exc)
    return None


def get_all_project_qmd_files() -> list[Path]:
    """Return all renderable QMD files in the project."""
    files = []
    for path in ROOT.glob("**/*.qmd"):
        if any(
            part in path.parts
            for part in [
                ".git",
                "node_modules",
                "_site",
                "docs",
                ".quarto",
                "build",
                "proximal_distal_energy_transfer",
            ]
        ):
            continue
        files.append(path)
    return sorted(files)


def validate_dates(check_only: bool = False) -> tuple[list[str], int]:
    """Validate all files against date contracts.

    Returns:
        (errors_list, total_files_scanned)
    """
    del check_only
    errors: list[str] = []
    files = get_all_project_qmd_files()

    for path in files:
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        content = path.read_text(encoding="utf-8")
        fm, _ = split_frontmatter(content)
        if not fm:
            continue

        date_val = fm.get("date")
        if date_val is not None:
            date_str = str(date_val).strip()
            if date_str.lower() == "today":
                errors.append(f"{rel}: contains forbidden 'date: today'")
            else:
                date_source = fm.get("date-source")
                if not date_source:
                    errors.append(f"{rel}: has date '{date_str}' but missing 'date-source:'")

        # If changes are defined, verify latest date matches date-modified if present
        changes = fm.get("changes")
        if isinstance(changes, list) and len(changes) > 0:
            latest_change = changes[0]
            if isinstance(latest_change, dict) and "date" in latest_change:
                expected_modified = str(latest_change["date"]).strip()
                date_modified = str(fm.get("date-modified", "")).strip()
                if date_modified and date_modified != expected_modified:
                    errors.append(
                        f"{rel}: date-modified '{date_modified}' does not match latest change '{expected_modified}'"
                    )

    return errors, len(files)


def apply_date_fixes() -> int:
    """Apply standard date fixes across QMD files."""
    modified_count = 0
    files = get_all_project_qmd_files()

    for path in files:
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            continue
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue

        raw_fm = parts[1]
        body = parts[2]

        try:
            fm = yaml.safe_load(raw_fm)
        except yaml.YAMLError as exc:
            logger.warning("Skipping unparseable frontmatter in %s: %s", path, exc)
            continue

        if not isinstance(fm, dict):
            continue

        changed = False

        date_val = fm.get("date")
        if date_val is not None:
            date_str = str(date_val).strip()
            if date_str.lower() == "today":
                fm["date"] = "Date unverified"
                fm["date-source"] = "unverified"
                git_date = get_latest_git_commit_date(path)
                if git_date and "date-modified" not in fm:
                    fm["date-modified"] = git_date
                changed = True
            elif date_str.lower() == "last-modified":
                fm["date"] = "Date unverified"
                fm["date-source"] = "unverified"
                changed = True
            elif DATE_REGEX.match(date_str) or hasattr(date_val, "strftime"):
                if "date-source" not in fm:
                    fm["date-source"] = "initial-publication-record"
                    changed = True

        if changed:
            new_fm = yaml.dump(fm, sort_keys=False, allow_unicode=True, width=1000)
            new_content = f"---\n{new_fm.strip()}\n---{body}"
            path.write_text(new_content, encoding="utf-8")
            modified_count += 1

    return modified_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Check date metadata without modifying files"
    )
    parser.add_argument("--fix", action="store_true", help="Apply automated date metadata fixes")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.fix:
        count = apply_date_fixes()
        print(f"Applied date metadata fixes to {count} file(s).")

    errors, scanned = validate_dates(check_only=args.check)
    if errors:
        print(
            f"Found {len(errors)} date contract violation(s) across {scanned} scanned files:",
            file=sys.stderr,
        )
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"Date metadata validation passed ({scanned} files scanned).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
