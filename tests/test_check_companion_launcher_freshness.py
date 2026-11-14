"""Tests for scripts/check_companion_launcher_freshness.py."""

from __future__ import annotations

import pytest

from scripts.check_companion_launcher_freshness import (
    active_provider_commit,
    companion_program_ids,
    launcher_tile_ids,
    main,
)


@pytest.mark.unit
def test_active_pin_covers_launcher_tiles_at_same_commit() -> None:
    commit = active_provider_commit()
    missing = launcher_tile_ids(commit) - companion_program_ids(commit)
    assert not missing, f"missing tiles: {sorted(missing)[:5]}"


@pytest.mark.unit
@pytest.mark.integration
def test_main_passes_on_repo_pin() -> None:
    assert main([]) == 0
