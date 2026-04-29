"""Smoke tests for mypy autofix command entrypoints."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_legacy_mypy_autofix_agent_is_thin() -> None:
    """The workflow-facing script should stay a thin package wrapper."""
    entrypoint = Path("scripts/mypy_autofix_agent.py")
    line_count = len(entrypoint.read_text(encoding="utf-8").splitlines())
    assert line_count <= 80


def test_legacy_mypy_autofix_agent_help() -> None:
    """The workflow-facing script path should remain callable."""
    result = subprocess.run(
        [sys.executable, "scripts/mypy_autofix_agent.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Mypy Autofix Agent" in result.stdout


def test_packaged_mypy_autofix_help() -> None:
    """The packaged module entrypoint should be callable."""
    result = subprocess.run(
        [sys.executable, "-m", "scripts.mypy_autofix", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Mypy Autofix Agent" in result.stdout
