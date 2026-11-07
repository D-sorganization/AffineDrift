#!/usr/bin/env python3
"""Prune non-deployable stray artifacts from the Quarto build output directory.

Issue #4597: the build output moved to ``_site/`` (see ``_quarto.yml``), which
is no longer the same directory as the tracked internal documentation under
``docs/`` (ADRs, dev logs, CSS plans). Raw markdown from that tracked content
can therefore no longer land in the deploy artifact, so this script only
handles the remaining, unrelated concerns: legacy HTML resources that Quarto's
render-exclusion copies pull into the output regardless, and a stale polyfill
tag Pandoc still emits.
"""

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
    Path("docs/development"),
    Path("research"),
)
INTERNAL_DEPLOY_FILES = (
    Path("articles/tangent-hyperplane-articles/Tangent_Hyperplanes.html"),
    Path("content/wrist-as-universal-joint/Wrist_Universal_Claude.html"),
)
LEGACY_MATH_POLYFILL = re.compile(
    r"\s*<script\s+src=[\"']https://cdnjs\.cloudflare\.com/polyfill/v3/"
    r"polyfill\.min\.js\?features=es6[\"']></script>\s*",
    re.IGNORECASE,
)
SITEMAP_URL_BLOCK = re.compile(
    r"\s*<url>\s*<loc>https?://[^/<]+/(?P<rel_path>[^<]+)</loc>.*?</url>",
    re.DOTALL,
)


def _is_internal_route(rel_path: str) -> bool:
    normalized = rel_path.lstrip("/")
    if any(normalized == f.as_posix() for f in INTERNAL_DEPLOY_FILES):
        return True
    return any(
        normalized == d.as_posix() or normalized.startswith(f"{d.as_posix()}/")
        for d in INTERNAL_DEPLOY_DIRECTORIES
    )


def strip_internal_sitemap_entries(docs_dir: Path) -> bool:
    """Remove pruned internal routes from ``sitemap.xml`` if present."""
    sitemap = docs_dir / "sitemap.xml"
    if not sitemap.is_file():
        return False
    original = sitemap.read_text(encoding="utf-8")
    sanitized = SITEMAP_URL_BLOCK.sub(
        lambda m: "" if _is_internal_route(m.group("rel_path")) else m.group(0),
        original,
    )
    if sanitized != original:
        sitemap.write_text(sanitized, encoding="utf-8")
        return True
    return False


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


def prune_internal_deploy_artifacts(docs_dir: Path) -> list[Path]:
    """Remove every explicitly nonpublic artifact from a rendered deployment.

    Quarto's render exclusions prevent QMD execution but do not stop existing
    HTML files under an excluded source tree from being copied as resources.
    This post-render boundary removes those known internal/retired HTML
    projections before manifest generation and upload.
    """
    strip_legacy_math_polyfill(docs_dir)
    deleted: list[Path] = []
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

    strip_internal_sitemap_entries(docs_dir)
    return deleted


def main() -> int:
    parser = argparse.ArgumentParser(description="Prune internal artifacts from deploy output")
    parser.add_argument(
        "--docs-dir",
        default="_site",
        help="Path to the Quarto build output directory (default: _site)",
    )
    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    deleted = prune_internal_deploy_artifacts(docs_dir)
    print(f"Pruned {len(deleted)} internal deploy artifacts from {docs_dir}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
