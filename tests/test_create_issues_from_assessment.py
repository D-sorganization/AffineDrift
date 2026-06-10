"""Behavioral tests for ``scripts/create_issues_from_assessment.py`` (issue #3230).

Covers the pure helpers ``issue_exists`` (open/closed and substring matching),
``prepare_issue_data`` (title assembly, description truncation, severity->label
mapping), and ``create_github_issue`` dry-run path (no subprocess executed).
"""

from __future__ import annotations

from scripts.create_issues_from_assessment import (
    create_github_issue,
    issue_exists,
    prepare_issue_data,
)


def test_issue_exists_matches_open_substring() -> None:
    existing = [{"title": "Fix the broken build pipeline", "state": "OPEN"}]
    assert issue_exists("broken build", existing) is True


def test_issue_exists_ignores_closed_issues() -> None:
    existing = [{"title": "Fix the broken build", "state": "CLOSED"}]
    assert issue_exists("broken build", existing) is False


def test_issue_exists_returns_false_when_no_match() -> None:
    existing = [{"title": "Unrelated topic", "state": "OPEN"}]
    assert issue_exists("something else entirely", existing) is False


def test_prepare_issue_data_builds_title_and_bug_label() -> None:
    data = prepare_issue_data(
        {"severity": "CRITICAL", "description": "Null deref in parser", "source": "F"},
        {"timestamp": "2026-06-09"},
        "AffineDrift",
    )
    assert data["title"].startswith("[AffineDrift] CRITICAL")
    assert "Null deref in parser" in data["title"]
    assert "bug" in data["labels"]
    assert "auto-generated" in data["labels"]


def test_prepare_issue_data_non_critical_gets_enhancement_label() -> None:
    data = prepare_issue_data(
        {"severity": "MINOR", "description": "Tidy docstring", "source": "B"},
        {},
        "AffineDrift",
    )
    assert "enhancement" in data["labels"]
    assert "bug" not in data["labels"]


def test_prepare_issue_data_truncates_long_description() -> None:
    long_desc = "x" * 200
    data = prepare_issue_data(
        {"severity": "MAJOR", "description": long_desc, "source": "A"},
        {},
        "Repo",
    )
    assert "..." in data["title"]
    # Truncated to 57 chars + "..." within the title segment.
    assert "x" * 60 not in data["title"]


def test_create_github_issue_dry_run_does_not_raise() -> None:
    assert create_github_issue("Title", "Body", ["label"], dry_run=True) is True
