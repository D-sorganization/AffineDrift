#!/usr/bin/env python3
"""Prune internal markdown and non-deployable source files from docs/ deploy artifact directory."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def prune_internal_markdown_files(docs_dir: Path) -> list[Path]:
    """Remove raw markdown files from docs/ deploy directory so internal docs are not published.

    Args:
        docs_dir: Path to the docs directory containing rendered output.

    Returns:
        List of deleted Path objects.
    """
    deleted: list[Path] = []
    if not docs_dir.exists():
        return deleted

    for md_file in list(docs_dir.rglob("*.md")):
        try:
            md_file.unlink()
            deleted.append(md_file)
        except OSError as exc:
            logger.warning("Failed to unlink %s: %s", md_file, exc)

    return deleted


def main() -> int:
    parser = argparse.ArgumentParser(description="Prune raw markdown from deploy output")
    parser.add_argument(
        "--docs-dir",
        default="docs",
        help="Path to docs directory (default: docs)",
    )
    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    deleted = prune_internal_markdown_files(docs_dir)
    print(f"Pruned {len(deleted)} internal markdown files from {docs_dir}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
