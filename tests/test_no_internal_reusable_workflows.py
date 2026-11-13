"""Public AD must not call internal Repository_Management reusable workflows (#5295).

GitHub refuses a public repository's call to an internal repository's
reusable workflow before any job is created, so such a workflow fails every
run with 0 jobs. Conflict Disarm did exactly that; it now calls the public
fleet-workflows provider instead (fleet-workflows#1).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
CONFLICT_DISARM = WORKFLOWS / "conflict-disarm.yml"
INTERNAL_PREFIX = "D-sorganization/Repository_Management/.github/workflows/"
# RM #2427: PR body lint; pinned SHA, no PR-head checkout in caller.
ALLOWED_RM_REUSABLE_PR_BODY_LINT = (
    f"{INTERNAL_PREFIX}reusable-pr-body-lint.yml@" "3b5e9f54febbd730bc2a650dc9193d26922ff49f"
)
FLEET_WORKFLOWS_CONFLICT_DISARM = (
    "D-sorganization/fleet-workflows/.github/workflows/reusable-conflict-disarm.yml"
)
# fleet-workflows commit that scopes the App token to the swept repo (#8).
FLEET_WORKFLOWS_PIN = "367b182c24ae3b01488fc1266130969e775023de"

pytestmark = [pytest.mark.unit, pytest.mark.headless_safe]


def _jobs(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")).get("jobs") or {}


@pytest.mark.parametrize("path", sorted(WORKFLOWS.glob("*.y*ml")), ids=lambda p: p.name)
def test_no_job_calls_an_internal_reusable_workflow(path: Path) -> None:
    for name, job in _jobs(path).items():
        uses = str(job.get("uses", ""))
        if uses.startswith(ALLOWED_RM_REUSABLE_PR_BODY_LINT):
            continue
        assert not uses.startswith(INTERNAL_PREFIX), name


def _conflict_disarm_job() -> dict[str, Any]:
    (job,) = _jobs(CONFLICT_DISARM).values()
    return job


def test_conflict_disarm_calls_the_sha_pinned_public_provider() -> None:
    """fleet-workflows#1: one public implementation, pinned to a reviewed commit."""
    job = _conflict_disarm_job()
    workflow, _, ref = str(job.get("uses", "")).partition("@")

    assert workflow == FLEET_WORKFLOWS_CONFLICT_DISARM
    assert ref == FLEET_WORKFLOWS_PIN
    assert re.fullmatch(r"[0-9a-f]{40}", ref)
    assert "steps" not in job, "the inlined sweep must be gone"


def test_collate_changes_uses_fleet_app_secrets() -> None:
    workflow = yaml.safe_load((WORKFLOWS / "collate-changes.yml").read_text(encoding="utf-8"))
    steps = workflow["jobs"]["collate"]["steps"]
    token_step = next(step for step in steps if step.get("id") == "app-token")
    validation_step = next(step for step in steps if step["name"] == "Validate fleet app secrets")

    assert token_step["with"]["client-id"] == "${{ secrets.FLEET_APP_ID }}"
    assert token_step["with"]["private-key"] == "${{ secrets.FLEET_APP_PRIVATE_KEY }}"
    assert "FLEET_APP_ID" in validation_step["run"]
    assert "FLEET_APP_PRIVATE_KEY" in validation_step["run"]


def test_conflict_disarm_keeps_the_dry_run_default() -> None:
    job = _conflict_disarm_job()

    assert job["with"]["dry_run"] == "${{ inputs.dry_run || 'true' }}"
    assert job["with"]["exclude_prs"] == "${{ inputs.exclude_prs || '' }}"
    assert job["secrets"] == {
        "JULES_APP_ID": "${{ secrets.FLEET_APP_ID }}",
        "JULES_APP_PRIVATE_KEY": "${{ secrets.FLEET_APP_PRIVATE_KEY }}",
    }
