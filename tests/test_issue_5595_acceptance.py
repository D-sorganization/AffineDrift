"""Regression guards for #5595 canonical parameters SSOT on main."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARAMETERS_MD = ROOT / "PARAMETERS.md"
CANONICAL_JSON = ROOT / "data/canonical_parameters.json"
PARAMETERS_PAGE = ROOT / "pages/parameters.qmd"

STALE_MARKERS = (
    "Ch 10-12",
    "Ch 1-31",
    "Vol 0-1",
    "m or M",
    "0.78 - 0.83",
)


def test_parameters_md_is_generated_from_canonical_json() -> None:
    text = PARAMETERS_MD.read_text(encoding="utf-8")
    assert "scripts/check_parameters.py" in text
    assert "data/canonical_parameters.json" in text
    assert "ch01" in text and "ch32" in text
    for marker in STALE_MARKERS:
        assert marker not in text


def test_parameters_page_points_agents_at_json_source() -> None:
    text = PARAMETERS_PAGE.read_text(encoding="utf-8")
    assert "data/canonical_parameters.json" in text


def test_check_parameters_script_exits_zero() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "scripts.check_parameters"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert CANONICAL_JSON.is_file()