#!/usr/bin/env python3
"""Validate the rendered-route claim audit and generate deterministic reports."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator, FormatChecker

from scripts.claim_audit_evidence import (
    ReviewEvidenceError,
    validate_digest_map,
    validate_review_evidence,
)
from scripts.claim_audit_ids import deferred_issue_url, source_route, stable_audit_id
from scripts.claim_audit_report import (
    BLOCKED_DISPOSITION,
    BLOCKING_PRIORITIES,
    MANIFEST_CONTRACT,
    REVIEW_DIMENSIONS,
    build_joined_report,
    publication_blocker_ids,
    render_markdown,
    write_or_check,
)
from scripts.claim_audit_types import AuditSources, GenerationOptions, ReportTargets

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INVENTORY = ROOT / "data/trust/claim_audit_inventory.json"
DEFAULT_SCHEMA = ROOT / "schemas/claim-audit-inventory-v1.schema.json"
DEFAULT_CLAIMS = ROOT / "data/trust/claim_registry.json"
DEFAULT_LEDGER = ROOT / "data/trust/claim_critique_ledger.json"
DEFAULT_REPORT_JSON = ROOT / "data/trust/generated/claim_audit_report.json"
DEFAULT_REPORT_MARKDOWN = ROOT / "reports/scientific-claim-audit.md"


class AuditContractError(ValueError):
    """Raised when the rendered-route audit fails closed."""


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuditContractError(f"Cannot load JSON contract {path}: {exc}") from exc


def _records(inventory: object) -> list[dict[str, object]]:
    if not isinstance(inventory, dict) or not isinstance(inventory.get("routes"), list):
        raise AuditContractError("Inventory routes must be a list")
    records = inventory["routes"]
    if not all(isinstance(record, dict) for record in records):
        raise AuditContractError("Inventory route records must be objects")
    return [record for record in records if isinstance(record, dict)]


def _schema_errors(inventory: object, schema_path: Path) -> list[str]:
    validator = Draft202012Validator(_json(schema_path), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(inventory), key=lambda error: list(error.absolute_path))
    return [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in errors
    ]


def _claim_authority(path: Path) -> tuple[dict[str, dict[str, object]], dict[str, set[str]]]:
    registry = _json(path)
    if not isinstance(registry, dict) or not isinstance(registry.get("pages"), list):
        raise AuditContractError("Claim registry pages must be a list")
    claims: dict[str, dict[str, object]] = {}
    by_route: dict[str, set[str]] = defaultdict(set)
    for page in registry["pages"]:
        if not isinstance(page, dict) or not isinstance(page.get("claims"), list):
            raise AuditContractError("Claim registry page is invalid")
        page_route = source_route(page.get("source_path"))
        for claim in page["claims"]:
            if not isinstance(claim, dict):
                raise AuditContractError("Claim registry claim is invalid")
            claim_id = str(claim.get("claim_id", ""))
            if not claim_id or claim_id in claims:
                raise AuditContractError(f"Duplicate or empty claim ID: {claim_id}")
            claims[claim_id] = claim
            by_route[page_route].add(claim_id)
    return claims, by_route


def _critique_authority(path: Path) -> tuple[dict[str, dict[str, object]], dict[str, set[str]]]:
    ledger = _json(path)
    if not isinstance(ledger, dict) or not isinstance(ledger.get("critiques"), list):
        raise AuditContractError("Critique ledger records must be a list")
    critiques: dict[str, dict[str, object]] = {}
    by_route: dict[str, set[str]] = defaultdict(set)
    for critique in ledger["critiques"]:
        if not isinstance(critique, dict):
            raise AuditContractError("Critique ledger record is invalid")
        critique_id = str(critique.get("critique_id", ""))
        if not critique_id or critique_id in critiques:
            raise AuditContractError(f"Duplicate or empty critique ID: {critique_id}")
        critiques[critique_id] = critique
        by_route[source_route(critique.get("source_path"))].add(critique_id)
        affected = critique.get("affected_pages", [])
        if not isinstance(affected, list):
            raise AuditContractError(f"{critique_id} affected pages must be a list")
        for page in affected:
            by_route[source_route(page)].add(critique_id)
    return critiques, by_route


def _validate_review(record: dict[str, object], root: Path) -> None:
    if record.get("status") != "reviewed":
        return
    review = record.get("review")
    if not isinstance(review, dict):
        raise AuditContractError(f"{record.get('route')} reviewed route lacks review evidence")
    dimensions = review.get("dimensions")
    if not isinstance(dimensions, list) or set(dimensions) != REVIEW_DIMENSIONS:
        raise AuditContractError(f"{record.get('route')} review dimensions are incomplete")
    try:
        validate_review_evidence(record, root)
    except ReviewEvidenceError as exc:
        raise AuditContractError(str(exc)) from exc


def _validate_deferment(record: dict[str, object]) -> None:
    if record.get("status") != "deferred":
        return
    route = str(record.get("route", ""))
    deferment = record.get("deferment")
    if not isinstance(deferment, dict):
        raise AuditContractError(f"{route} deferred route lacks deferment evidence")
    try:
        expected_issue = deferred_issue_url(route)
    except ValueError as exc:
        raise AuditContractError(str(exc)) from exc
    if deferment.get("issue_url") != expected_issue:
        raise AuditContractError(f"{route} must defer to its exact child issue {expected_issue}")


def _validate_findings(record: dict[str, object], root: Path) -> set[str]:
    findings = record.get("findings")
    if not isinstance(findings, list):
        raise AuditContractError(f"{record.get('route')} findings must be a list")
    ids: set[str] = set()
    for finding in findings:
        if not isinstance(finding, dict):
            raise AuditContractError(f"{record.get('route')} finding must be an object")
        finding_id = str(finding.get("finding_id", ""))
        if finding_id in ids:
            raise AuditContractError(f"Duplicate finding ID: {finding_id}")
        ids.add(finding_id)
        priority = finding.get("priority")
        disposition = finding.get("disposition")
        if priority in BLOCKING_PRIORITIES and disposition not in {
            "corrected",
            BLOCKED_DISPOSITION,
        }:
            raise AuditContractError(
                f"P0/P1 finding {finding_id} must be corrected or publication_blocked"
            )
        if disposition == "corrected":
            try:
                validate_digest_map(
                    root,
                    finding.get("evidence_paths"),
                    finding.get("evidence_sha256"),
                    label=f"corrected finding {finding_id} evidence",
                )
            except ReviewEvidenceError as exc:
                raise AuditContractError(str(exc)) from exc
            if not finding.get("verification_commit"):
                raise AuditContractError(
                    f"Corrected finding {finding_id} lacks verification commit"
                )
    return ids


def _validate_record_links(
    record: dict[str, object],
    claim_links: dict[str, set[str]],
    critique_links: dict[str, set[str]],
) -> None:
    route = str(record.get("route", ""))
    expected_claims = sorted(claim_links.get(route, set()))
    expected_critiques = sorted(critique_links.get(route, set()))
    if record.get("claim_ids") != expected_claims:
        raise AuditContractError(f"{route} claim authority links do not match #4019")
    if record.get("critique_ids") != expected_critiques:
        raise AuditContractError(f"{route} critique authority links do not match #4020")


def validate_inventory(inventory: object, sources: AuditSources) -> None:
    """Validate schema, stable identities, evidence, and exact authority links."""
    errors = _schema_errors(inventory, sources.schema)
    if errors:
        raise AuditContractError("; ".join(errors))
    records = _records(inventory)
    claims, claim_links = _claim_authority(sources.claims)
    critiques, critique_links = _critique_authority(sources.ledger)
    route_order = [str(record["route"]) for record in records]
    if route_order != sorted(route_order, key=str.casefold):
        raise AuditContractError("Inventory routes must be sorted deterministically")
    if len(route_order) != len(set(route_order)):
        raise AuditContractError("Inventory contains duplicate routes")
    finding_ids: set[str] = set()
    for record in records:
        route = str(record["route"])
        if record["audit_id"] != stable_audit_id(route):
            raise AuditContractError(f"{route} does not use its stable audit ID")
        _validate_record_links(record, claim_links, critique_links)
        _validate_review(record, sources.root)
        _validate_deferment(record)
        new_ids = _validate_findings(record, sources.root)
        if finding_ids.intersection(new_ids):
            raise AuditContractError("Finding IDs must be unique across routes")
        finding_ids.update(new_ids)
        for finding in cast(list[dict[str, object]], record["findings"]):
            if not set(cast(list[str], finding["claim_ids"])).issubset(claims):
                raise AuditContractError(f"{finding['finding_id']} has an unknown claim ID")
            if not set(cast(list[str], finding["critique_ids"])).issubset(critiques):
                raise AuditContractError(f"{finding['finding_id']} has an unknown critique ID")


def validate_manifest_coverage(inventory: object, manifest: object) -> None:
    """Require an exact one-to-one match with the rendered public manifest."""
    if not isinstance(manifest, dict) or manifest.get("schema_version") != MANIFEST_CONTRACT:
        raise AuditContractError("Rendered manifest schema is missing or unsupported")
    pages = manifest.get("pages")
    if not isinstance(pages, list) or not all(isinstance(page, dict) for page in pages):
        raise AuditContractError("Rendered manifest pages must be objects")
    rendered = [str(page.get("route", "")) for page in pages if isinstance(page, dict)]
    audited = [str(record["route"]) for record in _records(inventory)]
    if len(rendered) != len(set(rendered)):
        raise AuditContractError("Rendered manifest contains duplicate routes")
    if set(rendered) != set(audited):
        missing = sorted(set(rendered) - set(audited))
        extra = sorted(set(audited) - set(rendered))
        raise AuditContractError(
            f"Rendered-route coverage mismatch; missing={missing or 'none'}; extra={extra or 'none'}"
        )


def _initial_record(
    page: dict[str, object],
    claim_links: dict[str, set[str]],
    critique_links: dict[str, set[str]],
    as_of: str,
) -> dict[str, object]:
    route = str(page.get("route", ""))
    record: dict[str, object] = {
        "audit_id": stable_audit_id(route),
        "claim_ids": sorted(claim_links.get(route, set())),
        "critique_ids": sorted(critique_links.get(route, set())),
        "findings": [],
        "route": route,
    }
    if page.get("page_kind") == "system":
        record.update(
            {
                "status": "exempt",
                "exemption": {
                    "approved_by": "Issue #4021 scoped audit contract",
                    "approved_on": as_of,
                    "issue_url": "https://github.com/D-sorganization/AffineDrift/issues/4021",
                    "rationale": "The system route contains no scientific analysis or claim.",
                    "scope": "Static error and offline handling only.",
                },
            }
        )
    else:
        record.update(
            {
                "status": "deferred",
                "deferment": {
                    "issue_url": deferred_issue_url(route),
                    "next_gate": "Complete the route-level adversarial scientific claim review.",
                    "rationale": "No completed #4021 route-level adversarial review is registered.",
                },
            }
        )
    return record


def initialize_inventory(
    manifest: object,
    sources: AuditSources,
    as_of: str,
) -> dict[str, object]:
    """Create a deterministic fail-closed inventory from a rendered manifest."""
    try:
        date.fromisoformat(as_of)
    except ValueError as exc:
        raise AuditContractError(f"Inventory initialization date is invalid: {as_of}") from exc
    if not isinstance(manifest, dict) or manifest.get("schema_version") != MANIFEST_CONTRACT:
        raise AuditContractError("Rendered manifest schema is missing or unsupported")
    pages = manifest.get("pages")
    if not isinstance(pages, list) or not all(isinstance(page, dict) for page in pages):
        raise AuditContractError("Rendered manifest pages must be objects")
    _, claim_links = _claim_authority(sources.claims)
    _, critique_links = _critique_authority(sources.ledger)
    routes = [
        _initial_record(page, claim_links, critique_links, as_of)
        for page in pages
        if isinstance(page, dict)
    ]
    routes.sort(key=lambda record: str(record["route"]).casefold())
    inventory: dict[str, object] = {
        "claim_registry": "data/trust/claim_registry.json",
        "critique_ledger": "data/trust/claim_critique_ledger.json",
        "manifest_contract": MANIFEST_CONTRACT,
        "routes": routes,
        "schema_version": "1.1.0",
    }
    validate_inventory(inventory, sources)
    validate_manifest_coverage(inventory, manifest)
    return inventory


def enforce_publication(inventory: object) -> None:
    """Refuse publication while any governed P0/P1 finding remains blocked."""
    blockers = publication_blocker_ids(_records(inventory))
    if blockers:
        raise AuditContractError("P0/P1 publication blocker(s): " + ", ".join(blockers))


def build_report(inventory: object, sources: AuditSources) -> dict[str, object]:
    """Join audit state to claim/critique authorities without copying their prose."""
    claims, _ = _claim_authority(sources.claims)
    critiques, _ = _critique_authority(sources.ledger)
    return build_joined_report(_records(inventory), claims, critiques)


def generate(
    inventory_path: Path,
    sources: AuditSources,
    targets: ReportTargets,
    options: GenerationOptions | None = None,
) -> list[Path]:
    """Validate the inventory and generate or verify deterministic reports."""
    options = options or GenerationOptions()
    inventory = _json(inventory_path)
    validate_inventory(inventory, sources)
    if options.manifest is not None:
        validate_manifest_coverage(inventory, _json(options.manifest))
    if options.enforce:
        enforce_publication(inventory)
    report = build_report(inventory, sources)
    report_json = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    try:
        write_or_check(targets.json, report_json, options.check)
        write_or_check(targets.markdown, render_markdown(report), options.check)
    except ValueError as exc:
        raise AuditContractError(str(exc)) from exc
    return [targets.json, targets.markdown]


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--claims", type=Path, default=DEFAULT_CLAIMS)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--enforce-publication", action="store_true")
    parser.add_argument("--initialize-from-manifest", action="store_true")
    parser.add_argument("--as-of")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for local and protected publication gates."""
    args = _parse_args(argv)
    sources = AuditSources(args.schema, args.claims, args.ledger, args.root)
    targets = ReportTargets(args.report_json, args.report_markdown)
    options = GenerationOptions(args.manifest, args.check, args.enforce_publication)
    try:
        if args.initialize_from_manifest:
            if args.manifest is None or args.as_of is None:
                raise AuditContractError("Initialization requires --manifest and --as-of")
            inventory = initialize_inventory(_json(args.manifest), sources, args.as_of)
            canonical = json.dumps(inventory, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
            args.inventory.parent.mkdir(parents=True, exist_ok=True)
            args.inventory.write_text(canonical, encoding="utf-8", newline="\n")
        outputs = generate(args.inventory, sources, targets, options)
    except AuditContractError as exc:
        print(f"claim-audit inventory contract failed: {exc}", file=sys.stderr)
        return 1
    action = "verified" if args.check else "generated"
    print(f"{action} {len(outputs)} claim-audit report(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
