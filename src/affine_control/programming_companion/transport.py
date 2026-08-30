"""Bounded transport abstraction for companion provider bytes."""

from __future__ import annotations

from collections.abc import Iterator
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
        payload = bytearray()
        for chunk in chunks:
            payload.extend(chunk)
            if len(payload) > max_bytes:
                raise AcquisitionError("payload exceeds byte limit")
        return bytes(payload)
