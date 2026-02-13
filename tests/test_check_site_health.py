"""Tests for the site health check tool."""

import logging
from unittest.mock import patch

import pytest

# Add project root to path
from src.tools.check_site_health import check_site_health, parse_fail_on


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
        exit_code = check_site_health(
            fail_on=set(),
            ignore_quarto_alternate_formats=True,
        )

    assert exit_code == 0
    assert "No broken links found" in caplog.text
    assert "No orphaned files found" in caplog.text


def test_check_site_health_broken_link_warning_only(mock_docs_dir, caplog):
    """Test check_site_health detects broken links in warning-only mode."""
    caplog.set_level(logging.INFO)
    create_html_file(
        mock_docs_dir,
        "index.html",
        '<html><body><a href="missing.html">Broken</a></body></html>',
    )

    with patch("src.tools.check_site_health.DOCS_DIR", mock_docs_dir):
        exit_code = check_site_health(
            fail_on=set(),
            ignore_quarto_alternate_formats=True,
        )

    assert exit_code == 0
    assert "Found 1 broken links" in caplog.text
    assert "index.html -> missing.html" in caplog.text


def test_check_site_health_orphaned_file_warning_only(mock_docs_dir, caplog):
    """Test check_site_health detects orphaned files in warning-only mode."""
    caplog.set_level(logging.INFO)
    create_html_file(mock_docs_dir, "index.html", "<html></html>")
    create_html_file(mock_docs_dir, "orphan.html", "<html></html>")

    with patch("src.tools.check_site_health.DOCS_DIR", mock_docs_dir):
        exit_code = check_site_health(
            fail_on=set(),
            ignore_quarto_alternate_formats=True,
        )

    assert exit_code == 0
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
        exit_code = check_site_health(
            fail_on=set(),
            ignore_quarto_alternate_formats=True,
        )

    assert exit_code == 0
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
        exit_code = check_site_health(
            fail_on=set(),
            ignore_quarto_alternate_formats=True,
        )

    assert exit_code == 0
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
        exit_code = check_site_health(
            fail_on=set(),
            ignore_quarto_alternate_formats=True,
        )

    assert exit_code == 0
    assert "No broken links found" in caplog.text
    assert "No orphaned files found" in caplog.text


def test_check_site_health_archive_excluded(mock_docs_dir, caplog):
    """Test check_site_health excludes archive from orphan check."""
    caplog.set_level(logging.INFO)
    create_html_file(mock_docs_dir, "index.html", "<html></html>")
    create_html_file(mock_docs_dir, "archive/old.html", "<html></html>")

    with patch("src.tools.check_site_health.DOCS_DIR", mock_docs_dir):
        exit_code = check_site_health(
            fail_on=set(),
            ignore_quarto_alternate_formats=True,
        )

    assert exit_code == 0
    assert "No orphaned files found" in caplog.text


def test_check_site_health_entry_points_excluded(mock_docs_dir, caplog):
    """Test check_site_health excludes known entry points from orphan check."""
    caplog.set_level(logging.INFO)
    create_html_file(mock_docs_dir, "index.html", "<html></html>")
    create_html_file(mock_docs_dir, "404.html", "<html></html>")
    create_html_file(mock_docs_dir, "offline.html", "<html></html>")

    with patch("src.tools.check_site_health.DOCS_DIR", mock_docs_dir):
        exit_code = check_site_health(
            fail_on=set(),
            ignore_quarto_alternate_formats=True,
        )

    assert exit_code == 0
    assert "No orphaned files found" in caplog.text


def test_check_site_health_fails_on_broken_links(mock_docs_dir, caplog):
    """Test strict mode returns non-zero when broken links exist."""
    caplog.set_level(logging.INFO)
    create_html_file(
        mock_docs_dir,
        "index.html",
        '<html><body><a href="missing.html">Broken</a></body></html>',
    )

    with patch("src.tools.check_site_health.DOCS_DIR", mock_docs_dir):
        exit_code = check_site_health(
            fail_on={"broken"},
            ignore_quarto_alternate_formats=True,
        )

    assert exit_code == 1
    assert "Found 1 broken links" in caplog.text


def test_check_site_health_fails_on_orphaned_files(mock_docs_dir, caplog):
    """Test strict mode returns non-zero when orphaned files exist."""
    caplog.set_level(logging.INFO)
    create_html_file(mock_docs_dir, "index.html", "<html></html>")
    create_html_file(mock_docs_dir, "orphan.html", "<html></html>")

    with patch("src.tools.check_site_health.DOCS_DIR", mock_docs_dir):
        exit_code = check_site_health(
            fail_on={"orphaned"},
            ignore_quarto_alternate_formats=True,
        )

    assert exit_code == 1
    assert "Found 1 orphaned files" in caplog.text


def test_check_site_health_ignores_quarto_alternate_format_links(mock_docs_dir, caplog):
    """Test alternate-format links can be excluded from health checks."""
    caplog.set_level(logging.INFO)
    create_html_file(
        mock_docs_dir,
        "index.html",
        (
            "<html><body>"
            '<div class="quarto-alternate-formats">'
            '<a href="missing.pdf">PDF</a>'
            "</div>"
            "</body></html>"
        ),
    )

    with patch("src.tools.check_site_health.DOCS_DIR", mock_docs_dir):
        exit_code = check_site_health(
            fail_on={"broken"},
            ignore_quarto_alternate_formats=True,
        )

    assert exit_code == 0
    assert "No broken links found" in caplog.text


def test_parse_fail_on_all_alias():
    """Test parse_fail_on expands aliases and trims spaces."""
    parsed = parse_fail_on(" all ")
    assert parsed == {"broken", "orphaned"}


def test_parse_fail_on_specific_values():
    """Test parse_fail_on parses comma-separated values."""
    parsed = parse_fail_on("broken, orphaned")
    assert parsed == {"broken", "orphaned"}


def test_parse_fail_on_invalid_value_raises():
    """Test parse_fail_on rejects unsupported values."""
    with pytest.raises(ValueError, match="Unsupported"):
        parse_fail_on("broken,invalid")
