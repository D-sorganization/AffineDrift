"""Tests for the RSS feed generator script."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from scripts.generate_feed import (
    CHANNEL_DESCRIPTION,
    CHANNEL_TITLE,
    FeedItem,
    build_feed_xml,
    parse_date,
    to_rfc822,
)


class TestParseDate:
    """Tests for frontmatter date parsing."""

    def test_parses_iso_string(self):
        """An ISO date string parses to a date at UTC midnight."""
        result = parse_date("2025-11-28", fallback="2024-01-01")
        assert result == datetime(2025, 11, 28, tzinfo=UTC)

    def test_quoted_iso_string(self):
        """Surrounding quotes are tolerated."""
        result = parse_date('"2025-11-28"', fallback="2024-01-01")
        assert result == datetime(2025, 11, 28, tzinfo=UTC)

    def test_today_keyword_uses_fallback(self):
        """Quarto's ``today`` keyword falls back to the git/build date."""
        result = parse_date("today", fallback="2024-03-15")
        assert result == datetime(2024, 3, 15, tzinfo=UTC)

    def test_missing_uses_fallback(self):
        """An empty/missing date falls back deterministically."""
        result = parse_date("", fallback="2024-03-15")
        assert result == datetime(2024, 3, 15, tzinfo=UTC)

    def test_unparseable_uses_fallback(self):
        """A non-date string falls back rather than raising."""
        result = parse_date("sometime in spring", fallback="2024-03-15")
        assert result == datetime(2024, 3, 15, tzinfo=UTC)


class TestToRfc822:
    """Tests for RFC-822 date formatting."""

    def test_format(self):
        """Dates are formatted as RFC-822 with GMT zone."""
        dt = datetime(2025, 1, 27, tzinfo=UTC)
        assert to_rfc822(dt) == "Mon, 27 Jan 2025 00:00:00 GMT"

    def test_deterministic(self):
        """Formatting is stable across calls."""
        dt = datetime(2026, 6, 9, tzinfo=UTC)
        assert to_rfc822(dt) == to_rfc822(dt)


class TestBuildFeedXml:
    """Tests for assembling the RSS XML document."""

    def _items(self) -> list[FeedItem]:
        return [
            FeedItem(
                title="Older Article",
                link="https://affinedrift.com/articles/old.html",
                description="An older one.",
                pub_date=datetime(2024, 1, 15, tzinfo=UTC),
            ),
            FeedItem(
                title="Newer Article",
                link="https://affinedrift.com/articles/new.html",
                description="A newer one.",
                pub_date=datetime(2026, 2, 1, tzinfo=UTC),
            ),
        ]

    def test_channel_metadata_present(self):
        """The channel preserves the hand-written title/description/link."""
        xml = build_feed_xml(self._items(), build_date=datetime(2026, 6, 9, tzinfo=UTC))
        assert f"<title>{CHANNEL_TITLE}</title>" in xml
        assert CHANNEL_DESCRIPTION in xml
        assert "<link>https://affinedrift.com</link>" in xml
        assert xml.startswith('<?xml version="1.0" encoding="UTF-8"?>')

    def test_last_build_date_is_build_time(self):
        """lastBuildDate reflects the supplied build time."""
        xml = build_feed_xml(self._items(), build_date=datetime(2026, 6, 9, tzinfo=UTC))
        assert "<lastBuildDate>Tue, 09 Jun 2026 00:00:00 GMT</lastBuildDate>" in xml

    def test_items_sorted_newest_first(self):
        """Items are emitted in descending date order."""
        xml = build_feed_xml(self._items(), build_date=datetime(2026, 6, 9, tzinfo=UTC))
        assert xml.index("Newer Article") < xml.index("Older Article")

    def test_item_pubdate_is_rfc822(self):
        """Item pubDates are RFC-822 formatted."""
        xml = build_feed_xml(self._items(), build_date=datetime(2026, 6, 9, tzinfo=UTC))
        assert "<pubDate>Mon, 15 Jan 2024 00:00:00 GMT</pubDate>" in xml

    def test_cap_limits_item_count(self):
        """The feed caps the number of items."""
        many = [
            FeedItem(
                title=f"Article {i}",
                link=f"https://affinedrift.com/articles/{i}.html",
                description="x",
                pub_date=datetime(2024, 1, 1, tzinfo=UTC),
            )
            for i in range(50)
        ]
        xml = build_feed_xml(many, build_date=datetime(2026, 6, 9, tzinfo=UTC), cap=30)
        assert xml.count("<item>") == 30

    def test_escapes_special_characters(self):
        """Titles/descriptions with XML-special chars are escaped."""
        items = [
            FeedItem(
                title="Drift & Input <decomposition>",
                link="https://affinedrift.com/articles/x.html",
                description='Uses "quotes" & angle <brackets>.',
                pub_date=datetime(2025, 5, 1, tzinfo=UTC),
            )
        ]
        xml = build_feed_xml(items, build_date=datetime(2026, 6, 9, tzinfo=UTC))
        assert "Drift &amp; Input &lt;decomposition&gt;" in xml
        assert "<decomposition>" not in xml

    def test_deterministic_output(self):
        """Same inputs yield byte-identical output."""
        build_date = datetime(2026, 6, 9, tzinfo=UTC)
        xml1 = build_feed_xml(self._items(), build_date=build_date)
        xml2 = build_feed_xml(self._items(), build_date=build_date)
        assert xml1 == xml2


class TestDeployWorkflowWiring:
    """The deploy workflow must invoke the generators."""

    def _workflow_text(self) -> str:
        repo_root = Path(__file__).resolve().parent.parent
        return (repo_root / ".github" / "workflows" / "deploy-website.yml").read_text(
            encoding="utf-8"
        )

    def test_workflow_runs_feed_generator(self):
        """deploy-website.yml invokes generate_feed.py."""
        assert "scripts/generate_feed.py" in self._workflow_text()

    def test_workflow_runs_sitemap_generator(self):
        """deploy-website.yml invokes generate_sitemap.py."""
        assert "scripts/generate_sitemap.py" in self._workflow_text()
