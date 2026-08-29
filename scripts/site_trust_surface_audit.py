#!/usr/bin/env python3
"""Validate and report the #4063 site-level trust-surface audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator, FormatChecker

from scripts.claim_audit_ids import stable_audit_id

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_AUDIT = ROOT / "data/trust/site_trust_surface_audit.json"
DEFAULT_SCHEMA = ROOT / "schemas/site-trust-surface-audit-v1.schema.json"
DEFAULT_REPORT = ROOT / "reports/site-trust-surface-audit.md"
ISSUE_URL = "https://github.com/D-sorganization/AffineDrift/issues/4063"
SCOPED_SOURCES = {
    "/": "index.qmd",
    "/pages/about.html": "pages/about.qmd",
    "/pages/book-reviews.html": "pages/book-reviews.qmd",
    "/pages/collaborate.html": "pages/collaborate.qmd",
    "/pages/contact.html": "pages/contact.qmd",
    "/pages/daydreams-doodles.html": "pages/daydreams-doodles.qmd",
    "/pages/development-roadmap.html": "pages/development-roadmap.qmd",
    "/pages/drifter-manifesto.html": "pages/drifter-manifesto.qmd",
    "/pages/notation.html": "pages/notation.qmd",
    "/pages/overview.html": "pages/overview.qmd",
    "/pages/tangent-hyperplanes.html": "pages/tangent-hyperplanes.qmd",
    "/pages/technology.html": "pages/technology.qmd",
    "/pages/tools.html": "pages/tools.qmd",
}
BLOCKING_PRIORITIES = frozenset({"p0", "p1"})
BLOCKING_DISPOSITIONS = frozenset({"corrected", "publication_blocked"})


class SiteAuditContractError(ValueError):
    """Raised when the site-level audit is incomplete or inconsistent."""


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SiteAuditContractError(f"Cannot load JSON contract {path}: {exc}") from exc


def _records(audit: object) -> list[dict[str, object]]:
    if not isinstance(audit, dict) or not isinstance(audit.get("routes"), list):
        raise SiteAuditContractError("Audit routes must be a list")
    records = audit["routes"]
    if not all(isinstance(record, dict) for record in records):
        raise SiteAuditContractError("Audit route records must be objects")
    return cast(list[dict[str, object]], records)


def _validate_schema(audit: object, schema_path: Path) -> None:
    validator = Draft202012Validator(_json(schema_path), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(audit), key=lambda error: list(error.absolute_path))
    if errors:
        rendered = [
            f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
            for error in errors
        ]
        raise SiteAuditContractError("; ".join(rendered))


def _validate_scope(records: list[dict[str, object]]) -> None:
    observed = {str(record.get("route")): str(record.get("source_path")) for record in records}
    if len(records) != 13 or observed != SCOPED_SOURCES:
        raise SiteAuditContractError("Audit must match the exact 13-route scope")
    order = [str(record["route"]) for record in records]
    if order != sorted(order, key=str.casefold):
        raise SiteAuditContractError("Audit route scope must be deterministically sorted")
    for record in records:
        if record.get("audit_id") != stable_audit_id(str(record["route"])):
            raise SiteAuditContractError(f"{record['route']} does not use its stable audit ID")


def _reference_exists(reference: str, root: Path) -> bool:
    return reference.startswith("https://") or (root / reference).is_file()


def _validate_claims(record: dict[str, object], root: Path, seen: set[str]) -> None:
    claims = cast(list[dict[str, object]], record["claims"])
    classes = {str(item) for claim in claims for item in cast(list[str], claim["claim_classes"])}
    if set(cast(list[str], record["claim_classes"])) != classes:
        raise SiteAuditContractError(f"{record['route']} claim classes do not match its claims")
    for claim in claims:
        claim_id = str(claim["claim_id"])
        if claim_id in seen:
            raise SiteAuditContractError(f"Duplicate surface claim ID: {claim_id}")
        seen.add(claim_id)
        authority = cast(dict[str, object], claim["authority"])
        references = cast(list[str], authority["references"])
        if any(not _reference_exists(reference, root) for reference in references):
            raise SiteAuditContractError(f"{claim_id} has a missing authority reference")


def _validate_findings(record: dict[str, object], root: Path, seen: set[str]) -> None:
    for finding in cast(list[dict[str, object]], record["findings"]):
        finding_id = str(finding["finding_id"])
        if finding_id in seen:
            raise SiteAuditContractError(f"Duplicate finding ID: {finding_id}")
        seen.add(finding_id)
        if finding["priority"] in BLOCKING_PRIORITIES:
            if finding["disposition"] not in BLOCKING_DISPOSITIONS:
                raise SiteAuditContractError(f"P0/P1 finding {finding_id} is not closed or blocked")
        evidence = cast(list[str], finding.get("evidence_paths", []))
        if finding["disposition"] == "corrected" and (
            not evidence or any(not (root / path).is_file() for path in evidence)
        ):
            raise SiteAuditContractError(f"Corrected finding {finding_id} lacks local evidence")


def validate_audit(audit: object, schema_path: Path, root: Path) -> None:
    """Validate schema, exact scope, stable identities, evidence, and blockers."""
    _validate_schema(audit, schema_path)
    records = _records(audit)
    _validate_scope(records)
    claim_ids: set[str] = set()
    finding_ids: set[str] = set()
    for record in records:
        sources = [record["source_path"], *cast(list[str], record.get("included_source_paths", []))]
        if any(not (root / str(source)).is_file() for source in sources):
            raise SiteAuditContractError(f"Missing source for {record['route']}")
        _validate_claims(record, root, claim_ids)
        _validate_findings(record, root, finding_ids)


def build_report(audit: object) -> dict[str, object]:
    """Build a deterministic aggregate without duplicating authority prose."""
    records = _records(audit)
    classes: Counter[str] = Counter()
    states: Counter[str] = Counter()
    priorities: Counter[str] = Counter()
    dispositions: Counter[str] = Counter()
    routes: list[dict[str, object]] = []
    for record in records:
        claims = cast(list[dict[str, object]], record["claims"])
        findings = cast(list[dict[str, object]], record["findings"])
        classes.update(
            str(item) for claim in claims for item in cast(list[str], claim["claim_classes"])
        )
        states.update(str(claim["publication_state"]) for claim in claims)
        priorities.update(str(finding["priority"]) for finding in findings)
        dispositions.update(str(finding["disposition"]) for finding in findings)
        routes.append(_route_report(record, claims, findings))
    return {
        "claim_class_counts": dict(sorted(classes.items())),
        "finding_disposition_counts": dict(sorted(dispositions.items())),
        "finding_priority_counts": dict(sorted(priorities.items())),
        "publication_state_counts": dict(sorted(states.items())),
        "route_count": len(records),
        "routes": routes,
    }


def _route_report(
    record: dict[str, object],
    claims: list[dict[str, object]],
    findings: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "audit_id": record["audit_id"],
        "claim_classes": record["claim_classes"],
        "claim_count": len(claims),
        "finding_ids": [finding["finding_id"] for finding in findings],
        "route": record["route"],
        "source_path": record["source_path"],
        "included_source_paths": record.get("included_source_paths", []),
        "source_revision": record["source_revision"],
    }


def render_report(report: dict[str, object]) -> str:
    """Render the compact human-readable audit index."""
    lines = [
        "# Site-Level Trust-Surface Audit",
        "",
        "<!-- DO NOT EDIT. Generated by scripts/site_trust_surface_audit.py. -->",
        "",
        f"- Routes reviewed: {report['route_count']}",
        f"- Claim classes: {_counts(report['claim_class_counts'])}",
        f"- Publication states: {_counts(report['publication_state_counts'])}",
        f"- Finding priorities: {_counts(report['finding_priority_counts'])}",
        f"- Finding dispositions: {_counts(report['finding_disposition_counts'])}",
        "",
        "| Audit ID | Route | Source | Claim Classes | Claims | Findings | Review Revision |",
        "|---|---|---|---|---:|---|---|",
    ]
    for route in cast(list[dict[str, object]], report["routes"]):
        classes = ", ".join(str(item) for item in cast(list[str], route["claim_classes"]))
        findings = ", ".join(str(item) for item in cast(list[str], route["finding_ids"]))
        revision = str(route["source_revision"])
        lines.append(
            f"| `{route['audit_id']}` | `{route['route']}` | `{route['source_path']}` | "
            f"{classes} | {route['claim_count']} | {findings or 'None'} | `{revision}` |"
        )
    lines.append("")
    return "\n".join(lines)


def _counts(value: object) -> str:
    mapping = cast(dict[str, int], value)
    return ", ".join(f"{key}={mapping[key]}" for key in sorted(mapping)) or "none"


def generate_report(
    audit_path: Path,
    schema_path: Path,
    output_path: Path,
    root: Path,
    *,
    check: bool = False,
) -> Path:
    """Validate and write or compare the deterministic Markdown report."""
    audit = _json(audit_path)
    validate_audit(audit, schema_path, root)
    expected = render_report(build_report(audit))
    if check:
        if not output_path.is_file() or output_path.read_text(encoding="utf-8") != expected:
            raise SiteAuditContractError(f"Generated site audit report is stale: {output_path}")
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(expected, encoding="utf-8", newline="\n")
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        generate_report(args.audit, args.schema, args.report, ROOT, check=args.check)
    except SiteAuditContractError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
