"""Block checked-in generated agent automation artifacts."""

from __future__ import annotations

import fnmatch
import subprocess
import sys
from pathlib import Path, PurePosixPath

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.cli_output import write_stderr, write_stdout

FORBIDDEN_TRACKED_PATTERNS = (
    ".agent/*",
    ".claude/settings.local.json",
    ".gaai/project/contexts/artefacts/*",
    ".gaai/project/contexts/backlog/.delivery-locks/*_run.sh",
    ".gaai/project/contexts/backlog/.delivery-locks/*.lock",
    ".gaai/project/contexts/backlog/.delivery-logs/[!.]*",
)


def list_tracked_files() -> list[str]:
    """Return tracked file paths using Git's repository index."""
    result = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [PurePosixPath(path).as_posix() for path in result.stdout.splitlines()]


def find_forbidden_agent_artifacts(paths: list[str]) -> list[str]:
    """Return tracked agent automation artifacts that must remain local-only."""
    return [
        path
        for path in paths
        if any(fnmatch.fnmatchcase(path, pattern) for pattern in FORBIDDEN_TRACKED_PATTERNS)
    ]


def main() -> int:
    """Run the generated agent automation artifact policy check."""
    findings = find_forbidden_agent_artifacts(list_tracked_files())
    if findings:
        for finding in findings:
            write_stderr(f"Generated agent automation artifact is tracked: {finding}")
        return 1

    write_stdout("No generated agent automation artifacts are tracked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
