"""The vendored GAAI framework is gone and must not come back.

The owner retired GAAI fleet-wide (Repository_Management#2725). The checked-in
``.gaai/`` tree, its daemon launcher and its slash commands are removed; these
checks keep them, and live pointers to them, from returning.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# Files an agent or tool reads on every run. A GAAI pointer here would send it
# to files that no longer exist.
LIVE_ENTRY_POINTS = (
    "CLAUDE.md",
    "AGENTS.md",
    "README.md",
    ".gitignore",
    ".prettierignore",
    ".quartoignore",
    "pyproject.toml",
    "scripts/check_root_hygiene.py",
    "scripts/check_agent_automation_artifacts.py",
)

_GAAI = re.compile(r"gaai", re.IGNORECASE)
_FLEET_BLOCK = re.compile(r"<!-- BEGIN FLEET-MANAGED:.*?<!-- END FLEET-MANAGED.*?-->", re.DOTALL)


def test_vendored_tree_is_removed() -> None:
    assert not (REPO_ROOT / ".gaai").exists()


def test_daemon_launcher_is_removed() -> None:
    assert not (REPO_ROOT / "start-gaai-daemon.sh").exists()


def test_slash_commands_are_removed() -> None:
    commands = REPO_ROOT / ".claude" / "commands"
    leftovers = sorted(p.name for p in commands.glob("gaai-*")) if commands.is_dir() else []
    assert leftovers == []


@pytest.mark.parametrize("relative_path", LIVE_ENTRY_POINTS)
def test_live_entry_point_does_not_mention_gaai(relative_path: str) -> None:
    path = REPO_ROOT / relative_path
    if not path.is_file():
        return  # optional file (e.g. .quartoignore) absent: nothing to check
    text = _FLEET_BLOCK.sub(
        lambda m: "\n" * m.group(0).count("\n"), path.read_text(encoding="utf-8")
    )
    hits = [
        f"{relative_path}:{number}"
        for number, line in enumerate(text.splitlines(), start=1)
        if _GAAI.search(line)
    ]
    assert hits == []
