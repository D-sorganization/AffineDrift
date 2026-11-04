"""Unit tests for scripts/audit_workflows.py (issue #5249)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.audit_workflows import (
    WorkflowAuditRecord,
    audit_workflows,
    main,
    render_markdown_report,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_audit_workflows_flags_unpinned_action_and_interpolated_issue_title(
    tmp_path: Path,
) -> None:
    """Fixture workflow with unpinned action and interpolated issue title must flag both."""
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "unsafe.yml").write_text(
        "name: Unsafe Fixture\n"
        "on:\n"
        "  issues:\n"
        "    types: [opened]\n"
        "jobs:\n"
        "  triage:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - uses: actions/checkout@v4\n"
        "      - name: Echo issue title\n"
        "        run: |\n"
        '          echo "Title: ${{ github.event.issue.title }}"\n',
        encoding="utf-8",
    )

    records = audit_workflows(workflow_dir)

    assert len(records) == 1
    record: WorkflowAuditRecord = records[0]
    assert record.workflow == "unsafe.yml"
    assert record.top_level_permissions == "MISSING"
    assert record.has_findings is True
    assert any("actions/checkout@v4" in item for item in record.unpinned_uses)
    assert any("github.event.issue.title" in item for item in record.untrusted_run_interpolations)

    report = render_markdown_report(records)
    assert "unsafe.yml" in report
    assert "actions/checkout@v4" in report
    assert "github.event.issue.title" in report


def test_audit_workflows_ignores_env_binding_and_extracts_top_level_permissions(
    tmp_path: Path,
) -> None:
    """Safe env binding outside run: is not flagged when action is SHA-pinned."""
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "safe.yml").write_text(
        "name: Safe Fixture\n"
        "on: [push]\n"
        "permissions:\n"
        "  contents: read\n"
        "  pull-requests: write\n"
        "jobs:\n"
        "  check:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1\n"
        "      - name: Safe env usage\n"
        "        env:\n"
        "          ISSUE_TITLE: ${{ github.event.issue.title }}\n"
        "        run: |\n"
        '          printf "%s\\n" "$ISSUE_TITLE"\n',
        encoding="utf-8",
    )

    records = audit_workflows(workflow_dir)

    assert len(records) == 1
    record = records[0]
    assert record.workflow == "safe.yml"
    assert record.top_level_permissions == "contents: read, pull-requests: write"
    assert record.unpinned_uses == ()
    assert record.untrusted_run_interpolations == ()
    assert record.has_findings is False


def test_audit_workflows_rejects_missing_directory(tmp_path: Path) -> None:
    """Boundary validation raises ValueError when workflow_dir does not exist."""
    with pytest.raises(ValueError, match="Workflow directory does not exist"):
        audit_workflows(tmp_path / "nonexistent")


def test_audit_workflows_cli_and_repo_inventory(tmp_path: Path) -> None:
    """Repository workflow inventory covers every workflow file and matches committed report."""
    workflow_dir = REPO_ROOT / ".github" / "workflows"
    out_file = tmp_path / "report.md"
    rc = main(["--workflow-dir", str(workflow_dir), "--output", str(out_file)])
    assert rc == 0

    generated_table = out_file.read_text(encoding="utf-8").strip()
    committed_report = (REPO_ROOT / "docs" / "audits" / "workflow-hardening-5249.md").read_text(
        encoding="utf-8"
    )
    assert generated_table in committed_report
