"""Tests for URL stability / redirect-policy enforcement (#4503).

A previously published route must either still be published or be
documented in the ``config/redirects.yml`` ledger with evidence that the
alias was actually rendered. See ``src/tools/check_redirects.py``.
"""

import json
from pathlib import Path

import pytest

from src.core.contracts import PreconditionError
from src.tools.check_redirects import (
    find_unredirected_removed_routes,
    load_redirect_ledger,
    main,
    manifest_routes,
    verify_redirect_targets_rendered,
)

ROOT_DIR = Path(__file__).parent.parent


def _manifest(*routes: str) -> dict:
    return {"pages": [{"route": route} for route in routes]}


def test_contributing_documents_the_redirect_ledger() -> None:
    """The redirect ledger must be documented in CONTRIBUTING.md (#4503)."""
    content = (ROOT_DIR / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "config/redirects.yml" in content
    assert "aliases:" in content


def test_manifest_routes_extracts_route_set() -> None:
    """The route set is derived from each page's ``route`` field."""
    manifest = _manifest("/", "/articles/foo.html")
    assert manifest_routes(manifest) == {"/", "/articles/foo.html"}


def test_load_redirect_ledger_missing_file_returns_empty(tmp_path: Path) -> None:
    """A ledger that does not exist yet (no redirects recorded) is empty."""
    assert load_redirect_ledger(tmp_path / "missing.yml") == {}


def test_load_redirect_ledger_parses_entries(tmp_path: Path) -> None:
    """Ledger entries map the old route to the new route."""
    ledger = tmp_path / "redirects.yml"
    ledger.write_text(
        "redirects:\n"
        "  - from: /articles/old-name.html\n"
        "    to: /articles/new-name.html\n"
        "    issue: '#4505'\n"
        "    since: '2026-09-29'\n",
        encoding="utf-8",
    )
    assert load_redirect_ledger(ledger) == {"/articles/old-name.html": "/articles/new-name.html"}


def test_load_redirect_ledger_rejects_entry_missing_to(tmp_path: Path) -> None:
    """A malformed ledger entry (missing ``to``) fails loudly, not silently."""
    ledger = tmp_path / "redirects.yml"
    ledger.write_text("redirects:\n  - from: /old.html\n", encoding="utf-8")
    with pytest.raises(PreconditionError):
        load_redirect_ledger(ledger)


def test_find_unredirected_removed_routes_flags_route_without_redirect() -> None:
    """A route dropped between deploys with no ledger entry must be flagged."""
    previous = _manifest("/", "/articles/gone.html")
    current = _manifest("/")
    assert find_unredirected_removed_routes(previous, current, {}) == ["/articles/gone.html"]


def test_find_unredirected_removed_routes_allows_documented_redirect() -> None:
    """A dropped route with a matching ledger entry is not flagged."""
    previous = _manifest("/", "/articles/old-name.html")
    current = _manifest("/")
    redirects = {"/articles/old-name.html": "/articles/new-name.html"}
    assert find_unredirected_removed_routes(previous, current, redirects) == []


def test_find_unredirected_removed_routes_ignores_still_published_routes() -> None:
    """Routes present in both manifests are never flagged."""
    previous = _manifest("/", "/articles/stable.html")
    current = _manifest("/", "/articles/stable.html")
    assert find_unredirected_removed_routes(previous, current, {}) == []


def test_verify_redirect_targets_rendered_accepts_existing_alias_output(
    tmp_path: Path,
) -> None:
    """A ledger entry is only trusted once Quarto actually rendered the alias."""
    docs_dir = tmp_path / "docs" / "articles"
    docs_dir.mkdir(parents=True)
    (docs_dir / "old-name.html").write_text("<html></html>", encoding="utf-8")

    redirects = {"/articles/old-name.html": "/articles/new-name.html"}
    assert verify_redirect_targets_rendered(redirects, tmp_path / "docs") == []


def test_verify_redirect_targets_rendered_flags_missing_alias_output(
    tmp_path: Path,
) -> None:
    """A ledger entry with no rendered file means the alias never took effect."""
    (tmp_path / "docs").mkdir()
    redirects = {"/articles/old-name.html": "/articles/new-name.html"}
    assert verify_redirect_targets_rendered(redirects, tmp_path / "docs") == [
        "/articles/old-name.html"
    ]


def test_main_fails_when_route_removed_without_redirect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The CLI exits non-zero when a route vanished with no redirect ledger entry."""
    previous_path = tmp_path / "previous.json"
    current_path = tmp_path / "current.json"
    previous_path.write_text(json.dumps(_manifest("/", "/gone.html")), encoding="utf-8")
    current_path.write_text(json.dumps(_manifest("/")), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "check_redirects",
            "--previous-manifest",
            str(previous_path),
            "--current-manifest",
            str(current_path),
            "--redirects",
            str(tmp_path / "no-such-redirects.yml"),
        ],
    )
    assert main() == 1


def test_main_passes_when_removed_route_has_verified_redirect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The CLI succeeds when a removed route has a redirect with rendered output."""
    previous_path = tmp_path / "previous.json"
    current_path = tmp_path / "current.json"
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "old.html").write_text("<html></html>", encoding="utf-8")
    redirects_path = tmp_path / "redirects.yml"
    redirects_path.write_text(
        "redirects:\n  - from: /old.html\n    to: /new.html\n", encoding="utf-8"
    )
    previous_path.write_text(json.dumps(_manifest("/", "/old.html")), encoding="utf-8")
    current_path.write_text(json.dumps(_manifest("/", "/new.html")), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "check_redirects",
            "--previous-manifest",
            str(previous_path),
            "--current-manifest",
            str(current_path),
            "--redirects",
            str(redirects_path),
            "--docs-dir",
            str(docs_dir),
        ],
    )
    assert main() == 0


def test_main_skips_comparison_when_previous_manifest_is_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A missing previous manifest (first deploy, unreachable fetch) does not fail the build."""
    current_path = tmp_path / "current.json"
    current_path.write_text(json.dumps(_manifest("/")), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "check_redirects",
            "--previous-manifest",
            str(tmp_path / "missing-previous.json"),
            "--current-manifest",
            str(current_path),
            "--redirects",
            str(tmp_path / "missing-redirects.yml"),
        ],
    )
    assert main() == 0


def test_main_skips_comparison_when_previous_manifest_is_not_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An HTML error page saved as the previous manifest skips the check instead of crashing."""
    previous_path = tmp_path / "previous.json"
    previous_path.write_text("<html><body>404 Not Found</body></html>", encoding="utf-8")
    current_path = tmp_path / "current.json"
    current_path.write_text(json.dumps(_manifest("/")), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "check_redirects",
            "--previous-manifest",
            str(previous_path),
            "--current-manifest",
            str(current_path),
            "--redirects",
            str(tmp_path / "missing-redirects.yml"),
        ],
    )
    assert main() == 0
