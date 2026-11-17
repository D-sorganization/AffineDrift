"""Publication contract for the UpstreamDrift capture-to-model pipeline page (#5623)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "pages/upstreamdrift-capture-to-model-pipeline.qmd"
PINNED_COMMIT = "3afe09c1ed0247a459d16bf75cf0b28bb64f584a"


@pytest.fixture(scope="module")
def page_text() -> str:
    assert PAGE.is_file(), f"missing reference page: {PAGE}"
    return PAGE.read_text(encoding="utf-8")


def test_page_pins_upstreamdrift_commit(page_text: str) -> None:
    assert PINNED_COMMIT in page_text


def test_page_documents_bundle_defaults(page_text: str) -> None:
    required = (
        "sigma_px",
        "sigma_bone_m",
        "sigma_prior_m",
        "sigma_symmetry_m",
        "sigma_anchor_m",
        "gate_px",
        "6.0 px",
        "bundle.py",
    )
    missing = [token for token in required if token not in page_text]
    assert not missing, f"missing bundle documentation tokens: {missing}"


def test_page_links_core_motion_capture_modules(page_text: str) -> None:
    modules = (
        "motion_capture/reconstruct/bundle.py",
        "motion_capture/reconstruct/geometry.py",
        "motion_capture/reconstruct/temporal.py",
        "motion_capture/rig/__main__.py",
        "humanoid_character_builder/core/anthropometry.py",
    )
    for module in modules:
        assert module in page_text, f"expected link or path for {module}"


def test_page_lists_cli_and_artifacts(page_text: str) -> None:
    assert "motion_capture.reconstruct synth" in page_text
    assert "joints_3d_m.npy" in page_text
    assert "reconstruction.json" in page_text


def test_title_uses_title_case(page_text: str) -> None:
    title_match = re.search(r'^title:\s*"([^"]+)"', page_text, re.MULTILINE)
    assert title_match, "title front matter missing"
    title = title_match.group(1)
    assert title == "UpstreamDrift Capture-to-Model Pipeline"
