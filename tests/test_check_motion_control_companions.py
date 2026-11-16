"""Unit tests for scripts.check_motion_control_companions (#5615)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_motion_control_companions import (
    check_motion_control_companions,
    main,
)

ROOT = Path(__file__).resolve().parents[1]
MOTION = ROOT / "articles" / "motion-control"


def _write(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_check_passes_on_current_motion_control_tree() -> None:
    assert check_motion_control_companions(MOTION) == []


def test_check_flags_removed_jsx_companion(tmp_path: Path) -> None:
    motion = tmp_path / "motion-control"
    motion.mkdir()
    _write(motion / "chapter2_artifact.jsx", "export default function X() { return null; }")
    violations = check_motion_control_companions(motion)
    assert any("chapter2_artifact.jsx" in item for item in violations)


def test_check_flags_forbidden_jsx_extension(tmp_path: Path) -> None:
    motion = tmp_path / "motion-control"
    motion.mkdir()
    _write(motion / "fresh_companion.jsx")
    violations = check_motion_control_companions(motion)
    assert any("fresh_companion.jsx" in item for item in violations)


def test_check_flags_contradiction_markers_in_companion_md(tmp_path: Path) -> None:
    motion = tmp_path / "motion-control"
    motion.mkdir()
    _write(
        motion / "notes.md",
        "Stability: asymptotically orbitally stable if and only if the transverse map is stable.\n",
    )
    violations = check_motion_control_companions(motion)
    assert any("contradiction marker" in item for item in violations)


def test_check_flags_stale_summary_overclaims(tmp_path: Path) -> None:
    motion = tmp_path / "motion-control"
    motion.mkdir()
    _write(motion / "BOOK_SUMMARY.md", "# Summary\n\nThrowing Away the Target\n")
    violations = check_motion_control_companions(motion)
    assert any("BOOK_SUMMARY" in item for item in violations)


def test_main_exits_nonzero_when_violations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    motion = tmp_path / "motion-control"
    motion.mkdir()
    _write(motion / "chapter4_artifact.jsx")
    monkeypatch.setattr(
        "scripts.check_motion_control_companions.DEFAULT_MOTION_DIR",
        motion,
    )
    assert main([]) == 1
