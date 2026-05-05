"""Verify GitHub Actions references are pinned to immutable commit SHAs."""

from __future__ import annotations

import re
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.cli_output import write_stderr, write_stdout

WORKFLOW_DIR = Path(".github/workflows")
USES_PATTERN = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)")
FULL_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def find_unpinned_actions(workflow_dir: Path = WORKFLOW_DIR) -> list[str]:
    """Return workflow action references that are not pinned to full SHAs."""
    findings: list[str] = []
    workflow_paths = sorted(workflow_dir.glob("*.yml")) + sorted(workflow_dir.glob("*.yaml"))

    for workflow_path in workflow_paths:
        for line_number, line in enumerate(
            workflow_path.read_text(encoding="utf-8").splitlines(), 1
        ):
            match = USES_PATTERN.match(line)
            if not match:
                continue

            reference = match.group(1)
            if reference.startswith("./") or reference.startswith("docker://"):
                continue

            if "@" not in reference:
                findings.append(f"{workflow_path}:{line_number}: missing @ref in {reference}")
                continue

            ref = reference.rsplit("@", 1)[1]
            if not FULL_SHA_PATTERN.fullmatch(ref):
                findings.append(f"{workflow_path}:{line_number}: pin {reference} to a 40-char SHA")

    return findings


def main() -> int:
    """Run the workflow pin policy check."""
    findings = find_unpinned_actions()
    if findings:
        for finding in findings:
            write_stderr(finding)
        return 1

    write_stdout("All workflow actions are pinned to immutable SHAs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
