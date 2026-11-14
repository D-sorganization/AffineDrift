#!/usr/bin/env python3
"""Keep PARAMETERS.md and bound literals aligned with data/canonical_parameters.json.

Issue #5595: PARAMETERS.md must be generated from the registry, free of stale chapter
pointers, and consistent with AffineDrift modules that declare canonical values.

    python3 scripts/check_parameters.py
    python3 scripts/check_parameters.py --write-baseline config/parameters-baseline.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from scripts.canonical_parameters_registry import (
    DATA_PATH,
    PARAMETERS_MD,
    compile_check_pattern,
    iter_literal_checks,
    load_registry,
    match_literal,
    render_parameters_markdown,
    stale_markers,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def verify_markdown(
    payload: dict[str, object],
    parameters_path: Path = PARAMETERS_MD,
) -> list[str]:
    """Return errors when PARAMETERS.md diverges from the registry or has stale text."""
    errors: list[str] = []
    if not parameters_path.is_file():
        errors.append("PARAMETERS.md is missing")
        return errors
    expected = render_parameters_markdown(payload)
    actual = parameters_path.read_text(encoding="utf-8")
    if actual != expected:
        errors.append("PARAMETERS.md is out of date; run python3 scripts/generate_parameters_md.py")
    for marker in stale_markers(payload):
        if marker["pattern"] in actual:
            errors.append(
                f"PARAMETERS.md still contains stale pointer {marker['pattern']!r} "
                f"({marker['reason']})"
            )
    return errors


def resolve_path_glob(root: Path, path_glob: str) -> list[Path]:
    """Expand a repo-relative glob to existing files (single path if no wildcards)."""
    if any(ch in path_glob for ch in "*?[]"):
        return sorted(p for p in root.glob(path_glob) if p.is_file())
    path = root / path_glob
    return [path] if path.is_file() else []


def _scan_file_literals(
    root: Path,
    path: Path,
    entry_id: str,
    pattern: re.Pattern[str],
    expected: float,
    tolerance: float,
) -> tuple[list[dict[str, object]], int]:
    """Scan one file for registry-bound literals.

    Returns (findings, match_count) where match_count is lines the pattern matched.
    """
    findings: list[dict[str, object]] = []
    match_count = 0
    text = path.read_text(encoding="utf-8")
    for line_no, line in enumerate(text.splitlines(), start=1):
        match = pattern.search(line)
        if not match:
            continue
        match_count += 1
        value_text = match.group(1)
        if not match_literal(value_text, expected, tolerance):
            findings.append(
                {
                    "file": path.relative_to(root).as_posix(),
                    "line": line_no,
                    "rule": f"{entry_id} literal mismatch",
                    "fix": f"expected {expected} ± {tolerance}, found {value_text}",
                }
            )
    return findings, match_count


def scan_literal_checks(root: Path, payload: dict[str, object]) -> list[dict[str, object]]:
    """Find literal assignments that disagree with the registry."""
    findings: list[dict[str, object]] = []
    for entry, check in iter_literal_checks(payload):
        pattern = compile_check_pattern(str(check["pattern"]))
        paths = resolve_path_glob(root, str(check["path_glob"]))
        if not paths:
            findings.append(
                {
                    "file": str(check["path_glob"]),
                    "line": 0,
                    "rule": f"missing file for {entry.entry_id}",
                    "fix": "restore the bound module or update the registry",
                }
            )
            continue
        expected = float(check["expected"])
        tolerance = float(check.get("tolerance", 0.0))
        match_count = 0
        for path in paths:
            file_findings, file_matches = _scan_file_literals(
                root, path, entry.entry_id, pattern, expected, tolerance
            )
            findings.extend(file_findings)
            match_count += file_matches
        if match_count == 0:
            findings.append(
                {
                    "file": str(check["path_glob"]),
                    "line": 0,
                    "rule": f"{entry.entry_id} literal missing",
                    "fix": (
                        f"restore a bound literal matching pattern {check['pattern']!r} "
                        f"(expected {expected} ± {tolerance})"
                    ),
                }
            )
    return findings


def key(finding: dict[str, object]) -> str:
    """Baseline identity without line numbers."""
    return f"{finding['file']}::{finding['rule']}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--baseline", type=Path, help="JSON allowlist of literal findings")
    parser.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args()

    payload = load_registry(args.data)
    errors = verify_markdown(payload)
    findings = scan_literal_checks(args.root, payload)

    if args.write_baseline:
        if not args.baseline:
            print("--write-baseline requires --baseline", file=sys.stderr)
            return 2
        args.baseline.parent.mkdir(parents=True, exist_ok=True)
        args.baseline.write_text(
            json.dumps(sorted({key(f) for f in findings}), indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {len(findings)} permitted literal occurrence(s)")
        return 0

    permitted: set[str] = set()
    if args.baseline and args.baseline.exists():
        permitted = set(json.loads(args.baseline.read_text(encoding="utf-8")))

    new_findings = [f for f in findings if key(f) not in permitted]
    exit_code = 0
    for message in errors:
        print(f"::error::{message}")
        exit_code = 1
    for finding in new_findings:
        print(
            f"::error file={finding['file']},line={finding['line']}::"
            f"{finding['rule']}. {finding['fix']}"
        )
        exit_code = 1

    if exit_code == 0:
        print(
            "Parameters consistent with data/canonical_parameters.json. "
            f"{len(findings)} permitted literal occurrence(s)."
        )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
