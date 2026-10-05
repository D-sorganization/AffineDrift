"""Anti-phantom-merge rule 4 reads commits from the API, never a checkout (RM#1989)."""

from __future__ import annotations

import re
import shutil
import subprocess
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


# --- Rule 3 must see every changed file (AD#4935) ---------------------------

PAGE_SIZE = 100
REST_FILE_CAP = 3000

FAKE_GH = r"""#!/usr/bin/env bash
# Hermetic fake gh: `pr view --json files` is capped at 100 like GraphQL; the
# REST files endpoint only returns everything when --paginate is passed.
args="$*"
n="${FAKE_CHANGED_FILES:?}"
emit_files() {
  local limit="$1" i
  for ((i = 1; i <= limit; i++)); do
    if [ "$i" -eq "${FAKE_TARGET_INDEX:?}" ]; then
      echo "tests/target_file.py"
    else
      echo "docs/filler_$i.md"
    fi
  done
}
case "$args" in
  *"pr view"*"--json files"*) emit_files $(( n < 100 ? n : 100 )) ;;
  *"pr view"*"--json changedFiles"*) echo "$n" ;;
  *"pr view"*"--json title"*) echo "docs: bulk update" ;;
  *"pr view"*"--json body"*) echo "Closes #1" ;;
  *"pr view"*"--json labels"*) echo "" ;;
  *"pr comment"*) echo "$args" >> "${FAKE_COMMENT_LOG:?}" ;;
  *"issue view"*) echo "Touches tests/target_file.py" ;;
  *"/pulls/"*"/files"*)
    cap=$(( n < 3000 ? n : 3000 ))
    if [[ "$args" == *"--paginate"* ]]; then emit_files "$cap"
    else emit_files $(( cap < 100 ? cap : 100 )); fi ;;
  *"/pulls/"*"/commits"*) printf 'alice\tfix: something\n' ;;
  *) echo "unexpected gh call: $args" >&2; exit 99 ;;
esac
"""


def _guard_script() -> str:
    run = "\n".join(str(s.get("run", "")) for s in _steps())
    return run.replace("${{ github.actor }}", "tester")


def _run_guard(tmp_path: Path, changed_files: int, target_index: int) -> tuple[int, str]:
    bindir = tmp_path / "bin"
    bindir.mkdir()
    gh = bindir / "gh"
    gh.write_text(FAKE_GH, encoding="utf-8")
    gh.chmod(0o755)
    script = tmp_path / "guard.sh"
    script.write_text(_guard_script(), encoding="utf-8")
    comments = tmp_path / "comments.log"
    env = {
        "PATH": f"{bindir}:/usr/bin:/bin",
        "PR": "7",
        "REPO": "o/r",
        "GH_TOKEN": "x",
        "FAKE_CHANGED_FILES": str(changed_files),
        "FAKE_TARGET_INDEX": str(target_index),
        "FAKE_COMMENT_LOG": str(comments),
    }
    proc = subprocess.run(
        [shutil.which("bash") or "/bin/bash", str(script)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    log = comments.read_text(encoding="utf-8") if comments.exists() else ""
    return proc.returncode, proc.stdout + proc.stderr + log


def test_rule_3_lists_files_via_paginated_rest_api() -> None:
    script = _guard_script()
    assert re.search(r'gh api --paginate "repos/\$REPO/pulls/\$PR/files"', script)


def test_no_gh_pr_view_json_files_remains() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert not re.search(r"gh pr view[^\n]*--json\s+files\b", text)


def test_rule_3_truncation_at_rest_cap_is_handled_explicitly() -> None:
    script = _guard_script()
    assert "3000" in script or "3,000" in script


def test_rule_3_finds_issue_path_past_file_100(tmp_path: Path) -> None:
    code, out = _run_guard(tmp_path, changed_files=141, target_index=141)
    assert code == 0, out
    assert "Rule 3" not in out


def test_rule_3_still_fails_when_path_truly_absent(tmp_path: Path) -> None:
    code, out = _run_guard(tmp_path, changed_files=141, target_index=100000)
    assert code == 1
    assert "Rule 3" in out


def test_rule_3_fails_closed_above_rest_cap(tmp_path: Path) -> None:
    code, out = _run_guard(tmp_path, changed_files=REST_FILE_CAP + 1, target_index=REST_FILE_CAP)
    assert code == 1
    assert "Rule 3" in out
    assert "3,000" in out
