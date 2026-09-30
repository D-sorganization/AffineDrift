"""Turn nightly cross-browser Playwright JSON reports into deduplicated issues.

Reads one or more Playwright JSON reporter files (one per browser project),
finds tests whose final status is a real failure, and opens a GitHub issue per
distinct (browser, test title) pair -- skipping any pair already covered by an
open issue, since the title itself is the dedup key.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from pathlib import Path

from scripts.cli_output import write_stdout

ISSUE_TITLE_PREFIX = "[Cross-Browser Nightly]"
# "cross-browser" does not exist as a label in the repo and must never be
# created by this script; only labels that already exist are used.
ISSUE_LABELS = ("ci", "automation")
MISSING_REPORT_TITLE = "no test report produced (job failed before tests ran)"
MAX_INDIVIDUAL_ISSUES = 5
_REPORT_FILENAME_RE = re.compile(r"^playwright-report-(.+)\.json$")


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


def build_summary_issue_title(count: int, date: str) -> str:
    """Return the title for the single rollup issue opened when too many land at once."""
    return f"{ISSUE_TITLE_PREFIX} {count} failures on {date}"


def build_summary_issue_body(failures: list[dict[str, str]], run_url: str) -> str:
    """Return the body listing every failure folded into one summary issue."""
    lines = [
        f"The nightly cross-browser E2E job found {len(failures)} failing tests in one "
        "run -- filing them individually would be noisy, so they are rolled up into "
        "this single issue instead.",
        "",
        f"- **Run:** {run_url}",
        "",
        "| Browser | Test | File |",
        "| --- | --- | --- |",
    ]
    for failure in failures:
        lines.append(f"| {failure['project']} | `{failure['title']}` | `{failure['file']}` |")
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


def derive_project_from_report_path(path: Path) -> str:
    """Return the browser project name encoded in a report filename.

    Falls back to the filename stem when it does not match the expected
    ``playwright-report-<browser>.json`` shape, so an unexpected path still
    yields a usable (if less precise) project label instead of failing.
    """
    match = _REPORT_FILENAME_RE.match(path.name)
    return match.group(1) if match else path.stem


def missing_report_failure(path: Path) -> dict[str, str]:
    """Return the single synthetic failure entry for a missing/unreadable report."""
    return {
        "title": MISSING_REPORT_TITLE,
        "project": derive_project_from_report_path(path),
        "file": str(path),
    }


def load_report_failures(path: Path) -> list[dict[str, str]]:
    """Return failures from one Playwright JSON report.

    A missing file, an empty file, or unparseable JSON all mean the browser
    job died before producing real results -- each of those must surface as a
    failure entry for that browser rather than crashing this script or
    silently dropping the browser from the run.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return [missing_report_failure(path)]

    if not text.strip():
        return [missing_report_failure(path)]

    try:
        report = json.loads(text)
    except json.JSONDecodeError:
        return [missing_report_failure(path)]

    return list(iter_failed_specs(report))


def filter_cross_browser_titles(titles: Iterable[str]) -> list[str]:
    """Keep only titles that are actually this reporter's issues.

    ``gh issue list --search`` matches the query text anywhere it appears
    (case-insensitively), so this is a defensive check against a title that
    merely mentions the prefix rather than being one of this reporter's own.
    """
    return [title for title in titles if title.startswith(ISSUE_TITLE_PREFIX)]


def fetch_existing_open_titles(repo: str) -> list[str]:
    """Return titles of open issues previously filed by this reporter.

    Filters by a title search rather than a label: the repo has no
    "cross-browser" label and this script must never create one.
    """
    result = subprocess.run(  # noqa: S603 -- gh CLI with fixed, trusted arguments
        [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--search",
            f'"{ISSUE_TITLE_PREFIX}" in:title',
            "--json",
            "title",
            "--limit",
            "200",
        ],  # noqa: S607 -- relies on gh being on PATH, matching scripts/create_issues.py
        check=True,
        capture_output=True,
        text=True,
    )
    raw_titles = [item["title"] for item in json.loads(result.stdout)]
    return filter_cross_browser_titles(raw_titles)


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
        failures.extend(load_report_failures(Path(report_path)))

    if not failures:
        write_stdout("No cross-browser E2E failures found.")
        return 0

    existing_titles = fetch_existing_open_titles(args.repo)
    new_failures = select_new_failures(failures, existing_titles)

    if not new_failures:
        write_stdout(f"{len(failures)} failure(s) found; all already tracked by open issues.")
        return 0

    if len(new_failures) > MAX_INDIVIDUAL_ISSUES:
        date = datetime.now(UTC).strftime("%Y-%m-%d")
        title = build_summary_issue_title(len(new_failures), date)
        body = build_summary_issue_body(new_failures, args.run_url)
        if args.dry_run:
            write_stdout(f"Would create issue: {title}")
        else:
            write_stdout(f"Creating issue: {title}")
            create_issue(args.repo, title, body)
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
