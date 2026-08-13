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
ENFORCED_ACRONYMS = ("ZTCF", "ZVCF", "DCR", "DgCR")
CONTRACT_START = "<!-- TERMINOLOGY-CONTRACT:START -->"
CONTRACT_END = "<!-- TERMINOLOGY-CONTRACT:END -->"
CONTRACT_ROW = re.compile(
    r"^\|\s*\*\*(?P<acronym>[A-Za-z]+)\*\*\s*\|\s*"
    r"(?P<expansion>[^|]+?)\s*\|\s*(?P<qualifiers>[^|]+?)\s*\|\s*$"
)

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
    # Unsourced-claim markers. The macro is a legitimate way to be honest about a
    # claim you have not sourced yet, but eight of them accumulated for a year
    # and survived a PR titled "resolve 35+ citation TODOs" (#3501), each
    # rendering as a bold [?] in the PDF. Banning them by default means a new one
    # has to be added to the baseline deliberately, which makes it visible rather
    # than letting it sink into the corpus.
    (
        r"\\citeneeded",
        "unresolved citation marker",
        "a real citation, a derivation, or an explicit 'this is a modelling assumption'",
    ),
    (
        r"\[citation needed",
        "unresolved citation marker",
        "a real citation, a derivation, or an explicit 'this is a modelling assumption'",
    ),
)

COMPILED = tuple((re.compile(pattern), rule, fix) for pattern, rule, fix in BANNED)


def _authority_finding(acronym: str, message: str) -> dict[str, object]:
    """Build one fail-closed finding for a missing or malformed authority row."""
    return {
        "file": "NOTATION.md",
        "line": 1,
        "rule": "terminology authority",
        "term": acronym,
        "fix": message,
    }


def load_contract(root: Path) -> tuple[dict[str, dict[str, object]], list[dict[str, object]]]:
    """Parse the machine-readable terminology table in ``NOTATION.md``."""
    path = root / "NOTATION.md"
    if not path.is_file():
        findings = [
            _authority_finding(acronym, "add the canonical entry to NOTATION.md")
            for acronym in ENFORCED_ACRONYMS
        ]
        return {}, findings
    text = path.read_text(encoding="utf-8")
    if CONTRACT_START not in text or CONTRACT_END not in text:
        findings = [
            _authority_finding(acronym, "add the canonical terminology contract table")
            for acronym in ENFORCED_ACRONYMS
        ]
        return {}, findings
    body = text.split(CONTRACT_START, 1)[1].split(CONTRACT_END, 1)[0]
    contract: dict[str, dict[str, object]] = {}
    for line in body.splitlines():
        match = CONTRACT_ROW.match(line)
        if not match:
            continue
        acronym = match.group("acronym")
        contract[acronym] = {
            "expansion": match.group("expansion").strip(),
            "qualifiers": tuple(
                item.strip().lower()
                for item in match.group("qualifiers").split(",")
                if item.strip()
            ),
        }
    findings = [
        _authority_finding(acronym, f"add the {acronym} entry to NOTATION.md")
        for acronym in ENFORCED_ACRONYMS
        if acronym not in contract
    ]
    return contract, findings


def _normalize_words(value: str) -> str:
    """Normalize case and punctuation while preserving word order."""
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def _expansion_findings(
    relative: str, text: str, contract: dict[str, dict[str, object]]
) -> list[dict[str, object]]:
    """Reject explicit acronym expansions that do not match the authority."""
    findings: list[dict[str, object]] = []
    lines = text.splitlines()
    phrase_patterns = {
        "ZTCF": r"Zero(?:[-\s]+[A-Za-z]+){2,7}",
        "ZVCF": r"Zero(?:[-\s]+[A-Za-z]+){2,7}",
        "DCR": r"Drift(?:[-\s]+[A-Za-z]+){1,5}",
        "DgCR": r"Drag(?:[-\s]+[A-Za-z]+){1,5}",
    }
    for acronym, entry in contract.items():
        canonical = _normalize_words(str(entry["expansion"]))
        pattern = re.compile(
            rf"(?P<phrase>{phrase_patterns[acronym]})\s*\(\s*{acronym}\s*\)",
            flags=re.IGNORECASE,
        )
        for number, line in enumerate(lines, start=1):
            for match in pattern.finditer(line):
                phrase = _normalize_words(match.group("phrase"))
                if not phrase.endswith(canonical):
                    findings.append(
                        {
                            "file": relative,
                            "line": number,
                            "rule": f"{acronym} canonical expansion",
                            "term": match.group("phrase").strip(),
                            "fix": str(entry["expansion"]),
                        }
                    )
    return findings


def _ztcf_first_use_finding(
    relative: str, text: str, contract: dict[str, dict[str, object]]
) -> dict[str, object] | None:
    """Require the first visible ZTCF use to identify the construction."""
    match = re.search(r"\bZTCF\b", text)
    entry = contract.get("ZTCF")
    if match is None or entry is None:
        return None
    line = text.count("\n", 0, match.start()) + 1
    window = _normalize_words(text[max(0, match.start() - 120) : match.end() + 40])
    qualifiers = tuple(str(item) for item in entry["qualifiers"])
    if any(re.search(rf"\b{re.escape(qualifier)}\b", window) for qualifier in qualifiers):
        return None
    return {
        "file": relative,
        "line": line,
        "rule": "ZTCF first-use qualifier",
        "term": "ZTCF",
        "fix": "identify pointwise, stitched, forward, branched, or family scope",
    }


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
    contract, findings = load_contract(root)
    for path in iter_sources(root):
        relative = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8-sig")
        findings.extend(_expansion_findings(relative, text, contract))
        first_use = _ztcf_first_use_finding(relative, text, contract)
        if first_use is not None:
            findings.append(first_use)
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
