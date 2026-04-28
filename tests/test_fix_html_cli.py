"""CLI contract tests for the repository-root HTML normalization script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "fix_html.py"


def test_main_writes_normalized_html_to_output(tmp_path: Path) -> None:
    """The CLI should normalize input and write to an alternate output path."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    input_file = repo_root / "content" / "wrist-as-universal-joint" / "Wrist_Universal_Claude.html"
    input_file.parent.mkdir(parents=True)
    input_file.write_text("<p>\n<ul></li><li><p>\\begin{quote}", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo-root",
            str(repo_root),
            "--input",
            "content/wrist-as-universal-joint/Wrist_Universal_Claude.html",
            "--output",
            "build/Wrist_Universal_Claude.html",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    output_file = repo_root / "build" / "Wrist_Universal_Claude.html"
    assert result.returncode == 0, result.stderr
    assert output_file.read_text(encoding="utf-8") == "<ul>\n<li>\\begin{quote}"
    assert input_file.read_text(encoding="utf-8") == "<p>\n<ul></li><li><p>\\begin{quote}"


def test_main_dry_run_does_not_write_output(tmp_path: Path) -> None:
    """The CLI dry-run mode should report changes without writing files."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    input_file = repo_root / "content" / "wrist-as-universal-joint" / "Wrist_Universal_Claude.html"
    input_file.parent.mkdir(parents=True)
    input_file.write_text("<p>\n<ul></li><li>", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo-root",
            str(repo_root),
            "--input",
            "content/wrist-as-universal-joint/Wrist_Universal_Claude.html",
            "--output",
            "build/Wrist_Universal_Claude.html",
            "--dry-run",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert not (repo_root / "build" / "Wrist_Universal_Claude.html").exists()
    assert input_file.read_text(encoding="utf-8") == "<p>\n<ul></li><li>"
