"""Generate the content freshness report from page front matter (#4520, extends #4027).

Scans every rendered content page for a ``last-reviewed`` front-matter date and
reports which pages are stale: reviewed ``STALE_MONTHS`` or more months ago, or
never reviewed at all. The review date comes only from front matter -- never
from a file's mtime, git history, or the Quarto build/render date -- so an
unreviewed page is reported as unreviewed, not as freshly built.

Usage:
    python3 -m scripts.generate_freshness_report          # write the report
    python3 -m scripts.generate_freshness_report --check  # verify it is current
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from dataclasses import dataclass
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.cli_output import write_stderr, write_stdout
from src.tools.site_page_scan import find_content_pages, parse_front_matter

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / "reports/content-freshness.md"
STALE_MONTHS = 12
LAST_REVIEWED_KEY = "last-reviewed"
_REFERENCE_DATE_LINE = re.compile(r"^Reference date: (\d{4}-\d{2}-\d{2})\.", re.MULTILINE)


def _today() -> dt.date:
    """Return today's date; a seam so tests can control "today" without mocking stdlib."""
    return dt.date.today()


def _recorded_reference_date(output: Path) -> dt.date | None:
    """Return the reference date recorded in an already-generated report, if any."""
    if not output.is_file():
        return None
    match = _REFERENCE_DATE_LINE.search(output.read_text(encoding="utf-8"))
    return dt.date.fromisoformat(match.group(1)) if match else None


class FreshnessReportError(ValueError):
    """Raised when a page's review metadata cannot be trusted."""


@dataclass(frozen=True)
class FreshnessEntry:
    """One page's freshness state, derived only from its own front matter."""

    source_path: str
    route: str
    last_reviewed: dt.date | None
    months_since_review: int | None
    is_stale: bool


def months_since(reference: dt.date, reviewed: dt.date) -> int:
    """Return the count of whole calendar months between reviewed and reference."""
    months = (reference.year - reviewed.year) * 12 + (reference.month - reviewed.month)
    if reference.day < reviewed.day:
        months -= 1
    return max(months, 0)


def _coerce_review_date(value: object, source_path: str) -> dt.date | None:
    """Return the review date from a front-matter value, or None when absent."""
    if value is None:
        return None
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(str(value))
    except ValueError as exc:
        raise FreshnessReportError(
            f"{source_path}: {LAST_REVIEWED_KEY!r} is not an ISO date: {value!r}"
        ) from exc


def _route_for(rel: Path) -> str:
    """Map a page's repository-relative path to its public route."""
    return "/" + rel.with_suffix(".html").as_posix()


def scan_pages(root: Path, reference_date: dt.date) -> list[FreshnessEntry]:
    """Return a freshness entry for every rendered content page, sorted by path."""
    entries = []
    for page in find_content_pages(root):
        rel = page.relative_to(root)
        front_matter = parse_front_matter(page.read_text(encoding="utf-8", errors="ignore"))
        reviewed = _coerce_review_date(front_matter.get(LAST_REVIEWED_KEY), rel.as_posix())
        months = None if reviewed is None else months_since(reference_date, reviewed)
        entries.append(
            FreshnessEntry(
                source_path=rel.as_posix(),
                route=_route_for(rel),
                last_reviewed=reviewed,
                months_since_review=months,
                is_stale=reviewed is None or months >= STALE_MONTHS,
            )
        )
    return sorted(entries, key=lambda entry: entry.source_path)


def _aged_table(entries: list[FreshnessEntry]) -> list[str]:
    """Render the table of pages reviewed but now past the staleness threshold."""
    lines = [
        "## Reviewed More Than 12 Months Ago",
        "",
        "| Route | Source | Last Reviewed | Months Since |",
        "|---|---|---|---:|",
    ]
    for entry in entries:
        lines.append(
            f"| `{entry.route}` | `{entry.source_path}` | {entry.last_reviewed.isoformat()} | "
            f"{entry.months_since_review} |"
        )
    lines.append("")
    return lines


def _never_reviewed_table(entries: list[FreshnessEntry]) -> list[str]:
    """Render the table of pages that carry no review date at all."""
    lines = ["## Never Reviewed", "", "| Route | Source |", "|---|---|"]
    lines.extend(f"| `{entry.route}` | `{entry.source_path}` |" for entry in entries)
    lines.append("")
    return lines


def render_report(entries: list[FreshnessEntry], reference_date: dt.date) -> str:
    """Render the deterministic Markdown freshness report."""
    aged = [e for e in entries if e.is_stale and e.last_reviewed is not None]
    never = [e for e in entries if e.is_stale and e.last_reviewed is None]
    lines = [
        "# Content Freshness Report",
        "",
        "<!-- DO NOT EDIT. Generated by scripts/generate_freshness_report.py. -->",
        "",
        f"Reference date: {reference_date.isoformat()}. A page is stale when its "
        f"`{LAST_REVIEWED_KEY}` front matter is missing or {STALE_MONTHS}+ months old. This is "
        "never derived from a file's build date.",
        "",
        f"- Pages scanned: {len(entries)}",
        f"- Stale (reviewed {STALE_MONTHS}+ months ago): {len(aged)}",
        f"- Never reviewed: {len(never)}",
        "",
    ]
    if aged:
        lines.extend(_aged_table(aged))
    if never:
        lines.extend(_never_reviewed_table(never))
    return "\n".join(lines).rstrip("\n") + "\n"


def generate_report(root: Path, output: Path, reference_date: dt.date, *, check: bool) -> int:
    """Write or verify the content freshness report; return a process exit code."""
    content = render_report(scan_pages(root, reference_date), reference_date)
    if check:
        current = output.read_text(encoding="utf-8") if output.is_file() else None
        if current != content:
            write_stderr(f"{output} is stale; run python3 -m scripts.generate_freshness_report")
            return 1
        write_stdout("content freshness report is up to date")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8", newline="\n")
    write_stdout(f"wrote {output}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n", maxsplit=1)[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--as-of",
        type=dt.date.fromisoformat,
        default=None,
        help="Reference date for generation, as YYYY-MM-DD (default: today).",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.check:
        # Compare against the as-of date the existing report was generated with, not
        # today's date, so --check only fails when a source page actually changes.
        reference_date = _recorded_reference_date(args.output) or args.as_of or _today()
    else:
        reference_date = args.as_of or _today()
    try:
        return generate_report(args.root, args.output, reference_date, check=args.check)
    except FreshnessReportError as exc:
        write_stderr(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
