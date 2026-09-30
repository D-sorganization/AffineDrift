"""Tests for scripts/link-checker.py external-URL reporting (issue #4596).

The script file is ``scripts/link-checker.py`` (hyphenated), so it is loaded
via importlib rather than a normal import.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "link-checker.py"


@pytest.fixture(scope="module")
def link_checker():
    spec = importlib.util.spec_from_file_location("link_checker_under_test", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://doi.org/10.1000/xyz123", True),
        ("https://dx.doi.org/10.1000/xyz123", True),
        ("https://DOI.ORG/10.1000/xyz123", True),
        ("https://example.com/doi.org", False),
        ("https://example.com/article", False),
    ],
)
def test_is_doi_url(link_checker, url: str, expected: bool) -> None:
    assert link_checker.is_doi_url(url) is expected


def test_archive_org_suggestion_wraps_the_dead_url(link_checker) -> None:
    suggestion = link_checker.archive_org_suggestion("https://example.com/gone")
    assert suggestion == "https://web.archive.org/web/*/https://example.com/gone"


def test_validate_url_follows_redirects_for_doi_links(monkeypatch, link_checker) -> None:
    """DOI links resolve through a redirect by design; that must count as valid."""

    class FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *exc_info):
            return False

    class FakeOpener:
        def __init__(self, *handlers):
            self.handlers = handlers

        def open(self, req, timeout):
            # A SafeRedirectHandler-equipped opener follows the doi.org
            # redirect internally and returns the final 200 response.
            assert any(isinstance(h, link_checker.SafeRedirectHandler) for h in self.handlers)
            return FakeResponse()

    monkeypatch.setattr(link_checker, "build_opener", lambda *handlers: FakeOpener(*handlers))
    monkeypatch.setattr(link_checker, "is_safe_url", lambda url: True)

    is_valid, reason = link_checker.validate_url("https://doi.org/10.1000/xyz123")
    assert is_valid
    assert "200" in reason


def test_safe_redirect_handler_blocks_redirect_to_unsafe_host(monkeypatch, link_checker) -> None:
    """A doi.org redirect into a private/internal host must not be followed."""
    monkeypatch.setattr(link_checker, "is_safe_url", lambda url: False)

    handler = link_checker.SafeRedirectHandler()
    result = handler.redirect_request(None, None, 302, "Found", {}, "http://169.254.169.254/secret")

    assert result is None


def test_check_file_reports_archive_suggestion_for_broken_external_link(
    monkeypatch, tmp_path, link_checker
) -> None:
    file_path = tmp_path / "page.qmd"
    file_path.write_text("See https://example.com/dead-link for details.", encoding="utf-8")

    monkeypatch.setattr(
        link_checker, "validate_url", lambda url, retries=2: (False, "Client error (404)")
    )

    errors, warnings = link_checker.check_file(file_path, set(), external_only=True)

    assert errors == []
    assert len(warnings) == 1
    warning = warnings[0]
    assert warning["url"] == "https://example.com/dead-link"
    assert warning["reason"] == "Client error (404)"
    assert (
        warning["archive_suggestion"]
        == "https://web.archive.org/web/*/https://example.com/dead-link"
    )
    assert warning["file"] == str(file_path)


def test_main_writes_json_report_for_external_warnings(monkeypatch, tmp_path, link_checker) -> None:
    doc = tmp_path / "index.qmd"
    doc.write_text("Broken: https://example.com/dead-link", encoding="utf-8")
    report_path = tmp_path / "report.json"

    monkeypatch.setattr(
        link_checker, "validate_url", lambda url, retries=2: (False, "Client error (404)")
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "link-checker.py",
            "--root",
            str(tmp_path),
            "--external-only",
            "--json-report",
            str(report_path),
        ],
    )

    link_checker.main()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert len(report) == 1
    assert report[0]["url"] == "https://example.com/dead-link"
    assert report[0]["archive_suggestion"] == (
        "https://web.archive.org/web/*/https://example.com/dead-link"
    )


def test_main_writes_empty_json_report_when_no_warnings(
    monkeypatch, tmp_path, link_checker
) -> None:
    doc = tmp_path / "index.qmd"
    doc.write_text("No links here.", encoding="utf-8")
    report_path = tmp_path / "report.json"

    monkeypatch.setattr(
        "sys.argv",
        [
            "link-checker.py",
            "--root",
            str(tmp_path),
            "--external-only",
            "--json-report",
            str(report_path),
        ],
    )

    link_checker.main()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report == []
