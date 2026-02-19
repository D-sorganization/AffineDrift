#!/usr/bin/env python3
"""Generate comprehensive sitemap.xml with proper priorities and change frequencies."""

import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from src.tools.utils import setup_logging
from src.tools.utils.content_utils import collect_qmd_files, read_qmd_with_frontmatter

logger = setup_logging(__name__)


def get_git_last_modified(filepath: str) -> str:
    """Get last modified date from git history."""
    git_cmd = shutil.which("git")
    if not git_cmd:
        return datetime.now().strftime("%Y-%m-%d")

    try:
        result = subprocess.run(
            [git_cmd, "log", "-1", "--format=%cI", "--", filepath],  # noqa: S603
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            # Convert to W3C datetime format
            return result.stdout.strip()[:10]
    except (subprocess.SubprocessError, OSError) as e:
        logger.warning("Failed to get git modified date for %s: %s", filepath, e)
    return datetime.now().strftime("%Y-%m-%d")


def get_priority(filepath: str) -> str:
    """Determine page priority based on content type."""
    if filepath == "index.qmd":
        return "1.0"
    if filepath == "overview.qmd":
        return "0.9"
    if "theory-part" in filepath:
        return "0.9"
    if filepath.startswith("articles/"):
        return "0.8"
    if filepath.startswith("models"):
        return "0.7"
    if filepath.startswith("resources"):
        return "0.6"
    if filepath.startswith("repositories"):
        return "0.6"
    if filepath in ["bibliography.qmd", "drifter-manifesto.qmd"]:
        return "0.8"
    return "0.5"


def get_changefreq(filepath: str) -> str:
    """Determine expected change frequency."""
    if filepath == "index.qmd":
        return "weekly"
    if filepath.startswith("articles/"):
        return "monthly"
    if filepath.startswith("resources"):
        return "weekly"
    if filepath == "bibliography.qmd":
        return "weekly"
    return "monthly"


def main() -> None:
    """Generate sitemap.xml."""
    base_url = "https://affinedrift.com"
    pages: list[dict[str, str]] = []

    for filepath in collect_qmd_files():
        relative_path = str(filepath)
        url_path = relative_path.replace(".qmd", ".html")
        if url_path == "index.html":
            url_path = ""

        _content, frontmatter = read_qmd_with_frontmatter(filepath)

        # Skip pages without titles (likely not standalone pages)
        if not frontmatter.get("title") and filepath.name != "index.qmd":
            continue

        pages.append(
            {
                "loc": f"{base_url}/{url_path}",
                "lastmod": get_git_last_modified(relative_path),
                "changefreq": get_changefreq(relative_path),
                "priority": get_priority(relative_path),
                "title": frontmatter.get("title", ""),
            },
        )

    # Sort by priority
    pages.sort(key=lambda x: float(x["priority"]), reverse=True)

    # Generate XML
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        '        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9',
        '        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">',
        f"  <!-- Generated: {datetime.now().isoformat()} -->",
        f"  <!-- Total URLs: {len(pages)} -->",
        "",
    ]

    for page in pages:
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{page['loc']}</loc>")
        xml_lines.append(f"    <lastmod>{page['lastmod']}</lastmod>")
        xml_lines.append(f"    <changefreq>{page['changefreq']}</changefreq>")
        xml_lines.append(f"    <priority>{page['priority']}</priority>")
        xml_lines.append("  </url>")

    xml_lines.append("</urlset>")

    # Write sitemap
    sitemap_path = Path("docs/sitemap.xml")
    sitemap_path.write_text("\n".join(xml_lines), encoding="utf-8")

    # Also copy to root for Quarto
    root_sitemap = Path("sitemap.xml")
    root_sitemap.write_text("\n".join(xml_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
