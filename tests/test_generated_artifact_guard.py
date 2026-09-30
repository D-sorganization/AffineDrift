"""Regression tests for the committed-generated-artifact hermeticity guard."""

from __future__ import annotations

from pathlib import Path

import tests.conftest as conftest
from tests._generated_artifact_guard import (
    GUARDED_DIRS,
    changed_generated_artifacts,
    snapshot_generated_artifacts,
)


def _seed(root: Path) -> None:
    (root / "data/trust/generated").mkdir(parents=True)
    (root / "_includes/generated").mkdir(parents=True)
    (root / "data/trust/generated/registry.json").write_bytes(b'{"a": 1}\n')
    (root / "_includes/generated/summary.qmd").write_bytes(b"summary\n")
    (root / "data/trust/unguarded.json").write_bytes(b"{}\n")


def test_guard_covers_trust_generated_and_generated_partials() -> None:
    assert "data/trust/generated" in GUARDED_DIRS
    assert "_includes/generated" in GUARDED_DIRS


def test_unchanged_tree_reports_nothing(tmp_path: Path) -> None:
    _seed(tmp_path)
    before = snapshot_generated_artifacts(tmp_path)
    assert set(before) == {"data/trust/generated/registry.json", "_includes/generated/summary.qmd"}
    assert changed_generated_artifacts(before, snapshot_generated_artifacts(tmp_path)) == []


def test_modified_created_and_deleted_files_are_reported(tmp_path: Path) -> None:
    _seed(tmp_path)
    before = snapshot_generated_artifacts(tmp_path)

    (tmp_path / "data/trust/generated/registry.json").write_bytes(b'{"a": 2}\n')
    (tmp_path / "data/trust/generated/new.json").write_bytes(b"{}\n")
    (tmp_path / "_includes/generated/summary.qmd").unlink()
    (tmp_path / "data/trust/unguarded.json").write_bytes(b'{"ignored": true}\n')

    assert changed_generated_artifacts(before, snapshot_generated_artifacts(tmp_path)) == [
        "modified: data/trust/generated/registry.json",
        "created: data/trust/generated/new.json",
        "deleted: _includes/generated/summary.qmd",
    ]


def test_line_ending_rewrite_counts_as_modification(tmp_path: Path) -> None:
    """A Windows ``write_text`` round-trip (LF -> CRLF) dirties git, so it must fail."""
    _seed(tmp_path)
    before = snapshot_generated_artifacts(tmp_path)
    (tmp_path / "_includes/generated/summary.qmd").write_bytes(b"summary\r\n")
    assert changed_generated_artifacts(before, snapshot_generated_artifacts(tmp_path)) == [
        "modified: _includes/generated/summary.qmd"
    ]


def test_session_hooks_are_registered_in_conftest() -> None:
    assert callable(conftest.pytest_sessionstart)
    assert callable(conftest.pytest_sessionfinish)
    assert conftest._REPO_ROOT == Path(__file__).resolve().parents[1]
