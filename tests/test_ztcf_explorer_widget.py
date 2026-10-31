"""Governance of the WEB-06.4 ZTCF counterfactual explorer widget (#4534, ADR 0002).

Python owns the science (``src/affine_control/ztcf_explorer.py``); the browser
runs a checked JavaScript mirror. These tests pin the parity fixture to every
ported module and the registered ZTCF record, keep the widget self-hosted and
inside its class A budget, and keep the embedded provenance, caveats and
critique links in step with their sources of truth.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from scripts.generate_widget_parity import WIDGETS, fixture_path
from src.affine_control.ztcf_explorer import (
    DECLARED_TORQUE,
    FIXTURE_PATH,
    HORIZON,
    STEPS,
    load_fixture,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLE_PATH = "articles/zero-torque-counterfactual.qmd"
ARTICLE = REPO_ROOT / ARTICLE_PATH
LEDGER = REPO_ROOT / "data" / "trust" / "claim_critique_ledger.json"
WIDGET_FILES = (
    REPO_ROOT / "js" / "ztcf-explorer.js",
    REPO_ROOT / "js" / "ztcf-explorer-ui.js",
    REPO_ROOT / "css" / "ztcf-explorer.css",
)
#: ADR 0002 section 4, class A ceiling (uncompressed here, so stricter than the table).
CLASS_A_MAX_BYTES = 60 * 1024


def _spec():
    return next(spec for spec in WIDGETS if spec.widget == "ztcf-explorer")


def _widget_block() -> str:
    article = ARTICLE.read_text(encoding="utf-8")
    start = article.index('<div id="ztx-app">')
    return article[start : article.index('<script src="../js/ztcf-explorer.js">', start)]


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_fixture_pins_every_ported_module_and_the_registered_record() -> None:
    spec = _spec()
    fixture = json.loads(fixture_path(spec).read_text(encoding="utf-8"))
    assert fixture["source_sha256"] == _digest(REPO_ROOT / spec.source_path)
    assert set(fixture["dependency_sha256"]) == {
        "src/affine_control/golf_model.py",
        "src/affine_control/dynamics.py",
        "src/affine_control/ztcf_contract.py",
        "data/ztcf/planar_golf_forward_fixture_v2.json",
    }
    for path, digest in fixture["dependency_sha256"].items():
        assert digest == _digest(REPO_ROOT / path), path
    assert all(case["tolerance"] == {"abs": 1e-9, "rel": 1e-9} for case in fixture["cases"])


def test_widget_sources_are_self_hosted() -> None:
    for path in WIDGET_FILES:
        assert not re.search(r"https?://", path.read_text(encoding="utf-8")), path.name


def test_widget_fits_the_class_a_byte_budget() -> None:
    total = sum(path.stat().st_size for path in WIDGET_FILES)
    assert total <= CLASS_A_MAX_BYTES, f"{total} bytes > class A ceiling {CLASS_A_MAX_BYTES}"


def test_js_mirror_cites_every_python_function_it_ports() -> None:
    source = (REPO_ROOT / "js" / "ztcf-explorer.js").read_text(encoding="utf-8")
    for cited in (
        "golf_model.py::GolfModel",
        "GolfModel.com_jacobian",
        "GolfModel.rigid_mass_matrix",
        "GolfModel.potential_energy",
        "GolfModel.gravity_torque",
        "GolfModel.drift_acceleration",
        "GolfModel.clubhead_speed",
        "GolfModel.ztcf_trajectory",
        "dynamics.py::christoffel_coriolis",
        "ztcf_explorer.py::actual_trajectory",
        "ztcf_explorer.py::explore",
    ):
        assert cited in source, cited


def test_js_defaults_match_the_declared_scenario() -> None:
    source = (REPO_ROOT / "js" / "ztcf-explorer.js").read_text(encoding="utf-8")
    torque = ", ".join(f"{value:.1f}" for value in DECLARED_TORQUE)
    assert f"torque: [{torque}]" in source
    assert f"horizon: {HORIZON}," in source
    assert f"steps: {STEPS}," in source


def test_widget_is_embedded_on_the_ztcf_page_with_its_label() -> None:
    article = ARTICLE.read_text(encoding="utf-8")
    block = _widget_block()
    assert "Exploratory model output" in block
    assert 'id="ztx-data"' in block, "text alternative (data table) is required"
    assert "<noscript>" in block
    assert '<script src="../js/ztcf-explorer-ui.js"></script>' in article
    assert "  - ../css/ztcf-explorer.css" in article
    slider = re.search(r'<input id="ztx-step"[^>]*>', block)
    assert slider is not None
    assert f'max="{STEPS - 1}"' in slider.group(0)


def test_displayed_fixture_digest_is_the_registered_record() -> None:
    match = re.search(r'<code id="ztx-fixture-sha256">([0-9a-f]{64})</code>', _widget_block())
    assert match is not None
    assert match.group(1) == _digest(FIXTURE_PATH)
    assert FIXTURE_PATH.relative_to(REPO_ROOT).as_posix() in _widget_block()


def test_widget_states_the_fixture_non_identifiability_caveats() -> None:
    block = _widget_block()
    for item in load_fixture().interpretation.non_identifiability:
        assert f"<li>{item}</li>" in block, item


def test_widget_links_every_ledger_critique_of_the_page() -> None:
    critiques = json.loads(LEDGER.read_text(encoding="utf-8"))["critiques"]
    affecting = [c for c in critiques if ARTICLE_PATH in c["affected_pages"]]
    assert any(c["critique_id"] == "crit-ztcf-identifiability" for c in affecting)
    block = _widget_block()
    for critique in affecting:
        href = "../" + critique["source_path"].removesuffix(".md") + ".html"
        assert f'href="{href}"' in block, critique["critique_id"]
