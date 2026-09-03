#!/usr/bin/env python3
"""Enforce PR-keyed SPEC.md change-log rows (Repository_Management#1520).

Until #1520 a `SPEC.md` change-log entry carried *the next free serial spec
version* and the `Spec Version` field in section 1 had to be bumped to match.
Both are global counters, so two concurrent pull requests necessarily pick the
same next value and necessarily edit the same two lines. Every second merge
conflicted and the only possible resolution was "renumber my row above
theirs" — a conflict carrying no information. Twelve such re-merges were
performed across the fleet on 2026-09-03.

A row is now keyed by the pull request, which is unique by construction:

    | Date       | PR    | Changes          |
    | ---------- | ----- | ---------------- |
    | 2026-09-03 | #1520 | one-line summary |

What this gate enforces:

* the change log parses as the canonical `Date | PR | Changes` table;
* every row has an ISO date, a `#<number>` key (or the `n/a` legacy marker for
  a migrated historical row), and a non-empty summary;
* a `#<number>` key is never reused among rows dated on or after
  `PR_KEYED_SINCE` — a second row for one pull request means a row was copied
  rather than edited. Rows dated before the cutover are exempt, because several
  historical AffineDrift entries genuinely share a governing issue;
* a bare serial version sitting in the key column is an error, with a message
  naming the fix.

What it deliberately does **not** enforce: that the `Spec Version` field equals
the newest row. That equality was the second half of the treadmill. The field
is release-derived — `scripts/bump_spec_version.py` sets it when a release is
cut, and nothing else does.

"A substantive pull request adds a change-log row" is unchanged and still
enforced, by `.github/workflows/spec-check.yml`, which blocks a pull request
that touches `src/`, `tests/`, `pyproject.toml` or `package.json` without
touching `SPEC.md`. This gate is the format and uniqueness half of the same
contract; the two are complementary and neither replaces the other.

The row-format rules themselves live in `shared_scripts/spec_changelog.py`,
which is fleet-shared and synced from Repository_Management. This script is
only the AffineDrift entry point: it locates the module, delegates, and reports
in this repository's checker style. It does not restate the regexes.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

if __package__ in {None, ""}:  # pragma: no cover - direct-invocation shim
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.cli_output import write_stderr, write_stdout

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "SPEC.md"
SHARED_MODULE = REPO_ROOT / "shared_scripts" / "spec_changelog.py"

_ISSUE_URL = "https://github.com/D-sorganization/Repository_Management/issues/1520"


def load_spec_changelog(module_path: Path = SHARED_MODULE) -> ModuleType | None:
    """Import the fleet-shared change-log module by file path.

    Returns ``None`` when the module has not been synced into this repository
    yet. The caller warns rather than failing in that case: a repository that
    receives the gate config before the module must not be blocked from
    committing (campaign invariant 7).
    """
    if not module_path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("affinedrift_spec_changelog", module_path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def check(spec_path: Path = SPEC_PATH, *, module_path: Path = SHARED_MODULE) -> list[str]:
    """Return human-readable failures for ``spec_path``; empty means clean."""
    if not spec_path.is_file():
        return []
    module = load_spec_changelog(module_path)
    if module is None:
        write_stdout(
            "WARNING: shared_scripts/spec_changelog.py is not present; "
            "skipping the SPEC.md change-log format check."
        )
        return []
    text = spec_path.read_text(encoding="utf-8")
    try:
        changelog = module.parse_changelog(text)
    except module.SpecChangelogError as exc:
        return [
            f"{spec_path.name}: {exc}. The change log is a table keyed by pull "
            f"request: '| YYYY-MM-DD | #<pr> | summary |'. See {_ISSUE_URL}."
        ]
    return list(module.validate(changelog))


def main(argv: list[str] | None = None) -> int:
    """Report SPEC.md change-log boundary violations."""
    if hasattr(sys.stdout, "reconfigure"):
        # SPEC.md is UTF-8 and carries arrows and dashes; cp1252 stdout on
        # Windows would raise mid-report and make a passing check look crashed.
        sys.stdout.reconfigure(errors="backslashreplace")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec",
        default=str(SPEC_PATH),
        help="path to SPEC.md (default: the repository root SPEC.md)",
    )
    args = parser.parse_args(argv)

    failures = check(Path(args.spec))
    if failures:
        write_stderr("SPEC.md change-log check FAILED")
        for failure in failures:
            write_stderr(f"  - {failure}")
        write_stderr("")
        write_stderr(
            "Rows are keyed by pull request, never by a serial spec version, "
            "and the 'Spec Version' field is bumped at release time by "
            "scripts/bump_spec_version.py."
        )
        return 1
    write_stdout("SPEC.md change-log check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
