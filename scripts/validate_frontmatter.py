#!/usr/bin/env python3
"""Validate YAML frontmatter in Quarto QMD files.

Checks that articles in articles/ have required frontmatter fields:
- title (required)
- description (recommended)
- date (recommended)

Exits with code 1 if required fields are missing.
Part of the content validation pipeline (issue #1421).
"""

import re
import sys
from pathlib import Path

from scripts.cli_output import write_stdout
from src.tools.utils.frontmatter import split_frontmatter

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
    """Extract and parse YAML frontmatter from a QMD file.

    Thin wrapper around :func:`src.tools.utils.frontmatter.split_frontmatter`
    kept for backward compatibility with callers in this module.
    """
    fm, _ = split_frontmatter(content)
    return fm


H1 = re.compile(r"#\s+\S")
FENCE = re.compile(r"\s*(?:```+|~~~+)")


def has_body_h1(body: str) -> bool:
    """Return True if the body carries a level-1 heading outside fenced code.

    Quarto uses the first H1 as the document title when the frontmatter has
    none, so such a file is titled -- just not in YAML. Book chapters depend on
    this: a `{#sec-...}` anchor can only attach to a heading, never to a YAML
    key, so a chapter that is cross-referenced cannot keep its title in the
    frontmatter. Requiring both instead renders the title twice, which is what
    the book shipped until #3702.
    """
    in_fence = False
    for line in body.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence and H1.match(line):
            return True
    return False


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

    fm, body = split_frontmatter(content)
    if not fm:
        # No frontmatter at all — skip (some files are pure HTML/markdown without YAML)
        return []

    for field in REQUIRED_FIELDS:
        if fm.get(field):
            continue
        if field == "title" and has_body_h1(body):
            continue
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
