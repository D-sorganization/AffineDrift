from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .models import MypyError


def run_mypy(config_file: str | None = None, targets: list[str] | None = None) -> str:
    """Run mypy and return raw output."""
    if not targets:
        # Default to src and tests if no targets provided, but check if they exist
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
    # Show error codes for targeted fixes
    cmd.append("--show-error-codes")
    # Add non-interactive and ignore-missing-imports for agent use
    cmd.extend(["--ignore-missing-imports", "--non-interactive"])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    return result.stdout + result.stderr


def parse_mypy_output(output: str) -> list[MypyError]:
    """Parse mypy output into structured errors."""
    errors = []
    # Pattern: file.py:line:col: severity: message  [error-code]
    pattern = re.compile(
        r"^(.+?):(\d+):(\d+):\s+(error|note):\s+(.+?)(?:\s+\[([^\]]+)\])?\s*$"
    )
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
