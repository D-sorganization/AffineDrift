#!/usr/bin/env python3
"""Reject control characters in Quarto article sources.

Issue #5152 landed corrupted LaTeX in ``articles/after-one-solution-null-space-exploration.qmd``
when a shell write path interpreted ``\\top``, ``\\times``, and ``\\varnothing`` as escape
sequences: ``echo -e`` / ``printf`` turn ``\\t`` into TAB and ``\\v`` into vertical tab, and
a non-raw Python string does the same for ``\\t``/``\\v`` before the file is written. The
gate keeps ``articles/*.qmd`` free of bytes below U+0020 other than newline (LF).

    python3 scripts/check_article_control_characters.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "articles"
ALLOWED_CONTROL = frozenset({0x0A})  # LF only


def scan_articles(root: Path) -> list[dict[str, object]]:
    """Return one finding per disallowed control byte."""
    findings: list[dict[str, object]] = []
    articles = root / "articles"
    if not articles.is_dir():
        return findings
    for path in sorted(articles.rglob("*.qmd")):
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        for offset, byte in enumerate(data):
            if byte >= 0x20 or byte in ALLOWED_CONTROL:
                continue
            line = data[:offset].count(b"\n") + 1
            column = offset - data.rfind(b"\n", 0, offset)
            snippet = data[max(0, offset - 12) : offset + 12]
            findings.append(
                {
                    "file": relative,
                    "line": line,
                    "column": column,
                    "byte": f"0x{byte:02x}",
                    "snippet": snippet.decode("utf-8", errors="replace"),
                }
            )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repository root")
    args = parser.parse_args()

    findings = scan_articles(args.root)
    if not findings:
        print("articles/*.qmd: no disallowed control characters")
        return 0

    for finding in findings:
        print(
            f"::error file={finding['file']},line={finding['line']},"
            f"col={finding['column']}::"
            f"control character {finding['byte']} in article source "
            f"(context: {finding['snippet']!r})"
        )
    print(f"\n{len(findings)} disallowed control character(s) in articles/*.qmd")
    return 1


if __name__ == "__main__":
    sys.exit(main())
