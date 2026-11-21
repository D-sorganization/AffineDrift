#!/usr/bin/env python3
"""Static checks and optional live dry-run for label-merge-guard.yml."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "label-merge-guard.yml"
HOLD_LABEL = "do-not-merge"
AUTOMATE_LABEL = "do-not-automate"


def _load_workflow() -> dict[str, Any]:
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{WORKFLOW}: expected mapping at root")
    return data


def static_validate() -> list[str]:
    """Return human-readable violations; empty means pass."""
    errors: list[str] = []
    if not WORKFLOW.is_file():
        return [f"missing workflow file: {WORKFLOW}"]

    data = _load_workflow()
    triggers = data.get(True) or data.get("on")
    if not isinstance(triggers, dict):
        errors.append("on: must declare pull_request, merge_group, and issues")
        return errors

    pr_types = triggers.get("pull_request")
    if not isinstance(pr_types, dict):
        pr_types = {"types": pr_types} if isinstance(pr_types, list) else {}
    types = pr_types.get("types") if isinstance(pr_types, dict) else None
    for required in ("opened", "synchronize", "labeled", "unlabeled"):
        if not isinstance(types, list) or required not in types:
            errors.append(f"pull_request.types must include {required!r}")

    if "merge_group" not in triggers:
        errors.append("on.merge_group trigger is required for merge-queue enforcement")

    issue_types = triggers.get("issues")
    if not isinstance(issue_types, dict) or "closed" not in (issue_types.get("types") or []):
        errors.append("issues.types must include 'closed'")

    jobs = data.get("jobs") or {}
    merge_job = jobs.get("block-do-not-merge") if isinstance(jobs, dict) else None
    if not isinstance(merge_job, dict):
        errors.append("jobs.block-do-not-merge is required")
    else:
        script = _step_scripts(merge_job)
        if HOLD_LABEL not in script:
            errors.append("block-do-not-merge step must reference do-not-merge")
        if "merge_group" not in script and "MERGE_HEAD_REF" not in script:
            errors.append("block-do-not-merge must resolve PRs on merge_group")
        if re.search(r"github\.event\.pull_request", script):
            errors.append("block-do-not-merge run: must not interpolate github.event.pull_request")

    protect = jobs.get("protect-do-not-automate") if isinstance(jobs, dict) else None
    if not isinstance(protect, dict):
        errors.append("jobs.protect-do-not-automate is required")
    else:
        script = _step_scripts(protect)
        if AUTOMATE_LABEL not in script:
            errors.append("protect-do-not-automate must reference do-not-automate")
        if "issue reopen" not in script.lower() and "gh issue reopen" not in script:
            errors.append("protect-do-not-automate must reopen issues")

    if not data.get("concurrency"):
        errors.append("concurrency block is required")
    if not re.search(r"cancel-in-progress:\s*true", WORKFLOW.read_text(encoding="utf-8")):
        errors.append("cancel-in-progress: true is required")

    return errors


def _step_scripts(job: dict[str, Any]) -> str:
    parts: list[str] = []
    for step in job.get("steps") or []:
        if isinstance(step, dict) and isinstance(step.get("run"), str):
            parts.append(step["run"])
    return "\n".join(parts)


def live_pr_check(repo: str, pr: int) -> int:
    """Print JSON verdict for a PR's do-not-merge state (requires gh)."""
    proc = subprocess.run(
        ["gh", "pr", "view", str(pr), "--repo", repo, "--json", "labels,number,title"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return 1
    payload = json.loads(proc.stdout)
    names = {str(item.get("name", "")).lower() for item in payload.get("labels") or []}
    blocked = HOLD_LABEL in names
    out = {
        "repo": repo,
        "pr": pr,
        "title": payload.get("title"),
        "blocked_by_do_not_merge": blocked,
        "workflow_would_fail": blocked,
    }
    print(json.dumps(out, indent=2))
    return 0 if not blocked else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live-pr",
        nargs=2,
        metavar=("OWNER/REPO", "PR"),
        help="Optional gh-backed check for do-not-merge on a pull request",
    )
    args = parser.parse_args()

    errors = static_validate()
    if errors:
        for item in errors:
            print(f"static: {item}", file=sys.stderr)
        return 1
    print("static: label-merge-guard.yml structure OK")

    if args.live_pr:
        repo, pr_s = args.live_pr
        return live_pr_check(repo, int(pr_s))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
