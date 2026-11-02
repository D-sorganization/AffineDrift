"""Config contract for mobile layout audit routes (#5313)."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONFIG = REPO / "config" / "mobile-layout-audit-routes.json"
SMOKE_SPEC = REPO / "tests" / "e2e" / "mobile-smoke.spec.js"
LIGHTHOUSE = REPO / "config" / "lighthouserc.json"
_ROUTE_RE = re.compile(r"'(/[^']*)'")


def _smoke_routes() -> set[str]:
    block = SMOKE_SPEC.read_text(encoding="utf-8").split("const ROUTES = [", maxsplit=1)[1]
    block = block.split("];", maxsplit=1)[0]
    return set(_ROUTE_RE.findall(block))


def test_mobile_audit_routes_config_is_valid() -> None:
    """Audit manifest lists phone viewports and public HTML routes (#5313)."""
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    assert data["routes"]
    for route in data["routes"]:
        assert route.startswith("/")
        if route != "/":
            assert route.endswith(".html")
    assert len(data["viewports"]) >= 2
    for viewport in data["viewports"]:
        assert viewport["width"] >= 360
        assert viewport["height"] >= 800


def test_mobile_smoke_routes_match_audit_manifest() -> None:
    """E2E smoke and the audit manifest stay aligned (#5313)."""
    manifest = set(json.loads(CONFIG.read_text(encoding="utf-8"))["routes"])
    assert _smoke_routes() == manifest


def test_lighthouse_mobile_urls_match_audit_manifest() -> None:
    """Nightly Lighthouse mobile URLs match the audit route set (#5313)."""
    manifest = set(json.loads(CONFIG.read_text(encoding="utf-8"))["routes"])
    lh = json.loads(LIGHTHOUSE.read_text(encoding="utf-8"))
    paths = {
        url.replace("http://127.0.0.1:8080", "").replace("http://localhost:8000", "")
        for url in lh["ci"]["collect"]["url"]
    }
    assert paths == manifest
