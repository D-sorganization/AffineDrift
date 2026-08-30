"""Adversarial contracts for the real bounded HTTPS transport adapter."""

from __future__ import annotations

from collections.abc import Iterator
from types import TracebackType

import pytest
import requests

from src.affine_control.programming_companion import AcquisitionError, RequestsTransport

URL = (
    "https://raw.githubusercontent.com/D-sorganization/UpstreamDrift/"
    + "1" * 40
    + "/dist/companion/manifest.json"
)


class FakeResponse:
    """Minimal streaming response contract used without real network access."""

    def __init__(
        self,
        status_code: int,
        chunks: tuple[bytes | requests.RequestException, ...] = (),
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self._chunks = chunks
        self.headers = headers or {}
        self.url = URL
        self.iterated = False

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    def iter_content(self, _chunk_size: int) -> Iterator[bytes]:
        self.iterated = True
        for chunk in self._chunks:
            if isinstance(chunk, requests.RequestException):
                raise chunk
            yield chunk


@pytest.mark.unit
def test_requests_transport_streams_a_bounded_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = FakeResponse(200, (b"abc", b"def"), {"Content-Length": "6"})
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: response)

    result = RequestsTransport().fetch(URL, 6)

    assert result.payload == b"abcdef"
    assert result.requested_url == URL
    assert result.final_url == URL
    assert result.redirects == ()


@pytest.mark.unit
def test_requests_transport_rejects_redirect_without_reading_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = FakeResponse(302, (b"untrusted",), {"Location": "https://evil.example"})
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: response)

    with pytest.raises(AcquisitionError, match="redirects are forbidden"):
        RequestsTransport().fetch(URL, 100)

    assert response.iterated is False


@pytest.mark.unit
@pytest.mark.parametrize("content_length", ["101", "-1", "not-an-integer"])
def test_requests_transport_rejects_invalid_content_length_before_streaming(
    monkeypatch: pytest.MonkeyPatch, content_length: str
) -> None:
    response = FakeResponse(200, (b"body",), {"Content-Length": content_length})
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: response)

    with pytest.raises(AcquisitionError, match="Content-Length|byte limit"):
        RequestsTransport().fetch(URL, 100)

    assert response.iterated is False


@pytest.mark.unit
def test_requests_transport_enforces_incremental_limit_without_header(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = FakeResponse(200, (b"a" * 60, b"b" * 41))
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: response)

    with pytest.raises(AcquisitionError, match="byte limit"):
        RequestsTransport().fetch(URL, 100)


@pytest.mark.unit
def test_requests_transport_normalizes_request_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(*_args: object, **_kwargs: object) -> FakeResponse:
        raise requests.Timeout("manufactured timeout")

    monkeypatch.setattr(requests, "get", fail)

    with pytest.raises(AcquisitionError, match="provider acquisition failed"):
        RequestsTransport().fetch(URL, 100)


@pytest.mark.unit
def test_requests_transport_normalizes_stream_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = FakeResponse(200, (b"partial", requests.Timeout("stream timeout")))
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: response)

    with pytest.raises(AcquisitionError, match="provider acquisition failed"):
        RequestsTransport().fetch(URL, 100)
