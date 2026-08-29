#!/usr/bin/env python3
"""Prune internal markdown and non-deployable source files from docs/ deploy artifact directory."""

from __future__ import annotations

import argparse
import logging
import re
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

INTERNAL_DEPLOY_DIRECTORIES = (
    Path("articles/tangent-hyperplane-contraction"),
    Path("articles/tangent-hyperplane-articles/Drafts_Original_Articles"),
)
INTERNAL_DEPLOY_FILES = (Path("articles/tangent-hyperplane-articles/Tangent_Hyperplanes.html"),)
LEGACY_MATH_POLYFILL = re.compile(
    r"\s*<script\s+src=[\"']https://cdnjs\.cloudflare\.com/polyfill/v3/"
    r"polyfill\.min\.js\?features=es6[\"']></script>\s*",
    re.IGNORECASE,
)


def strip_legacy_math_polyfill(docs_dir: Path) -> list[Path]:
    """Remove Pandoc's obsolete ES6 polyfill without touching the math gate.

    The configured local placeholder makes Pandoc serialize TeX for MathJax,
    while ``mathjax-loader.html`` conditionally loads the pinned runtime. Pandoc
    still emits this legacy third-party polyfill; modern supported browsers do
    not need it, and the site's CSP intentionally rejects it.
    """
    changed: list[Path] = []
    if not docs_dir.is_dir():
        return changed

    for html_file in sorted(docs_dir.rglob("*.html")):
        content = html_file.read_text(encoding="utf-8")
        sanitized, replacements = LEGACY_MATH_POLYFILL.subn("\n", content)
        if replacements:
            html_file.write_text(sanitized, encoding="utf-8")
            changed.append(html_file)
    return changed


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


def prune_internal_deploy_artifacts(docs_dir: Path) -> list[Path]:
    """Remove every explicitly nonpublic artifact from a rendered deployment.

    Quarto's render exclusions prevent QMD execution but do not stop existing
    HTML files under an excluded source tree from being copied as resources.
    This post-render boundary therefore removes both raw Markdown and the known
    internal/retired HTML projections before manifest generation and upload.
    """
    strip_legacy_math_polyfill(docs_dir)
    deleted = prune_internal_markdown_files(docs_dir)
    if not docs_dir.is_dir():
        return deleted

    for relative_path in INTERNAL_DEPLOY_FILES:
        target = docs_dir / relative_path
        if target.is_file():
            target.unlink()
            deleted.append(target)

    for relative_dir in INTERNAL_DEPLOY_DIRECTORIES:
        target_dir = docs_dir / relative_dir
        if not target_dir.is_dir():
            continue
        files = sorted(path for path in target_dir.rglob("*") if path.is_file())
        shutil.rmtree(target_dir)
        deleted.extend(files)

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
    deleted = prune_internal_deploy_artifacts(docs_dir)
    print(f"Pruned {len(deleted)} internal deploy artifacts from {docs_dir}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
