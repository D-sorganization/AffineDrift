"""Tests for scripts/prune_internal_docs_from_deploy.py."""

from __future__ import annotations

from pathlib import Path

from scripts.prune_internal_docs_from_deploy import prune_internal_markdown_files


def test_prune_internal_markdown_files_removes_md_only(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.html").write_text("<h1>Home</h1>", encoding="utf-8")
    (docs / "styles.css").write_text("body {}", encoding="utf-8")
    (docs / "GOVERNANCE.md").write_text("# Governance", encoding="utf-8")

    sub = docs / "operations"
    sub.mkdir()
    (sub / "runbook.md").write_text("# Runbook", encoding="utf-8")
    (sub / "report.html").write_text("<h1>Report</h1>", encoding="utf-8")

    deleted = prune_internal_markdown_files(docs)

    assert len(deleted) == 2
    assert not (docs / "GOVERNANCE.md").exists()
    assert not (sub / "runbook.md").exists()
    assert (docs / "index.html").exists()
    assert (docs / "styles.css").exists()
    assert (sub / "report.html").exists()


def test_prune_internal_markdown_files_handles_missing_dir(tmp_path: Path):
    non_existent = tmp_path / "non_existent"
    deleted = prune_internal_markdown_files(non_existent)
    assert deleted == []
