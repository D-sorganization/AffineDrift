#!/usr/bin/env python3
"""Normalize the wrist article HTML with repo-root-relative path handling.

The script keeps the existing HTML cleanup rules, but resolves paths relative to
the repository root so it can run from any checkout without a hardcoded local
Windows path.
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from src.tools.utils.cli_contracts import ensure_existing_dir, ensure_existing_file

DEFAULT_INPUT = Path("content/wrist-as-universal-joint/Wrist_Universal_Claude.html")

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the HTML normalization script."""
    parser = argparse.ArgumentParser(description="Normalize generated wrist article HTML")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Repository root used to resolve relative paths",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Input HTML file, resolved relative to --repo-root by default",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output HTML file; defaults to rewriting the input in place",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing files",
    )
    return parser


def resolve_repo_relative_path(repo_root: Path, path: Path) -> Path:
    """Resolve a CLI path against the repository root when it is relative."""
    return path if path.is_absolute() else repo_root / path


def remove_paragraph_wrappers_before_lists(content: str) -> str:
    """Remove stray paragraph tags before list blocks."""
    while "<p>\n\n" in content:
        content = content.replace("<p>\n\n", "<p>\n")
    content = content.replace("<p>\n<ul>", "<ul>")
    return content.replace("<p>\n<ol>", "<ol>")


def normalize_list_item_spacing(content: str) -> str:
    """Normalize list-item separators to one item per line."""
    while "</li></li>" in content:
        content = content.replace("</li></li>", "</li>")
    return content.replace("</li><li>", "</li>\n<li>")


def normalize_list_block_openers(content: str) -> str:
    """Fix malformed list openers that contain stray list-item markup."""
    content = content.replace("<ul></li>\n<li>", "<ul>\n<li>")
    content = content.replace("<ul>\n</li>\n<li>", "<ul>\n<li>")
    content = content.replace("<ol></li>\n<li>", "<ol>\n<li>")
    return content.replace("<ol>\n</li>\n<li>", "<ol>\n<li>")


def unwrap_math_block_paragraphs(content: str) -> str:
    """Remove paragraph wrappers around math and quote blocks."""
    content = content.replace("<p>\\begin{align}", "\\begin{align}")
    content = content.replace("\\end{align}</p>", "\\end{align}")
    return content.replace("<p>\\begin{quote}", "\\begin{quote}")


def normalize_html_content(content: str) -> str:
    """Apply the normalization rules used by the legacy fixer."""
    content = remove_paragraph_wrappers_before_lists(content)
    content = normalize_list_item_spacing(content)
    content = normalize_list_block_openers(content)
    return unwrap_math_block_paragraphs(content)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the normalization CLI."""
    args = build_parser().parse_args(argv)

    try:
        repo_root = ensure_existing_dir(str(args.repo_root), value_name="--repo-root")
        input_path = resolve_repo_relative_path(repo_root, args.input)
        input_file = ensure_existing_file(str(input_path), value_name="--input")
        output_path = (
            resolve_repo_relative_path(repo_root, args.output) if args.output else input_file
        )
    except ValueError as exc:
        logger.error(str(exc))
        return 2

    original = input_file.read_text(encoding="utf-8")
    normalized = normalize_html_content(original)

    if args.dry_run:
        if output_path != input_file or normalized != original:
            logger.info("[DRY-RUN] Would write %s", output_path)
        else:
            logger.info("[DRY-RUN] No changes needed for %s", input_file)
        return 0

    if output_path == input_file:
        if normalized != original:
            input_file.write_text(normalized, encoding="utf-8")
            logger.info("Wrote %s", input_file)
        else:
            logger.info("No changes needed for %s", input_file)
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(normalized, encoding="utf-8")
    logger.info("Wrote %s", output_path)
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    sys.exit(main())
