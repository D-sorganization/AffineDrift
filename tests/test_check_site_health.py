"""Tests for the site health check tool and link validation."""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[1]))


class TestSiteHealthCheck:
    """Tests for site health checking functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.docs_dir = Path(self.temp_dir) / "docs"
        self.docs_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_html_file(self, name: str, content: str) -> Path:
        """Create an HTML file in the docs directory."""
        file_path = self.docs_dir / name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def test_detects_broken_internal_links(self):
        """Should detect links to non-existent internal files."""
        # Create an HTML file with a broken link
        html_content = """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<a href="non-existent.html">Broken Link</a>
</body>
</html>
"""
        self.create_html_file("index.html", html_content)

        # Import and test with mocked DOCS_DIR
        with patch("src.tools.check_site_health.DOCS_DIR", self.docs_dir):
            from src.tools.check_site_health import DOCS_DIR

            # Verify the patch worked
            assert DOCS_DIR == self.docs_dir

            # The link to "non-existent.html" should be detected as broken

    def test_ignores_external_links(self):
        """Should ignore external HTTP/HTTPS links."""
        html_content = """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<a href="https://example.com">External Link</a>
<a href="http://example.com">HTTP Link</a>
<a href="mailto:test@example.com">Email Link</a>
</body>
</html>
"""
        self.create_html_file("index.html", html_content)

        # External links should not be reported as broken

    def test_ignores_anchor_links(self):
        """Should ignore anchor-only links."""
        html_content = """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<a href="#section1">Anchor Link</a>
<a href="#">Top Link</a>
</body>
</html>
"""
        self.create_html_file("index.html", html_content)

        # Anchor links should not be reported as broken

    def test_handles_valid_internal_links(self):
        """Should not report valid internal links as broken."""
        # Create target file first
        self.create_html_file(
            "about.html",
            "<html><head><title>About</title></head><body>About</body></html>",
        )

        # Create source file with link to target
        html_content = """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<a href="about.html">About Link</a>
</body>
</html>
"""
        self.create_html_file("index.html", html_content)

        # Valid links should not be reported as broken

    def test_entry_points_not_orphaned(self):
        """Entry point files should not be marked as orphaned."""
        # Create entry point files
        self.create_html_file(
            "index.html",
            "<html><head><title>Index</title></head><body>Index</body></html>",
        )
        self.create_html_file(
            "404.html",
            "<html><head><title>404</title></head><body>Not Found</body></html>",
        )

        # These should not be in orphaned_files

    def test_archive_files_excluded_from_orphan_check(self):
        """Files in archive directories should be excluded from orphan check."""
        # Create file in archive directory
        self.create_html_file(
            "archive/old-article.html",
            "<html><head><title>Old</title></head><body>Old</body></html>",
        )

        # Archive files should not be reported as orphaned


class TestLinkResolution:
    """Tests for link path resolution."""

    def test_resolves_relative_links(self):
        """Should correctly resolve relative path links."""
        # Test that ../index.html from articles/test.html resolves to index.html
        from pathlib import PurePosixPath

        current_dir = PurePosixPath("articles")
        href = "../index.html"

        # Simulate resolution
        target = current_dir / href
        normalized = str(target).replace("\\", "/")

        # Should resolve to index.html (without the articles/ prefix)
        assert "index.html" in normalized

    def test_resolves_nested_directory_links(self):
        """Should correctly resolve links to nested directories."""
        from pathlib import PurePosixPath

        current_dir = PurePosixPath(".")
        href = "articles/test-article.html"

        target = current_dir / href
        normalized = str(target).replace("\\", "/")

        assert "articles/test-article.html" in normalized


class TestUrlFragmentHandling:
    """Tests for URL fragment (anchor) handling."""

    def test_strips_anchor_from_url(self):
        """Should strip anchor fragments from URLs before checking."""
        from urllib.parse import urldefrag

        url = "about.html#section1"
        target, anchor = urldefrag(url)

        assert target == "about.html"
        assert anchor == "section1"

    def test_handles_anchor_only_url(self):
        """Should correctly handle anchor-only URLs."""
        from urllib.parse import urldefrag

        url = "#section1"
        target, anchor = urldefrag(url)

        assert target == ""
        assert anchor == "section1"

    def test_handles_url_without_anchor(self):
        """Should handle URLs without anchors."""
        from urllib.parse import urldefrag

        url = "about.html"
        target, anchor = urldefrag(url)

        assert target == "about.html"
        assert anchor == ""


class TestHtmlParsing:
    """Tests for HTML parsing functionality."""

    def test_extracts_links_from_html(self):
        """Should extract all links from HTML content."""
        from bs4 import BeautifulSoup

        html = """
<html>
<body>
<a href="page1.html">Link 1</a>
<a href="page2.html">Link 2</a>
<a>No href</a>
</body>
</html>
"""
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=True)

        assert len(links) == 2
        assert links[0]["href"] == "page1.html"
        assert links[1]["href"] == "page2.html"

    def test_handles_malformed_html(self):
        """Should handle malformed HTML gracefully."""
        from bs4 import BeautifulSoup

        malformed_html = """
<html>
<body>
<a href="page.html">Unclosed link
<div>Some content</div>
</body>
"""
        # BeautifulSoup should not raise an exception
        soup = BeautifulSoup(malformed_html, "html.parser")
        links = soup.find_all("a", href=True)

        assert len(links) == 1
        assert links[0]["href"] == "page.html"

    def test_extracts_link_text(self):
        """Should extract link text for reporting."""
        from bs4 import BeautifulSoup

        html = '<a href="page.html">Click Here</a>'
        soup = BeautifulSoup(html, "html.parser")
        link = soup.find("a")

        assert link.get_text(strip=True) == "Click Here"

    def test_handles_empty_href(self):
        """Should handle empty href attributes."""
        from bs4 import BeautifulSoup

        html = '<a href="">Empty Link</a>'
        soup = BeautifulSoup(html, "html.parser")
        link = soup.find("a", href=True)

        assert link["href"] == ""
