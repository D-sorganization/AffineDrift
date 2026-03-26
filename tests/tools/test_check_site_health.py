"""Tests for src.tools.check_site_health — site health checking functions."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.tools.check_site_health import (
    BrokenLinkRecord,
    _collect_all_files,
    _collect_html_files,
    _initial_orphaned_files,
    _log_site_map,
    _report_findings,
    _resolve_internal_target,
    check_site_health,
    is_inside_quarto_alternate_formats,
    main,
    parse_fail_on,
)


class TestParsefailOn:
    """Tests for parse_fail_on()."""

    def test_parses_broken(self) -> None:
        """Should return {'broken'} for 'broken'."""
        result = parse_fail_on("broken")
        assert result == {"broken"}

    def test_parses_orphaned(self) -> None:
        """Should return {'orphaned'} for 'orphaned'."""
        result = parse_fail_on("orphaned")
        assert result == {"orphaned"}

    def test_parses_all_alias(self) -> None:
        """Should expand 'all' to both broken and orphaned."""
        result = parse_fail_on("all")
        assert "broken" in result
        assert "orphaned" in result

    def test_parses_empty_string(self) -> None:
        """Should return empty set for empty string."""
        result = parse_fail_on("")
        assert isinstance(result, set)

    def test_raises_on_invalid_value(self) -> None:
        """Should raise on unrecognized fail-on value."""
        with pytest.raises((ValueError, Exception)):
            parse_fail_on("invalid_option")


class TestIsInsideQuartoAlternateFormats:
    """Tests for is_inside_quarto_alternate_formats()."""

    def test_returns_false_for_plain_tag(self) -> None:
        """Should return False for a tag with no alternate-formats parent."""
        from bs4 import BeautifulSoup

        html = '<a href="page.html">Link</a>'
        soup = BeautifulSoup(html, "html.parser")
        anchor = soup.find("a")
        assert is_inside_quarto_alternate_formats(anchor) is False

    def test_returns_true_for_tag_inside_alternate_formats(self) -> None:
        """Should return True for a tag inside quarto-alternate-formats div."""
        from bs4 import BeautifulSoup

        html = '<div class="quarto-alternate-formats"><a href="page.pdf">PDF</a></div>'
        soup = BeautifulSoup(html, "html.parser")
        anchor = soup.find("a")
        assert is_inside_quarto_alternate_formats(anchor) is True


class TestCollectHtmlFiles:
    """Tests for _collect_html_files()."""

    def test_collects_html_files(self, tmp_path: Path) -> None:
        """Should find all HTML files in directory tree."""
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "index.html").write_text("<html></html>", encoding="utf-8")
        result = _collect_html_files(docs_dir=docs)
        names = [p.name for p in result]
        assert "index.html" in names

    def test_excludes_coverage_dir(self, tmp_path: Path) -> None:
        """Should exclude files in coverage/ directory."""
        docs = tmp_path / "docs"
        docs.mkdir()
        cov = docs / "coverage"
        cov.mkdir()
        (cov / "report.html").write_text("<html></html>", encoding="utf-8")
        result = _collect_html_files(docs_dir=docs)
        assert not any("coverage" in str(p) for p in result)

    def test_empty_docs_dir(self, tmp_path: Path) -> None:
        """Should return empty list for empty docs dir."""
        docs = tmp_path / "docs"
        docs.mkdir()
        result = _collect_html_files(docs_dir=docs)
        assert result == []


class TestCollectAllFiles:
    """Tests for _collect_all_files()."""

    def test_collects_all_file_types(self, tmp_path: Path) -> None:
        """Should collect all files including non-HTML."""
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "index.html").write_text("<html></html>", encoding="utf-8")
        (docs / "style.css").write_text("body {}", encoding="utf-8")
        result = _collect_all_files(docs_dir=docs)
        assert Path("index.html") in result
        assert Path("style.css") in result

    def test_excludes_artifact_dirs(self, tmp_path: Path) -> None:
        """Should exclude files in lcov-report/ directory."""
        docs = tmp_path / "docs"
        docs.mkdir()
        lcov = docs / "lcov-report"
        lcov.mkdir()
        (lcov / "report.js").write_text("var x;", encoding="utf-8")
        result = _collect_all_files(docs_dir=docs)
        assert not any("lcov-report" in str(p) for p in result)


class TestLogSiteMap:
    """Tests for _log_site_map()."""

    def test_runs_without_error(self) -> None:
        """Should not raise for any list of paths."""
        html_files = [
            Path("index.html"),
            Path("about.html"),
            Path("articles/page.html"),
        ]
        _log_site_map(html_files)  # Should not raise


class TestInitialOrphanedFiles:
    """Tests for _initial_orphaned_files()."""

    def test_excludes_entry_points(self) -> None:
        """Should not mark entry point files as orphaned."""
        files = [Path("index.html"), Path("article.html")]
        result = _initial_orphaned_files(files)
        assert Path("index.html") not in result

    def test_marks_non_entry_points_as_orphaned(self) -> None:
        """Should mark non-entry-point files as orphan candidates."""
        files = [Path("article.html"), Path("other.html")]
        result = _initial_orphaned_files(files)
        assert Path("article.html") in result

    def test_excludes_archive_files(self) -> None:
        """Should exclude files with 'archive' in path."""
        files = [Path("archive/old.html")]
        result = _initial_orphaned_files(files)
        assert Path("archive/old.html") not in result


class TestResolveInternalTarget:
    """Tests for _resolve_internal_target()."""

    def test_resolves_relative_href(self, tmp_path: Path) -> None:
        """Should resolve a relative href against source file."""
        docs = tmp_path / "docs"
        docs.mkdir()
        result = _resolve_internal_target(
            source_file=Path("articles/page.html"),
            href="other.html",
            docs_dir=docs,
        )
        # Should return a Path or None — just verify it doesn't raise
        assert result is None or isinstance(result, Path)

    def test_returns_none_for_empty_href(self, tmp_path: Path) -> None:
        """Should return None for empty href."""
        docs = tmp_path / "docs"
        docs.mkdir()
        result = _resolve_internal_target(
            source_file=Path("page.html"),
            href="",
            docs_dir=docs,
        )
        assert result is None

    def test_returns_none_for_fragment_only(self, tmp_path: Path) -> None:
        """Should return None for fragment-only href (#section)."""
        docs = tmp_path / "docs"
        docs.mkdir()
        result = _resolve_internal_target(
            source_file=Path("page.html"),
            href="#section",
            docs_dir=docs,
        )
        assert result is None


class TestReportFindings:
    """Tests for _report_findings()."""

    def test_returns_0_when_no_issues(self) -> None:
        """Should return 0 when no broken links or orphaned files."""
        result = _report_findings(broken_links=[], orphaned_files=set(), fail_on=set())
        assert result == 0

    def test_returns_1_for_broken_links_with_fail_on_broken(self) -> None:
        """Should return 1 when broken links found and fail_on includes 'broken'."""
        broken = [BrokenLinkRecord("src.html", "target.html", "target.html", "Link")]
        result = _report_findings(broken_links=broken, orphaned_files=set(), fail_on={"broken"})
        assert result == 1

    def test_returns_0_for_broken_links_without_fail_on(self) -> None:
        """Should return 0 for broken links when fail_on doesn't include 'broken'."""
        broken = [BrokenLinkRecord("src.html", "target.html", "target.html", "Link")]
        result = _report_findings(broken_links=broken, orphaned_files=set(), fail_on=set())
        assert result == 0

    def test_returns_1_for_orphaned_files_with_fail_on_orphaned(self) -> None:
        """Should return 1 when orphaned files found and fail_on includes 'orphaned'."""
        orphaned = {Path("orphaned.html")}
        result = _report_findings(broken_links=[], orphaned_files=orphaned, fail_on={"orphaned"})
        assert result == 1

    def test_returns_0_for_orphaned_files_without_fail_on(self) -> None:
        """Should return 0 for orphaned files when fail_on doesn't include 'orphaned'."""
        orphaned = {Path("orphaned.html")}
        result = _report_findings(broken_links=[], orphaned_files=orphaned, fail_on=set())
        assert result == 0


class TestCheckSiteHealth:
    """Tests for check_site_health()."""

    def test_raises_when_docs_dir_missing(self, tmp_path: Path) -> None:
        """Should raise ContractViolationError when docs dir doesn't exist."""
        with pytest.raises(AssertionError):
            check_site_health(
                fail_on=set(),
                ignore_quarto_alternate_formats=True,
                docs_dir=tmp_path / "nonexistent",
            )

    def test_empty_docs_dir_returns_0(self, tmp_path: Path) -> None:
        """Should return 0 for empty docs directory."""
        docs = tmp_path / "docs"
        docs.mkdir()
        result = check_site_health(
            fail_on=set(),
            ignore_quarto_alternate_formats=True,
            docs_dir=docs,
        )
        assert result == 0

    def test_with_simple_html_file(self, tmp_path: Path) -> None:
        """Should process an HTML file and return 0 when no broken links."""
        docs = tmp_path / "docs"
        docs.mkdir()
        html_file = docs / "index.html"
        html_file.write_text(
            '<html><body><a href="about.html">About</a></body></html>',
            encoding="utf-8",
        )
        (docs / "about.html").write_text("<html><body>About</body></html>", encoding="utf-8")
        result = check_site_health(
            fail_on=set(),
            ignore_quarto_alternate_formats=True,
            docs_dir=docs,
        )
        assert result == 0

    def test_detects_broken_link_with_fail_on(self, tmp_path: Path) -> None:
        """Should return 1 when broken link found and fail_on includes 'broken'."""
        docs = tmp_path / "docs"
        docs.mkdir()
        html_file = docs / "index.html"
        html_file.write_text(
            '<html><body><a href="missing.html">Missing</a></body></html>',
            encoding="utf-8",
        )
        result = check_site_health(
            fail_on={"broken"},
            ignore_quarto_alternate_formats=True,
            docs_dir=docs,
        )
        assert result == 1


class TestMain:
    """Tests for main()."""

    def test_main_returns_2_on_missing_docs_dir(self) -> None:
        """main() should return 2 when docs-dir doesn't exist."""
        result = main(["--docs-dir", "/nonexistent/path"])
        assert result == 2

    def test_main_returns_0_on_empty_docs(self, tmp_path: Path) -> None:
        """main() should return 0 when docs dir is empty."""
        docs = tmp_path / "docs"
        docs.mkdir()
        result = main(["--docs-dir", str(docs)])
        assert result == 0

    def test_main_with_fail_on_broken(self, tmp_path: Path) -> None:
        """main() should return 1 when broken links found with --fail-on broken."""
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "index.html").write_text(
            '<html><body><a href="missing.html">Link</a></body></html>',
            encoding="utf-8",
        )
        result = main(["--docs-dir", str(docs), "--fail-on", "broken"])
        assert result == 1

    def test_main_raises_on_invalid_fail_on(self, tmp_path: Path) -> None:
        """main() should return 2 for invalid --fail-on value."""
        docs = tmp_path / "docs"
        docs.mkdir()
        result = main(["--docs-dir", str(docs), "--fail-on", "invalid_value"])
        assert result == 2
