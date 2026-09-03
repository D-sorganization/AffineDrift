"""Validate repository root hygiene against strict allowlists."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path, PurePosixPath

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.cli_output import write_stderr, write_stdout

REPO_ROOT = Path(__file__).resolve().parents[1]

# Allowed tracked files at the repository root
ALLOWED_TRACKED_ROOT_FILES: frozenset[str] = frozenset(
    {
        ".dockerignore",
        ".env.example",
        ".gitattributes",
        ".gitignore",
        ".gitleaksignore",
        ".htmlvalidate.json",
        ".htmlvalidateignore",
        ".nojekyll",
        ".pre-commit-config.yaml",
        ".pre-commit-hooks.yaml",
        ".prettierignore",
        ".python-version",
        ".quarto-version",
        ".quartoignore",
        ".stylelintignore",
        "404.qmd",
        "AGENTS.md",
        "AGENT_HANDOFF.md",
        "CHANGELOG.md",
        "CLAUDE.md",
        "CNAME",
        "CONTRIBUTING.md",
        "COPYRIGHT.md",
        "Dockerfile",
        "LICENSE",
        "Makefile",
        "NOTATION.md",
        "PARAMETERS.md",
        "README.md",
        "SECURITY.md",
        "SPEC.md",
        "VERSION",
        "_quarto.yml",
        "babel.config.js",
        "custom.scss",
        "docker-compose.yml",
        "favicon.ico",
        "feed.xml",
        "index.qmd",
        "jest.config.js",
        "listings.json",
        "manifest.json",
        "offline.html",
        "package-lock.json",
        "package.json",
        "playwright.config.js",
        "preview-articles.sh",
        "pyproject.toml",
        "requirements-benchmarks.txt",
        "requirements-docker.lock",
        "requirements.txt",
        "robots.txt",
        "service-worker.js",
        "sitemap.xml",
        "start-gaai-daemon.sh",
        "start-preview.sh",
        "stylelint.config.mjs",
        "styles.css",
    }
)

# Allowed tracked directories at the repository root
ALLOWED_TRACKED_ROOT_DIRECTORIES: frozenset[str] = frozenset(
    {
        ".Jules",
        ".benchmarks",
        ".claude",
        ".gaai",
        ".github",
        ".jules",
        ".vscode",
        "_includes",
        "_templates",
        "articles",
        "assessments",
        "benchmarks",
        "books",
        "config",
        "content",
        "content-development",
        "critiques",
        "css",
        "data",
        "docs",
        "js",
        "legacy-pages",
        "logo",
        "models",
        "notebooks",
        "pages",
        "pics",
        "references",
        "reports",
        "repositories",
        "resources",
        "schemas",
        "scripts",
        # Fleet-shared modules synced from Repository_Management
        # (Repository_Management#1520).
        "shared_scripts",
        "src",
        "static",
        "tests",
        "tools",
    }
)

# Forbidden scratch or review artifacts that must never appear at repo root
FORBIDDEN_ROOT_FILES: frozenset[str] = frozenset(
    {
        ".ci_trigger.py",
        "AffineDrift_Content_Review_Instructions.docx",
        "Geometry_of_Motion_Volume_0.pdf",
        "ISSUE_content_loss_ch09.md",
        "PR_AGRACHEV_INTEGRATION.md",
        "PR_DESCRIPTION.md",
        "The_Geometry_of_Motion_Complete.pdf",
        "The_Physics_of_Golf.pdf",
        "TURNOVER_PROMPT.md",
        "brute_merge.ps1",
        "magic_numbers_report.txt",
        "main.pdf",
        "notes_workspace_escape.png",
        "pr_body.txt",
        "replace.patch",
        "ruff_errors.txt",
        "test.diff",
        "test_bibliography_perf.js",
        "test_notes.html",
        "tmp1.tmp",
        "uv.lock",
    }
)

# Forbidden directories that must never appear at repo root
FORBIDDEN_ROOT_DIRECTORIES: frozenset[str] = frozenset(
    {
        ".agent",
        ".tmp_issue_bodies",
        "deploy",
        "tmp_issue_bodies",
    }
)

# Local development and build caches permitted on disk (untracked)
PERMITTED_LOCAL_CACHES: frozenset[str] = frozenset(
    {
        ".coverage",
        ".git",
        ".hypothesis",
        ".mypy_cache",
        ".pytest_cache",
        ".quarto",
        ".ruff_cache",
        "coverage.json",
        "coverage.xml",
        "node_modules",
        "playwright-report",
        "test-results",
    }
)


def list_tracked_root_items() -> tuple[set[str], set[str]]:
    """Return tracked root files and top-level directories using Git index."""
    result = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    tracked_files: set[str] = set()
    tracked_dirs: set[str] = set()

    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        pure = PurePosixPath(line)
        parts = pure.parts
        if len(parts) == 1:
            tracked_files.add(parts[0])
        elif len(parts) > 1:
            tracked_dirs.add(parts[0])

    return tracked_files, tracked_dirs


def check_tracked_allowlist() -> list[str]:
    """Verify that all tracked root files and directories are explicitly allowlisted."""
    findings: list[str] = []
    tracked_files, tracked_dirs = list_tracked_root_items()

    unexpected_files = sorted(tracked_files - ALLOWED_TRACKED_ROOT_FILES)
    for name in unexpected_files:
        findings.append(f"Tracked root file not in allowlist: {name}")

    unexpected_dirs = sorted(tracked_dirs - ALLOWED_TRACKED_ROOT_DIRECTORIES)
    for name in unexpected_dirs:
        findings.append(f"Tracked root directory not in allowlist: {name}")

    return findings


def check_forbidden_artifacts_on_disk() -> list[str]:
    """Verify that forbidden artifacts or directories do not exist on disk."""
    findings: list[str] = []

    for item in REPO_ROOT.iterdir():
        name = item.name
        if item.is_file():
            if name in FORBIDDEN_ROOT_FILES:
                findings.append(f"Forbidden root file present on disk: {name}")
            elif name not in ALLOWED_TRACKED_ROOT_FILES and name not in PERMITTED_LOCAL_CACHES:
                findings.append(f"Unallowlisted file present at repo root: {name}")
        elif item.is_dir():
            if name in FORBIDDEN_ROOT_DIRECTORIES:
                findings.append(f"Forbidden root directory present on disk: {name}")
            elif (
                name not in ALLOWED_TRACKED_ROOT_DIRECTORIES and name not in PERMITTED_LOCAL_CACHES
            ):
                findings.append(f"Unallowlisted directory present at repo root: {name}")

    return findings


def run_checks() -> list[str]:
    """Execute all root hygiene checks and return all findings."""
    findings: list[str] = []
    findings.extend(check_tracked_allowlist())
    findings.extend(check_forbidden_artifacts_on_disk())
    return findings


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for root hygiene verification."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run in verify mode and exit non-zero on violations",
    )
    parser.parse_args(argv)

    findings = run_checks()
    if findings:
        for finding in findings:
            write_stderr(f"HYGIENE ERROR: {finding}")
        write_stderr(f"Total violations: {len(findings)}")
        return 1

    write_stdout("Repository root hygiene verified: all items match allowlist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
