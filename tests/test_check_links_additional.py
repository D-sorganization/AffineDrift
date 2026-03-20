"""Additional regression tests for link checker boundary behavior."""

from pathlib import Path

from src.tools.check_links import (
    _is_html_link_resolvable,
    _normalize_internal_url,
    _path_exists_in_search_roots,
    _resolve_target_path,
    _should_scan_file,
    unique_broken,
)


def test_should_scan_file_excludes_docs_tree() -> None:
    assert not _should_scan_file(Path("docs/page.qmd"))


def test_should_scan_file_excludes_content_tree() -> None:
    assert not _should_scan_file(Path("content/page.qmd"))


def test_should_scan_file_excludes_node_modules() -> None:
    assert not _should_scan_file(Path("node_modules/pkg/index.js"))


def test_normalize_internal_url_drops_fragment_for_internal_link() -> None:
    assert _normalize_internal_url("guide.html#intro") == "guide.html"


def test_resolve_target_path_handles_root_relative_urls(tmp_path: Path) -> None:
    source = tmp_path / "articles" / "index.qmd"
    source.parent.mkdir(parents=True)
    source.write_text("", encoding="utf-8")
    resolved = _resolve_target_path(root_path=tmp_path, file_path=source, url="/docs/page.html")
    assert resolved == tmp_path / "docs" / "page.html"


def test_path_exists_in_search_roots_checks_docs_fallback(tmp_path: Path) -> None:
    target = tmp_path / "assets" / "chart.png"
    docs_target = tmp_path / "docs" / "assets" / "chart.png"
    docs_target.parent.mkdir(parents=True)
    docs_target.write_text("ok", encoding="utf-8")
    assert _path_exists_in_search_roots(root_path=tmp_path, target_path=target)


def test_is_html_link_resolvable_accepts_directory_with_index_qmd(tmp_path: Path) -> None:
    target = tmp_path / "guides" / "swing"
    target.mkdir(parents=True)
    (target / "index.qmd").write_text("", encoding="utf-8")
    assert _is_html_link_resolvable(root_path=tmp_path, target_path=target)


def test_unique_broken_deduplicates_identical_findings() -> None:
    links = [("a.qmd", 10, "missing.html"), ("a.qmd", 10, "missing.html")]
    assert unique_broken(links) == [("a.qmd", 10, "missing.html")]


def test_is_html_link_resolvable_accepts_md_source(tmp_path: Path) -> None:
    """HTML link should resolve when a matching .md source file exists."""
    target = tmp_path / "pages" / "guide.html"
    md_file = tmp_path / "pages" / "guide.md"
    md_file.parent.mkdir(parents=True)
    md_file.write_text("# Guide", encoding="utf-8")
    assert _is_html_link_resolvable(root_path=tmp_path, target_path=target)


def test_is_broken_link_returns_false_for_external_links(tmp_path: Path) -> None:
    """_is_broken_link should return False for external (https://) links."""
    from src.tools.check_links import _is_broken_link

    source = tmp_path / "page.qmd"
    source.write_text("", encoding="utf-8")
    # External links are normalized to None so should not be broken
    assert not _is_broken_link(root_path=tmp_path, file_path=source, link="https://example.com")
