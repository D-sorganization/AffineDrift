"""Contract tests for repository required checks and runner routing guards.

Acceptance criteria for Repository_Management#2845:
- Exactly ONE job across all repository workflows produces each required check name:
  'Reject hosted runner routing', 'quality-gate', and 'Block do-not-merge label'.
- .github/workflows/local-only-runner-guard.yml triggers on every pull_request
  (no paths or paths-ignore filter) and merge_group.
- No workflow job or step carries a 'Bypass' name or executes 'echo "Bypass"'.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = [pytest.mark.unit, pytest.mark.headless_safe]

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"

REQUIRED_CHECK_NAMES = (
    "Reject hosted runner routing",
    "quality-gate",
    "Block do-not-merge label",
)


def _load_workflows() -> list[tuple[Path, dict[str, Any]]]:
    """Load all YAML workflow definitions in .github/workflows."""
    workflows: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(WORKFLOWS_DIR.glob("*.yml")) + sorted(WORKFLOWS_DIR.glob("*.yaml")):
        content = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(content, dict):
            workflows.append((path, content))
    return workflows


def _extract_triggers(workflow_data: dict[str, Any]) -> dict[str, Any]:
    """Extract triggers handling PyYAML's parsing of bare 'on:' as boolean True."""
    raw: dict[Any, Any] = workflow_data
    triggers = raw.get("on")
    if triggers is None:
        triggers = raw.get(True)
    if not isinstance(triggers, dict):
        if isinstance(triggers, list):
            return {event: None for event in triggers}
        if isinstance(triggers, str):
            return {triggers: None}
        return {}
    return triggers


def _find_bypass_in_step(path_name: str, job_id: str, idx: int, step: Any) -> list[str]:
    """Inspect a workflow step for bypass markers."""
    findings: list[str] = []
    if not isinstance(step, dict):
        return findings

    step_name = str(step.get("name") or f"step-{idx}")
    if re.search(r"\bbypass\b", step_name, re.IGNORECASE):
        findings.append(f"{path_name} job '{job_id}' step '{step_name}' name contains 'Bypass'")
    run_cmd = str(step.get("run") or "")
    if re.search(r'echo\s+["\']Bypass["\']', run_cmd, re.IGNORECASE):
        findings.append(
            f"{path_name} job '{job_id}' step '{step_name}' runs echo Bypass: {run_cmd.strip()}"
        )
    return findings


def _find_bypass_in_job(path_name: str, job_id: str, job: Any) -> list[str]:
    """Inspect a workflow job and its steps for bypass markers."""
    findings: list[str] = []
    if not isinstance(job, dict):
        return findings

    job_name = str(job.get("name") or job_id)
    if re.search(r"\bbypass\b", job_name, re.IGNORECASE):
        findings.append(f"{path_name} job '{job_id}' name contains 'Bypass': {job_name}")

    steps = job.get("steps") or []
    if isinstance(steps, list):
        for idx, step in enumerate(steps):
            findings.extend(_find_bypass_in_step(path_name, job_id, idx, step))
    return findings


def test_required_check_jobs_are_unique_across_workflows() -> None:
    """Each required check must be produced by exactly ONE job across all workflows."""
    workflows = _load_workflows()
    assert workflows, "No workflow files found in .github/workflows"

    check_producers: dict[str, list[tuple[str, str, str]]] = {
        name: [] for name in REQUIRED_CHECK_NAMES
    }

    for path, data in workflows:
        jobs = data.get("jobs") or {}
        if not isinstance(jobs, dict):
            continue
        for job_id, job in jobs.items():
            if not isinstance(job, dict):
                continue
            effective_name = str(job.get("name") or job_id)
            if effective_name in check_producers:
                check_producers[effective_name].append((path.name, str(job_id), effective_name))

    for check_name, producers in check_producers.items():
        assert len(producers) == 1, (
            f"Expected exactly 1 job producing check '{check_name}', "
            f"found {len(producers)}: {producers}"
        )


def test_local_only_runner_guard_triggers_on_all_pull_requests_and_merge_group() -> None:
    """local-only-runner-guard.yml must run on all pull_request events and merge_group."""
    guard_path = WORKFLOWS_DIR / "local-only-runner-guard.yml"
    assert guard_path.is_file(), "local-only-runner-guard.yml not found"

    data = yaml.safe_load(guard_path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "Invalid YAML in local-only-runner-guard.yml"

    triggers = _extract_triggers(data)
    assert "pull_request" in triggers, "local-only-runner-guard.yml missing pull_request trigger"
    assert "merge_group" in triggers, "local-only-runner-guard.yml missing merge_group trigger"

    pr_config = triggers["pull_request"]
    if isinstance(pr_config, dict):
        assert "paths" not in pr_config, (
            "local-only-runner-guard.yml must not restrict pull_request with 'paths' filter; "
            "it must evaluate runner routing on every PR"
        )
        assert (
            "paths-ignore" not in pr_config
        ), "local-only-runner-guard.yml must not restrict pull_request with 'paths-ignore' filter"


def test_no_workflow_job_or_step_contains_bypass() -> None:
    """Workflows must not define bypass placeholder jobs, steps, or echo commands."""
    workflows = _load_workflows()
    findings: list[str] = []

    for path, data in workflows:
        jobs = data.get("jobs") or {}
        if not isinstance(jobs, dict):
            continue
        for job_id, job in jobs.items():
            findings.extend(_find_bypass_in_job(path.name, str(job_id), job))

    assert not findings, "Found bypass workflow elements:\n" + "\n".join(findings)
