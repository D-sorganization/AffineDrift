"""Issue #5627: WEB-06.3 sandbox club defaults and signature graphic caption."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from scripts.generate_signature_graphic import INCLUDE_PATH, build_scene, long_description
from src.affine_control.double_pendulum_affine import SANDBOX_DEFAULT_PARAMS

REPO = Path(__file__).resolve().parents[1]
PARITY = REPO / "tests/fixtures/widgets/drift-control-sandbox.parity.json"


def test_sandbox_default_params_use_a_realistic_club() -> None:
    """Club mass, COM along link 2, and rotary inertia match a driver-scale payload."""
    params = SANDBOX_DEFAULT_PARAMS
    assert 0.30 <= params.m2 <= 0.35
    assert 0.75 <= params.l_c2 <= 0.88
    assert params.I_c2 > 0.0


def test_parity_fixture_pins_the_same_club_defaults() -> None:
    fixture = json.loads(PARITY.read_text(encoding="utf-8"))
    preset = next(case for case in fixture["cases"] if case["id"] == "preset-shoulder-drive")
    params = preset["inputs"]["params"]
    assert params["m2"] == pytest.approx(SANDBOX_DEFAULT_PARAMS.m2)
    assert params["l_c2"] == pytest.approx(SANDBOX_DEFAULT_PARAMS.l_c2)
    assert params["I_c2"] == pytest.approx(SANDBOX_DEFAULT_PARAMS.I_c2)


def test_hero_long_description_states_units_and_scaled_tangent_arrows() -> None:
    scene = build_scene()
    text = long_description(scene)
    assert "rad/s" in text and "rad/s²" in text
    assert re.search(r"three arrows show the change over", text, re.I) is None
    assert re.search(r"scaled by .+ for visibility", text, re.I) is not None
    include = (REPO / INCLUDE_PATH).read_text(encoding="utf-8")
    assert re.search(r"three arrows show the change over", include, re.I) is None


def test_theory_part_one_sandbox_slider_default_matches_fixture() -> None:
    article = (REPO / "articles/theory-part1.qmd").read_text(encoding="utf-8")
    match = re.search(r'<input id="dcsb-m2"[^>]*value="([^"]+)"', article)
    assert match is not None
    assert float(match.group(1)) == pytest.approx(SANDBOX_DEFAULT_PARAMS.m2)
