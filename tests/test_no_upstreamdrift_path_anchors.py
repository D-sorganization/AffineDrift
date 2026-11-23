"""Guard against placeholder path_anchors_* directories (#5624 cleanup)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAMDRIFT_DATA = ROOT / "data" / "upstreamdrift"


def test_no_path_anchors_directories_remain() -> None:
    """Anti-phantom placeholder dirs must not persist after #5624 close-out."""
    if not UPSTREAMDRIFT_DATA.is_dir():
        return
    offenders = sorted(
        p.name
        for p in UPSTREAMDRIFT_DATA.iterdir()
        if p.is_dir() and p.name.startswith("path_anchors_")
    )
    assert offenders == [], f"remove placeholder directories: {offenders}"
