"""Governance of the rotation-converter widget (#4127, ADR 0002).

Python reference (``src/tools/rotation_reference_examples.py``) mirrors the canonical
Tools algorithms (``Tools/src/rotation_converter/``); the browser runs ``js/rotation-converter.js``.
These tests verify that the parity fixture is current and deterministic, pins the cited
source digest, and respects self-hosting requirements.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.generate_widget_parity import (
    WIDGETS,
    WidgetSpec,
    fixture_path,
    render_fixture,
    stale_fixtures,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
WIDGET_FILE = REPO_ROOT / "js" / "rotation-converter.js"
CDN_HOSTS = ("cdn.jsdelivr.net", "unpkg.com", "cdn.plot.ly", "esm.sh", "cdn.skypack.dev")


def _spec() -> WidgetSpec:
    return next(spec for spec in WIDGETS if spec.widget == "rotation-converter")


def test_parity_fixture_is_current() -> None:
    assert stale_fixtures() == [], "run: python -m scripts.generate_widget_parity"


def test_fixture_pins_the_cited_source_digest() -> None:
    spec = _spec()
    fixture = json.loads(fixture_path(spec).read_text(encoding="utf-8"))
    source = REPO_ROOT / spec.source_path
    assert fixture["source_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert fixture["schema"] == "affinedrift/widget-parity/v1"
    assert fixture["tolerance"] == {"abs": 1e-12, "rel": 1e-12}


def test_fixture_pins_every_module_the_js_mirror_ports() -> None:
    spec = _spec()
    fixture = json.loads(fixture_path(spec).read_text(encoding="utf-8"))
    for dep in spec.dependency_paths:
        assert dep in fixture["dependency_sha256"]
        dep_path = REPO_ROOT / dep
        assert (
            fixture["dependency_sha256"][dep] == hashlib.sha256(dep_path.read_bytes()).hexdigest()
        )


def test_render_is_deterministic() -> None:
    assert render_fixture(_spec()) == render_fixture(_spec())


def test_widget_sources_are_self_hosted() -> None:
    text = WIDGET_FILE.read_text(encoding="utf-8")
    for host in CDN_HOSTS:
        assert host not in text, f"{WIDGET_FILE.name} references {host}"
    assert (
        "http://" not in text and "https://" not in text
    ), f"{WIDGET_FILE.name} references a remote URL"
