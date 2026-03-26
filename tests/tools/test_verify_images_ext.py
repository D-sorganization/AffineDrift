"""Extended tests for src.tools.verify_images — broken URL paths and main()."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestCheckUrlPaths:
    """Tests for check_url() local and external broken paths."""

    def test_broken_local_image_returns_message(self, tmp_path: Path) -> None:
        """Should return error message for missing local image."""
        from src.tools.verify_images import check_url

        result = check_url("nonexistent.png", tmp_path / "page.html")
        assert result is not None
        assert "BROKEN" in result

    def test_existing_local_image_returns_none(self, tmp_path: Path) -> None:
        """Should return None for existing local image."""
        from src.tools.verify_images import check_url

        img = tmp_path / "image.png"
        img.write_bytes(b"png data")
        html = tmp_path / "page.html"
        result = check_url("image.png", html)
        assert result is None

    def test_external_url_with_http_error_returns_message(self) -> None:
        """Should return error for external URL returning 404."""
        from src.tools.verify_images import check_url

        mock_response = MagicMock()
        mock_response.status_code = 404
        with patch("src.tools.verify_images.requests.head", return_value=mock_response):
            result = check_url("https://example.com/missing.png", "page.html")
        assert result is not None
        assert "BROKEN" in result

    def test_external_url_with_os_error_returns_message(self) -> None:
        """Should return error for external URL with OS error."""

        from src.tools.verify_images import check_url

        with patch(
            "src.tools.verify_images.requests.head",
            side_effect=OSError("OS error"),
        ):
            result = check_url("https://example.com/image.png", "page.html")
        assert result is not None
        assert "BROKEN" in result


class TestVerifyImagesMain:
    """Tests for main() function in verify_images."""

    def test_main_runs_without_error_in_empty_dir(self, tmp_path: Path) -> None:
        """main() should not raise in directory with no .qmd or .html files."""
        from src.tools.verify_images import main

        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            main()  # Should complete without raising
        finally:
            os.chdir(original)

    def test_main_processes_html_files(self, tmp_path: Path) -> None:
        """main() should process .html files without raising."""
        from src.tools.verify_images import main

        html_file = tmp_path / "page.html"
        html_file.write_text('<img src="logo.png">', encoding="utf-8")

        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            main()
        finally:
            os.chdir(original)
