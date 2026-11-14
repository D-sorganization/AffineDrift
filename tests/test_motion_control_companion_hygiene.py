"""Guardrails for motion-control companion files (issue #5615)."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MOTION_CONTROL = ROOT / "articles" / "motion-control"

REMOVED_COMPANIONS = (
    "chapter2_artifact.jsx",
    "chapter3_artifact.jsx",
    "chapter4_artifact.jsx",
    "Book Expansion and Writing.md",
)

_SCAN_ROOTS = (
    ROOT / "articles",
    ROOT / "tests",
    ROOT / "docs",
    ROOT / "research",
    ROOT / "scripts",
)
_SKIP_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pyc", ".zip"}


def test_removed_jsx_and_transcript_companions_are_absent() -> None:
    for name in REMOVED_COMPANIONS:
        assert not (MOTION_CONTROL / name).exists(), f"stale companion still present: {name}"


def test_book_summary_matches_rewritten_scope() -> None:
    text = (MOTION_CONTROL / "BOOK_SUMMARY.md").read_text(encoding="utf-8")
    for phrase in (
        "Throwing Away the Target",
        "15-DOF musculoskeletal",
        "revolutionary framework",
        "first comprehensive treatment",
        "Funnel synthesis for the complete swing",
        "Underactuation as Advantage",
    ):
        assert phrase not in text
    assert "Motion, Targets, and Timing" in text
    assert "Geometry, Feasible Dynamics, and Robust Outcomes" in text


def test_compile_book_uses_repo_relative_paths_and_subtitle() -> None:
    source = (MOTION_CONTROL / "compile_book.py").read_text(encoding="utf-8")
    for forbidden in ("/mnt/project/", "/home/claude/", "A New Framework for Nonlinear Systems"):
        assert forbidden not in source
    assert "_SCRIPT_DIR = Path(__file__).resolve().parent" in source
    assert "Geometry, Feasible Dynamics, and Robust Outcomes" in source


@pytest.mark.parametrize("name", REMOVED_COMPANIONS)
def test_repo_has_no_links_to_removed_motion_control_companions(name: str) -> None:
    matches: list[str] = []
    for base in _SCAN_ROOTS:
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix in _SKIP_SUFFIXES:
                continue
            if path == Path(__file__):
                continue
            try:
                body = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if name in body:
                matches.append(str(path.relative_to(ROOT)))
    assert not matches, f"links to removed companion {name}: {matches[:10]}"
