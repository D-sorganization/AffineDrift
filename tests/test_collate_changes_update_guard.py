"""Tests for collate-changes workflow update guard configuration."""

from pathlib import Path
from typing import Any, cast

import pytest
import yaml

pytestmark = [pytest.mark.unit, pytest.mark.headless_safe]
ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "collate-changes.yml"
PROPOSAL_STEP = "Propose collation as a pull request"


def _get_proposal_step() -> dict[str, Any]:
    data = cast("dict[str, Any]", yaml.safe_load(WORKFLOW.read_text("utf-8")))
    steps = data["jobs"]["collate"]["steps"]
    return next(step for step in steps if step.get("name") == PROPOSAL_STEP)


def test_collate_workflow_defines_both_guards() -> None:
    """Workflow proposal step must define both automerge guard and update guard."""
    proposal = _get_proposal_step()
    env = proposal.get("env", {})
    assert env.get("GUARD") == ".rm-tools/scripts/automerge_guard.py"
    assert env.get("UPDATE_GUARD") == ".rm-tools/scripts/pr_update_guard.py"


def test_pre_push_check_uses_update_guard_not_automerge_guard() -> None:
    """Pre-push editability check must invoke UPDATE_GUARD instead of bare GUARD."""
    proposal = _get_proposal_step()
    script = cast("str", proposal["run"])
    assert 'python3 "$UPDATE_GUARD" "$REPO_SLUG" "$PR_NUM"' in script
    assert '! python3 "$GUARD" "$REPO_SLUG" "$PR_NUM"' not in script


def test_post_push_arming_retains_automerge_guard() -> None:
    """Post-push auto-merge arming must continue using automerge_guard with squash strategy."""
    proposal = _get_proposal_step()
    script = cast("str", proposal["run"])
    assert 'python3 "$GUARD" "$REPO_SLUG" "$PR_NUM" --arm --strategy squash' in script
