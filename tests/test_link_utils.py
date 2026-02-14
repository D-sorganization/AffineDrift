"""Tests for the shared link utility module."""

from __future__ import annotations

from pathlib import Path

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

    def test_http_is_external(self) -> None:
        assert is_external_url("http://example.com") is True

    def test_https_is_external(self) -> None:
        assert is_external_url("https://example.com") is True

    def test_mailto_is_external(self) -> None:
        assert is_external_url("mailto:user@example.com") is True

    def test_tel_is_external(self) -> None:
        assert is_external_url("tel:+1234567890") is True

    def test_ftp_is_external(self) -> None:
        assert is_external_url("ftp://files.example.com") is True

    def test_relative_is_not_external(self) -> None:
        assert is_external_url("page.html") is False

    def test_absolute_is_not_external(self) -> None:
        assert is_external_url("/articles/page.html") is False

    def test_fragment_is_not_external(self) -> None:
        assert is_external_url("#section") is False


class TestIsFragmentOnly:
    """Tests for is_fragment_only()."""

    def test_fragment(self) -> None:
        assert is_fragment_only("#section") is True

    def test_empty_fragment(self) -> None:
        assert is_fragment_only("#") is True

    def test_page_with_fragment(self) -> None:
        assert is_fragment_only("page.html#section") is False

    def test_relative_path(self) -> None:
        assert is_fragment_only("page.html") is False


class TestStripFragment:
    """Tests for strip_fragment()."""

    def test_removes_fragment(self) -> None:
        assert strip_fragment("page.html#section-1") == "page.html"

    def test_fragment_only_returns_empty(self) -> None:
        assert strip_fragment("#anchor") == ""

    def test_no_fragment(self) -> None:
        assert strip_fragment("page.html") == "page.html"

    def test_empty_string(self) -> None:
        assert strip_fragment("") == ""


class TestNormalizeInternalUrl:
    """Tests for normalize_internal_url()."""

    def test_normal_url(self) -> None:
        assert normalize_internal_url("articles/page.html") == "articles/page.html"

    def test_strips_fragment(self) -> None:
        assert normalize_internal_url("page.html#section") == "page.html"

    def test_skips_external_http(self) -> None:
        assert normalize_internal_url("https://example.com") is None

    def test_skips_external_mailto(self) -> None:
        assert normalize_internal_url("mailto:user@example.com") is None

    def test_skips_fragment_only(self) -> None:
        assert normalize_internal_url("#section") is None

    def test_skips_template_variable(self) -> None:
        assert normalize_internal_url("${BASE_URL}/page") is None

    def test_skips_ellipsis(self) -> None:
        assert normalize_internal_url("...") is None

    def test_skips_single_char(self) -> None:
        assert normalize_internal_url("/") is None

    def test_decodes_percent_encoding(self) -> None:
        assert normalize_internal_url("my%20page.html") == "my page.html"


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
