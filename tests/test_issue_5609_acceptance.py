"""Bundled acceptance checks for issue #5609 (lay companion pin and links close-out)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "tests/evidence/5609-proximal-distal-companion.json"
PIN = ROOT / "data/companion/proximal_distal_companion_upstream_pin.json"


def test_issue_5609_upstream_pin_gate_passes_without_remote_roundtrip() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/check_proximal_distal_companion_upstream_pins.py",
            "--no-verify-remotes",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_issue_5609_evidence_bundle_records_pin_and_guards() -> None:
    assert EVIDENCE.is_file()
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert payload.get("issue") == 5609
    pin_commit = json.loads(PIN.read_text(encoding="utf-8"))["commit"]
    assert payload.get("companion_upstream_commit") == pin_commit
    assert payload.get("pin_check") == "scripts/check_proximal_distal_companion_upstream_pins.py"
    assert "tests/test_proximal_distal_companion_5609.py" in payload.get("regression_modules", [])
