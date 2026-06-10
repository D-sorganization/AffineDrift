#!/usr/bin/env python3
"""Generate an RSS 2.0 feed.xml from the site's QMD content.

Replaces the hand-maintained (and 16-months-stale) ``feed.xml`` with a build
artifact derived from the same article set as ``generate_sitemap.py``. Pure
transform helpers are unit-tested in ``tests/test_generate_feed.py``.
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

from src.tools.utils import setup_logging
from src.tools.utils.content_utils import collect_qmd_files, read_qmd_with_frontmatter

logger = setup_logging(__name__)

BASE_URL = "https://affinedrift.com"
CHANNEL_TITLE = "AffineDrift"
CHANNEL_DESCRIPTION = "Educational engineering mathematics — articles, theory, and tools."

# Same content surface as the sitemap generator.
FEED_CONTENT_DIRS = [
    ".",
    "articles",
    "books",
    "models",
    "pages",
    "repositories",
    "resources",
]

MAX_ITEMS = 30


def qmd_path_to_url(filepath: Path, base_url: str = BASE_URL) -> str:
    """Convert a QMD source path to its public article URL."""
    url_path = filepath.with_suffix(".html").as_posix()
    if url_path == "index.html":
        return f"{base_url}/"
    return f"{base_url}/{url_path}"


def parse_date(value: object) -> datetime | None:
    """Parse a frontmatter ``date`` value into a UTC datetime.

    Accepts ``YYYY-MM-DD`` (and ``YYYY/MM/DD``) strings and datetime/date
    objects. Returns ``None`` for unparseable / missing values rather than
    raising, so a single malformed article never breaks the whole feed.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    # ``date`` objects (no time component).
    if hasattr(value, "year") and not isinstance(value, str):
        try:
            return datetime(value.year, value.month, value.day, tzinfo=UTC)
        except (TypeError, ValueError):
            return None
    text = str(value).strip().replace("/", "-")
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text[: len(fmt) + 4], fmt).replace(tzinfo=UTC)
        except ValueError:
            continue
    return None


def rfc822(dt: datetime) -> str:
    """Format a datetime as an RFC-822 string (RSS pubDate format)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return format_datetime(dt)


def collect_feed_items(
    content_dirs: list[str] | None = None,
    base_url: str = BASE_URL,
) -> list[dict[str, str]]:
    """Build the list of feed items (title/link/description/pubDate), newest first."""
    dirs = content_dirs or FEED_CONTENT_DIRS
    items: list[dict[str, object]] = []

    for filepath in collect_qmd_files(dirs):
        _content, frontmatter = read_qmd_with_frontmatter(filepath)
        title = frontmatter.get("title")
        if not title:
            continue
        dt = parse_date(frontmatter.get("date"))
        items.append(
            {
                "title": str(title),
                "link": qmd_path_to_url(filepath, base_url),
                "description": str(frontmatter.get("description", "") or ""),
                "_date": dt,
            },
        )

    # Newest first; undated items sink to the bottom but stay deterministic by link.
    items.sort(
        key=lambda it: (
            it["_date"] or datetime.min.replace(tzinfo=UTC),
            str(it["link"]),
        ),
        reverse=True,
    )

    rendered: list[dict[str, str]] = []
    for it in items[:MAX_ITEMS]:
        dt = it["_date"]
        rendered.append(
            {
                "title": str(it["title"]),
                "link": str(it["link"]),
                "description": str(it["description"]),
                "pubDate": rfc822(dt) if isinstance(dt, datetime) else "",
            },
        )
    return rendered


def build_feed_xml(
    items: list[dict[str, str]],
    *,
    base_url: str = BASE_URL,
    build_time: datetime | None = None,
) -> str:
    """Render feed items into an RSS 2.0 document (pure function)."""
    build_time = build_time or datetime.now(UTC)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "  <channel>",
        f"    <title>{escape(CHANNEL_TITLE)}</title>",
        f"    <link>{escape(base_url)}/</link>",
        f"    <description>{escape(CHANNEL_DESCRIPTION)}</description>",
        "    <language>en-us</language>",
        f"    <lastBuildDate>{rfc822(build_time)}</lastBuildDate>",
        f'    <atom:link href="{escape(base_url)}/feed.xml" '
        'rel="self" type="application/rss+xml" />',
    ]
    for item in items:
        lines.append("    <item>")
        lines.append(f"      <title>{escape(item['title'])}</title>")
        lines.append(f"      <link>{escape(item['link'])}</link>")
        lines.append(f'      <guid isPermaLink="true">{escape(item["link"])}</guid>')
        if item.get("description"):
            lines.append(f"      <description>{escape(item['description'])}</description>")
        if item.get("pubDate"):
            lines.append(f"      <pubDate>{item['pubDate']}</pubDate>")
        lines.append("    </item>")
    lines.append("  </channel>")
    lines.append("</rss>")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    """Generate feed.xml."""
    parser = argparse.ArgumentParser(description="Generate the site RSS feed.xml")
    parser.add_argument(
        "--output",
        default=None,
        help="Write the feed to this single path instead of docs/ + root.",
    )
    args = parser.parse_args(argv)

    items = collect_feed_items()
    xml = build_feed_xml(items)
    logger.info("Generated feed with %d items", len(items))

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(xml, encoding="utf-8")
    else:
        Path("docs/feed.xml").write_text(xml, encoding="utf-8")
        Path("feed.xml").write_text(xml, encoding="utf-8")


if __name__ == "__main__":
    main()
