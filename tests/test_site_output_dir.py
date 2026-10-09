"""Pin the Quarto output directory apart from the tracked internal documentation.

Issue #4597: ``output-dir`` used to be ``docs``, the same directory that holds
tracked internal files (ADRs, development logs, CSS plans), so every deploy had to
prune them out of the artifact. The output now lives in a git-ignored ``_site/``
directory, so internal documentation cannot land in the published site.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_OUTPUT_DIR = "_site"
INTERNAL_DOCS_DIR = "docs"
# Quarto publishes these asset types; a tracked copy under docs/ is a stale build mirror.
PUBLISHED_ASSET_SUFFIXES = {".css", ".js", ".pdf"}
WORKFLOW_DOCS_OUTPUT = re.compile(r"(--docs-dir|--directory)[ =]docs\b")


def _output_dir() -> str:
    config = yaml.safe_load((ROOT / "_quarto.yml").read_text(encoding="utf-8"))
    return str(config["project"]["output-dir"])


def _tracked_files(pathspec: str) -> list[str]:
    git = shutil.which("git")
    if git is None:
        pytest.skip("git is unavailable")
    result = subprocess.run(  # noqa: S603 - fixed argv, no shell, no user input
        [git, "ls-files", "--", pathspec],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.skip("git metadata is unavailable")
    return result.stdout.splitlines()


def test_quarto_output_dir_is_site() -> None:
    assert _output_dir() == EXPECTED_OUTPUT_DIR


def test_output_dir_is_distinct_from_internal_docs() -> None:
    output = Path(_output_dir()).resolve()
    internal = Path(INTERNAL_DOCS_DIR).resolve()
    assert output != internal
    assert internal not in output.parents
    assert output not in internal.parents


def test_output_dir_is_gitignored_and_untracked() -> None:
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert f"/{EXPECTED_OUTPUT_DIR}/" in ignored
    assert _tracked_files(EXPECTED_OUTPUT_DIR) == []


def test_internal_docs_hold_no_published_build_mirrors() -> None:
    mirrors = [
        path
        for path in _tracked_files(INTERNAL_DOCS_DIR)
        if Path(path).suffix in PUBLISHED_ASSET_SUFFIXES
    ]
    assert mirrors == []


def test_workflows_do_not_treat_docs_as_build_output() -> None:
    offenders = [
        workflow.name
        for workflow in (ROOT / ".github" / "workflows").glob("*.yml")
        if WORKFLOW_DOCS_OUTPUT.search(workflow.read_text(encoding="utf-8"))
    ]
    assert offenders == []
