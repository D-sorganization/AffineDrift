"""Contract and behavior tests for the shared CI apt bootstrap used by static-checks and E2E."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "ci" / "install_headless_system_deps.sh"

REQUIRED_SNIPPETS = (
    "DPkg::Lock::Timeout",
    "dl.google.com",
    "libasound2t64",
    "libasound2",
    "libgl1",
    "APT_INSTALL_OK",
)

FORBIDDEN_LOCK_PATHS = (
    "/var/lib/apt/lists/lock",
    "/var/cache/apt/archives/lock",
    "/var/lib/dpkg/lock",
)

SUDO_PROBE_FAIL = """#!/usr/bin/env bash
if [[ "$1" == "-n" && "$2" == "true" ]]; then
  exit 1
fi
exit 0
"""

SUDO_DELEGATE = """#!/usr/bin/env bash
if [[ "$1" == "-n" && "$2" == "true" ]]; then
  exit 0
fi
if [[ "$1" == "env" ]]; then
  shift
  exec "$@"
fi
exit 0
"""

APT_GET_ALWAYS_FAIL = """#!/usr/bin/env bash
exit 1
"""

APT_CACHE_MISSING_T64 = """#!/usr/bin/env bash
exit 1
"""

SLEEP_NOOP = """#!/usr/bin/env bash
exit 0
"""


def _run_with_mock_bins(
    tmp_path: Path,
    bins: Mapping[str, str],
    *,
    extra_env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    bindir = tmp_path / "bin"
    bindir.mkdir()
    for name, body in bins.items():
        script = bindir / name
        script.write_text(body, encoding="utf-8")
        script.chmod(0o755)
    env = {**os.environ, "PATH": f"{bindir}:{os.environ.get('PATH', '')}"}
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["/bin/bash", str(SCRIPT)],
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
        timeout=30,
        check=False,
    )


def test_install_headless_system_deps_script_exists() -> None:
    assert SCRIPT.is_file(), f"missing CI bootstrap script: {SCRIPT}"


def test_install_headless_system_deps_script_contract() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for snippet in REQUIRED_SNIPPETS:
        assert snippet in text, f"bootstrap script must mention {snippet!r}"


def test_install_headless_system_deps_never_unlinks_apt_lock_files() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for path in FORBIDDEN_LOCK_PATHS:
        assert path not in text, f"bootstrap script must not unlink apt/dpkg lock {path!r}"


def test_install_headless_system_deps_exits_when_sudo_unavailable(tmp_path: Path) -> None:
    result = _run_with_mock_bins(tmp_path, {"sudo": SUDO_PROBE_FAIL})
    assert result.returncode == 0
    assert "No passwordless sudo" in result.stdout


def test_install_headless_system_deps_warns_when_apt_update_never_succeeds(tmp_path: Path) -> None:
    result = _run_with_mock_bins(
        tmp_path,
        {
            "sudo": SUDO_DELEGATE,
            "apt-get": APT_GET_ALWAYS_FAIL,
            "apt-cache": APT_CACHE_MISSING_T64,
            "sleep": SLEEP_NOOP,
        },
    )
    assert result.returncode == 0
    assert "apt-get update could not complete" in result.stdout


def test_ci_standard_invokes_shared_bootstrap() -> None:
    workflow = REPO_ROOT / ".github" / "workflows" / "ci-standard.yml"
    text = workflow.read_text(encoding="utf-8")
    assert text.count("bash scripts/ci/install_headless_system_deps.sh") >= 2


def test_ci_standard_qt_step_never_unlinks_apt_lock_files() -> None:
    workflow = REPO_ROOT / ".github" / "workflows" / "ci-standard.yml"
    text = workflow.read_text(encoding="utf-8")
    marker = "name: Install Qt system libraries"
    start = text.index(marker)
    next_job = text.find("\n  tests:", start)
    qt_block = text[start:next_job] if next_job != -1 else text[start : start + 4000]
    for path in FORBIDDEN_LOCK_PATHS:
        assert (
            path not in qt_block
        ), f"Qt apt bootstrap in ci-standard.yml must not unlink apt/dpkg lock {path!r}"
