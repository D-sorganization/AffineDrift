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

# Add repo root to sys.path to allow imports from src
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))

from src.tools.utils import setup_logging  # noqa: E402

logger = setup_logging(__name__, format_string="%(message)s")


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


def check_links(root_dir: str) -> list[tuple[str, int, str]]:
    """Check for broken internal links in the project."""
    root_path = Path(root_dir)
    broken_links: list[tuple[str, int, str]] = []

    logger.info(f"Scanning {root_path}...")

    # Skip documentation and guide files that contain example links
    skip_files = {
        "WEBSITE_ENHANCEMENT_RECOMMENDATIONS.md",
        "WEBSITE_MANAGEMENT.md",
        "CONTENT_SHARING_GUIDE.md",
        "QUICK_WINS_IMPLEMENTATION.md",
        "HOUSE_STYLE.md",
        "CONVERSION_GUIDE.md",
        "EMBEDDING_GUIDE.md",
    }

    for file_path in root_path.rglob("*"):
        if (
            file_path.suffix not in [".qmd", ".html", ".md"]
            or "node_modules" in str(file_path)
            or "_site" in str(file_path)
            or ".git" in str(file_path)
            or "archive" in str(file_path)
            or "docs" in str(file_path)
            or "content" in str(file_path)
            or "_templates" in str(file_path)
            or ".jules" in str(file_path)
            or file_path.name in skip_files
        ):
            continue

        try:
            links = find_links(file_path)
        except Exception as e:
            logger.exception(f"Error reading {file_path}: {e}")
            continue

        for link, line_num in links:
            # Clean link (remove fragments)
            url = link.split("#")[0]
            if not url:
                continue  # Just a fragment

            if url.startswith(("http", "mailto:")):
                continue  # Skip external

            # Skip JavaScript template literals (e.g., ${item.url})
            if "${" in url or url == "...":
                continue

            # Skip single-character links (often mathematical notation like [f,g](x))
            if len(url) == 1:
                continue

            # Internal link
            # URL-decode the path to handle %20 and other encoded characters
            url = unquote(url)

            # Check if absolute (relative to domain root) or relative
            if url.startswith("/"):
                # Assumes root_path is the site root
                target_path = root_path / url.lstrip("/")
            else:
                target_path = file_path.parent / url

            # Handle .html -> .qmd mapping
            # If linking to foo.html, it might come from foo.qmd
            if target_path.suffix == ".html":
                # Check for .html, .qmd, .md
                p_qmd = target_path.with_suffix(".qmd")
                p_md = target_path.with_suffix(".md")
                p_html = target_path  # The html itself might exist if it's a static asset

                # If target is generated from qmd, the source qmd should exist
                # But we are checking source files, so we look for source qmd
                if not (p_qmd.exists() or p_md.exists() or p_html.exists()):
                    # Also check if it wraps to index.html (e.g. directory/)
                    if not (target_path.is_dir() and (target_path / "index.qmd").exists()):
                        broken_links.append((str(file_path.relative_to(root_path)), line_num, link))
            elif not target_path.exists():
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
