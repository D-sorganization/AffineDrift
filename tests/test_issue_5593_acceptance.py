"""Bundled acceptance checks for issue #5593 frame and convention pinning."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "tests/evidence/5593-frame-conventions.json"


def test_issue_5593_site_frame_gate_passes() -> None:
    proc = subprocess.run(
        [sys.executable, "scripts/check_site_frame_conventions.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_issue_5593_evidence_bundle_records_gate() -> None:
    assert EVIDENCE.is_file()
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert payload.get("issue") == 5593
    assert payload.get("pin_check") == "scripts/check_site_frame_conventions.py"
    assert "tests/test_frames_conventions_5593.py" in payload.get("regression_modules", [])


def test_issue_5593_agent_registry_includes_y_up_frame() -> None:
    conventions = json.loads((ROOT / "data/agent/conventions.json").read_text(encoding="utf-8"))
    ids = {row["id"] for row in conventions["conventions"]}
    assert "y-up-impact-target-frame" in ids
