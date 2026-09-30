#!/usr/bin/env python3
"""Keep internal governance vocabulary out of reader prose (issue #4588).

Reader-facing pages borrowed five words from the repository's own governance
apparatus -- "governed", "qualified", "provenance", "protected", and
"fail-closed" -- to describe claim-review status, evidence status, and pinned
commits. Readers who have never seen `.gaai/` or the falsification ledgers
have no way to know these carry a repository-specific meaning.

This gate warns (see the CI step's `continue-on-error`) when one of the five
terms appears on a reader page. It does not fire on the evidence and developer
surfaces where the vocabulary is native: `articles/_generated/` (generated
trust/critique annotations) and `models/programming/` (the programming
companion consumer docs). A term that is a deliberate, glossary-linked mention
is grandfathered through an explicit baseline, in the same style as
`check_terminology.py`.

    python3 scripts/check_governance_vocabulary.py
    python3 scripts/check_governance_vocabulary.py --baseline config/governance-vocabulary-baseline.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SEARCH_ROOTS = ("articles", "books", "models", "pages", "resources")
EXCLUDE_PREFIXES = ("articles/_generated", "models/programming")
SUFFIXES = {".qmd"}

# (regex, human-readable label)
TERMS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bgoverned\b", re.IGNORECASE), "governed"),
    (re.compile(r"\bqualified\b", re.IGNORECASE), "qualified"),
    (re.compile(r"\bprovenance\b", re.IGNORECASE), "provenance"),
    (re.compile(r"\bprotected\b", re.IGNORECASE), "protected"),
    (re.compile(r"\bfails?[-\s]closed\b", re.IGNORECASE), "fail-closed"),
)

GLOSSARY_FIX = "use plain language, or link the term to pages/glossary.qmd on first use per page"


def iter_sources(root: Path) -> list[Path]:
    """Every reader-facing `.qmd` file outside the evidence/developer surfaces."""
    found: list[Path] = []
    for name in SEARCH_ROOTS:
        directory = root / name
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*")):
            if path.suffix not in SUFFIXES:
                continue
            relative = path.relative_to(root).as_posix()
            if any(relative.startswith(f"{prefix}/") for prefix in EXCLUDE_PREFIXES):
                continue
            found.append(path)
    return found


def scan(root: Path) -> list[dict[str, object]]:
    """Return one finding per governance-vocabulary occurrence on a reader page."""
    findings: list[dict[str, object]] = []
    for path in iter_sources(root):
        relative = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8-sig")
        for number, line in enumerate(text.splitlines(), start=1):
            for pattern, label in TERMS:
                if pattern.search(line):
                    findings.append(
                        {
                            "file": relative,
                            "line": number,
                            "term": label,
                            "fix": GLOSSARY_FIX,
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
                f"::warning file={finding['file']},line={finding['line']}::"
                f"internal governance vocabulary in reader prose: '{finding['term']}'. "
                f"{finding['fix']}."
            )
        print()
        print(
            f"{len(new)} governance-vocabulary occurrence(s) outside the evidence/developer "
            "surfaces. See issue #4588."
        )
        return 1

    permitted_count = len(findings)
    print(
        f"Governance vocabulary contained. {permitted_count} permitted historical mention(s) "
        "from the baseline."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
