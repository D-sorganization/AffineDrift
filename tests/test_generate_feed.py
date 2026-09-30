"""Tests for the RSS feed generator script."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from scripts.generate_feed import (
    CHANNEL_DESCRIPTION,
    CHANNEL_TITLE,
    FeedItem,
    FeedValidationError,
    build_feed_xml,
    main,
    parse_date,
    to_rfc822,
    validate_feed_xml,
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


class TestValidateFeedXml:
    """Tests for RSS 2.0 structural validation (acceptance criterion: feed validates)."""

    def _valid_xml(self) -> str:
        items = [
            FeedItem(
                title="An Article",
                link="https://affinedrift.com/articles/a.html",
                description="Description.",
                pub_date=datetime(2026, 1, 1, tzinfo=UTC),
            )
        ]
        return build_feed_xml(items, build_date=datetime(2026, 6, 9, tzinfo=UTC))

    def test_generated_feed_is_valid(self):
        """The generator's own output passes validation with no errors."""
        assert validate_feed_xml(self._valid_xml()) == []

    def test_empty_item_list_is_valid(self):
        """A feed with zero items (e.g. no dated content yet) is still valid RSS."""
        assert (
            validate_feed_xml(build_feed_xml([], build_date=datetime(2026, 6, 9, tzinfo=UTC))) == []
        )

    def test_rejects_malformed_xml(self):
        """Unparseable XML is reported, not silently accepted."""
        errors = validate_feed_xml("<rss><channel>")
        assert errors
        assert any("not well-formed" in e for e in errors)

    def test_rejects_wrong_rss_version(self):
        """A non-2.0 RSS version is flagged."""
        xml = self._valid_xml().replace('version="2.0"', 'version="0.91"')
        errors = validate_feed_xml(xml)
        assert any("version" in e for e in errors)

    def test_rejects_missing_channel_title(self):
        """A channel missing its required <title> fails validation."""
        xml = self._valid_xml().replace(f"<title>{CHANNEL_TITLE}</title>", "", 1)
        errors = validate_feed_xml(xml)
        assert any("title" in e for e in errors)

    def test_rejects_item_missing_link(self):
        """An item missing <link> fails validation."""
        xml = self._valid_xml().replace(
            "<link>https://affinedrift.com/articles/a.html</link>", "", 1
        )
        errors = validate_feed_xml(xml)
        assert any("link" in e for e in errors)

    def test_rejects_relative_item_link(self):
        """An item <link> that is not an absolute http(s) URL fails validation."""
        xml = self._valid_xml().replace(
            "https://affinedrift.com/articles/a.html", "/articles/a.html"
        )
        errors = validate_feed_xml(xml)
        assert any("absolute" in e for e in errors)

    def test_rejects_unparseable_pubdate(self):
        """A <pubDate> that is not RFC-822 fails validation."""
        xml = self._valid_xml().replace("Thu, 01 Jan 2026 00:00:00 GMT", "not-a-date", 1)
        errors = validate_feed_xml(xml)
        assert any("pubDate" in e for e in errors)

    def test_rejects_duplicate_guids(self):
        """Two items sharing a <guid> fail validation (readers dedupe on guid)."""
        items = [
            FeedItem(
                title="First",
                link="https://affinedrift.com/articles/a.html",
                description="d1",
                pub_date=datetime(2026, 1, 1, tzinfo=UTC),
            ),
            FeedItem(
                title="Second",
                link="https://affinedrift.com/articles/a.html",
                description="d2",
                pub_date=datetime(2026, 2, 1, tzinfo=UTC),
            ),
        ]
        xml = build_feed_xml(items, build_date=datetime(2026, 6, 9, tzinfo=UTC))
        errors = validate_feed_xml(xml)
        assert any("duplicate" in e.lower() for e in errors)


class TestMainValidatesBeforeWriting:
    """``main()`` must fail loudly instead of writing an invalid feed (DbC)."""

    def test_invalid_feed_raises_and_writes_nothing(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(
            "scripts.generate_feed.build_feed_xml", lambda *_args, **_kwargs: "<rss><channel>"
        )
        monkeypatch.setattr("sys.argv", ["generate_feed.py", "--output", "docs/feed.xml"])

        with pytest.raises(FeedValidationError):
            main()

        assert not (tmp_path / "docs" / "feed.xml").exists()
        assert not (tmp_path / "feed.xml").exists()


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
