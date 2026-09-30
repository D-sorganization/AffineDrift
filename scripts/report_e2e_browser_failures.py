"""Turn nightly cross-browser Playwright JSON reports into deduplicated issues.

Reads one or more Playwright JSON reporter files (one per browser project),
finds tests whose final status is a real failure, and opens a GitHub issue per
distinct (browser, test title) pair -- skipping any pair already covered by an
open issue, since the title itself is the dedup key.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections.abc import Iterable, Iterator
from pathlib import Path

from scripts.cli_output import write_stdout

ISSUE_TITLE_PREFIX = "[Cross-Browser Nightly]"
ISSUE_LABELS = ("ci", "cross-browser", "automation")


def iter_failed_specs(report: dict) -> Iterator[dict[str, str]]:
    """Yield one entry per test whose final verdict was an unexpected failure."""
    for suite in report.get("suites", []):
        yield from _iter_suite_failures(suite)


def _iter_suite_failures(suite: dict, inherited_file: str = "") -> Iterator[dict[str, str]]:
    file = suite.get("file") or inherited_file
    for spec in suite.get("specs", []):
        for test in spec.get("tests", []):
            if test.get("status") == "unexpected":
                yield {
                    "title": spec.get("title", ""),
                    "project": test.get("projectName", ""),
                    "file": file,
                }
    for nested in suite.get("suites", []):
        yield from _iter_suite_failures(nested, inherited_file=file)


def build_issue_title(project: str, spec_title: str) -> str:
    """Return the dedup key: the same (browser, test) always maps to one title."""
    return f"{ISSUE_TITLE_PREFIX} {project}: {spec_title}"


def build_issue_body(failure: dict[str, str], run_url: str) -> str:
    """Return the issue body describing one failure."""
    lines = [
        f"The nightly cross-browser E2E job found a failure on **{failure['project']}**.",
        "",
        f"- **Test:** `{failure['title']}`",
        f"- **File:** `{failure['file']}`",
        f"- **Run:** {run_url}",
        "",
        "Opened automatically. If this test fails again on the same browser after "
        "this issue is closed, a new issue will be opened for it.",
    ]
    return "\n".join(lines)


def select_new_failures(
    failures: Iterable[dict[str, str]], existing_titles: Iterable[str]
) -> list[dict[str, str]]:
    """Return failures not already covered by an open issue, deduped by title."""
    seen = set(existing_titles)
    selected: list[dict[str, str]] = []
    for failure in failures:
        title = build_issue_title(failure["project"], failure["title"])
        if title in seen:
            continue
        seen.add(title)
        selected.append(failure)
    return selected


def load_report(path: Path) -> dict:
    """Load a single Playwright JSON reporter file."""
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_existing_open_titles(repo: str) -> list[str]:
    """Return titles of open issues previously filed by this reporter."""
    result = subprocess.run(  # noqa: S603 -- gh CLI with fixed, trusted arguments
        [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--label",
            "cross-browser",
            "--json",
            "title",
            "--limit",
            "200",
        ],  # noqa: S607 -- relies on gh being on PATH, matching scripts/create_issues.py
        check=True,
        capture_output=True,
        text=True,
    )
    return [item["title"] for item in json.loads(result.stdout)]


def create_issue(repo: str, title: str, body: str) -> None:
    """Open a GitHub issue for one failure using the gh CLI."""
    subprocess.run(  # noqa: S603 -- gh CLI with fixed, trusted arguments
        [
            "gh",
            "issue",
            "create",
            "--repo",
            repo,
            "--title",
            title,
            "--body",
            body,
            "--label",
            ",".join(ISSUE_LABELS),
        ],  # noqa: S607 -- relies on gh being on PATH, matching scripts/create_issues.py
        check=True,
    )


def main(argv: list[str] | None = None) -> int:
    """Report and file issues for cross-browser E2E failures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        action="append",
        required=True,
        help="Path to a Playwright JSON reporter file; repeatable, one per browser.",
    )
    parser.add_argument("--repo", required=True, help="OWNER/REPO to file issues against.")
    parser.add_argument("--run-url", required=True, help="Link to the workflow run.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the issues that would be created without calling gh.",
    )
    args = parser.parse_args(argv)

    failures: list[dict[str, str]] = []
    for report_path in args.report:
        failures.extend(iter_failed_specs(load_report(Path(report_path))))

    if not failures:
        write_stdout("No cross-browser E2E failures found.")
        return 0

    existing_titles = fetch_existing_open_titles(args.repo)
    new_failures = select_new_failures(failures, existing_titles)

    if not new_failures:
        write_stdout(f"{len(failures)} failure(s) found; all already tracked by open issues.")
        return 0

    for failure in new_failures:
        title = build_issue_title(failure["project"], failure["title"])
        body = build_issue_body(failure, args.run_url)
        if args.dry_run:
            write_stdout(f"Would create issue: {title}")
            continue
        write_stdout(f"Creating issue: {title}")
        create_issue(args.repo, title, body)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
