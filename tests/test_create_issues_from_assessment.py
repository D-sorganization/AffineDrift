"""Tests for assessment-to-GitHub-issue creation helpers."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts import create_issues_from_assessment


def test_issue_exists_matches_open_similar_titles_only() -> None:
    """Duplicate detection should ignore closed issues and match similar open titles."""
    existing = [
        {"state": "CLOSED", "title": "Critical docs gap"},
        {"state": "OPEN", "title": "[Repo] CRITICAL Testing: missing coverage"},
    ]

    assert create_issues_from_assessment.issue_exists("missing coverage", existing)
    assert not create_issues_from_assessment.issue_exists("Critical docs gap", existing)


def test_create_github_issue_dry_run_does_not_call_gh(monkeypatch) -> None:
    """Dry runs should report success without invoking gh."""
    monkeypatch.setattr(
        create_issues_from_assessment.subprocess,
        "run",
        lambda *_args, **_kwargs: pytest.fail("gh should not be called"),
    )

    assert create_issues_from_assessment.create_github_issue(
        "Title", "Body", ["quality-control"], dry_run=True
    )


def test_create_github_issue_passes_labels_to_gh(monkeypatch) -> None:
    """Issue creation should pass title, body, and comma-joined labels."""
    calls: list[list[str]] = []

    def fake_run(cmd, capture_output, text, check):
        calls.append(cmd)
        assert capture_output is True
        assert text is True
        assert check is True
        return subprocess.CompletedProcess(cmd, 0, stdout="https://example/1\n")

    monkeypatch.setattr(create_issues_from_assessment.subprocess, "run", fake_run)

    assert create_issues_from_assessment.create_github_issue(
        "Title", "Body", ["bug", "quality-control"]
    )
    assert calls == [
        [
            "gh",
            "issue",
            "create",
            "--title",
            "Title",
            "--body",
            "Body",
            "--label",
            "bug,quality-control",
        ]
    ]


def test_prepare_issue_data_formats_title_body_and_labels(monkeypatch) -> None:
    """Finding metadata should become a bounded GitHub issue payload."""
    monkeypatch.setattr(create_issues_from_assessment, "get_repo_short_name", lambda: "Repo")
    issue = {
        "severity": "CRITICAL",
        "description": "**Missing** tests for `module`\nsecond line",
        "source": "Assessment_G_Results",
    }

    data = create_issues_from_assessment.prepare_issue_data(
        issue, {"timestamp": "2026-06-10"}, "Repo"
    )

    assert data["title"].startswith("[Repo] CRITICAL")
    assert "Missing tests for module" in data["title"]
    assert "bug" in data["labels"]
    assert "2026-06-10" in data["body"]


def test_process_assessment_findings_filters_and_dry_runs(tmp_path: Path, monkeypatch) -> None:
    """Processing should filter severities and skip existing checks when disabled."""
    summary = {
        "timestamp": "now",
        "critical_issues": [
            {"severity": "CRITICAL", "description": "A problem", "source": "Assessment_G"},
            {"severity": "MINOR", "description": "Small", "source": "Assessment_A"},
        ],
    }
    summary_path = tmp_path / "summary.json"
    summary_path.write_text(json.dumps(summary), encoding="utf-8")
    created: list[str] = []
    monkeypatch.setattr(
        create_issues_from_assessment,
        "create_github_issue",
        lambda title, _body, _labels, dry_run=False: created.append(title) or True,
    )

    exit_code = create_issues_from_assessment.process_assessment_findings(
        summary_path, ["CRITICAL"], check_existing=False, dry_run=True
    )

    assert exit_code == 0
    assert len(created) == 1
