"""The vendored GAAI tree is retired and must not return (RM #2725)."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_gaai_tree_and_launcher_are_removed() -> None:
    assert not (REPO_ROOT / ".gaai").exists()
    assert not (REPO_ROOT / "start-gaai-daemon.sh").exists()
