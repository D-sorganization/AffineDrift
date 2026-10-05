"""Governance of the WEB-06.3 Drift vs Control sandbox widget (#4533, ADR 0002).

Python owns the science (``src/affine_control/double_pendulum_affine.py``); the
browser runs a checked JavaScript mirror. These tests keep the parity fixture
current, keep the widget self-hosted and inside its class A budget, and keep it
embedded on theory Part 1 with its exploratory-output label.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from scripts.generate_widget_parity import WIDGETS, fixture_path, render_fixture, stale_fixtures

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLE = REPO_ROOT / "articles" / "theory-part1.qmd"
WIDGET_FILES = (
    REPO_ROOT / "js" / "drift-control-sandbox.js",
    REPO_ROOT / "js" / "drift-control-sandbox-ui.js",
    REPO_ROOT / "css" / "drift-control-sandbox.css",
)
#: ADR 0002 section 2: hosts a widget must never load from.
CDN_HOSTS = ("cdn.jsdelivr.net", "unpkg.com", "cdn.plot.ly", "esm.sh", "cdn.skypack.dev")
#: ADR 0002 section 4, class A ceiling (uncompressed here, so stricter than the table).
CLASS_A_MAX_BYTES = 60 * 1024


def _spec():
    return next(spec for spec in WIDGETS if spec.widget == "drift-control-sandbox")


def test_parity_fixture_is_current() -> None:
    assert stale_fixtures() == [], "run: python -m scripts.generate_widget_parity"


def test_fixture_pins_the_cited_source_digest() -> None:
    spec = _spec()
    fixture = json.loads(fixture_path(spec).read_text(encoding="utf-8"))
    source = REPO_ROOT / spec.source_path
    assert fixture["source_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert fixture["schema"] == "affinedrift/widget-parity/v1"
    assert fixture["tolerance"] == {"abs": 1e-12, "rel": 1e-12}
    integrated = [case for case in fixture["cases"] if case["id"].startswith("preset-")]
    assert integrated and all(c["tolerance"] == {"abs": 1e-9, "rel": 1e-9} for c in integrated)


def test_fixture_pins_every_module_the_js_mirror_ports() -> None:
    spec = _spec()
    fixture = json.loads(fixture_path(spec).read_text(encoding="utf-8"))
    dynamics = "src/affine_control/dynamics.py"
    assert spec.dependency_paths == (dynamics,)
    assert fixture["dependency_sha256"] == {
        dynamics: hashlib.sha256((REPO_ROOT / dynamics).read_bytes()).hexdigest()
    }


def test_render_is_deterministic() -> None:
    assert render_fixture(_spec()) == render_fixture(_spec())


def test_widget_sources_are_self_hosted() -> None:
    for path in WIDGET_FILES:
        text = path.read_text(encoding="utf-8")
        for host in CDN_HOSTS:
            assert host not in text, f"{path.name} references {host}"
        assert not re.search(r"https?://", text), f"{path.name} references a remote URL"


def test_widget_fits_the_class_a_byte_budget() -> None:
    total = sum(path.stat().st_size for path in WIDGET_FILES)
    assert total <= CLASS_A_MAX_BYTES, f"{total} bytes > class A ceiling {CLASS_A_MAX_BYTES}"


def test_js_mirror_cites_every_python_function_it_ports() -> None:
    source = (REPO_ROOT / "js" / "drift-control-sandbox.js").read_text(encoding="utf-8")
    for cited in (
        "dynamics.py::double_pendulum_mass_matrix",
        "dynamics.py::christoffel_coriolis",
        "dynamics.py::double_pendulum_coriolis",
        "dynamics.py::planar_double_pendulum_trajectory",
        "double_pendulum_affine.py::affine_split",
        "double_pendulum_affine.py::grad_potential",
        "double_pendulum_affine.py::generalized_torque",
        "double_pendulum_affine.py::tip_acceleration_split",
        "double_pendulum_affine.py::simulate",
    ):
        assert cited in source, cited


def test_widget_is_embedded_on_theory_part_one_with_its_label() -> None:
    article = ARTICLE.read_text(encoding="utf-8")
    assert 'id="dcsb-app"' in article
    assert '<script src="../js/drift-control-sandbox.js"></script>' in article
    assert '<script src="../js/drift-control-sandbox-ui.js"></script>' in article
    assert '<link rel="stylesheet" href="../css/drift-control-sandbox.css">' in article
    assert "Exploratory model output" in article
    assert 'id="dcsb-data"' in article, "text alternative (data table) is required"
    assert "<noscript>" in article.split('id="dcsb-app"', 1)[1]


def test_article_slider_defaults_match_the_fixture_scenario() -> None:
    article = ARTICLE.read_text(encoding="utf-8")
    fixture = json.loads(fixture_path(_spec()).read_text(encoding="utf-8"))
    preset = next(c for c in fixture["cases"] if c["id"] == "preset-shoulder-drive")["inputs"]
    expected = {
        "dcsb-shoulder": preset["shoulder"],
        "dcsb-wrist": preset["wrist"],
        "dcsb-l1": preset["params"]["l1"],
        "dcsb-l2": preset["params"]["l2"],
        "dcsb-m1": preset["params"]["m1"],
        "dcsb-m2": preset["params"]["m2"],
    }
    for element_id, value in expected.items():
        match = re.search(rf'<input id="{element_id}"[^>]*value="([^"]+)"', article)
        assert match is not None, element_id
        assert float(match.group(1)) == value, element_id
    assert re.search(r'<option value="shoulder-drive" selected>', article)
