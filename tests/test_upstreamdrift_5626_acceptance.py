"""End-to-end acceptance checks for AffineDrift #5626 (issue close-out).

The guides, companion pin refresh, and CI gates landed across #5663, #5686,
#5732, and #5756. This module bundles the four public acceptance bullets so a
single pytest target proves they still hold on the branch under review.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

GATE_MODULES = (
    "scripts.check_upstreamdrift_install_docs",
    "scripts.check_upstreamdrift_readme_parity",
    "scripts.check_upstreamdrift_headless_docs",
    "scripts.check_companion_launcher_freshness",
)

GUIDE_PAGES = (
    ROOT / "pages/upstreamdrift-getting-started.qmd",
    ROOT / "pages/upstreamdrift-headless-and-agents.qmd",
)
CATALOG_PAGE = ROOT / "models/programming/programs.qmd"
ACTIVE_LOCK = ROOT / "data/companion/active-lock.json"


@pytest.mark.integration
@pytest.mark.parametrize("module", GATE_MODULES)
def test_5626_ci_gate_module_exits_zero(module: str) -> None:
    """Each #5626 gate script must pass when invoked like CI."""
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
def test_5626_publishable_guides_exist() -> None:
    for path in GUIDE_PAGES:
        assert path.is_file(), f"missing guide page: {path.as_posix()}"


@pytest.mark.unit
def test_5626_program_catalog_names_active_provider_commit() -> None:
    lock = json.loads(ACTIVE_LOCK.read_text(encoding="utf-8"))
    commit = lock["provider"]["commit"]
    assert isinstance(commit, str) and len(commit) == 40
    catalog_text = CATALOG_PAGE.read_text(encoding="utf-8")
    assert (
        commit[:12] in catalog_text
    ), "programs.qmd must cite the active companion pin for catalog regeneration"


@pytest.mark.unit
def test_5626_llms_txt_advertises_install_and_headless_guides() -> None:
    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "upstreamdrift-getting-started" in llms
    assert "upstreamdrift-headless-and-agents" in llms
    assert "ud-sim" in llms


@pytest.mark.unit
def test_5626_evidence_manifest_lists_gates() -> None:
    """Evidence JSON under tests/evidence/ anchors #5626 close-out for audits."""
    path = ROOT / "tests/evidence/5626-upstreamdrift-guides.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    gates = payload["acceptance"]["install_readme_parity"]
    assert "scripts.check_upstreamdrift_readme_parity" in gates
