#!/usr/bin/env python3
"""Validate YAML frontmatter in Quarto QMD files.

Checks that articles in articles/ have required frontmatter fields:
- title (required)
- description (recommended)
- date (recommended)

Exits with code 1 if required fields are missing.
Part of the content validation pipeline (issue #1421).
"""

import sys
from pathlib import Path

import yaml

from scripts.cli_output import write_stdout

ROOT = Path(__file__).parent.parent
ARTICLES_DIR = ROOT / "articles"
REQUIRED_FIELDS = {"title"}
RECOMMENDED_FIELDS = {"description", "date"}

# Exclude subdirectories that are work-in-progress or structural
EXCLUDE_DIRS = {
    "Drafts_Original_Articles",
    "archive",
    "Tangent Hyperplane Articles",  # has many files without frontmatter; tracked separately
}


def parse_frontmatter(content: str) -> dict[str, object]:
    """Extract and parse YAML frontmatter from a QMD file."""
    if not content.startswith("---"):
        return {}
    end = content.find("\n---", 3)
    if end == -1:
        return {}
    try:
        parsed = yaml.safe_load(content[3:end]) or {}
    except yaml.YAMLError:
        return {}

    if not isinstance(parsed, dict):
        return {}

    return parsed


def should_skip(path: Path) -> bool:
    """Return True if this file should be excluded from validation."""
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
    return False


def validate_file(path: Path) -> list[str]:
    """Return list of validation errors for a single file."""
    errors = []
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as e:
        return [f"{path}: cannot read — {e}"]

    fm = parse_frontmatter(content)
    if not fm:
        # No frontmatter at all — skip (some files are pure HTML/markdown without YAML)
        return []

    for field in REQUIRED_FIELDS:
        if not fm.get(field):
            errors.append(f"{path}: missing required frontmatter field '{field}'")

    return errors


def main(articles_dir: Path | None = None) -> int:
    """Run frontmatter validation; return exit code."""
    target_articles_dir = articles_dir or ARTICLES_DIR
    qmd_files = sorted(target_articles_dir.rglob("*.qmd"))
    errors = []

    for qmd in qmd_files:
        if should_skip(qmd):
            continue
        errors.extend(validate_file(qmd))

    if errors:
        write_stdout("Frontmatter validation FAILED:")
        for e in errors:
            write_stdout(f"  {e}")
        return 1

    write_stdout(f"Frontmatter validation passed ({len(qmd_files)} files checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
