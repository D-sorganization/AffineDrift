"""Tests for the site health check tool."""

import logging
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[1]))

from src.tools.check_site_health import check_site_health


@pytest.fixture
def mock_docs_dir(tmp_path):
    """Create a temporary docs directory structure."""
    docs = tmp_path / "docs"
    docs.mkdir()
    return docs


def create_html_file(docs_dir, name, content):
    """Create an HTML file in the docs directory."""
    file_path = docs_dir / name
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return file_path


def test_check_site_health_no_issues(mock_docs_dir, caplog):
    """Test check_site_health with no broken links or orphaned files."""
    caplog.set_level(logging.INFO)
    create_html_file(
        mock_docs_dir,
        "index.html",
        '<html><body><a href="about.html">About</a></body></html>',
    )
    create_html_file(
        mock_docs_dir,
        "about.html",
        '<html><body><a href="index.html">Home</a></body></html>',
    )

    with patch("src.tools.check_site_health.DOCS_DIR", mock_docs_dir):
        check_site_health()

    assert "No broken links found" in caplog.text
    assert "No orphaned files found" in caplog.text


def test_check_site_health_broken_link(mock_docs_dir, caplog):
    """Test check_site_health detects broken links (warns but doesn't exit)."""
    caplog.set_level(logging.INFO)
    create_html_file(
        mock_docs_dir,
        "index.html",
        '<html><body><a href="missing.html">Broken</a></body></html>',
    )

    with patch("src.tools.check_site_health.DOCS_DIR", mock_docs_dir):
        # Broken links are now warnings, not failures
        check_site_health()

    assert "Found 1 broken links" in caplog.text
    assert "index.html -> missing.html" in caplog.text


def test_check_site_health_orphaned_file(mock_docs_dir, caplog):
    """Test check_site_health detects orphaned files (warns but doesn't exit)."""
    caplog.set_level(logging.INFO)
    create_html_file(mock_docs_dir, "index.html", "<html></html>")
    create_html_file(mock_docs_dir, "orphan.html", "<html></html>")

    with patch("src.tools.check_site_health.DOCS_DIR", mock_docs_dir):
        # Orphaned files are now warnings, not failures
        check_site_health()

    assert "Found 1 orphaned files" in caplog.text
    assert "orphan.html" in caplog.text


def test_check_site_health_ignores_external_links(mock_docs_dir, caplog):
    """Test check_site_health ignores external links."""
    caplog.set_level(logging.INFO)
    create_html_file(
        mock_docs_dir,
        "index.html",
        '<html><body><a href="https://example.com">External</a></body></html>',
    )

    with patch("src.tools.check_site_health.DOCS_DIR", mock_docs_dir):
        check_site_health()

    assert "No broken links found" in caplog.text


def test_check_site_health_ignores_anchors(mock_docs_dir, caplog):
    """Test check_site_health ignores anchors."""
    caplog.set_level(logging.INFO)
    create_html_file(
        mock_docs_dir,
        "index.html",
        '<html><body><a href="#top">Top</a></body></html>',
    )

    with patch("src.tools.check_site_health.DOCS_DIR", mock_docs_dir):
        check_site_health()

    assert "No broken links found" in caplog.text


def test_check_site_health_resolves_nested_links(mock_docs_dir, caplog):
    """Test check_site_health resolves relative links in nested directories."""
    caplog.set_level(logging.INFO)
    # Link from index to article to avoid orphan
    create_html_file(
        mock_docs_dir,
        "index.html",
        '<html><body><a href="articles/article.html">Article</a></body></html>',
    )
    # Link from article back to index
    create_html_file(
        mock_docs_dir,
        "articles/article.html",
        '<html><body><a href="../index.html">Home</a></body></html>',
    )

    with patch("src.tools.check_site_health.DOCS_DIR", mock_docs_dir):
        check_site_health()

    assert "No broken links found" in caplog.text
    assert "No orphaned files found" in caplog.text


def test_check_site_health_archive_excluded(mock_docs_dir, caplog):
    """Test check_site_health excludes archive from orphan check."""
    caplog.set_level(logging.INFO)
    create_html_file(mock_docs_dir, "index.html", "<html></html>")
    create_html_file(mock_docs_dir, "archive/old.html", "<html></html>")

    with patch("src.tools.check_site_health.DOCS_DIR", mock_docs_dir):
        check_site_health()

    assert "No orphaned files found" in caplog.text


def test_check_site_health_entry_points_excluded(mock_docs_dir, caplog):
    """Test check_site_health excludes known entry points from orphan check."""
    caplog.set_level(logging.INFO)
    create_html_file(mock_docs_dir, "index.html", "<html></html>")
    create_html_file(mock_docs_dir, "404.html", "<html></html>")
    create_html_file(mock_docs_dir, "offline.html", "<html></html>")

    with patch("src.tools.check_site_health.DOCS_DIR", mock_docs_dir):
        check_site_health()

    assert "No orphaned files found" in caplog.text
