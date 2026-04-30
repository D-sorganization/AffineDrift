#!/usr/bin/env python3
"""Check bibliography.json data quality.

Validates:
  - Required fields present (id, title, authors, year, type)
  - No 'et al.' placeholder author entries
  - No duplicate IDs
  - Papers have DOI or URL (with budget exemptions)

Exits 0 on success, 1 on violations.

Closes issue #1531 and #1532.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

from src.core.contracts import require

logger = logging.getLogger(__name__)

_NO_ID = "<no id>"

# ─── custom error ────────────────────────────────────────────────────────────


class BibliographyError(Exception):
    """Raised when the bibliography file is unreadable or malformed."""


# ─── I/O ─────────────────────────────────────────────────────────────────────


def load_and_validate(path: Path) -> list[dict[str, Any]]:
    """Load bibliography JSON and verify it is a list.

    Precondition: path points to a readable file.
    Postcondition: return value is a non-empty list of dicts.
    """
    require(path is not None, "path must not be None")

    if not path.exists():
        raise BibliographyError(f"Bibliography file not found: {path}")

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BibliographyError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(raw, list):
        raise BibliographyError(f"Bibliography must be a JSON list, got {type(raw).__name__}")

    return raw  # type: ignore[return-value]


# ─── checks ──────────────────────────────────────────────────────────────────

_REQUIRED_FIELDS = ("id", "title", "authors", "year", "type")


def check_required_fields(entries: list[dict[str, Any]]) -> list[str]:
    """Return violation messages for entries missing required fields."""
    violations: list[str] = []
    for entry in entries:
        entry_id = entry.get("id") or _NO_ID
        for field in _REQUIRED_FIELDS:
            value = entry.get(field)
            missing = value is None or value == "" or value == []
            if missing:
                violations.append(f"[{entry_id}] missing required field '{field}'")
    return violations


def _load_et_al_exempt_ids(budget_path: Path | None) -> set[str]:
    """Load the set of entry IDs exempt from the et al. author check."""
    if budget_path is None or not budget_path.exists():
        return set()
    try:
        data = json.loads(budget_path.read_text(encoding="utf-8"))
        return set(data.get("et_al_exempt_ids", []))
    except (json.JSONDecodeError, KeyError):
        return set()


def check_no_et_al_authors(
    entries: list[dict[str, Any]],
    budget_path: Path | None = None,
) -> list[str]:
    """Return violation messages for entries that use 'et al.' as an author.

    'et al.' is a display convention, not a data value.  Full author names
    must be stored so the bibliography can be sorted and searched properly.
    Entries listed in the budget file under ``et_al_exempt_ids`` are exempt.
    """
    exempt_ids = _load_et_al_exempt_ids(budget_path)
    violations: list[str] = []
    for entry in entries:
        entry_id = entry.get("id", _NO_ID)
        if entry_id in exempt_ids:
            continue
        for author in entry.get("authors", []):
            if isinstance(author, str) and author.strip().lower() == "et al.":
                violations.append(f"[{entry_id}] 'et al.' used as author — replace with real names")
                break  # one violation per entry is enough
    return violations


def check_no_duplicate_ids(entries: list[dict[str, Any]]) -> list[str]:
    """Return violation messages for duplicate entry IDs."""
    seen: dict[str, int] = {}
    for entry in entries:
        eid = entry.get("id", "")
        seen[eid] = seen.get(eid, 0) + 1

    violations: list[str] = []
    for eid, count in seen.items():
        if count > 1:
            violations.append(f"Duplicate id '{eid}' appears {count} times")
    return violations


def _load_exempt_ids(budget_path: Path | None) -> set[str]:
    """Load the set of entry IDs exempt from the DOI/URL check."""
    if budget_path is None or not budget_path.exists():
        return set()
    try:
        data = json.loads(budget_path.read_text(encoding="utf-8"))
        return set(data.get("exempt_ids", []))
    except (json.JSONDecodeError, KeyError):
        return set()


def _has_nonempty(entry: dict[str, Any], field: str) -> bool:
    """Return True if entry[field] is a non-empty string."""
    value = entry.get(field)
    return bool(value and str(value).strip())


def check_papers_have_doi_or_url(
    entries: list[dict[str, Any]],
    budget_path: Path | None = None,
) -> list[str]:
    """Return violation messages for paper-type entries without a DOI or URL.

    Books and software are exempt — they often lack stable DOIs.
    Entries listed in the budget file are also exempt.
    """
    exempt_ids = _load_exempt_ids(budget_path)
    violations: list[str] = []
    for entry in entries:
        entry_id = entry.get("id", _NO_ID)
        if entry.get("type") != "paper":
            continue
        if entry_id in exempt_ids:
            continue
        if not _has_nonempty(entry, "doi") and not _has_nonempty(entry, "url"):
            violations.append(f"[{entry_id}] paper-type entry has neither 'doi' nor 'url'")
    return violations


# ─── main ────────────────────────────────────────────────────────────────────


def main() -> int:
    """Run all bibliography quality checks and report violations."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    repo_root = Path(__file__).resolve().parent.parent
    bib_path = repo_root / "data" / "bibliography.json"
    budget_path = repo_root / "config" / "bibliography_quality_budget.json"

    try:
        entries = load_and_validate(bib_path)
    except BibliographyError as exc:
        logger.error("%s", exc)
        return 1

    all_violations: list[str] = []

    for check_fn, kwargs in [
        (check_required_fields, {}),
        (check_no_et_al_authors, {"budget_path": budget_path}),
        (check_no_duplicate_ids, {}),
        (check_papers_have_doi_or_url, {"budget_path": budget_path}),
    ]:
        violations = check_fn(entries, **kwargs)  # type: ignore[call-arg]
        all_violations.extend(violations)

    if all_violations:
        logger.error("Bibliography quality check FAILED (%d violations):", len(all_violations))
        for v in all_violations:
            logger.error("  %s", v)
        return 1

    logger.info(
        "Bibliography quality check passed (%d entries, 0 violations).",
        len(entries),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
