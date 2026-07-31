#!/usr/bin/env python3
"""Enforce one expansion per project acronym across the textbook corpus.

Issue #3526 found the project's two signature acronyms had fragmented: ZTCF was
expanded five different ways and DCR meant five different things, including one
definition bounded in [0,1] sitting alongside claims of "20:1". A reader had no
way to know what any DCR figure meant.

`NOTATION.md` is the single source of truth. This gate keeps the corpus matching
it, so a variant reintroduced in a later edit fails CI rather than accumulating.

Deliberate historical mentions -- a warning box explaining what an earlier
revision said -- are allowed through an explicit baseline, in the same style as
`check_latex_structure.py` and `check_tree_parity.py`.

    python3 scripts/check_terminology.py
    python3 scripts/check_terminology.py --baseline config/terminology-baseline.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SEARCH_ROOTS = ("articles", "pages", "resources")
SUFFIXES = {".tex", ".qmd"}

# (regex, human-readable rule, what to use instead)
BANNED: tuple[tuple[str, str, str], ...] = (
    (
        r"Zero[-\s]Torque\s+Control\s+Fraction",
        "ZTCF expansion",
        "Zero Torque Counterfactual",
    ),
    (
        r"Zero[-\s]Torque\s+Controlled\s+Flight",
        "ZTCF expansion",
        "Zero Torque Counterfactual",
    ),
    (
        r"Zero[-\s]Torque[-\s]Contribution[-\s]to[-\s]Force",
        "ZTCF expansion",
        "Zero Torque Counterfactual",
    ),
    (
        r"zero[-\s]torque\s+constraint\s+force\s+analysis",
        "ZTCF expansion",
        "Zero Torque Counterfactual",
    ),
    (
        r"Drift[-\s]Correction[-\s]Response",
        "DCR expansion",
        "Drift-Control Ratio for the ratio; a different name for a latency",
    ),
    (
        r"Disturbance\s+Rejection\s+vs\.?\s+Control",
        "DCR expansion",
        "Drift-Control Ratio",
    ),
    (
        r"ch:control_affine_decomposition",
        "dangling cross-reference",
        "ch:zero_torque_counterfactual",
    ),
)

COMPILED = tuple((re.compile(pattern), rule, fix) for pattern, rule, fix in BANNED)


def iter_sources(root: Path) -> list[Path]:
    """Every .tex and .qmd file under the configured search roots."""
    found: list[Path] = []
    for name in SEARCH_ROOTS:
        directory = root / name
        if directory.is_dir():
            found.extend(p for p in sorted(directory.rglob("*")) if p.suffix in SUFFIXES)
    return found


def scan(root: Path) -> list[dict[str, object]]:
    """Return one finding per banned term occurrence."""
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
        help="JSON file of permitted occurrences (deliberate historical mentions)",
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
                f"{finding['rule']}: banned term matching /{finding['term']}/. "
                f"Use: {finding['fix']}"
            )
        print()
        print(f"{len(new)} terminology violation(s). NOTATION.md is the source of truth.")
        return 1

    permitted_count = len(findings)
    print(
        f"Terminology consistent. {permitted_count} permitted historical mention(s) "
        "from the baseline."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
