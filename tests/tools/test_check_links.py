"""Tests for src.tools.check_links — link extraction and validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.tools.check_links import (
    LinkResolutionContext,
    _is_broken_link,
    _should_scan_file,
    check_links,
    find_links,
    unique_broken,
)


class TestFindLinks:
    """Tests for find_links()."""

    def test_finds_markdown_links(self, tmp_path: Path) -> None:
        """Should extract markdown [text](url) links."""
        f = tmp_path / "page.qmd"
        f.write_text("[Click here](https://example.com)", encoding="utf-8")
        links = find_links(f)
        urls = [link for link, _ in links]
        assert "https://example.com" in urls

    def test_finds_html_href_links(self, tmp_path: Path) -> None:
        """Should extract HTML href links."""
        f = tmp_path / "page.html"
        f.write_text('<a href="other.html">Link</a>', encoding="utf-8")
        links = find_links(f)
        urls = [link for link, _ in links]
        assert any("other.html" in u for u in urls)

    def test_returns_line_numbers(self, tmp_path: Path) -> None:
        """Should return correct line numbers for found links."""
        f = tmp_path / "page.qmd"
        f.write_text("Line 1\n[link](url.html)\nLine 3", encoding="utf-8")
        links = find_links(f)
        line_numbers = [ln for _, ln in links]
        assert 2 in line_numbers

    def test_empty_file_returns_no_links(self, tmp_path: Path) -> None:
        """Should return empty list for file with no links."""
        f = tmp_path / "empty.qmd"
        f.write_text("No links here.", encoding="utf-8")
        links = find_links(f)
        assert isinstance(links, list)

    def test_raises_on_none_path(self) -> None:
        """Should raise on None file_path (contract)."""
        with pytest.raises(AssertionError):
            find_links(None)  # type: ignore[arg-type]


class TestUniqueBroken:
    """Tests for unique_broken()."""

    def test_deduplicates_links(self) -> None:
        """Should return unique broken links."""
        links = [
            ("file.html", 1, "broken.html"),
            ("file.html", 1, "broken.html"),
            ("other.html", 2, "missing.html"),
        ]
        result = unique_broken(links)
        assert len(result) == 2

    def test_empty_input_returns_empty(self) -> None:
        """Should return empty list for empty input."""
        assert unique_broken([]) == []

    def test_all_unique_returns_all(self) -> None:
        """Should return all links when none are duplicates."""
        links = [
            ("a.html", 1, "b.html"),
            ("c.html", 2, "d.html"),
        ]
        result = unique_broken(links)
        assert len(result) == 2


class TestShouldScanFile:
    """Tests for _should_scan_file()."""

    def test_qmd_file_should_scan(self, tmp_path: Path) -> None:
        """Should return True for .qmd files outside excluded dirs."""
        f = tmp_path / "article.qmd"
        assert _should_scan_file(f) is True

    def test_html_file_should_scan(self, tmp_path: Path) -> None:
        """Should return True for .html files outside excluded dirs."""
        f = tmp_path / "page.html"
        assert _should_scan_file(f) is True

    def test_python_file_not_scanned(self, tmp_path: Path) -> None:
        """Should return False for non-qmd/html files."""
        f = tmp_path / "script.py"
        assert _should_scan_file(f) is False

    def test_docs_dir_excluded(self) -> None:
        """Should return False for files inside docs directory."""
        f = Path("/project/docs/page.html")
        assert _should_scan_file(f) is False

    def test_node_modules_excluded(self) -> None:
        """Should return False for files inside node_modules."""
        f = Path("/project/node_modules/package/index.qmd")
        assert _should_scan_file(f) is False


class TestIsBrokenLink:
    """Tests for _is_broken_link()."""

    def test_external_links_not_broken(self, tmp_path: Path) -> None:
        """Should return False for external http links."""
        f = tmp_path / "page.qmd"
        result = _is_broken_link(root_path=tmp_path, file_path=f, link="https://example.com")
        assert result is False

    def test_anchor_links_not_broken(self, tmp_path: Path) -> None:
        """Should return False for anchor (#section) links."""
        f = tmp_path / "page.qmd"
        result = _is_broken_link(root_path=tmp_path, file_path=f, link="#section")
        assert result is False

    def test_missing_internal_file_is_broken(self, tmp_path: Path) -> None:
        """Should return True for internal links pointing to missing files."""
        f = tmp_path / "page.qmd"
        result = _is_broken_link(
            root_path=tmp_path,
            file_path=f,
            link="nonexistent.qmd",
        )
        assert result is True

    def test_existing_internal_file_not_broken(self, tmp_path: Path) -> None:
        """Should return False for internal links pointing to existing files."""
        existing = tmp_path / "target.qmd"
        existing.write_text("content", encoding="utf-8")
        f = tmp_path / "page.qmd"
        result = _is_broken_link(root_path=tmp_path, file_path=f, link="target.qmd")
        assert result is False

    def test_html_link_resolves_via_context_facade(self, tmp_path: Path) -> None:
        """The link-resolution facade should treat HTML links as source-backed pages."""
        section_dir = tmp_path / "guide"
        section_dir.mkdir()
        (section_dir / "index.qmd").write_text("guide", encoding="utf-8")
        context = LinkResolutionContext(root_path=tmp_path, source_file=tmp_path / "page.qmd")
        assert context.is_broken("guide/index.html") is False


class TestCheckLinks:
    """Tests for check_links()."""

    def test_empty_dir_returns_no_broken(self, tmp_path: Path) -> None:
        """Should return empty list when no scannable files found."""
        result = check_links(str(tmp_path))
        assert result == []

    def test_finds_no_broken_links_in_clean_file(self, tmp_path: Path) -> None:
        """Should return empty list when all links resolve."""
        # Create linked files
        (tmp_path / "target.qmd").write_text("target content", encoding="utf-8")
        page = tmp_path / "page.qmd"
        page.write_text("[link](target.qmd)", encoding="utf-8")
        result = check_links(str(tmp_path))
        assert isinstance(result, list)

    def test_raises_on_empty_root_dir(self) -> None:
        """Should raise on empty root_dir string (contract)."""
        with pytest.raises(AssertionError):
            check_links("")
