"""Extract and validate links from HTML and Markdown files.

This tool scans files for both Markdown-style [text](url) links and
HTML href="url" links, then validates that internal links resolve to
existing files and external links are properly formatted.

Usage:
    python check_links.py <file_path>

Example:
    python check_links.py docs/articles/my-article.html
"""

import logging
import sys
from pathlib import Path

from src.core.contracts import require
from src.tools.utils import setup_logging
from src.tools.utils.link_utils import (
    ALL_LINK_PATTERNS,
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


def find_links(file_path: Path) -> list[tuple[str, int]]:
    """Extract links and exact source line numbers from a file."""
    require(file_path is not None, "file_path must not be None")
    with open(file_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    links: list[tuple[str, int]] = []
    for line_number, line in enumerate(lines, start=1):
        for pattern in ALL_LINK_PATTERNS:
            links.extend([(match.strip(), line_number) for match in pattern.findall(line)])
    return links


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
    p_qmd = target_path.with_suffix(".qmd")
    p_md = target_path.with_suffix(".md")
    if _path_exists_in_search_roots(root_path=root_path, target_path=p_qmd):
        return True
    if _path_exists_in_search_roots(root_path=root_path, target_path=p_md):
        return True
    if _path_exists_in_search_roots(root_path=root_path, target_path=target_path):
        return True
    return target_path.is_dir() and (target_path / "index.qmd").exists()


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


if __name__ == "__main__":
    broken = check_links(".")
    if broken:
        logger.info("\nBroken Links Found:")
        for file, line, link in broken:
            logger.info(f"{file}:{line} -> {link}")
        sys.exit(1)
    else:
        logger.info("\nNo broken internal links found.")
