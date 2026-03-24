"""Tests for image verification helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from src.tools.verify_images import check_url, extract_image_urls, process_file


def test_extract_image_urls_collects_markdown_and_html_sources() -> None:
    """Both Markdown and HTML image references should be discovered."""
    content = '<img src="images/chart.png"> ![Alt](https://example.com/plot.png)'

    urls = extract_image_urls(content)

    assert urls == ["images/chart.png", "https://example.com/plot.png"]


def test_check_url_uses_get_when_head_is_not_allowed() -> None:
    """405 responses should fall back from HEAD to GET."""
    head_response = MagicMock(status_code=405)
    get_response = MagicMock(status_code=200)

    with (
        patch("src.tools.verify_images.requests.head", return_value=head_response),
        patch("src.tools.verify_images.requests.get", return_value=get_response) as mock_get,
    ):
        result = check_url("https://example.com/image.png", Path("page.qmd"))

    assert result is None
    mock_get.assert_called_once()
    get_response.close.assert_called_once()


def test_check_url_reports_missing_local_files(tmp_path: Path) -> None:
    """Missing local image references should include both attempted resolutions."""
    file_path = tmp_path / "pages" / "page.qmd"
    file_path.parent.mkdir(parents=True)
    file_path.write_text("content", encoding="utf-8")

    result = check_url("assets/missing.png", file_path)

    assert result is not None
    assert "BROKEN (Local)" in result
    assert "assets/missing.png" in result


def test_process_file_collects_only_broken_results(tmp_path: Path) -> None:
    """File processing should preserve only failing image checks."""
    file_path = tmp_path / "page.qmd"
    file_path.write_text(
        '![One](ok.png)\n<img src="broken.png" alt="Broken">',
        encoding="utf-8",
    )

    with patch(
        "src.tools.verify_images.check_url",
        side_effect=[None, "BROKEN (Local): broken.png"],
    ):
        results = process_file(file_path)

    assert results == ["BROKEN (Local): broken.png"]
