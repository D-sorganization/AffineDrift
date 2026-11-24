"""Bundled acceptance checks for issue #5590 (close-out lane)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_core_theory_figure_provenance import run_checks

REPO_ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = REPO_ROOT / "tests/evidence/5590-core-theory-figures.json"


def test_issue_5590_provenance_check_script_passes() -> None:
    """Standalone provenance gate must pass (no matplotlib required)."""
    assert run_checks() == []


def test_issue_5590_provenance_cli_exit_zero() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "scripts.check_core_theory_figure_provenance"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_issue_5590_evidence_bundle_lists_pins_and_generators() -> None:
    assert EVIDENCE.is_file(), "Missing acceptance evidence bundle"
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert payload.get("issue") == 5590
    pins = payload.get("pin_records", [])
    assert "data/core_theory/ztcf_figure_run_v1.json" in pins
    gens = payload.get("generator_modules", [])
    assert "scripts/core_theory_figures/ztcf.py" in gens
    assert payload.get("model_ladder_f15") is True
