"""Guard against drift between the program registry and hub card counts (#5617)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.affine_control.programming_companion.catalog_counts import (
    committed_program_hub_counts,
    committed_program_registry_count,
)

ROOT = Path(__file__).resolve().parents[1]
PROGRAMMING_DIR = ROOT / "models" / "programming"
INDEX_QMD = PROGRAMMING_DIR / "index.qmd"
PROGRAMS_QMD = PROGRAMMING_DIR / "programs.qmd"
ON_RAMP_PATHS_QMD = ROOT / "resources" / "on-ramp-paths.qmd"


@pytest.mark.unit
def test_program_registry_and_hub_card_counts_match() -> None:
    """Hub card copy must match the programs registry table and headings."""
    registry_count = committed_program_registry_count(PROGRAMS_QMD.read_text(encoding="utf-8"))
    title_count, blurb_count = committed_program_hub_counts(INDEX_QMD.read_text(encoding="utf-8"))
    assert title_count == registry_count
    assert blurb_count == registry_count


@pytest.mark.unit
def test_on_ramp_paths_uses_the_live_program_registry_count() -> None:
    """On-ramp self-check copy must track the registry, not a stale hard-coded total."""
    registry_count = committed_program_registry_count(PROGRAMS_QMD.read_text(encoding="utf-8"))
    on_ramp = ON_RAMP_PATHS_QMD.read_text(encoding="utf-8")
    matches = [int(value) for value in re.findall(r"from the (\d+)-record directory", on_ramp)]
    assert matches, "on-ramp paths must mention the program directory size"
    assert len(matches) == 1
    assert matches[0] == registry_count
