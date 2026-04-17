"""Require hard job timeouts for self-hosted GitHub Actions jobs."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

DEFAULT_WORKFLOW_DIR = Path(".github/workflows")
DEFAULT_MAX_TIMEOUT_MINUTES = 120
FLEET_LABEL = "d-sorg-fleet"


def _uses_fleet_runner(runs_on: Any) -> bool:
    if runs_on == FLEET_LABEL:
        return True
    if isinstance(runs_on, list):
        return FLEET_LABEL in runs_on
    return False


def _valid_timeout(value: Any, max_minutes: int) -> bool:
    return isinstance(value, int) and 0 < value <= max_minutes


def find_timeout_violations(
    workflow_dir: Path = DEFAULT_WORKFLOW_DIR,
    max_minutes: int = DEFAULT_MAX_TIMEOUT_MINUTES,
) -> list[str]:
    """Return fleet jobs that lack a bounded integer timeout."""
    violations: list[str] = []

    for path in sorted(workflow_dir.glob("*.yml")) + sorted(workflow_dir.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        jobs = data.get("jobs", {})
        if not isinstance(jobs, dict):
            continue

        for job_name, job in jobs.items():
            if not isinstance(job, dict) or not _uses_fleet_runner(job.get("runs-on")):
                continue
            timeout = job.get("timeout-minutes")
            if not _valid_timeout(timeout, max_minutes):
                violations.append(
                    f"{path}:{job_name} must set timeout-minutes to an integer "
                    f"between 1 and {max_minutes}"
                )

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify self-hosted GitHub Actions jobs have hard timeouts."
    )
    parser.add_argument(
        "--workflow-dir",
        type=Path,
        default=DEFAULT_WORKFLOW_DIR,
        help="Directory containing GitHub Actions workflow YAML files.",
    )
    parser.add_argument(
        "--max-minutes",
        type=int,
        default=DEFAULT_MAX_TIMEOUT_MINUTES,
        help="Largest allowed self-hosted job timeout.",
    )
    args = parser.parse_args()

    violations = find_timeout_violations(args.workflow_dir, args.max_minutes)
    if violations:
        print("Self-hosted runner timeout policy violations:")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print("All d-sorg-fleet jobs define bounded timeout-minutes values.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
