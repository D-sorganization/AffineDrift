"""The workflow-file gate must not demand ``timeout-minutes`` from a reusable caller (#5853).

GitHub allows only a fixed set of keywords on a job that calls a reusable workflow and
``timeout-minutes`` is not one of them, so ``pr-body-lint.yml`` could never satisfy the
gate: keeping the key fails every run with 0 jobs, dropping it fails the lint. The called
workflow owns the timeout, so the gate has to recognise a caller-only workflow.
"""

from __future__ import annotations

import functools
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

pytestmark = [pytest.mark.integration, pytest.mark.headless_safe]

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
LINTER = WORKFLOWS / "lint-workflow-files.yml"
STEP_NAME = "Require timeout-minutes, concurrency, cancel-in-progress"

# A shell function takes precedence over a PATH lookup, so the gate stays hermetic.
GH_STUB = """gh() { printf '%s\\n' "$*" >> comments.log; }
"""

CALLER_ONLY = """name: Caller
on:
  pull_request_target:
    types: [opened]
concurrency:
  group: caller-${{ github.event.pull_request.number }}
  cancel-in-progress: true
jobs:
  lint:
    uses: D-sorganization/Repository_Management/.github/workflows/reusable-thing.yml@3b5e9f54febbd730bc2a650dc9193d26922ff49f
    with:
      pr_number: ${{ github.event.pull_request.number }}
"""

INLINE_ONLY = """name: Inline
on:
  pull_request:
concurrency:
  group: inline-${{ github.ref }}
  cancel-in-progress: true
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1
"""

CALLER_WITH_INLINE = """name: Mixed
on:
  pull_request:
concurrency:
  group: mixed-${{ github.ref }}
  cancel-in-progress: true
jobs:
  lint:
    uses: D-sorganization/fleet-workflows/.github/workflows/reusable-thing.yml@367b182c24ae3b01488fc1266130969e775023de
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1
"""

CALLER_WITHOUT_CONCURRENCY = """name: Naked caller
on:
  pull_request:
jobs:
  lint:
    uses: D-sorganization/fleet-workflows/.github/workflows/reusable-thing.yml@367b182c24ae3b01488fc1266130969e775023de
"""


def _candidates() -> list[str]:
    names: list[str] = []
    git = shutil.which("git")
    if git:
        # Git for Windows ships bash next to cmd/git.exe and it is the one bash here.
        names.append(str(Path(git).parents[1] / "bin" / "bash.exe"))
    found = shutil.which("bash")
    if found:
        names.append(found)
    names += ["/bin/bash", "/usr/bin/bash"]
    return names


@functools.lru_cache(maxsize=1)
def _usable_bash() -> str | None:
    """First bash that actually runs a command.

    ``where bash`` on Windows resolves to the WSL launcher, which can be present and
    completely broken; a probe keeps the gate honest instead of testing noise.
    """
    for candidate in _candidates():
        try:
            probe = subprocess.run(
                [candidate, "--norc", "-c", "exit 0"], capture_output=True, check=False, timeout=20
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if probe.returncode == 0:
            return candidate
    return None


def _lint_script() -> str:
    """The gate's own bash, lifted from the workflow so the test cannot drift from CI."""
    steps = yaml.safe_load(LINTER.read_text(encoding="utf-8"))["jobs"]["lint"]["steps"]
    run = next(str(step["run"]) for step in steps if step.get("name") == STEP_NAME)
    # Actions interpolates these before bash ever sees them.
    return GH_STUB + re.sub(r"\$\{\{[^}]*\}\}", "stubbed", run)


def _gate(tmp_path: Path, fixtures: dict[str, str]) -> tuple[int, str, str]:
    bash = _usable_bash()
    if bash is None:
        pytest.skip("no working bash on this host")
    for name, body in fixtures.items():
        (tmp_path / name).write_text(body, encoding="utf-8")
    # The gh stub is a shell function, so inheriting the environment cannot leak a
    # real call to GitHub; wiping it instead stops Git bash from starting on Windows.
    env = os.environ.copy()
    env["FILES"] = "\n".join(fixtures) + "\n"
    proc = subprocess.run(
        [bash, "--norc", "-s"],
        cwd=tmp_path,
        env=env,
        input=_lint_script(),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    log_path = tmp_path / "comments.log"
    log = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    return proc.returncode, proc.stdout + proc.stderr, log


def test_caller_only_workflow_needs_no_timeout_minutes(tmp_path: Path) -> None:
    """The timeout lives in the called workflow, so the caller must not be asked for it."""
    code, out, _ = _gate(tmp_path, {"caller.yml": CALLER_ONLY})

    assert code == 0, out
    assert "missing timeout-minutes" not in out


def test_real_pr_body_lint_caller_passes_the_gate(tmp_path: Path) -> None:
    """#5853 end to end: the caller that started this now passes unchanged."""
    source = (WORKFLOWS / "pr-body-lint.yml").read_text(encoding="utf-8")
    code, out, _ = _gate(tmp_path, {"pr-body-lint.yml": source})

    assert code == 0, out
    assert "missing timeout-minutes" not in out


def test_inline_job_still_requires_timeout_minutes(tmp_path: Path) -> None:
    """Exempting callers must not relax the rule for jobs that can set the key."""
    code, out, log = _gate(tmp_path, {"inline.yml": INLINE_ONLY})

    assert code == 1
    assert "missing timeout-minutes" in out
    assert "inline.yml" in out
    assert "pr comment" in log


def test_mixed_caller_and_inline_job_still_requires_timeout_minutes(tmp_path: Path) -> None:
    """One inline job is enough to keep the requirement on the whole file."""
    code, out, _ = _gate(tmp_path, {"mixed.yml": CALLER_WITH_INLINE})

    assert code == 1
    assert "missing timeout-minutes" in out


def test_caller_exempt_still_requires_concurrency(tmp_path: Path) -> None:
    """The exemption covers the timeout only; protections stay enforced."""
    code, out, _ = _gate(tmp_path, {"naked.yml": CALLER_WITHOUT_CONCURRENCY})

    assert code == 1
    assert "missing concurrency block" in out
    assert "missing timeout-minutes" not in out


def test_every_shipped_workflow_passes_the_gate(tmp_path: Path) -> None:
    """No workflow in the repository may rely on a rule the gate cannot satisfy."""
    fixtures = {p.name: p.read_text(encoding="utf-8") for p in sorted(WORKFLOWS.glob("*.y*ml"))}
    assert fixtures, "no workflows found"
    code, out, _ = _gate(tmp_path, fixtures)

    assert code == 0, out
