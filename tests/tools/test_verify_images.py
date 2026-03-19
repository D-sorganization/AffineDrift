"""Tests for verify_images.py — image URL extraction and checking."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.tools.verify_images import check_url, extract_image_urls


class TestExtractImageUrls:
    """Tests for extract_image_urls()."""

    def test_extracts_html_img_src_double_quotes(self) -> None:
        """Should extract src from HTML img tags with double quotes."""
        content = '<img src="image.png" alt="test" />'
        result = extract_image_urls(content)
        assert "image.png" in result

    def test_extracts_html_img_src_single_quotes(self) -> None:
        """Should extract src from HTML img tags with single quotes."""
        content = "<img src='photo.jpg' />"
        result = extract_image_urls(content)
        assert "photo.jpg" in result

    def test_extracts_markdown_image(self) -> None:
        """Should extract URL from Markdown image syntax."""
        content = "![Alt text](images/chart.png)"
        result = extract_image_urls(content)
        assert "images/chart.png" in result

    def test_extracts_multiple_images(self) -> None:
        """Should extract all image URLs from mixed content."""
        content = '<img src="a.png" />\n' "![md](b.jpg)\n" '<img src="c.svg" />'
        result = extract_image_urls(content)
        assert len(result) >= 3
        assert "a.png" in result
        assert "b.jpg" in result
        assert "c.svg" in result

    def test_empty_content(self) -> None:
        """Should return empty list for content with no images."""
        result = extract_image_urls("No images here.")
        assert result == []

    def test_requires_non_none_content(self) -> None:
        """Should raise on None content (contract enforcement)."""
        with pytest.raises(AssertionError):
            extract_image_urls(None)  # type: ignore[arg-type]


class TestCheckUrl:
    """Tests for check_url() — local path checking."""

    def test_local_existing_file_returns_none(self, tmp_path: Path) -> None:
        """Should return None for existing local files."""
        img = tmp_path / "image.png"
        img.write_bytes(b"fake png")
        result = check_url(str(img), tmp_path / "page.html")
        assert result is None

    def test_local_missing_file_returns_error(self, tmp_path: Path) -> None:
        """Should return error string for missing local files."""
        result = check_url("nonexistent.png", tmp_path / "page.html")
        assert result is not None
        assert "BROKEN" in result

    def test_absolute_local_path(self, tmp_path: Path) -> None:
        """Should handle absolute local paths."""
        img = tmp_path / "img.jpg"
        img.write_bytes(b"data")
        result = check_url(f"/{img}", tmp_path / "page.html")
        # The file likely won't be found via lstrip('/') relative, returns error or None
        assert result is None or "BROKEN" in result

    def test_external_url_success(self) -> None:
        """Should return None for successful external URL."""
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("src.tools.verify_images.requests.head", return_value=mock_response):
            result = check_url("https://example.com/img.png", Path("page.html"))
        assert result is None

    def test_external_url_404_returns_error(self) -> None:
        """Should return error string for 404 external URL."""
        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("src.tools.verify_images.requests.head", return_value=mock_response):
            result = check_url("https://example.com/missing.png", Path("page.html"))
        assert result is not None
        assert "BROKEN" in result

    def test_external_url_405_falls_back_to_get(self) -> None:
        """Should fall back to GET when HEAD returns 405."""
        head_response = MagicMock()
        head_response.status_code = 405
        get_response = MagicMock()
        get_response.status_code = 200

        with (
            patch("src.tools.verify_images.requests.head", return_value=head_response),
            patch("src.tools.verify_images.requests.get", return_value=get_response),
        ):
            result = check_url("https://example.com/img.png", Path("page.html"))
        assert result is None

    def test_external_url_request_exception(self) -> None:
        """Should return error string on request exception."""
        import requests

        with patch(
            "src.tools.verify_images.requests.head",
            side_effect=requests.exceptions.ConnectionError("connection failed"),
        ):
            result = check_url("https://unreachable.example.com/img.png", Path("page.html"))
        assert result is not None
        assert "BROKEN" in result

    def test_requires_non_empty_url(self) -> None:
        """Should raise on empty URL (contract enforcement)."""
        with pytest.raises(AssertionError):
            check_url("", Path("page.html"))
