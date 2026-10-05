"""Anti-phantom-merge rule 4 reads commits from the API, never a checkout (RM#1989)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "anti-phantom-merge.yml"

pytestmark = [pytest.mark.unit, pytest.mark.headless_safe]


def _steps() -> list[dict[str, Any]]:
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    return list(data["jobs"]["guard"]["steps"])


def test_rule_4_reads_pr_commits_from_rest_api() -> None:
    script = "\n".join(str(s.get("run", "")) for s in _steps())
    assert "pulls/$PR/commits" in script
    assert "--paginate" in script
    assert not re.search(r"\bgit\s+(log|fetch|rev-list)\b", script)


def test_no_step_checks_out_a_repository_tree() -> None:
    """Both events behave identically: no head or base checkout is needed."""
    uses = [str(s.get("uses", "")) for s in _steps()]
    assert not [u for u in uses if u.startswith("actions/checkout")]


def test_no_step_references_pr_head_under_pull_request_target() -> None:
    text = yaml.safe_dump(_steps())
    assert "pull_request.head" not in text


def test_run_blocks_do_not_interpolate_untrusted_expressions() -> None:
    for step in _steps():
        run = str(step.get("run", ""))
        assert "github.event.pull_request" not in run
        assert "head_ref" not in run
