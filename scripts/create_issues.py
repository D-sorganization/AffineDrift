"""Create GitHub issues from the repository's report outputs."""

from __future__ import annotations

import subprocess
from collections.abc import Iterable
from pathlib import Path

from scripts.cli_output import write_stdout


def create_issue(title: str, body: str) -> None:
    """Create a GitHub issue using the gh CLI."""
    subprocess.run(["gh", "issue", "create", "--title", title, "--body", body], check=True)


def _iter_report_issue_specs(report_path: Path) -> Iterable[tuple[str, str]]:
    """Yield issue title/body pairs derived from the magic-number report."""
    content = report_path.read_text(encoding="utf-8")

    for block in content.split("--- ")[1:]:
        lines = block.strip().split("\n")
        if not lines:
            continue

        filename = lines[0].replace(" ---", "").strip()
        stats_line = lines[1] if len(lines) > 1 else ""
        instances = lines[2:]

        if "Total instances found: 0" in stats_line:
            continue

        issue_title = f"Add explicit sources for magic numbers/studies in {filename}"
        body = f"**File**: `{filename}`\n"
        body += f"**{stats_line}**\n\n"
        body += (
            "We need to track down instances of numbers, magic numbers, or 'studies' that are "
            "referenced without an explicit source in the text. We cannot make up numbers or "
            "reference studies without citing them. Please write from a point of humility.\n\n"
        )
        body += "### Examples found in this file:\n"
        for instance in instances[:5]:
            body += f"- `{instance}`\n"

        if len(instances) > 5:
            body += "\n*(See scripts/find_magic_numbers.py output for more)*\n"

        yield issue_title, body


def main(repo_root: Path | None = None) -> int:
    """Create the repository's pending GitHub issues."""
    repo_root = repo_root or Path(__file__).resolve().parent.parent

    issue_specs = [
        (
            "Replace 'Zero-Torque Constraint Field' with 'Zero-Torque Counterfactual'",
            "The zero torque counterfactual is incorrectly called the 'Zero Torque Constraint "
            "Field' in some parts of the text (e.g., ch19_aerodynamic_drag). This needs to be "
            "corrected globally.",
        ),
        (
            "Decrease text size across both textbooks",
            "The size of the text on the pages seems huge. While easier to read, it makes the "
            "books seem less substantial. Please decrease the global text size (e.g., in "
            "Quarto/LaTeX configurations) to be more in line with professional texts.",
        ),
        (
            "Increase page margins across both textbooks",
            "Evaluate and modify the margins around the book pages in both The Physics of Golf and "
            "The Geometry of Motion. The current margins are too tight to the edges and need to be "
            "larger.",
        ),
    ]

    issue_specs.extend(_iter_report_issue_specs(repo_root / "magic_numbers_report.txt"))

    for title, body in issue_specs:
        write_stdout(f"Creating issue: {title}")
        create_issue(title, body)

    write_stdout("All issues created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
