#!/usr/bin/env python3
"""Validate and report the #4062 book and publication-roadmap audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator, FormatChecker

from scripts.claim_audit_ids import stable_audit_id

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_AUDIT = ROOT / "data/trust/book_publication_audit.json"
DEFAULT_SCHEMA = ROOT / "schemas/book-publication-audit-v1.schema.json"
DEFAULT_REPORT = ROOT / "reports/book-publication-audit.md"
SCOPED_SOURCES = {
    "/books/biomechanics-biology-to-systems.html": "books/biomechanics-biology-to-systems.qmd",
    "/books/control-is-motion.html": "books/control-is-motion.qmd",
    "/books/human-motor-control.html": "books/human-motor-control.qmd",
    "/books/index.html": "books/index.qmd",
    "/books/roadmap.html": "books/roadmap.qmd",
    "/books/tangent-space-methods.html": "books/tangent-space-methods.qmd",
}
BLOCKING_PRIORITIES = frozenset({"p0", "p1"})
CLOSED_BLOCKERS = frozenset({"corrected", "publication_blocked"})


class BookAuditContractError(ValueError):
    """Raised when the book audit is incomplete or inconsistent."""


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BookAuditContractError(f"Cannot load JSON contract {path}: {exc}") from exc


def _records(audit: object) -> list[dict[str, object]]:
    if not isinstance(audit, dict) or not isinstance(audit.get("routes"), list):
        raise BookAuditContractError("Audit routes must be a list")
    records = audit["routes"]
    if not all(isinstance(record, dict) for record in records):
        raise BookAuditContractError("Audit route records must be objects")
    return cast(list[dict[str, object]], records)


def _validate_schema(audit: object, schema_path: Path) -> None:
    validator = Draft202012Validator(_json(schema_path), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(audit), key=lambda error: list(error.absolute_path))
    if errors:
        rendered = [
            f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
            for error in errors
        ]
        raise BookAuditContractError("; ".join(rendered))


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_source_evidence(record: dict[str, object], root: Path) -> None:
    source_path = str(record["source_path"])
    source = root / source_path
    if not source.is_file() or _digest(source) != record["source_sha256"]:
        raise BookAuditContractError(f"Source digest mismatch for {record['route']}: {source_path}")
    paths = cast(list[str], record["included_source_paths"])
    digests = cast(dict[str, str], record["included_source_sha256"])
    if set(paths) != set(digests):
        raise BookAuditContractError(
            f"Included source paths do not match digests for {record['route']}"
        )
    for path in paths:
        source = root / path
        if not source.is_file() or _digest(source) != digests[path]:
            raise BookAuditContractError(
                f"Included source digest mismatch for {record['route']}: {path}"
            )


def _validate_record(
    record: dict[str, object], root: Path, claim_ids: set[str], finding_ids: set[str]
) -> None:
    _validate_source_evidence(record, root)
    claims = cast(list[dict[str, object]], record["claims"])
    observed_classes = {
        str(item) for claim in claims for item in cast(list[str], claim["claim_classes"])
    }
    if observed_classes != set(cast(list[str], record["claim_classes"])):
        raise BookAuditContractError(f"Claim classes do not match claims for {record['route']}")
    for claim in claims:
        claim_id = str(claim["claim_id"])
        if claim_id in claim_ids:
            raise BookAuditContractError(f"Duplicate book claim ID: {claim_id}")
        claim_ids.add(claim_id)
        for reference in cast(list[str], claim["authority_references"]):
            if not reference.startswith("https://") and not (root / reference).is_file():
                raise BookAuditContractError(
                    f"Missing authority reference for {claim_id}: {reference}"
                )
    for finding in cast(list[dict[str, object]], record["findings"]):
        finding_id = str(finding["finding_id"])
        if finding_id in finding_ids:
            raise BookAuditContractError(f"Duplicate book finding ID: {finding_id}")
        finding_ids.add(finding_id)
        if (
            finding["priority"] in BLOCKING_PRIORITIES
            and finding["disposition"] not in CLOSED_BLOCKERS
        ):
            raise BookAuditContractError(f"P0/P1 finding {finding_id} is not corrected or blocked")
        for evidence in cast(list[str], finding["evidence_paths"]):
            if not (root / evidence).is_file():
                raise BookAuditContractError(
                    f"Missing finding evidence for {finding_id}: {evidence}"
                )


def validate_audit(audit: object, schema_path: Path, root: Path) -> None:
    """Validate exact scope, schema, immutable source bytes, claims, and blockers."""
    _validate_schema(audit, schema_path)
    records = _records(audit)
    observed = {str(record.get("route")): str(record.get("source_path")) for record in records}
    if len(records) != 6 or observed != SCOPED_SOURCES:
        raise BookAuditContractError("Audit must match the exact six-route book scope")
    if [str(record["route"]) for record in records] != sorted(observed, key=str.casefold):
        raise BookAuditContractError("Audit routes must be deterministically sorted")
    claim_ids: set[str] = set()
    finding_ids: set[str] = set()
    for record in records:
        if record["audit_id"] != stable_audit_id(str(record["route"])):
            raise BookAuditContractError(f"Unstable audit ID for {record['route']}")
        _validate_record(record, root, claim_ids, finding_ids)


def build_report(audit: object) -> dict[str, object]:
    """Build a deterministic summary without duplicating audit authority prose."""
    classes: Counter[str] = Counter()
    states: Counter[str] = Counter()
    priorities: Counter[str] = Counter()
    dispositions: Counter[str] = Counter()
    routes: list[dict[str, object]] = []
    for record in _records(audit):
        claims = cast(list[dict[str, object]], record["claims"])
        findings = cast(list[dict[str, object]], record["findings"])
        classes.update(
            str(item) for claim in claims for item in cast(list[str], claim["claim_classes"])
        )
        states.update(str(claim["publication_state"]) for claim in claims)
        priorities.update(str(finding["priority"]) for finding in findings)
        dispositions.update(str(finding["disposition"]) for finding in findings)
        routes.append(
            {
                "audit_id": record["audit_id"],
                "claim_classes": record["claim_classes"],
                "claim_count": len(claims),
                "finding_ids": [finding["finding_id"] for finding in findings],
                "route": record["route"],
                "source_path": record["source_path"],
                "source_sha256": record["source_sha256"],
                "source_revision": record["source_revision"],
            }
        )
    return {
        "claim_class_counts": dict(sorted(classes.items())),
        "finding_disposition_counts": dict(sorted(dispositions.items())),
        "finding_priority_counts": dict(sorted(priorities.items())),
        "publication_state_counts": dict(sorted(states.items())),
        "route_count": len(routes),
        "routes": routes,
    }


def _counts(value: object) -> str:
    mapping = cast(dict[str, int], value)
    return ", ".join(f"{key}={mapping[key]}" for key in sorted(mapping)) or "none"


def _markdown_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    """Render the deterministic, Prettier-compatible audit table."""
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]

    def cells(row: list[str]) -> str:
        values = [
            value.rjust(widths[index]) if index == 5 else value.ljust(widths[index])
            for index, value in enumerate(row)
        ]
        return "| " + " | ".join(values) + " |"

    separators = [
        ("-" * (widths[index] - 1) + ":") if index == 5 else "-" * widths[index]
        for index in range(len(headers))
    ]
    return [cells(headers), cells(separators), *(cells(row) for row in rows)]


def render_report(report: dict[str, object]) -> str:
    """Render the compact human-readable book audit index."""
    lines = [
        "# Book and Publication-Roadmap Audit",
        "",
        "<!-- DO NOT EDIT. Generated by scripts/book_publication_audit.py. -->",
        "",
        f"- Routes reviewed: {report['route_count']}",
        f"- Claim classes: {_counts(report['claim_class_counts'])}",
        f"- Publication states: {_counts(report['publication_state_counts'])}",
        f"- Finding priorities: {_counts(report['finding_priority_counts'])}",
        f"- Finding dispositions: {_counts(report['finding_disposition_counts'])}",
        "",
    ]
    rows: list[list[str]] = []
    for route in cast(list[dict[str, object]], report["routes"]):
        classes = ", ".join(str(item) for item in cast(list[str], route["claim_classes"]))
        findings = ", ".join(str(item) for item in cast(list[str], route["finding_ids"]))
        rows.append(
            [
                f"`{route['audit_id']}`",
                f"`{route['route']}`",
                f"`{route['source_path']}`",
                f"`{route['source_sha256']}`",
                classes,
                str(route["claim_count"]),
                findings,
                f"`{route['source_revision']}`",
            ]
        )
    lines.extend(
        _markdown_table(
            [
                "Audit ID",
                "Route",
                "Source",
                "SHA-256",
                "Claim Classes",
                "Claims",
                "Findings",
                "Review Revision",
            ],
            rows,
        )
    )
    lines.append("")
    return "\n".join(lines)


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
            raise BookAuditContractError(f"Generated book audit report is stale: {output_path}")
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
    except BookAuditContractError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
