"""Terminal report formatting for code quality results.

Provides ANSI color output and structured report generation.
"""

from __future__ import annotations

import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output formatting.

    Automatically disables colors when stderr is not a TTY.
    """

    if sys.stderr.isatty():
        HEADER = "\033[95m"
        BLUE = "\033[94m"
        CYAN = "\033[96m"
        GREEN = "\033[92m"
        WARNING = "\033[93m"
        FAIL = "\033[91m"
        ENDC = "\033[0m"
        BOLD = "\033[1m"
    else:
        HEADER = ""
        BLUE = ""
        CYAN = ""
        GREEN = ""
        WARNING = ""
        FAIL = ""
        ENDC = ""
        BOLD = ""


def report_issues(
    all_issues: list[tuple[Path, list[tuple[int, str, str]]]],
) -> None:
    """Write a formatted quality report to stderr.

    Args:
        all_issues: List of ``(filepath, issues)`` pairs where each issue
            is ``(line_number, message, code_snippet)``.
    """
    sys.stderr.write(f"{Colors.FAIL}{Colors.BOLD}❌ Quality check FAILED{Colors.ENDC}\n\n")
    for filepath, issues in all_issues:
        sys.stderr.write(f"\n{Colors.CYAN}{filepath}:{Colors.ENDC}\n")
        for line_num, message, code in issues:
            if line_num > 0:
                sys.stderr.write(f"  Line {Colors.BOLD}{line_num}{Colors.ENDC}: {message}\n")
                if code:
                    sys.stderr.write(f"    > {Colors.WARNING}{code}{Colors.ENDC}\n")
            else:
                sys.stderr.write(f"  {message}\n")

    total_issues = sum(len(issues) for _, issues in all_issues)
    sys.stderr.write(
        f"\n{Colors.FAIL}Total issues: {total_issues}{Colors.ENDC}\n",
    )
