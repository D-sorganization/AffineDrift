"""Bounded transport abstraction for companion provider bytes."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

import requests

from .errors import AcquisitionError
from .models import FetchResult

HTTP_OK = 200
CHUNK_BYTES = 64 * 1024


class Transport(Protocol):
    """Fetch bytes without granting the consumer direct network access."""

    def fetch(self, url: str, max_bytes: int) -> FetchResult:
        """Return at most ``max_bytes`` and all redirect evidence."""
        ...


class RequestsTransport:
    """HTTPS transport that rejects redirects and bounds streaming payloads."""

    def __init__(self, timeout_seconds: float = 20.0) -> None:
        """Configure a positive request timeout."""
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._timeout_seconds = timeout_seconds

    def fetch(self, url: str, max_bytes: int) -> FetchResult:
        """Fetch one response without following redirects."""
        if max_bytes <= 0:
            raise AcquisitionError("payload byte limit must be positive")
        try:
            response = requests.get(
                url,
                allow_redirects=False,
                stream=True,
                timeout=self._timeout_seconds,
            )
            with response:
                if 300 <= response.status_code < 400:
                    raise AcquisitionError("provider redirects are forbidden")
                if response.status_code != HTTP_OK:
                    raise AcquisitionError(f"provider returned HTTP {response.status_code}")
                self._validate_content_length(response.headers.get("Content-Length"), max_bytes)
                payload = self._bounded_bytes(response.iter_content(CHUNK_BYTES), max_bytes)
                return FetchResult(url, response.url, (), payload)
        except requests.RequestException as exc:
            raise AcquisitionError(f"provider acquisition failed: {exc}") from exc

    @staticmethod
    def _validate_content_length(raw_length: str | None, max_bytes: int) -> None:
        """Reject malformed, negative, or oversized declared lengths."""
        if raw_length is None:
            return
        try:
            content_length = int(raw_length)
        except ValueError as exc:
            raise AcquisitionError("provider returned an invalid Content-Length") from exc
        if content_length < 0 or content_length > max_bytes:
            raise AcquisitionError("payload exceeds byte limit")

    @staticmethod
    def _bounded_bytes(chunks: Iterator[bytes], max_bytes: int) -> bytes:
        """Accumulate chunks only while the incremental limit holds."""
        payload = bytearray()
        for chunk in chunks:
            payload.extend(chunk)
            if len(payload) > max_bytes:
                raise AcquisitionError("payload exceeds byte limit")
        return bytes(payload)


class DirectoryTransport:
    """Serve an already-downloaded provider bundle (an extracted Actions artifact).

    Every URL must start with ``url_prefix`` (the policy's object URL with an
    empty path); the remainder is a single file name resolved inside ``root``.
    Symlinks, nested paths, missing files, and oversized files are rejected, so
    the consumer's validation and store contracts apply unchanged (#4123).
    """

    def __init__(self, root: Path, url_prefix: str) -> None:
        """Bind one extracted bundle directory to one URL prefix."""
        if not url_prefix.startswith("https://") or not url_prefix.endswith("/"):
            raise AcquisitionError("directory transport prefix must be an https URL ending in /")
        if root.is_symlink() or not root.is_dir():
            raise AcquisitionError("directory transport root must be a real directory")
        self._root = root
        self._url_prefix = url_prefix

    def fetch(self, url: str, max_bytes: int) -> FetchResult:
        """Read one bounded regular file addressed by an approved URL."""
        if max_bytes <= 0:
            raise AcquisitionError("payload byte limit must be positive")
        if not url.startswith(self._url_prefix):
            raise AcquisitionError("URL is outside the bundle transport prefix")
        name = url[len(self._url_prefix) :]
        if not name or "/" in name or "\\" in name or name in {".", ".."}:
            raise AcquisitionError("bundle transport only serves single file names")
        target = self._root / name
        if target.is_symlink() or not target.is_file():
            raise AcquisitionError(f"bundle file is missing or unsafe: {name}")
        if target.stat().st_size > max_bytes:
            raise AcquisitionError("payload exceeds byte limit")
        return FetchResult(url, url, (), target.read_bytes())
