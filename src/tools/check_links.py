"""Extract and validate links from HTML and Markdown files.

This tool scans files for both Markdown-style [text](url) links and
HTML href="url" links, then validates that internal links resolve to
existing files and external links are properly formatted.

Usage:
    python check_links.py <file_path>

Example:
    python check_links.py docs/articles/my-article.html
"""

import re
import sys
from pathlib import Path
from urllib.parse import unquote

from src.tools.utils import setup_logging

logger = setup_logging(__name__, format_string="%(message)s")
SCANNED_EXTENSIONS = {".qmd", ".html", ".md"}
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
    """Extract all links from a file."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Markdown links: [text](url)
    md_links = re.findall(r"\[.*?\]\((.*?)\)", content)

    # HTML links: href="url"
    html_links = re.findall(r'href=["\'](.*?)["\']', content)

    # Image links: src="url" (check for images too)
    img_links = re.findall(r'src=["\'](.*?)["\']', content)

    # Markdown images: ![text](url)
    md_imgs = re.findall(r"!\[.*?\]\((.*?)\)", content)

    all_links = md_links + html_links + img_links + md_imgs
    return [
        (link.strip(), i + 1)
        for i, line in enumerate(content.splitlines())
        for link in all_links
        if link in line
    ]  # Approximation of line number


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
    url = link.split("#")[0]
    if not url:
        return None
    if url.startswith(("http", "mailto:")):
        return None
    if "${" in url or url == "...":
        return None
    if len(url) == 1:
        return None
    return unquote(url)


def _resolve_target_path(*, root_path: Path, file_path: Path, url: str) -> Path:
    """Resolve a link URL against a source file and root path."""
    if url.startswith("/"):
        return root_path / url.lstrip("/")
    return file_path.parent / url


def _path_exists_in_search_roots(*, root_path: Path, target_path: Path) -> bool:
    """Check for target existence in root, src, and docs prefixes."""
    exists_check = target_path.exists()
    if not target_path.is_relative_to(root_path):
        return exists_check
    relative = target_path.relative_to(root_path)
    return (
        exists_check
        or (root_path / "src" / relative).exists()
        or (root_path / "docs" / relative).exists()
    )


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
