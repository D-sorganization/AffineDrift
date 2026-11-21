"""Backward-compatible entry point; canonical generator is scripts/build_launch_monitor_figures.py."""

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]

if __name__ == "__main__":
    subprocess.check_call(  # noqa: S603 -- reason: fixed argv, no shell
        [sys.executable, str(_REPO_ROOT / "scripts" / "build_launch_monitor_figures.py")],
        cwd=_REPO_ROOT,
    )
