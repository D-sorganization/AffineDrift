#!/usr/bin/env python3
"""Enforce NOTATION.md's control-affine input-map notation across content sources.

Issue #4582 found lowercase $g(x)$ used for the control-affine input map on the
home page (`index.qmd`), several textbook chapters, and 12 critique files, even
though `NOTATION.md:342-346` reserves lowercase $g$ for gravity and requires
uppercase $G(x)$ for the input map. This gate keeps the corpus matching that
rule, in the same baseline style as `check_terminology.py`.

A genuinely different symbol -- for example the inequality-constraint $g(x)$ in
an optimal-control barrier-function derivation, which has nothing to do with
the control-affine input map -- is permitted through the baseline rather than
rewritten, since rewriting it to $G(x)$ would misrepresent the math.

    python3 scripts/check_notation.py
    python3 scripts/check_notation.py --baseline config/notation-baseline.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SEARCH_ROOTS = ("articles", "books", "content", "critiques", "models", "pages", "resources")
ROOT_FILES = ("index.qmd",)
SUFFIXES = {".tex", ".qmd", ".md"}

# (regex, human-readable rule, what to use instead)
BANNED: tuple[tuple[str, str, str], ...] = (
    (
        r"g\(x\)",
        "control-affine input map uses lowercase g(x)",
        "uppercase G(x) -- NOTATION.md reserves lowercase g(q) for gravity and "
        "requires uppercase G(x) for the control-affine input map",
    ),
)

COMPILED = tuple((re.compile(pattern), rule, fix) for pattern, rule, fix in BANNED)


def iter_sources(root: Path) -> list[Path]:
    """Every .tex, .qmd, and .md file under the configured search roots."""
    found: list[Path] = []
    for name in SEARCH_ROOTS:
        directory = root / name
        if directory.is_dir():
            found.extend(p for p in sorted(directory.rglob("*")) if p.suffix in SUFFIXES)
    for name in ROOT_FILES:
        path = root / name
        if path.is_file() and path.suffix in SUFFIXES:
            found.append(path)
    return sorted(set(found))


def scan(root: Path) -> list[dict[str, object]]:
    """Return one finding per banned pattern occurrence."""
    findings: list[dict[str, object]] = []
    for path in iter_sources(root):
        relative = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8-sig")
        for number, line in enumerate(text.splitlines(), start=1):
            for pattern, rule, fix in COMPILED:
                if pattern.search(line):
                    findings.append(
                        {
                            "file": relative,
                            "line": number,
                            "rule": rule,
                            "term": pattern.pattern,
                            "fix": fix,
                        }
                    )
    return findings


def key(finding: dict[str, object]) -> str:
    """Baseline identity. Deliberately excludes the line number.

    Pinning the line would make every unrelated edit above a permitted mention
    look like a new violation.
    """
    return f"{finding['file']}::{finding['term']}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repository root to scan")
    parser.add_argument(
        "--baseline",
        type=Path,
        help="JSON file of permitted occurrences (a distinct g(x) meaning, or a quoted source)",
    )
    parser.add_argument(
        "--write-baseline", action="store_true", help="rewrite the baseline from the scan"
    )
    args = parser.parse_args()

    findings = scan(args.root)

    if args.write_baseline:
        if not args.baseline:
            print("--write-baseline requires --baseline", file=sys.stderr)
            return 2
        args.baseline.parent.mkdir(parents=True, exist_ok=True)
        args.baseline.write_text(
            json.dumps(sorted({key(f) for f in findings}), indent=2) + "\n", encoding="utf-8"
        )
        print(f"wrote {len(findings)} permitted occurrence(s) to {args.baseline}")
        return 0

    permitted: set[str] = set()
    if args.baseline and args.baseline.exists():
        permitted = set(json.loads(args.baseline.read_text(encoding="utf-8")))

    new = [f for f in findings if key(f) not in permitted]
    if new:
        for finding in new:
            print(
                f"::error file={finding['file']},line={finding['line']}::"
                f"{finding['rule']}. Use: {finding['fix']}"
            )
        print()
        print(f"{len(new)} notation violation(s). NOTATION.md is the source of truth.")
        return 1

    permitted_count = len(findings)
    print(f"Notation consistent. {permitted_count} permitted occurrence(s) from the baseline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
