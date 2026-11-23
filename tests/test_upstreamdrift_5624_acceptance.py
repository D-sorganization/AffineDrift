"""End-to-end acceptance checks for AffineDrift #5624 (issue close-out).

Inventory prose, PARAMETERS crosswalk, and CI gates landed in #5664 and #5758.
This module bundles the three public acceptance bullets for merge verification.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

GATE_MODULES = (
    "scripts.check_upstreamdrift_physics_models",
    "scripts.check_parameters",
)

INVENTORY = ROOT / "articles/upstreamdrift-physics-models.qmd"
PARAMETERS = ROOT / "PARAMETERS.md"
CONTRACT = ROOT / "data/upstreamdrift/physics_models_contract.json"
MANIFEST = ROOT / "data/agent/canonical_pages.json"


@pytest.mark.integration
@pytest.mark.parametrize("module", GATE_MODULES)
def test_5624_ci_gate_module_exits_zero(module: str) -> None:
    completed = subprocess.run(
        [sys.executable, "-m", module],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert (
        completed.returncode == 0
    ), f"{module} failed:\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"


@pytest.mark.unit
def test_5624_inventory_covers_four_model_families() -> None:
    text = INVENTORY.read_text(encoding="utf-8")
    for heading in (
        "## Putting and Green Simulation",
        "## Ball Flight and Atmosphere",
        "## Impact and Gear Effect",
        "## Injury Screening Module",
    ):
        assert heading in text, f"inventory missing section: {heading}"


@pytest.mark.unit
def test_5624_mismatch_flags_link_trackers() -> None:
    text = INVENTORY.read_text(encoding="utf-8")
    assert "MISMATCH (G2)" in text
    assert "MISMATCH (G4" in text
    assert "MISMATCH (G11)" in text
    assert "#15010" in text and "#15011" in text


@pytest.mark.unit
def test_5624_parameters_crosswalk_lists_upstream_defaults() -> None:
    text = PARAMETERS.read_text(encoding="utf-8")
    assert "UpstreamDrift" in text
    assert "SPIN_DECAY_RATE_S" in text
    assert "HOLE_RADIUS_M" in text
    assert "articles/upstreamdrift-physics-models" in text


@pytest.mark.unit
def test_5624_agent_discovery_lists_physics_inventory() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    paths = [page["path"] for section in manifest["sections"] for page in section["pages"]]
    assert "/articles/upstreamdrift-physics-models.html" in paths
    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "upstreamdrift-physics-models" in llms


@pytest.mark.unit
def test_5624_evidence_manifest_lists_contract() -> None:
    path = ROOT / "tests/evidence/5624-upstreamdrift-physics.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["contract"] == "data/upstreamdrift/physics_models_contract.json"
