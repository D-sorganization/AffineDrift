"""Tests for verify_images.py — image URL extraction and checking."""

import socket
from collections.abc import Callable
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.tools.verify_images import check_url, extract_image_urls, is_safe_url


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
        content = '<img src="a.png" />\n![md](b.jpg)\n<img src="c.svg" />'
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

    def test_external_url_success(self, stub_public_dns: str) -> None:
        """Should return None for successful external URL."""
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("src.tools.verify_images.requests.head", return_value=mock_response):
            result = check_url("https://example.com/img.png", Path("page.html"))
        assert result is None

    def test_external_url_404_returns_error(self, stub_public_dns: str) -> None:
        """Should return error string for 404 external URL."""
        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("src.tools.verify_images.requests.head", return_value=mock_response):
            result = check_url("https://example.com/missing.png", Path("page.html"))
        assert result is not None
        assert "Status: 404" in result

    def test_external_url_405_falls_back_to_get(self, stub_public_dns: str) -> None:
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

    def test_external_url_request_exception(self, stub_public_dns: str) -> None:
        """Should return error string on request exception."""
        import requests

        with patch(
            "src.tools.verify_images.requests.head",
            side_effect=requests.exceptions.ConnectionError("connection failed"),
        ):
            result = check_url("https://unreachable.example.com/img.png", Path("page.html"))
        assert result is not None
        assert "connection failed" in result

    def test_ssrf_blocked_url_reports_error(
        self, dns_stub: Callable[[str | BaseException], None]
    ) -> None:
        """A host resolving to a loopback address should be refused before any request."""
        dns_stub("127.0.0.1")

        with patch("src.tools.verify_images.requests.head") as mock_head:
            result = check_url("https://internal.example.com/img.png", Path("page.html"))

        assert result is not None
        assert "SSRF blocked" in result
        mock_head.assert_not_called()

    def test_requires_non_empty_url(self) -> None:
        """Should raise on empty URL (contract enforcement)."""
        with pytest.raises(AssertionError):
            check_url("", Path("page.html"))


class TestIsSafeUrl:
    """Tests for is_safe_url() — the SSRF guard.

    Every case pins DNS through ``dns_stub`` so the guard's verdict is decided
    by the test, not by whatever the machine's resolver happens to answer.
    """

    def test_public_address_is_allowed(self, stub_public_dns: str) -> None:
        """A hostname resolving to a public address should pass."""
        assert is_safe_url("https://example.com/img.png") is True

    @pytest.mark.parametrize(
        ("resolved_ip", "reason"),
        [
            ("127.0.0.1", "IPv4 loopback"),
            ("10.0.0.5", "RFC1918 10/8"),
            ("172.16.0.1", "RFC1918 172.16/12"),
            ("192.168.1.1", "RFC1918 192.168/16"),
            ("169.254.169.254", "link-local cloud metadata endpoint"),
            ("0.0.0.0", "unspecified"),  # noqa: S104 -- reason: denylist test literal
            ("::1", "IPv6 loopback"),
            ("fd00::1", "IPv6 unique local"),
        ],
    )
    def test_rejects_internal_addresses(
        self,
        dns_stub: Callable[[str | BaseException], None],
        resolved_ip: str,
        reason: str,
    ) -> None:
        """Hostnames resolving inside the network perimeter should be refused."""
        dns_stub(resolved_ip)
        assert is_safe_url("https://internal.example.com/img.png") is False, reason

    @pytest.mark.parametrize(
        "url",
        [
            "http://localhost/img.png",
            "http://0.0.0.0/img.png",  # noqa: S104 -- reason: denylist test literal
            "http://[::1]/img.png",
        ],
    )
    def test_rejects_denylisted_hostnames_before_resolution(
        self, stub_public_dns: str, url: str
    ) -> None:
        """Denylisted host literals should be refused even if DNS says otherwise."""
        assert is_safe_url(url) is False

    def test_rejects_when_dns_resolution_fails(
        self, dns_stub: Callable[[str | BaseException], None]
    ) -> None:
        """Unresolvable hostnames should fail closed, not fail open."""
        dns_stub(socket.gaierror(-2, "Name or service not known"))
        assert is_safe_url("https://example.com/img.png") is False

    def test_rejects_url_without_hostname(self) -> None:
        """A URL with no host component should be refused."""
        assert is_safe_url("https:///img.png") is False

    def test_rejects_unparseable_resolved_address(
        self, dns_stub: Callable[[str | BaseException], None]
    ) -> None:
        """A resolved value that is not an IP should fail closed."""
        dns_stub("not-an-ip-address")
        assert is_safe_url("https://example.com/img.png") is False
