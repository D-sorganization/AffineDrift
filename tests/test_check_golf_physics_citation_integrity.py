"""Tests for scripts/check_golf_physics_citation_integrity.py."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_cli_passes_on_repository_tree() -> None:
    repo = Path(__file__).resolve().parents[1]
    script = repo / "scripts" / "check_golf_physics_citation_integrity.py"
    env = {**os.environ, "PYTHONPATH": str(repo)}
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=repo,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "passed" in completed.stdout.lower()
