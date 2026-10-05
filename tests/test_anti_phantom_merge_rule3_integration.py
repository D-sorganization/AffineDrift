"""Rule 3 run end to end against a hermetic fake ``gh`` (AD#4935).

These tests spawn ``bash`` and write a fake binary to disk, so they are
integration tier; the static checks live in test_anti_phantom_merge_workflow.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from tests.test_anti_phantom_merge_workflow import _guard_script

pytestmark = [pytest.mark.integration, pytest.mark.headless_safe]

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
