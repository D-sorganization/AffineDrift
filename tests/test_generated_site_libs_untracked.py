"""Governance tests for generated Quarto vendor artifacts (issue #3182).

Quarto bundles its vendor JavaScript/CSS libraries into ``site_libs/`` inside the
render output directory (``docs/site_libs/``, which is git-ignored). A stale copy
was previously committed at the repository root, where it inflated source-quality
metrics and added ~13k lines of generated code to the tracked tree. These tests
keep that artifact from creeping back in.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _tracked_files() -> list[str]:
    cmd = ["git", "ls-files"]
    result = subprocess.run(  # noqa: S603 -- hardcoded git command in trusted env
        cmd,  # noqa: S607 -- "git" resolved from PATH in trusted env
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.splitlines()


def test_root_site_libs_not_tracked() -> None:
    """No Quarto-generated ``site_libs/`` files are tracked at the repo root."""
    offenders = [path for path in _tracked_files() if path.startswith("site_libs/")]
    assert offenders == [], (
        "Root-level site_libs/ is Quarto-generated output and must not be tracked; "
        f"found tracked files: {offenders}"
    )


def test_root_site_libs_is_gitignored() -> None:
    """A path under root ``site_libs/`` is ignored so the artifact cannot return."""
    cmd = ["git", "check-ignore", "site_libs/quarto-html/quarto.js"]
    result = subprocess.run(  # noqa: S603 -- hardcoded git command in trusted env
        cmd,  # noqa: S607 -- "git" resolved from PATH in trusted env
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    # git check-ignore exits 0 and echoes the path when it is ignored.
    assert result.returncode == 0, "Root site_libs/ should be covered by .gitignore"
    assert "site_libs" in result.stdout
