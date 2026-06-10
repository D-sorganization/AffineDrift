"""Tests for the RSS feed generator (scripts/generate_feed.py)."""

from datetime import UTC, datetime
from pathlib import Path

from scripts.generate_feed import (
    build_feed_xml,
    parse_date,
    qmd_path_to_url,
    rfc822,
)


class TestParseDate:
    def test_iso_string(self):
        dt = parse_date("2026-05-07")
        assert dt is not None
        assert (dt.year, dt.month, dt.day) == (2026, 5, 7)

    def test_slash_separated(self):
        dt = parse_date("2026/01/02")
        assert dt is not None
        assert (dt.year, dt.month, dt.day) == (2026, 1, 2)

    def test_none_returns_none(self):
        assert parse_date(None) is None

    def test_malformed_returns_none_not_raises(self):
        # A single malformed article must never break the whole feed.
        assert parse_date("not-a-date") is None

    def test_datetime_passthrough_gets_utc(self):
        dt = parse_date(datetime(2026, 3, 1))
        assert dt is not None
        assert dt.tzinfo is not None


class TestRfc822:
    def test_format_is_rfc822(self):
        dt = datetime(2026, 5, 7, tzinfo=UTC)
        out = rfc822(dt)
        # e.g. "Thu, 07 May 2026 00:00:00 +0000"
        assert "May 2026" in out
        assert out.startswith(("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"))


class TestUrl:
    def test_article_url(self):
        assert (
            qmd_path_to_url(Path("articles/test.qmd"))
            == "https://affinedrift.com/articles/test.html"
        )

    def test_index_url_is_root(self):
        assert qmd_path_to_url(Path("index.qmd")) == "https://affinedrift.com/"


class TestBuildFeedXml:
    def _items(self):
        return [
            {
                "title": "Newer Article",
                "link": "https://affinedrift.com/articles/newer.html",
                "description": "A newer one",
                "pubDate": "Thu, 07 May 2026 00:00:00 +0000",
            },
            {
                "title": "Older & Special <Article>",
                "link": "https://affinedrift.com/articles/older.html",
                "description": "",
                "pubDate": "Mon, 01 Jan 2024 00:00:00 +0000",
            },
        ]

    def test_valid_rss_structure(self):
        xml = build_feed_xml(
            self._items(),
            build_time=datetime(2026, 6, 9, tzinfo=UTC),
        )
        assert xml.startswith("<?xml")
        assert '<rss version="2.0"' in xml
        assert "<channel>" in xml and "</channel>" in xml
        assert xml.count("<item>") == 2

    def test_lastbuilddate_uses_build_time(self):
        xml = build_feed_xml(
            self._items(),
            build_time=datetime(2026, 6, 9, tzinfo=UTC),
        )
        assert "Jun 2026" in xml.split("<lastBuildDate>")[1].split("</lastBuildDate>")[0]

    def test_xml_escaping(self):
        xml = build_feed_xml(self._items())
        # Raw "<Article>" / "&" must be escaped, never emitted literally.
        assert "Older &amp; Special &lt;Article&gt;" in xml
        assert "<Article>" not in xml

    def test_empty_items_still_valid_channel(self):
        xml = build_feed_xml([])
        assert "<channel>" in xml
        assert "<item>" not in xml


class TestWorkflowWiring:
    """The deploy workflow must actually invoke the generators (issue #3220)."""

    def test_deploy_workflow_runs_feed_and_sitemap(self):
        workflow = Path(".github/workflows/deploy-website.yml").read_text(encoding="utf-8")
        assert "scripts/generate_feed.py" in workflow
        assert "scripts/generate_sitemap.py" in workflow
