#!/usr/bin/env python3
"""Select changed paths that must run protected site and visual E2E checks."""

from __future__ import annotations

import sys
from collections.abc import Iterable

EXACT_PATHS = frozenset(
    {
        ".github/workflows/ci-standard.yml",
        ".github/workflows/deploy-website.yml",
        "_quarto.yml",
        "custom.scss",
        "package-lock.json",
        "package.json",
        "reports/scientific-claim-audit.md",
        "schemas/public-site-screenshot-baseline-v1.schema.json",
        "schemas/public-site-screenshot-evidence-v1.schema.json",
        "scripts/bundle_css.py",
        "scripts/e2e_relevant_paths.py",
        "scripts/prune_internal_docs_from_deploy.py",
        "scripts/public-site-evidence.js",
        "scripts/public_site_manifest.py",
        "scripts/sync_frontend_assets.py",
        "scripts/update_sw_cache_version.py",
        "scripts/verify-public-site-visual.js",
        "scripts/verify-public-site.js",
        "styles.css",
    }
)
PATH_PREFIXES = (
    "books/",
    "critiques/",
    "css/",
    "js/",
    "pages/",
    "posts/",
    "resources/",
    "src/js/",
    "tests/e2e/",
)
DOCS_DEPLOY_SUFFIXES = (".css", ".html", ".js", ".qmd")


def normalize_path(path: str) -> str:
    """Return the repository-relative, POSIX-style spelling of a changed path."""
    return path.strip().replace("\\", "/").removeprefix("./")


def is_e2e_relevant(path: str) -> bool:
    """Return whether one repository path can affect browser evidence."""
    normalized = normalize_path(path)
    if not normalized:
        return False
    if normalized in EXACT_PATHS:
        return True
    if normalized.startswith("playwright.config."):
        return True
    if normalized.endswith(".qmd"):
        return True
    if normalized.startswith(PATH_PREFIXES):
        return True
    return normalized.startswith("docs/") and normalized.endswith(DOCS_DEPLOY_SUFFIXES)


def relevant_paths(paths: Iterable[str]) -> tuple[str, ...]:
    """Filter changed paths deterministically while preserving Git order."""
    return tuple(
        normalized
        for path in paths
        if (normalized := normalize_path(path)) and is_e2e_relevant(normalized)
    )


def main() -> int:
    """Print relevant changed paths, one per line, for GitHub Actions."""
    selected = relevant_paths(sys.stdin)
    if selected:
        sys.stdout.write("\n".join(selected) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
