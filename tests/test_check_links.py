"""Tests for internal link checker helpers and behavior."""

from pathlib import Path

from src.tools.check_links import (
    _is_broken_link,
    _normalize_internal_url,
    _should_scan_file,
)


def test_normalize_internal_url_filters_non_internal_links() -> None:
    """External or placeholder links should be ignored."""
    assert _normalize_internal_url("https://example.com") is None
    assert _normalize_internal_url("mailto:test@example.com") is None
    assert _normalize_internal_url("#section") is None
    assert _normalize_internal_url("${item.url}") is None
    assert _normalize_internal_url("...") is None
    assert _normalize_internal_url("x") is None


def test_normalize_internal_url_decodes_paths() -> None:
    """Internal links should be url-decoded."""
    assert _normalize_internal_url("docs/My%20File.html") == "docs/My File.html"


def test_should_scan_file_excludes_known_skip_targets() -> None:
    """Known guidance docs should be excluded from checks."""
    assert not _should_scan_file(Path("CONTRIBUTING.md"))
    assert not _should_scan_file(Path("archive/page.qmd"))
    assert _should_scan_file(Path("pages/page.qmd"))


def test_is_broken_link_allows_html_to_qmd_mapping(tmp_path: Path) -> None:
    """Links to generated .html should resolve when source .qmd exists."""
    root = tmp_path
    source = root / "pages" / "index.qmd"
    source.parent.mkdir(parents=True)
    source.write_text("", encoding="utf-8")
    (root / "pages" / "guide.qmd").write_text("", encoding="utf-8")

    assert not _is_broken_link(root_path=root, file_path=source, link="guide.html")


def test_is_broken_link_checks_src_prefix_for_assets(tmp_path: Path) -> None:
    """Non-html links can resolve through src/ prefix lookup."""
    root = tmp_path
    source = root / "pages" / "index.qmd"
    source.parent.mkdir(parents=True)
    source.write_text("", encoding="utf-8")

    asset = root / "src" / "tools" / "diagram.png"
    asset.parent.mkdir(parents=True)
    asset.write_text("png", encoding="utf-8")

    assert not _is_broken_link(root_path=root, file_path=source, link="/tools/diagram.png")


def test_is_broken_link_detects_missing_internal_target(tmp_path: Path) -> None:
    """Missing internal targets should be reported as broken."""
    root = tmp_path
    source = root / "pages" / "index.qmd"
    source.parent.mkdir(parents=True)
    source.write_text("", encoding="utf-8")

    assert _is_broken_link(root_path=root, file_path=source, link="missing.html")
