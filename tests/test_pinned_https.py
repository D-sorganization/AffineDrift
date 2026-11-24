"""Tests for scripts/pinned_https.py and the two checks that fetch through it."""

from __future__ import annotations

import io

import pytest

from scripts import (
    check_companion_launcher_freshness,
    check_upstreamdrift_readme_parity,
    pinned_https,
)
from scripts.pinned_https import GITHUB_RAW_HOST, read_pinned_https

COMMIT = "a" * 40


class _Response(io.BytesIO):
    def __enter__(self) -> _Response:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()


@pytest.fixture
def opened(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """URLs that reached ``urlopen``; no test touches the network."""
    urls: list[str] = []

    def fake_urlopen(url: str, timeout: float) -> _Response:
        urls.append(url)
        return _Response(b'{"tiles": [{"id": "golf"}]}')

    monkeypatch.setattr(pinned_https.urllib.request, "urlopen", fake_urlopen)
    return urls


@pytest.mark.unit
def test_an_https_url_on_the_pinned_host_is_fetched(opened: list[str]) -> None:
    url = f"https://{GITHUB_RAW_HOST}/D-sorganization/UpstreamDrift/{COMMIT}/README.md"

    assert read_pinned_https(url, host=GITHUB_RAW_HOST) == b'{"tiles": [{"id": "golf"}]}'
    assert opened == [url]


@pytest.mark.unit
@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        f"http://{GITHUB_RAW_HOST}/D-sorganization/UpstreamDrift/x/README.md",
        f"ftp://{GITHUB_RAW_HOST}/x",
        "https://example.invalid/README.md",
        f"https://{GITHUB_RAW_HOST}.example.invalid/README.md",
        f"https://user@{GITHUB_RAW_HOST}/README.md",
        f"https://{GITHUB_RAW_HOST}:8443/README.md",
        f"HTTPS://{GITHUB_RAW_HOST.upper()}@example.invalid/x",
        "",
    ],
)
def test_any_other_scheme_or_host_is_refused_before_a_request(url: str, opened: list[str]) -> None:
    with pytest.raises(ValueError, match="refusing to fetch"):
        read_pinned_https(url, host=GITHUB_RAW_HOST)

    assert opened == []


@pytest.mark.unit
def test_both_checks_fetch_only_from_the_pinned_host(opened: list[str]) -> None:
    assert check_companion_launcher_freshness.launcher_tile_ids(COMMIT) == {"golf"}
    assert check_upstreamdrift_readme_parity.fetch_readme(COMMIT).startswith("{")

    assert len(opened) == 2
    assert all(
        url.startswith(f"https://{GITHUB_RAW_HOST}/D-sorganization/UpstreamDrift/{COMMIT}/")
        for url in opened
    )


@pytest.mark.unit
@pytest.mark.parametrize("commit", ["../../../evil", "x@example.invalid/", "main"])
def test_a_commit_that_is_not_a_sha_never_reaches_the_network(
    commit: str, opened: list[str]
) -> None:
    with pytest.raises(ValueError):
        check_companion_launcher_freshness.launcher_tile_ids(commit)
    with pytest.raises(ValueError):
        check_upstreamdrift_readme_parity.fetch_readme(commit)

    assert opened == []
