"""Tests for the shared link utility module."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.tools.utils.link_utils import (
    ALL_LINK_PATTERNS,
    HTML_HREF_PATTERN,
    HTML_SRC_PATTERN,
    MARKDOWN_IMAGE_PATTERN,
    MARKDOWN_LINK_PATTERN,
    is_external_url,
    is_fragment_only,
    normalize_internal_url,
    path_exists_in_search_roots,
    resolve_relative_path,
    strip_fragment,
)


class TestIsExternalUrl:
    """Tests for is_external_url()."""

    @pytest.mark.parametrize(
        "url",
        [
            "http://example.com",
            "https://example.com",
            "mailto:user@example.com",
            "tel:+1234567890",
            "ftp://files.example.com",
        ],
    )
    def test_external_urls(self, url: str) -> None:
        assert is_external_url(url) is True

    @pytest.mark.parametrize(
        "url",
        [
            "page.html",
            "/articles/page.html",
            "#section",
        ],
    )
    def test_non_external_urls(self, url: str) -> None:
        assert is_external_url(url) is False


class TestIsFragmentOnly:
    """Tests for is_fragment_only()."""

    @pytest.mark.parametrize("url", ["#section", "#"])
    def test_fragment_only(self, url: str) -> None:
        assert is_fragment_only(url) is True

    @pytest.mark.parametrize("url", ["page.html#section", "page.html"])
    def test_not_fragment_only(self, url: str) -> None:
        assert is_fragment_only(url) is False


class TestStripFragment:
    """Tests for strip_fragment()."""

    @pytest.mark.parametrize(
        ("url", "expected"),
        [
            ("page.html#section-1", "page.html"),
            ("#anchor", ""),
            ("page.html", "page.html"),
            ("", ""),
        ],
    )
    def test_strip_fragment(self, url: str, expected: str) -> None:
        assert strip_fragment(url) == expected


class TestNormalizeInternalUrl:
    """Tests for normalize_internal_url()."""

    @pytest.mark.parametrize(
        ("url", "expected"),
        [
            ("articles/page.html", "articles/page.html"),
            ("page.html#section", "page.html"),
            ("my%20page.html", "my page.html"),
        ],
    )
    def test_normalizes_valid_urls(self, url: str, expected: str) -> None:
        assert normalize_internal_url(url) == expected

    @pytest.mark.parametrize(
        "url",
        [
            "https://example.com",
            "mailto:user@example.com",
            "#section",
            "${BASE_URL}/page",
            "...",
            "/",
        ],
    )
    def test_skips_non_internal_urls(self, url: str) -> None:
        assert normalize_internal_url(url) is None


class TestResolveRelativePath:
    """Tests for resolve_relative_path()."""

    def test_absolute_url(self) -> None:
        root = Path("/project")
        source = Path("/project/docs/article.html")
        result = resolve_relative_path(root=root, source_file=source, url="/assets/img.png")
        assert result == Path("/project/assets/img.png")

    def test_relative_url(self) -> None:
        root = Path("/project")
        source = Path("/project/docs/article.html")
        result = resolve_relative_path(root=root, source_file=source, url="images/logo.png")
        assert result == Path("/project/docs/images/logo.png")


class TestPathExistsInSearchRoots:
    """Tests for path_exists_in_search_roots()."""

    def test_existing_file(self, tmp_path: Path) -> None:
        (tmp_path / "test.html").write_text("hello")
        assert path_exists_in_search_roots(root=tmp_path, target=tmp_path / "test.html") is True

    def test_missing_file(self, tmp_path: Path) -> None:
        assert path_exists_in_search_roots(root=tmp_path, target=tmp_path / "missing.html") is False

    def test_finds_in_src_prefix(self, tmp_path: Path) -> None:
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "file.py").write_text("content")
        assert path_exists_in_search_roots(root=tmp_path, target=tmp_path / "file.py") is True

    def test_finds_in_docs_prefix(self, tmp_path: Path) -> None:
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "page.html").write_text("content")
        assert path_exists_in_search_roots(root=tmp_path, target=tmp_path / "page.html") is True

    def test_returns_false_when_target_not_relative_to_root(self, tmp_path: Path) -> None:
        """path_exists_in_search_roots should return False when target is outside root."""
        # Use an absolute path outside root that doesn't exist
        # The function first checks target.exists() (returns False), then is_relative_to
        target = Path("/tmp/__gaai_nonexistent_target_xyz_12345/page.html")
        # Ensure it doesn't exist and is not relative to tmp_path
        assert not target.exists()
        assert path_exists_in_search_roots(root=tmp_path, target=target) is False


class TestLinkPatterns:
    """Tests for compiled link patterns."""

    def test_markdown_link_pattern(self) -> None:
        matches = MARKDOWN_LINK_PATTERN.findall("[click here](page.html)")
        assert "page.html" in matches

    def test_markdown_image_excluded_from_link(self) -> None:
        matches = MARKDOWN_LINK_PATTERN.findall("![alt](image.png)")
        assert matches == []

    def test_markdown_image_pattern(self) -> None:
        matches = MARKDOWN_IMAGE_PATTERN.findall("![alt](image.png)")
        assert "image.png" in matches

    def test_html_href_pattern(self) -> None:
        matches = HTML_HREF_PATTERN.findall('<a href="page.html">link</a>')
        assert "page.html" in matches

    def test_html_src_pattern(self) -> None:
        matches = HTML_SRC_PATTERN.findall('<img src="image.png">')
        assert "image.png" in matches

    def test_all_patterns_tuple(self) -> None:
        assert len(ALL_LINK_PATTERNS) == 4
