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
