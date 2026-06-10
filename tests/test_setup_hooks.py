"""Tests for git hook setup orchestration."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts import setup_hooks


def test_check_pre_commit_installed_handles_missing_executable(monkeypatch) -> None:
    """Missing pre-commit should be reported as not installed."""

    def missing_command(_cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
        raise FileNotFoundError("pre-commit")

    monkeypatch.setattr(setup_hooks, "run_command", missing_command)

    assert not setup_hooks.check_pre_commit_installed()


def test_install_pre_commit_installs_when_absent(monkeypatch) -> None:
    """The installer should call pip only when pre-commit is absent."""
    commands: list[list[str]] = []

    monkeypatch.setattr(setup_hooks, "check_pre_commit_installed", lambda: False)
    monkeypatch.setattr(
        setup_hooks,
        "run_command",
        lambda cmd, check=True: commands.append(cmd) or subprocess.CompletedProcess(cmd, 0, "", ""),
    )

    setup_hooks.install_pre_commit()

    assert commands == [[setup_hooks.sys.executable, "-m", "pip", "install", "pre-commit"]]


def test_install_hooks_and_push_hooks_use_pre_commit(monkeypatch) -> None:
    """Hook installers should invoke the expected pre-commit commands."""
    commands: list[list[str]] = []
    monkeypatch.setattr(
        setup_hooks,
        "run_command",
        lambda cmd, check=True: commands.append(cmd) or subprocess.CompletedProcess(cmd, 0, "", ""),
    )

    setup_hooks.install_hooks()
    setup_hooks.install_push_hooks()

    assert commands == [
        ["pre-commit", "install"],
        ["pre-commit", "install", "--hook-type", "pre-push"],
    ]


def test_verify_installation_reports_hook_paths(tmp_path: Path, monkeypatch, caplog) -> None:
    """Verification should inspect the current repository's .git/hooks paths."""
    hooks_dir = tmp_path / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "pre-commit").write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    with caplog.at_level(setup_hooks.logging.INFO):
        setup_hooks.verify_installation()

    assert "[OK] pre-commit hook" in caplog.text
    assert "[MISSING] pre-push hook" in caplog.text


def test_main_exits_on_command_failure(monkeypatch) -> None:
    """Command failures should become a non-zero SystemExit."""
    monkeypatch.setattr(
        setup_hooks,
        "install_pre_commit",
        lambda: (_ for _ in ()).throw(
            subprocess.CalledProcessError(1, ["pre-commit"], "out", "err")
        ),
    )

    with pytest.raises(SystemExit) as exc_info:
        setup_hooks.main()

    assert exc_info.value.code == 1
