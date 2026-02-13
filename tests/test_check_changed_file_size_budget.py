"""Tests for changed-file module size budget checks."""

import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import check_changed_file_size_budget


def test_merge_base_falls_back_to_head_parent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Fallback should return HEAD~1 when merge-base resolution fails."""

    def fake_run(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise subprocess.CalledProcessError(1, "git")

    monkeypatch.setattr(check_changed_file_size_budget.subprocess, "run", fake_run)
    assert check_changed_file_size_budget._merge_base(tmp_path) == "HEAD~1"


def test_changed_files_parses_git_diff_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Changed-file parser should return non-empty trimmed paths."""

    def fake_run(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        return SimpleNamespace(stdout="src/tools/a.py\n\nscripts/x.py\n")

    monkeypatch.setattr(check_changed_file_size_budget.subprocess, "run", fake_run)
    changed = check_changed_file_size_budget._changed_files(tmp_path, "abc123")
    assert changed == ["src/tools/a.py", "scripts/x.py"]


def test_changed_files_falls_back_to_git_show_on_diff_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """When merge-base diff fails, fallback should parse HEAD file list."""
    calls: list[list[str]] = []

    def fake_run(args, **_kwargs):  # type: ignore[no-untyped-def]
        calls.append(args)
        if args[0:2] == ["git", "diff"]:
            raise subprocess.CalledProcessError(128, args)
        return SimpleNamespace(stdout="scripts/check_changed_file_size_budget.py\n")

    monkeypatch.setattr(check_changed_file_size_budget.subprocess, "run", fake_run)
    changed = check_changed_file_size_budget._changed_files(tmp_path, "HEAD~1")
    assert changed == ["scripts/check_changed_file_size_budget.py"]
    assert calls[0][0:2] == ["git", "diff"]
    assert calls[1][0:2] == ["git", "diff"]
    assert calls[2][0:2] == ["git", "diff"]
    assert calls[3][0:2] == ["git", "show"]


def test_changed_files_uses_first_non_empty_result(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The first successful non-empty candidate command should be returned."""
    calls: list[list[str]] = []

    def fake_run(args, **_kwargs):  # type: ignore[no-untyped-def]
        calls.append(args)
        rev_range = args[-1]
        if rev_range == "abc123...HEAD":
            return SimpleNamespace(stdout="")
        if rev_range == "HEAD^1...HEAD":
            return SimpleNamespace(stdout="scripts/run_assessment.py\n")
        raise subprocess.CalledProcessError(128, args)

    monkeypatch.setattr(check_changed_file_size_budget.subprocess, "run", fake_run)
    changed = check_changed_file_size_budget._changed_files(tmp_path, "abc123")
    assert changed == ["scripts/run_assessment.py"]
    assert calls[0][-1] == "abc123...HEAD"
    assert calls[1][-1] == "HEAD^1...HEAD"


def test_changed_files_returns_empty_on_ci_when_all_commands_fail(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """CI fallback should fail-open instead of raising false-positive failures."""

    def fake_run(args, **_kwargs):  # type: ignore[no-untyped-def]
        if args[0:2] == ["git", "fetch"]:
            return SimpleNamespace(stdout="")
        raise subprocess.CalledProcessError(128, args)

    monkeypatch.setattr(check_changed_file_size_budget.subprocess, "run", fake_run)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_BASE_REF", "main")
    assert check_changed_file_size_budget._changed_files(tmp_path, "HEAD~1") == []
