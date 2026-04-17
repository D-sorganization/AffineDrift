from __future__ import annotations

from pathlib import Path

from scripts.check_self_hosted_timeouts import find_timeout_violations


def _write_workflow(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_reports_fleet_job_without_timeout(tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    _write_workflow(
        workflow_dir / "missing.yml",
        """
name: Missing Timeout
jobs:
  pdf:
    runs-on: d-sorg-fleet
    steps:
      - run: echo slow
""",
    )

    assert find_timeout_violations(workflow_dir) == [
        f"{workflow_dir / 'missing.yml'}:pdf must set timeout-minutes to an integer between 1 and 120"
    ]


def test_accepts_bounded_fleet_timeout(tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    _write_workflow(
        workflow_dir / "bounded.yml",
        """
name: Bounded
jobs:
  render:
    runs-on: [self-hosted, d-sorg-fleet]
    timeout-minutes: 45
    steps:
      - run: echo ok
""",
    )

    assert find_timeout_violations(workflow_dir) == []


def test_ignores_github_hosted_jobs(tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    _write_workflow(
        workflow_dir / "hosted.yml",
        """
name: Hosted
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo ok
""",
    )

    assert find_timeout_violations(workflow_dir) == []
