#!/usr/bin/env python3
"""Fail when GitHub Actions workflows can route to hosted runners."""

from __future__ import annotations

from pathlib import Path

WORKFLOW_DIR = Path(".github") / "workflows"
BANNED = (
    "ubuntu-latest",
    "windows-latest",
    "macos-latest",
    "force_cloud",
    "mode=cloud",
    "Routing to GitHub-hosted",
    "using GitHub-hosted",
    "runner=ubuntu-latest",
    "runner=windows-latest",
    "runner=macos-latest",
)

# Files allowlisted from the hosted-runner scan. The tripwire workflow
# intentionally runs on a hosted runner; everything else must stay local.
LEGACY_HOSTED_RUNNER_ALLOWLIST = {
    ".github/workflows/local-only-runner-guard.yml",
}


def scan_workflow_text(path_label: str, text: str) -> list[str]:
    """Return banned-token findings for a single workflow's text.

    Pure helper (no filesystem) so the runner-routing gate is unit-testable.
    ``path_label`` is used only for human-readable finding messages.
    """
    findings: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for token in BANNED:
            if token in line:
                findings.append(f"{path_label}:{line_number}: banned hosted-runner token {token!r}")
    return findings


def main() -> int:
    """Scan workflow files and fail if any can route to hosted runners.

    Returns ``0`` when every workflow is local-only (or the workflow directory
    is absent) and ``1`` when at least one offending workflow is found.
    """
    failures: list[str] = []
    if not WORKFLOW_DIR.exists():
        return 0

    for path in sorted(WORKFLOW_DIR.rglob("*")):
        if path.suffix not in {".yml", ".yaml"}:
            continue

        if path.as_posix() in LEGACY_HOSTED_RUNNER_ALLOWLIST:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8-sig")
        failures.extend(scan_workflow_text(path.as_posix(), text))

    if failures:
        print("GitHub-hosted runner routing is forbidden. Use local self-hosted runners only.")
        print("\n".join(failures))
        return 1

    print("Workflow runner routing is local-only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
