#!/usr/bin/env python3
"""Generate ``feed.xml`` (RSS 2.0) from rendered article frontmatter.

The feed was previously a hand-maintained, committed artifact that drifted 16+
months stale. This generator walks the same article set as
``generate_sitemap.py`` (reusing ``collect_qmd_files`` /
``read_qmd_with_frontmatter`` from ``src.tools.utils.content_utils``), maps
frontmatter ``title`` / ``description`` / ``date`` to RSS ``<item>`` elements,
sorts newest-first, caps the item count, and stamps ``lastBuildDate`` with the
build time. Output is deterministic for a given content state because undated
("today") articles fall back to their git last-modified date.

Usage::

    python3 scripts/generate_feed.py                      # writes docs/feed.xml + feed.xml
    python3 scripts/generate_feed.py --output docs/feed.xml
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree
from xml.sax.saxutils import escape

from src.tools.utils import setup_logging
from src.tools.utils.content_utils import collect_qmd_files, read_qmd_with_frontmatter

logger = setup_logging(__name__)


class FeedValidationError(ValueError):
    """Raised when a generated RSS feed fails RSS 2.0 structural validation."""


BASE_URL = "https://affinedrift.com"
CHANNEL_TITLE = "AffineDrift"
CHANNEL_DESCRIPTION = (
    "Affine control theory for golf swing dynamics - Research articles, models, and resources"
)
MANAGING_EDITOR = "contact@affinedrift.com"
DEFAULT_CAP = 30

# Directories scanned for feed-worthy content (mirrors the article-bearing
# subset of generate_sitemap.py's SITEMAP_CONTENT_DIRS).
FEED_CONTENT_DIRS = ["articles"]


@dataclass(frozen=True)
class FeedItem:
    """A single RSS ``<item>``."""

    title: str
    link: str
    description: str
    pub_date: datetime


def get_git_last_modified(filepath: str) -> str:
    """Return a file's git last-modified date as ``YYYY-MM-DD``.

    Falls back to today's date when git is unavailable. This keeps output
    deterministic for a committed content state (the same as
    ``generate_sitemap.py``).
    """
    git_cmd = shutil.which("git")
    if not git_cmd:
        return datetime.now(tz=UTC).strftime("%Y-%m-%d")
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
    except (subprocess.SubprocessError, OSError) as exc:
        logger.warning("Failed to get git modified date for %s: %s", filepath, exc)
    return datetime.now(tz=UTC).strftime("%Y-%m-%d")


def parse_date(raw: str, fallback: str) -> datetime:
    """Parse a frontmatter ``date`` into a UTC datetime.

    Quarto's literal ``today`` keyword, empty values, and unparseable strings
    fall back to ``fallback`` (an ISO ``YYYY-MM-DD`` string) so output stays
    deterministic.
    """
    value = (raw or "").strip().strip("'\"").strip()
    if value and value.lower() != "today":
        try:
            return datetime.strptime(value[:10], "%Y-%m-%d").replace(tzinfo=UTC)
        except ValueError:
            logger.warning("Unparseable date %r; using fallback %s", raw, fallback)
    return datetime.strptime(fallback[:10], "%Y-%m-%d").replace(tzinfo=UTC)


def to_rfc822(dt: datetime) -> str:
    """Format a datetime as an RFC-822 date string in GMT.

    Uses fixed English day/month abbreviations so output is locale-independent
    and deterministic.
    """
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    return (
        f"{days[dt.weekday()]}, {dt.day:02d} {months[dt.month - 1]} {dt.year} "
        f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d} GMT"
    )


def qmd_path_to_url(filepath: Path) -> str:
    """Convert a QMD path to its absolute site URL."""
    url_path = filepath.with_suffix(".html").as_posix()
    return f"{BASE_URL}/{url_path}"


def collect_items() -> list[FeedItem]:
    """Collect feed items from article frontmatter, newest first."""
    items: list[FeedItem] = []
    for filepath in collect_qmd_files(FEED_CONTENT_DIRS):
        _content, frontmatter = read_qmd_with_frontmatter(filepath)
        title = frontmatter.get("title", "").strip()
        if not title:
            continue
        fallback = get_git_last_modified(str(filepath))
        pub_date = parse_date(frontmatter.get("date", ""), fallback)
        items.append(
            FeedItem(
                title=title,
                link=qmd_path_to_url(filepath),
                description=frontmatter.get("description", "").strip(),
                pub_date=pub_date,
            )
        )
    # Sort newest first; tie-break on link for determinism.
    items.sort(key=lambda it: (it.pub_date, it.link), reverse=True)
    return items


def build_feed_xml(
    items: list[FeedItem],
    build_date: datetime,
    cap: int = DEFAULT_CAP,
) -> str:
    """Render the RSS 2.0 XML document for the given items.

    Items are sorted newest-first (tie-broken on link) before capping so output
    is deterministic regardless of input order.
    """
    ordered = sorted(items, key=lambda it: (it.pub_date, it.link), reverse=True)
    capped = ordered[:cap]
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "  <channel>",
        f"    <title>{escape(CHANNEL_TITLE)}</title>",
        f"    <link>{BASE_URL}</link>",
        f"    <description>{escape(CHANNEL_DESCRIPTION)}</description>",
        "    <language>en-us</language>",
        f"    <managingEditor>{MANAGING_EDITOR}</managingEditor>",
        f"    <webMaster>{MANAGING_EDITOR}</webMaster>",
        f"    <lastBuildDate>{to_rfc822(build_date)}</lastBuildDate>",
        f'    <atom:link href="{BASE_URL}/feed.xml" rel="self" type="application/rss+xml"/>',
    ]
    for item in capped:
        lines.extend(
            [
                "    <item>",
                f"      <title>{escape(item.title)}</title>",
                f"      <link>{escape(item.link)}</link>",
                f"      <description>{escape(item.description)}</description>",
                f"      <pubDate>{to_rfc822(item.pub_date)}</pubDate>",
                f'      <guid isPermaLink="true">{escape(item.link)}</guid>',
                "    </item>",
            ]
        )
    lines.append("  </channel>")
    lines.append("</rss>")
    return "\n".join(lines) + "\n"


def validate_feed_xml(xml: str) -> list[str]:
    """Validate an RSS 2.0 document, returning structural errors (empty if valid).

    Checks well-formedness, required ``<rss version="2.0">``/``<channel>``
    elements, and per-item ``link``/``guid``/``pubDate`` shape (absolute URL,
    unique guid, RFC-822 date) so an invalid feed is caught before it is
    published, not discovered by a reader's feed client.
    """
    errors: list[str] = []
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError as exc:
        return [f"XML is not well-formed: {exc}"]

    if root.tag != "rss":
        return [f"root element must be <rss>, got <{root.tag}>"]
    if root.get("version") != "2.0":
        errors.append(f"rss version must be '2.0', got {root.get('version')!r}")

    channel = root.find("channel")
    if channel is None:
        return [*errors, "missing required <channel> element"]

    for required in ("title", "link", "description"):
        element = channel.find(required)
        if element is None or not (element.text or "").strip():
            errors.append(f"channel missing required <{required}>")

    guids: list[str] = []
    for index, item in enumerate(channel.findall("item")):
        title = item.find("title")
        description = item.find("description")
        has_title = title is not None and (title.text or "").strip()
        has_description = description is not None and (description.text or "").strip()
        if not has_title and not has_description:
            errors.append(f"item {index}: must have a <title> or <description>")

        link = item.find("link")
        link_text = (link.text or "").strip() if link is not None else ""
        if not link_text:
            errors.append(f"item {index}: missing required <link>")
        elif not link_text.startswith(("http://", "https://")):
            errors.append(
                f"item {index}: <link> must be an absolute http(s) URL, got {link_text!r}"
            )

        guid = item.find("guid")
        guid_text = (guid.text or "").strip() if guid is not None else ""
        if not guid_text:
            errors.append(f"item {index}: missing required <guid>")
        else:
            guids.append(guid_text)

        pub_date = item.find("pubDate")
        pub_date_text = (pub_date.text or "").strip() if pub_date is not None else ""
        if not pub_date_text:
            errors.append(f"item {index}: missing required <pubDate>")
        else:
            try:
                parsedate_to_datetime(pub_date_text)
            except (TypeError, ValueError) as exc:
                errors.append(f"item {index}: <pubDate> {pub_date_text!r} is not RFC-822: {exc}")

    duplicate_guids = sorted({g for g in guids if guids.count(g) > 1})
    if duplicate_guids:
        errors.append(f"duplicate <guid> values: {duplicate_guids}")

    return errors


def main() -> int:
    """Generate the feed and write it to the output path(s)."""
    parser = argparse.ArgumentParser(description="Generate RSS feed.xml")
    parser.add_argument(
        "--output",
        default="docs/feed.xml",
        help="Output path for the generated feed (default: docs/feed.xml)",
    )
    args = parser.parse_args()

    items = collect_items()
    build_date = datetime.now(tz=UTC).replace(microsecond=0)
    xml = build_feed_xml(items, build_date=build_date)

    errors = validate_feed_xml(xml)
    if errors:
        raise FeedValidationError(
            "Generated feed.xml failed RSS 2.0 validation:\n"
            + "\n".join(f"  - {error}" for error in errors)
        )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(xml, encoding="utf-8")
    logger.info("Wrote %d feed items to %s", min(len(items), DEFAULT_CAP), output)

    # Also write a root copy so Quarto resource-copying stays consistent with
    # sitemap.xml behaviour.
    root_copy = Path("feed.xml")
    root_copy.write_text(xml, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
