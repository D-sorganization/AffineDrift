from __future__ import annotations

import argparse
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from src.tools.utils import setup_logging
from src.tools.utils.content_utils import collect_qmd_files, read_qmd_with_frontmatter

logger = setup_logging(__name__)

SITEMAP_CONTENT_DIRS = [
    ".",
    "articles",
    "books",
    "critiques",
    "models",
    "pages",
    "repositories",
    "resources",
]


def get_git_last_modified(filepath: str) -> str:
    """Get last modified date from git history."""
    git_cmd = shutil.which("git")
    if not git_cmd:
        return datetime.now().strftime("%Y-%m-%d")

    try:
        result = subprocess.run(
            [git_cmd, "log", "-1", "--format=%cI", "--", filepath],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()[:10]
    except (subprocess.SubprocessError, OSError) as e:
        logger.warning("Failed to get git modified date for %s: %s", filepath, e)
    return datetime.now().strftime("%Y-%m-%d")


def get_git_last_modified_map() -> dict[str, str]:
    """Get mapping of relative filepaths to last modified date using a single git command."""
    git_cmd = shutil.which("git")
    if not git_cmd:
        return {}

    date_map: dict[str, str] = {}
    try:
        result = subprocess.run(
            [git_cmd, "log", "--format=COMMIT:%cI", "--name-only"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            check=False,
        )
        if result.returncode == 0 and result.stdout:
            current_date = ""
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith("COMMIT:"):
                    current_date = line[7:17]
                elif current_date:
                    norm_path = Path(line).as_posix()
                    if norm_path not in date_map:
                        date_map[norm_path] = current_date
    except (subprocess.SubprocessError, OSError) as e:
        logger.warning("Failed to batch get git modified dates: %s", e)
    return date_map


def extract_title(content: str, frontmatter: dict[str, Any], filepath: Path) -> str:
    """Extract page title from YAML frontmatter or first markdown heading."""
    title = frontmatter.get("title")
    if title:
        return str(title)
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return ""


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


def qmd_path_to_url_path(filepath: Path) -> str:
    """Convert a QMD path to the corresponding site URL path."""
    url_path = filepath.with_suffix(".html").as_posix()
    if url_path == "index.html":
        return ""
    return url_path


def main() -> None:
    """Generate sitemap.xml."""
    parser = argparse.ArgumentParser(description="Generate sitemap.xml")
    parser.add_argument(
        "--output",
        default="docs/sitemap.xml",
        help="Output path for the generated sitemap (default: docs/sitemap.xml)",
    )
    args = parser.parse_args()

    base_url = "https://affinedrift.com"
    pages: list[dict[str, str]] = []
    git_dates = get_git_last_modified_map()
    now_obj = datetime.now()
    iso_now = now_obj.isoformat()
    today = iso_now[:10]

    for filepath in collect_qmd_files(SITEMAP_CONTENT_DIRS):
        if filepath.name in ["404.qmd", "offline.qmd"]:
            continue

        relative_path = filepath.as_posix()
        url_path = qmd_path_to_url_path(filepath)

        content, frontmatter = read_qmd_with_frontmatter(filepath)
        title = extract_title(content, frontmatter, filepath)

        # Skip pages without titles or headings (unless root index.qmd)
        if not title and filepath.name != "index.qmd":
            continue

        lastmod = git_dates.get(relative_path)
        if not lastmod:
            lastmod = get_git_last_modified(relative_path) or today

        pages.append(
            {
                "loc": f"{base_url}/{url_path}",
                "lastmod": lastmod,
                "changefreq": get_changefreq(relative_path),
                "priority": get_priority(relative_path),
                "title": title,
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
        f"  <!-- Generated: {iso_now} -->",
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
    sitemap_path = Path(args.output)
    sitemap_path.parent.mkdir(parents=True, exist_ok=True)
    sitemap_path.write_text("\n".join(xml_lines), encoding="utf-8")

    # Also copy to root for Quarto
    root_sitemap = Path("sitemap.xml")
    root_sitemap.write_text("\n".join(xml_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
