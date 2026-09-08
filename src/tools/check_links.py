"""Extract and validate links from HTML and Markdown files.

This tool scans files for both Markdown-style [text](url) links and
HTML href="url" links, then validates that internal links resolve to
existing files and external links are properly formatted.

Source-level site link quality checks (include-aware internal link
resolution, path-style normalization, related coverage, orphan detection —
issue #3899) live in ``src.tools.utils.link_checks`` and are exposed here:

Usage:
    python -m src.tools.check_links                 # legacy broken-link scan
    python -m src.tools.check_links --source-checks # site link quality gate

Exit codes:
    0 — no violations; 1 — violations found. See docs/LINK-CHECKER.md.
"""

import argparse
import logging
import sys
from pathlib import Path

from src.core.contracts import require
from src.tools.utils import setup_logging
from src.tools.utils.link_checks import DEFAULT_CONFIG_NAME, run_source_checks
from src.tools.utils.link_utils import (
    find_links,
    html_target_resolvable,
    normalize_internal_url,
    path_exists_in_search_roots,
    resolve_relative_path,
)

logger = logging.getLogger(__name__)

logger = setup_logging(__name__, format_string="%(message)s")
SCANNED_EXTENSIONS = {".qmd", ".html"}
SKIP_FILES = {
    "WEBSITE_ENHANCEMENT_RECOMMENDATIONS.md",
    "WEBSITE_MANAGEMENT.md",
    "CONTENT_SHARING_GUIDE.md",
    "QUICK_WINS_IMPLEMENTATION.md",
    "HOUSE_STYLE.md",
    "CONVERSION_GUIDE.md",
    "EMBEDDING_GUIDE.md",
    "CONTRIBUTING.md",
}


def unique_broken(links: list[tuple[str, int, str]]) -> list[tuple[str, int, str]]:
    """Remove duplicate broken links."""
    seen = set()
    unique = []
    for link in links:
        if link not in seen:
            unique.append(link)
            seen.add(link)
    return unique


def _should_scan_file(file_path: Path) -> bool:
    """Return whether a file should be scanned for internal links."""
    return not (
        file_path.suffix not in SCANNED_EXTENSIONS
        or "node_modules" in str(file_path)
        or "_site" in str(file_path)
        or ".git" in str(file_path)
        or "archive" in str(file_path)
        or "docs" in str(file_path)
        or "content" in str(file_path)
        or "_templates" in str(file_path)
        or ".jules" in str(file_path)
        or file_path.name in SKIP_FILES
    )


def _normalize_internal_url(link: str) -> str | None:
    """Normalize link and return internal URL or None for skipped links."""
    return normalize_internal_url(link)


def _resolve_target_path(*, root_path: Path, file_path: Path, url: str) -> Path:
    """Resolve a link URL against a source file and root path."""
    return resolve_relative_path(root=root_path, source_file=file_path, url=url)


def _path_exists_in_search_roots(*, root_path: Path, target_path: Path) -> bool:
    """Check for target existence in root, src, and docs prefixes."""
    return path_exists_in_search_roots(root=root_path, target=target_path)


def _is_html_link_resolvable(*, root_path: Path, target_path: Path) -> bool:
    """Check whether an HTML link can map to source or generated files."""
    return html_target_resolvable(root=root_path, target=target_path)


def _is_broken_link(*, root_path: Path, file_path: Path, link: str) -> bool:
    """Return True if a link is internal and unresolved."""
    url = _normalize_internal_url(link)
    if url is None:
        return False
    target_path = _resolve_target_path(root_path=root_path, file_path=file_path, url=url)
    if target_path.suffix == ".html":
        return not _is_html_link_resolvable(root_path=root_path, target_path=target_path)
    return not _path_exists_in_search_roots(root_path=root_path, target_path=target_path)


def check_links(root_dir: str) -> list[tuple[str, int, str]]:
    """Check for broken internal links in the project."""
    require(len(root_dir) > 0, "root_dir must not be empty")
    root_path = Path(root_dir)
    broken_links: list[tuple[str, int, str]] = []

    logger.info(f"Scanning {root_path}...")

    for file_path in root_path.rglob("*"):
        if not _should_scan_file(file_path):
            continue

        try:
            links = find_links(file_path)
        except (ConnectionError, TimeoutError, OSError) as e:
            logger.exception(f"Error reading {file_path}: {e}")
            continue

        for link, line_num in links:
            if _is_broken_link(root_path=root_path, file_path=file_path, link=link):
                broken_links.append((str(file_path.relative_to(root_path)), line_num, link))

    return unique_broken(broken_links)


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="python -m src.tools.check_links",
        description=(
            "Legacy broken-link scan by default; --source-checks runs the "
            "site link quality gate (issue #3899)."
        ),
    )
    parser.add_argument(
        "--source-checks",
        action="store_true",
        help=("run source-level checks: internal links, path style, " "related coverage, orphans"),
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_NAME,
        help="budget config name resolved under config/ (default: %(default)s)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run link checks and return an exit code (0 pass, 1 violations)."""
    args = _build_parser().parse_args(argv)
    if args.source_checks:
        return run_source_checks(".", args.config)
    broken = check_links(".")
    if broken:
        logger.info("\nBroken Links Found:")
        for file, line, link in broken:
            logger.info(f"{file}:{line} -> {link}")
        return 1
    logger.info("\nNo broken internal links found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
