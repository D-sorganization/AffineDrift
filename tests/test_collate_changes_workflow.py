"""Regression test for #5532: collate-changes workflow uses pr_update_guard."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "collate-changes.yml"


def test_collate_changes_workflow_uses_pr_update_guard_and_automerge_guard() -> None:
    text = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "UPDATE_GUARD: .rm-tools/scripts/pr_update_guard.py" in text
    assert "GUARD: .rm-tools/scripts/automerge_guard.py" in text
    assert 'python3 "$UPDATE_GUARD" "$REPO_SLUG" "$PR_NUM"' in text
    assert 'python3 "$GUARD" "$REPO_SLUG" "$PR_NUM" --arm --strategy squash' in text
