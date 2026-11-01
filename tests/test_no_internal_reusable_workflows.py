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
FLEET_WORKFLOWS_CONFLICT_DISARM = (
    "D-sorganization/fleet-workflows/.github/workflows/reusable-conflict-disarm.yml"
)
# fleet-workflows commit that scopes the App token to the swept repo (#8).
FLEET_WORKFLOWS_PIN = "__FW_SHA__"

pytestmark = [pytest.mark.unit, pytest.mark.headless_safe]


def _jobs(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")).get("jobs") or {}


@pytest.mark.parametrize("path", sorted(WORKFLOWS.glob("*.y*ml")), ids=lambda p: p.name)
def test_no_job_calls_an_internal_reusable_workflow(path: Path) -> None:
    for name, job in _jobs(path).items():
        assert not str(job.get("uses", "")).startswith(INTERNAL_PREFIX), name


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


def test_conflict_disarm_keeps_the_dry_run_default() -> None:
    job = _conflict_disarm_job()

    assert job["with"]["dry_run"] == "${{ inputs.dry_run || 'true' }}"
    assert job["with"]["exclude_prs"] == "${{ inputs.exclude_prs || '' }}"
    assert set(job["secrets"]) == {"JULES_APP_ID", "JULES_APP_PRIVATE_KEY"}
