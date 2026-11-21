"""Contract tests for .github/workflows/label-merge-guard.yml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "label-merge-guard.yml"

pytestmark = [pytest.mark.unit, pytest.mark.headless_safe]


def _triggers(data: dict[str, Any]) -> dict[str, Any]:
    """PyYAML parses bare ``on:`` as boolean True (#5249 pattern)."""
    triggers = data.get(True) or data.get("on")
    if not isinstance(triggers, dict):
        raise KeyError("workflow triggers")
    return triggers


def _workflow() -> dict[str, Any]:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _merge_step_script() -> str:
    job = _workflow()["jobs"]["block-do-not-merge"]
    return "\n".join(str(step.get("run", "")) for step in job["steps"])


def _protect_step_script() -> str:
    job = _workflow()["jobs"]["protect-do-not-automate"]
    return "\n".join(str(step.get("run", "")) for step in job["steps"])


def test_triggers_include_merge_queue_and_label_events() -> None:
    on = _triggers(_workflow())
    assert "merge_group" in on
    assert "closed" in on["issues"]["types"]
    for event in ("opened", "synchronize", "labeled", "unlabeled"):
        assert event in on["pull_request"]["types"]


def test_merge_job_has_no_checkout_and_reads_labels_via_gh() -> None:
    job = _workflow()["jobs"]["block-do-not-merge"]
    uses = [str(step.get("uses", "")) for step in job["steps"]]
    assert not any(u.startswith("actions/checkout") for u in uses)
    script = _merge_step_script()
    assert "gh pr view" in script
    assert "do-not-merge" in script
    assert "github.event.pull_request" not in script


def test_merge_job_resolves_pr_on_merge_group() -> None:
    script = _merge_step_script()
    assert "MERGE_HEAD_REF" in script
    assert "gh pr list" in script


def test_issue_job_reopens_on_automation_close() -> None:
    script = _protect_step_script()
    assert "gh issue reopen" in script
    assert "do-not-automate" in script
    assert "human must close" in script.lower()


def test_dry_run_script_static_validation_passes() -> None:
    from scripts.dry_run_label_merge_guard import static_validate

    assert static_validate() == []
