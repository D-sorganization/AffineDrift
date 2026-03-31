"""I/O helpers for the Mypy Autofix Agent.

Handles running mypy as a subprocess, reading/writing Python source files,
and parsing raw mypy output into structured MypyError objects.
"""

from __future__ import annotations

import logging
import re
import subprocess
from pathlib import Path

from scripts.mypy_models import MypyError

logger = logging.getLogger(__name__)


def run_mypy(config_file: str | None = None, targets: list[str] | None = None) -> str:
    """Run mypy and return raw output.

    Args:
        config_file: Optional path to a mypy config file.
        targets: Directories/files to check.  Defaults to src/ + tests/.

    Returns:
        Combined stdout + stderr from mypy.
    """
    if not targets:
        targets = []
        if Path("src").exists():
            targets.append("src")
        if Path("tests").exists():
            targets.append("tests")
        if not targets:
            targets = ["."]

    cmd = ["mypy"] + targets + ["--no-error-summary"]
    if config_file:
        cmd.extend(["--config-file", config_file])
    cmd.append("--show-error-codes")
    cmd.extend(["--ignore-missing-imports", "--non-interactive"])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    return result.stdout + result.stderr


def parse_mypy_output(output: str) -> list[MypyError]:
    """Parse raw mypy output into a list of structured MypyError objects.

    Args:
        output: Raw text output from mypy.

    Returns:
        List of parsed errors (notes and errors without a code are dropped).
    """
    errors: list[MypyError] = []
    pattern = re.compile(r"^(.+?):(\d+):(\d+):\s+(error|note):\s+(.+?)(?:\s+\[([^\]]+)\])?\s*$")
    for line in output.splitlines():
        match = pattern.match(line.strip())
        if match:
            file_path, line_no, col, severity, message, code = match.groups()
            if severity == "error" and code:
                errors.append(
                    MypyError(
                        file=file_path,
                        line=int(line_no),
                        column=int(col),
                        severity=severity,
                        message=message,
                        code=code or "unknown",
                    )
                )
    return errors


def read_file_lines(filepath: str) -> list[str]:
    """Read a Python source file and return its lines (preserving newlines).

    Args:
        filepath: Path to the file.

    Returns:
        List of lines with newline characters intact, or [] if the file is absent.
    """
    path = Path(filepath)
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


def write_file_lines(filepath: str, lines: list[str]) -> None:
    """Write a list of lines back to a file.

    Args:
        filepath: Destination path.
        lines: Lines to write (should include newline characters).
    """
    Path(filepath).write_text("".join(lines), encoding="utf-8")


def is_safe_path(filepath: str) -> bool:
    """Return True if *filepath* is safe to modify.

    Only files inside src/ or tests/, with a .py extension, that are not in
    hidden directories, __pycache__, or vendor folders are considered safe.

    Args:
        filepath: File path to evaluate.

    Returns:
        True when the file may be modified by the agent.
    """
    path = Path(filepath)
    parts = path.parts
    if not any(p in ("src", "tests") for p in parts):
        return False
    if any(p.startswith(".") or p == "__pycache__" or p == "vendor" for p in parts):
        return False
    return path.suffix == ".py"
