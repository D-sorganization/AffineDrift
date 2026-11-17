"""Config contract for the phone layout audit route manifest (#5313)."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONFIG = REPO / "config" / "mobile-layout-audit-routes.json"
SMOKE_SPEC = REPO / "tests" / "e2e" / "mobile-smoke.spec.js"
LIGHTHOUSE = REPO / "config" / "lighthouserc.json"


def _manifest() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def _source_for(route: str) -> Path:
    stem = "index" if route == "/" else route.lstrip("/").removesuffix(".html")
    return REPO / f"{stem}.qmd"


def test_manifest_lists_phone_viewports_and_html_routes() -> None:
    """The manifest names iPhone and Android phone viewports and public HTML routes."""
    data = _manifest()
    labels = {viewport["label"] for viewport in data["viewports"]}
    assert {"iphone", "android-narrow"} <= labels
    for viewport in data["viewports"]:
        assert 360 <= viewport["width"] <= 430
        assert viewport["height"] >= 800
    assert data["routes"]
    for route in data["routes"]:
        assert route == "/" or (route.startswith("/") and route.endswith(".html")), route


def test_every_manifest_route_has_a_source_page() -> None:
    """A route without a Quarto source would 404 in the smoke run."""
    missing = [route for route in _manifest()["routes"] if not _source_for(route).is_file()]
    assert missing == []


def test_smoke_spec_reads_routes_and_viewports_from_the_manifest() -> None:
    """The Playwright smoke spec drives every manifest viewport, so the two cannot drift."""
    spec = SMOKE_SPEC.read_text(encoding="utf-8")
    assert "config/mobile-layout-audit-routes.json" in spec
    assert "const ROUTES = [" not in spec
    assert "audit.viewports" in spec


def test_lighthouse_mobile_urls_match_the_manifest() -> None:
    """Nightly Lighthouse mobile URLs audit the same route set."""
    lighthouse = json.loads(LIGHTHOUSE.read_text(encoding="utf-8"))
    paths = {
        url.removeprefix("http://localhost:8000") for url in lighthouse["ci"]["collect"]["url"]
    }
    assert paths == set(_manifest()["routes"])
