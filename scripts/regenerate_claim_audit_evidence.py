#!/usr/bin/env python3
"""Rewrite claim-audit evidence digests from the current tree (AffineDrift #4124).

The scientific claim-audit ledgers bind every reviewed route and every corrected
finding to exact SHA-256 digests of their evidence. Those digests are the point of
the contract, but they must be refreshed whenever a bound file changes; doing that
by hand is how ``main`` went red for three days. This script recomputes every digest
map in dependency order and regenerates the derived reports:

1. ``data/trust/site_trust_surface_audit.json`` (source, include, finding digests)
2. ``reports/site-trust-surface-audit.md``
3. ``data/trust/claim_audit_inventory.json`` (review and finding digests)
4. ``data/trust/generated/claim_audit_report.json`` + ``reports/scientific-claim-audit.md``

Only digest values are rewritten, in place, so prettier-formatted ledgers keep their
formatting; the declared evidence paths, rationales, reviewers and commits are never
touched. ``--check`` reports drift without writing anything and exits non-zero, which
is what the ``quality-gate`` job and the pre-commit hook run.

Usage:
    python -m scripts.regenerate_claim_audit_evidence [--check]
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import cast

from scripts.claim_audit_evidence import ReviewEvidenceError, evidence_digests, file_sha256
from scripts.claim_audit_types import AuditSources, GenerationOptions, ReportTargets
from scripts.generate_claim_audit_inventory import (
    DEFAULT_CLAIMS,
    DEFAULT_INVENTORY,
    DEFAULT_LEDGER,
    DEFAULT_REPORT_JSON,
    DEFAULT_REPORT_MARKDOWN,
    DEFAULT_SCHEMA,
    AuditContractError,
    generate,
)
from scripts.site_trust_surface_audit import (
    DEFAULT_AUDIT,
    DEFAULT_REPORT,
    SiteAuditContractError,
    generate_report,
)
from scripts.site_trust_surface_audit import DEFAULT_SCHEMA as SITE_SCHEMA

ROOT = Path(__file__).resolve().parent.parent
HEX_DIGITS = frozenset("0123456789abcdef")


class EvidenceRegenerationError(ValueError):
    """Raised when a ledger cannot be refreshed from the current tree."""


def _load(path: Path) -> dict[str, object]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceRegenerationError(f"Cannot load {path}: {exc}") from exc
    if not isinstance(document, dict):
        raise EvidenceRegenerationError(f"{path} must contain a JSON object")
    return cast(dict[str, object], document)


def _dump(document: object) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _is_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= HEX_DIGITS


def _digest_replacements(before: object, after: object) -> dict[tuple[str, str], str]:
    """Collect ``(key, old_digest) -> new_digest`` pairs between two ledger trees.

    Every digest sits under a string key (an evidence path, ``source_sha256``, or an
    included-source path) whose value is the 64-hex digest, so ``(key, old)`` names
    the exact text to patch without re-serialising the ledger.
    """
    replacements: dict[tuple[str, str], str] = {}
    if isinstance(before, dict) and isinstance(after, dict):
        for key, old_value in before.items():
            new_value = after.get(key)
            if _is_digest(old_value) and _is_digest(new_value):
                if old_value != new_value:
                    replacements[(str(key), cast(str, old_value))] = cast(str, new_value)
            else:
                replacements.update(_digest_replacements(old_value, new_value))
    elif isinstance(before, list) and isinstance(after, list):
        for old_item, new_item in zip(before, after, strict=True):
            replacements.update(_digest_replacements(old_item, new_item))
    return replacements


def patched_text(original: str, before: object, after: object) -> str:
    """Return the ledger text with only its digest values rewritten in place.

    Falls back to a canonical re-serialisation when the structure itself changed
    (evidence paths added or removed), which is the rare hand-edit case; prettier
    then normalises the formatting on commit.
    """
    text = original
    for (key, old_digest), new_digest in _digest_replacements(before, after).items():
        needle = f'"{key}": "{old_digest}"'
        if needle not in text:
            return _dump(after)
        text = text.replace(needle, f'"{key}": "{new_digest}"')
    if json.loads(text) != after:
        return _dump(after)
    return text


def _refresh_digest_map(root: Path, holder: dict[str, object], label: str) -> int:
    """Recompute ``holder['evidence_sha256']`` from ``holder['evidence_paths']``."""
    paths = holder.get("evidence_paths")
    if paths is None:
        return 0
    if not isinstance(paths, list) or not all(isinstance(path, str) for path in paths):
        raise EvidenceRegenerationError(f"{label} evidence paths must be strings")
    try:
        fresh = evidence_digests(root, cast(list[str], paths))
    except ReviewEvidenceError as exc:
        raise EvidenceRegenerationError(f"{label}: {exc}") from exc
    if holder.get("evidence_sha256") == fresh:
        return 0
    holder["evidence_sha256"] = fresh
    return 1


def _routes(document: dict[str, object], label: str) -> list[dict[str, object]]:
    routes = document.get("routes")
    if not isinstance(routes, list) or not all(isinstance(route, dict) for route in routes):
        raise EvidenceRegenerationError(f"{label} routes must be objects")
    return cast(list[dict[str, object]], routes)


def _findings(route: dict[str, object], label: str) -> list[dict[str, object]]:
    findings = route.get("findings", [])
    if not isinstance(findings, list) or not all(isinstance(item, dict) for item in findings):
        raise EvidenceRegenerationError(f"{label} findings must be objects")
    return cast(list[dict[str, object]], findings)


def _source_digest(root: Path, raw_path: object, label: str) -> str:
    source = root / str(raw_path)
    if not isinstance(raw_path, str) or not source.is_file():
        raise EvidenceRegenerationError(f"{label} source is missing: {raw_path}")
    return file_sha256(source)


def refresh_site_audit(document: dict[str, object], root: Path) -> int:
    """Refresh source, included-source, and finding digests of the site audit."""
    changed = 0
    for route in _routes(document, "site audit"):
        label = f"site audit {route.get('route')}"
        digest = _source_digest(root, route.get("source_path"), label)
        if route.get("source_sha256") != digest:
            route["source_sha256"] = digest
            changed += 1
        included = route.get("included_source_paths", [])
        if not isinstance(included, list):
            raise EvidenceRegenerationError(f"{label} included sources must be a list")
        included_digests = {str(path): _source_digest(root, path, label) for path in included}
        if route.get("included_source_sha256") != included_digests:
            route["included_source_sha256"] = included_digests
            changed += 1
        for finding in _findings(route, label):
            changed += _refresh_digest_map(root, finding, f"{label} {finding.get('finding_id')}")
    return changed


def refresh_inventory(document: dict[str, object], root: Path) -> int:
    """Refresh review and corrected-finding digests of the route inventory."""
    changed = 0
    for route in _routes(document, "inventory"):
        label = f"inventory {route.get('route')}"
        review = route.get("review")
        if isinstance(review, dict):
            changed += _refresh_digest_map(root, cast(dict[str, object], review), f"{label} review")
        for finding in _findings(route, label):
            changed += _refresh_digest_map(root, finding, f"{label} {finding.get('finding_id')}")
    return changed


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)


def _refresh_ledger(
    path: Path,
    refresh: Callable[[dict[str, object], Path], int],
    root: Path,
    check: bool,
    drift: list[str],
) -> None:
    original = path.read_text(encoding="utf-8")
    document = _load(path)
    before = copy.deepcopy(document)
    refresh(document, root)
    content = patched_text(original, before, document)
    if content == original:
        return
    drift.append(_relative(path))
    if not check:
        path.write_text(content, encoding="utf-8", newline="\n")


def regenerate(root: Path = ROOT, *, check: bool = False) -> list[str]:
    """Refresh both ledgers and their reports; return the paths that drifted."""
    drift: list[str] = []

    _refresh_ledger(DEFAULT_AUDIT, refresh_site_audit, root, check, drift)
    try:
        generate_report(DEFAULT_AUDIT, SITE_SCHEMA, DEFAULT_REPORT, root, check=check)
    except SiteAuditContractError as exc:
        if not check:
            raise EvidenceRegenerationError(str(exc)) from exc
        drift.append(f"{_relative(DEFAULT_REPORT)} ({exc})")

    _refresh_ledger(DEFAULT_INVENTORY, refresh_inventory, root, check, drift)
    try:
        generate(
            DEFAULT_INVENTORY,
            AuditSources(DEFAULT_SCHEMA, DEFAULT_CLAIMS, DEFAULT_LEDGER, root),
            ReportTargets(DEFAULT_REPORT_JSON, DEFAULT_REPORT_MARKDOWN),
            GenerationOptions(check=check),
        )
    except AuditContractError as exc:
        if not check:
            raise EvidenceRegenerationError(str(exc)) from exc
        drift.append(f"{_relative(DEFAULT_REPORT_MARKDOWN)} ({exc})")
    return drift


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n", maxsplit=1)[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report stale digests or reports without rewriting anything (exit 1 on drift).",
    )
    args = parser.parse_args(argv)
    try:
        drift = regenerate(check=args.check)
    except EvidenceRegenerationError as exc:
        print(f"claim-audit evidence regeneration failed: {exc}", file=sys.stderr)
        return 1
    if args.check:
        if drift:
            print(
                "claim-audit evidence is stale; run "
                "`python -m scripts.regenerate_claim_audit_evidence`:",
                file=sys.stderr,
            )
            for item in drift:
                print(f"  - {item}", file=sys.stderr)
            return 1
        print("claim-audit evidence digests and reports are current")
        return 0
    if drift:
        print(f"rewrote {len(drift)} claim-audit file(s):")
        for item in drift:
            print(f"  - {item}")
    else:
        print("claim-audit evidence digests and reports were already current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
