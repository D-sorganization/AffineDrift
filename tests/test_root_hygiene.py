"""Repository root hygiene checks."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_ROOT_ARTIFACTS = {
    ".ci_trigger.py",
    "Geometry_of_Motion_Volume_0.pdf",
    "ISSUE_content_loss_ch09.md",
    "PR_AGRACHEV_INTEGRATION.md",
    "PR_DESCRIPTION.md",
    "The_Geometry_of_Motion_Complete.pdf",
    "The_Physics_of_Golf.pdf",
    "brute_merge.ps1",
    "magic_numbers_report.txt",
    "main.pdf",
    "notes_workspace_escape.png",
    "pr_body.txt",
    "ruff_errors.txt",
    "test.diff",
    "test_notes.html",
    "tmp1.tmp",
}

FORBIDDEN_ROOT_DIRECTORIES = {
    ".tmp_issue_bodies",
    "tmp_issue_bodies",
}


def test_review_and_build_artifacts_are_not_tracked_at_repo_root() -> None:
    """Root-level scratch files should not ship with the Quarto source tree."""
    present = sorted(
        path.name
        for path in REPO_ROOT.iterdir()
        if path.is_file() and path.name in FORBIDDEN_ROOT_ARTIFACTS
    )
    assert present == []


def test_transient_run_id_files_are_not_tracked_at_repo_root() -> None:
    """Windows path-shaped run markers should stay out of the repository root."""
    present = sorted(path.name for path in REPO_ROOT.glob("C*tmprunid.txt") if path.is_file())
    assert present == []


def test_issue_body_scratch_directories_are_not_tracked_at_repo_root() -> None:
    """Wave planning scratch directories should not ship as source files."""
    present = sorted(
        path.name
        for path in REPO_ROOT.iterdir()
        if path.is_dir() and path.name in FORBIDDEN_ROOT_DIRECTORIES
    )
    assert present == []


def test_empty_tmp_files_are_not_tracked_in_book_sources() -> None:
    """Book source directories should not contain empty local temp files."""
    temp_files = sorted(
        path.relative_to(REPO_ROOT).as_posix()
        for path in REPO_ROOT.glob("articles/**/*.tmp")
        if path.is_file()
    )
    assert temp_files == []
