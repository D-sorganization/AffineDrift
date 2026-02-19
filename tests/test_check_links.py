"""Tests for internal link checker helpers and behavior."""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.tools.check_links import (
    _is_broken_link,
    _normalize_internal_url,
    _should_scan_file,
    check_links,
    find_links,
)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com",
        "mailto:test@example.com",
        "#section",
        "${item.url}",
        "...",
        "x",
    ],
)
def test_normalize_internal_url_filters_non_internal_links(url: str) -> None:
    """External or placeholder links should be ignored."""
    assert _normalize_internal_url(url) is None


def test_normalize_internal_url_decodes_paths() -> None:
    """Internal links should be url-decoded."""
    assert _normalize_internal_url("docs/My%20File.html") == "docs/My File.html"


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("CONTRIBUTING.md", False),
        ("archive/page.qmd", False),
        ("pages/page.qmd", True),
    ],
)
def test_should_scan_file(path: str, expected: bool) -> None:
    """Known guidance docs and archive should be excluded from checks."""
    assert _should_scan_file(Path(path)) == expected


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


def test_find_links_extracts_precise_line_numbers(tmp_path: Path) -> None:
    """Mixed link syntax should map to exact source lines."""
    file_path = tmp_path / "page.qmd"
    file_path.write_text(
        "\n".join(
            [
                "[Guide](guide.html)",
                "![Diagram](assets/plot.png)",
                '<a href="about.html">About</a>',
                '<img src="assets/photo.png" alt="Photo">',
            ],
        ),
        encoding="utf-8",
    )

    assert find_links(file_path) == [
        ("guide.html", 1),
        ("assets/plot.png", 2),
        ("about.html", 3),
        ("assets/photo.png", 4),
    ]


def test_find_links_keeps_duplicate_links_on_different_lines(tmp_path: Path) -> None:
    """Same URL on multiple lines should preserve per-line diagnostics."""
    file_path = tmp_path / "dup.qmd"
    file_path.write_text(
        "\n".join(
            [
                "[One](shared.html)",
                "[Two](shared.html)",
            ],
        ),
        encoding="utf-8",
    )

    assert find_links(file_path) == [("shared.html", 1), ("shared.html", 2)]


def test_check_links_integration(tmp_path: Path) -> None:
    """End-to-end integration test for check_links."""
    # Setup valid and broken structure
    (tmp_path / "index.qmd").write_text("[Valid](page.html)", encoding="utf-8")
    (tmp_path / "page.qmd").write_text("Content", encoding="utf-8")

    (tmp_path / "broken.md").write_text("[Broken](missing.html)", encoding="utf-8")

    # Run check
    results = check_links(str(tmp_path))

    # Verify results
    assert len(results) == 1
    file, line, link = results[0]
    assert file == "broken.md"
    assert line == 1
    assert link == "missing.html"


def test_check_links_handles_read_errors(tmp_path: Path) -> None:
    """Ensure scanner survives file read errors."""
    (tmp_path / "unreadable.qmd").write_text("content", encoding="utf-8")

    with patch("src.tools.check_links.find_links", side_effect=OSError("Read failed")):
        results = check_links(str(tmp_path))
        assert results == []
