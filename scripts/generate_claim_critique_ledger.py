#!/usr/bin/env python3
"""Validate and generate public claim/critique adjudication surfaces."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LEDGER = ROOT / "data/trust/claim_critique_ledger.json"
DEFAULT_SCHEMA = ROOT / "schemas/claim-critique-ledger-v1.schema.json"
DEFAULT_CLAIMS = ROOT / "data/trust/claim_registry.json"

ADJUDICATED = frozenset({"responded", "resolved", "rejected"})
ALLOWED_TRANSITIONS = {
    "unknown": {"open", "responded", "deferred"},
    "open": {"responded", "deferred"},
    "responded": {"open", "resolved", "rejected", "deferred"},
    "deferred": {"open", "responded"},
    "resolved": set(),
    "rejected": set(),
}


class LedgerContractError(ValueError):
    """Raised when claim/critique governance fails closed."""


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LedgerContractError(f"Cannot load JSON contract {path}: {exc}") from exc


def normalized_status(status: object) -> str:
    """Normalize unknown critique state to the public fail-closed OPEN state."""
    value = str(status)
    return "open" if value == "unknown" else value


def _checked_repo_file(root: Path, raw_path: str, missing_message: str) -> Path:
    """Resolve a declared repository file without allowing path traversal."""
    parts = PurePosixPath(raw_path).parts
    if any(part in {".", ".."} for part in parts):
        raise LedgerContractError(f"Repository path traversal is forbidden: {raw_path}")
    candidate = (root / Path(*parts)).resolve()
    resolved_root = root.resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise LedgerContractError(f"Repository path traversal is forbidden: {raw_path}") from exc
    if not candidate.is_file():
        raise LedgerContractError(missing_message)
    return candidate


def _claim_ids(claims_path: Path) -> set[str]:
    claims = _json(claims_path)
    if not isinstance(claims, dict) or not isinstance(claims.get("pages"), list):
        raise LedgerContractError("Claim registry pages must be a list")
    result: set[str] = set()
    for page in claims["pages"]:
        if not isinstance(page, dict) or not isinstance(page.get("claims"), list):
            raise LedgerContractError("Claim registry page is invalid")
        for claim in page["claims"]:
            if not isinstance(claim, dict):
                raise LedgerContractError("Claim registry claim is invalid")
            claim_id = str(claim.get("claim_id", ""))
            if not claim_id or claim_id in result:
                raise LedgerContractError(f"Duplicate or empty claim ID: {claim_id}")
            result.add(claim_id)
    return result


def _public_critiques(root: Path) -> set[str]:
    excluded = {"DEFENSE_STRATEGY.md", "INLINE_SUGGESTIONS.md"}
    return {
        path.relative_to(root).as_posix()
        for path in (root / "critiques").glob("*.md")
        if "-bibliography" not in path.name and path.name not in excluded
    }


def _schema_errors(ledger: object, schema_path: Path) -> list[str]:
    validator = Draft202012Validator(_json(schema_path), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(ledger), key=lambda error: list(error.absolute_path))
    return [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in errors
    ]


def validate_ledger(
    ledger: object,
    schema_path: Path = DEFAULT_SCHEMA,
    claims_path: Path = DEFAULT_CLAIMS,
    root: Path = ROOT,
) -> None:
    """Validate schema, coverage, references, transitions, and active statements."""
    errors = _schema_errors(ledger, schema_path)
    if errors:
        raise LedgerContractError("; ".join(errors))
    if not isinstance(ledger, dict):
        raise LedgerContractError("Ledger must be an object")
    critiques = ledger.get("critiques")
    if not isinstance(critiques, list):
        raise LedgerContractError("Ledger critiques must be a list")

    known_claims = _claim_ids(claims_path)
    critique_ids: set[str] = set()
    sources: set[str] = set()
    for raw in critiques:
        if not isinstance(raw, dict):
            raise LedgerContractError("Critique record must be an object")
        critique_id = str(raw["critique_id"])
        source = str(raw["source_path"])
        if critique_id in critique_ids:
            raise LedgerContractError(f"Duplicate critique ID: {critique_id}")
        if source in sources:
            raise LedgerContractError(f"Duplicate critique source: {source}")
        critique_ids.add(critique_id)
        sources.add(source)
        _checked_repo_file(root, source, f"Missing critique source: {source}")

        affected = raw.get("affected_pages")
        if not isinstance(affected, list):
            raise LedgerContractError(f"{critique_id} affected pages must be a list")
        for page in affected:
            _checked_repo_file(
                root,
                str(page),
                f"{critique_id} has missing affected page: {page}",
            )

        related = raw.get("related_claim_ids")
        if not isinstance(related, list):
            raise LedgerContractError(f"{critique_id} related claim IDs must be a list")
        dangling = sorted(str(value) for value in related if str(value) not in known_claims)
        if dangling:
            raise LedgerContractError(
                f"{critique_id} has dangling claim ID(s): {', '.join(dangling)}"
            )

        status = normalized_status(raw["disposition"])
        adjudication = raw.get("adjudication")
        if status in ADJUDICATED and not isinstance(adjudication, dict):
            raise LedgerContractError(f"{critique_id} requires adjudication evidence")
        if isinstance(adjudication, dict):
            evidence = adjudication.get("evidence_paths")
            if not isinstance(evidence, list):
                raise LedgerContractError(f"{critique_id} adjudication evidence must be a list")
            for path in evidence:
                _checked_repo_file(
                    root,
                    str(path),
                    f"{critique_id} has missing evidence path: {path}",
                )

        history = raw.get("history", [])
        if not isinstance(history, list):
            raise LedgerContractError(f"{critique_id} history must be a list")
        previous_target: str | None = None
        for event in history:
            if not isinstance(event, dict):
                raise LedgerContractError(f"{critique_id} history event must be an object")
            source_status = normalized_status(event["from"])
            target_status = normalized_status(event["to"])
            if previous_target is not None and source_status != previous_target:
                raise LedgerContractError(
                    f"{critique_id} has non-contiguous history: "
                    f"{previous_target} -> {source_status}"
                )
            if target_status not in ALLOWED_TRANSITIONS[source_status]:
                raise LedgerContractError(
                    f"{critique_id} invalid transition: {source_status} -> {target_status}"
                )
            previous_target = target_status
        if history and normalized_status(history[-1]["to"]) != status:
            raise LedgerContractError(f"{critique_id} history does not end at disposition {status}")

        if status == "resolved":
            markers = raw.get("contradiction_markers", [])
            if not isinstance(markers, list):
                raise LedgerContractError(f"{critique_id} contradiction markers must be a list")
            if not markers:
                raise LedgerContractError(
                    f"{critique_id} resolved state requires a contradiction marker"
                )
            page_text = "\n".join(
                _checked_repo_file(
                    root,
                    str(page),
                    f"{critique_id} has missing affected page: {page}",
                ).read_text(encoding="utf-8")
                for page in affected
            )
            active = [str(marker) for marker in markers if str(marker) in page_text]
            if active:
                raise LedgerContractError(
                    f"{critique_id} contradictory active statement remains: {active[0]}"
                )

    expected = _public_critiques(root)
    if sources != expected:
        missing = sorted(expected - sources)
        extra = sorted(sources - expected)
        raise LedgerContractError(
            f"Critique coverage mismatch; missing={missing or 'none'}; extra={extra or 'none'}"
        )


def load_ledger(
    ledger_path: Path = DEFAULT_LEDGER,
    schema_path: Path = DEFAULT_SCHEMA,
    claims_path: Path = DEFAULT_CLAIMS,
    root: Path = ROOT,
) -> dict[str, object]:
    """Load and validate the canonical ledger."""
    ledger = _json(ledger_path)
    validate_ledger(ledger, schema_path, claims_path, root)
    if not isinstance(ledger, dict):
        raise LedgerContractError("Ledger must be an object")
    return ledger


def _title(root: Path, source: str) -> str:
    text = (root / source).read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise LedgerContractError(f"Critique source lacks frontmatter title: {source}")
    try:
        metadata = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        raise LedgerContractError(f"Invalid critique frontmatter: {source}: {exc}") from exc
    if not isinstance(metadata, dict) or not isinstance(metadata.get("title"), str):
        raise LedgerContractError(f"Critique source lacks frontmatter title: {source}")
    return str(metadata["title"])


def _route(source_path: str) -> str:
    path = Path(source_path)
    return f"/{path.with_suffix('.html').as_posix()}"


def _page_links(pages: list[object]) -> str:
    links: list[str] = []
    for page in pages:
        label = Path(str(page)).stem.replace("-", " ")
        label = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", label).title()
        links.append(f"[{html.escape(label)}]({_route(str(page))})")
    return ", ".join(links)


def _list_field(record: dict[str, object], key: str) -> list[object]:
    value = record.get(key)
    if not isinstance(value, list):
        raise LedgerContractError(f"{record.get('critique_id', '<record>')} {key} must be a list")
    return value


def _status_rows(ledger: dict[str, object], root: Path) -> list[dict[str, object]]:
    critiques = ledger["critiques"]
    if not isinstance(critiques, list):
        raise LedgerContractError("Ledger critiques must be a list")
    rows: list[dict[str, object]] = []
    for raw in critiques:
        if not isinstance(raw, dict):
            raise LedgerContractError("Critique record must be an object")
        adjudication = raw.get("adjudication")
        verification = "Not verified"
        if isinstance(adjudication, dict):
            verification = (
                f"{adjudication['verified_on']} at "
                f"`{str(adjudication['verification_commit'])[:12]}`"
            )
        rows.append(
            {
                **raw,
                "title": _title(root, str(raw["source_path"])),
                "status": normalized_status(raw["disposition"]),
                "verification": verification,
            }
        )
    return sorted(rows, key=lambda row: str(row["critique_id"]))


def _render_status(rows: list[dict[str, object]], digest: str) -> str:
    lines = [
        "<!-- DO NOT EDIT. Generated by scripts/generate_claim_critique_ledger.py.",
        f"     Ledger SHA-256: {digest} -->",
        "",
        "## Governed Critique Status",
        "",
        "Unknown dispositions fail closed to **Open**. Responded is not the same as resolved; provenance establishes review history, not independent scientific validation.",
        "",
        "| Critique | Severity | Disposition | Affected Pages | Verification |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| [{html.escape(str(row['title']))}]({_route(str(row['source_path']))}) "
            f"| {str(row['severity']).title()} | {str(row['status']).title()} "
            f"| {_page_links(_list_field(row, 'affected_pages'))} | {row['verification']} |"
        )
    lines.append("")
    return "\n".join(lines)


def _render_defense(rows: list[dict[str, object]], ledger: dict[str, object], digest: str) -> str:
    defaults = ledger["defaults"]
    if not isinstance(defaults, dict):
        raise LedgerContractError("Ledger defaults must be an object")
    lines = [
        "---",
        'title: "AffineDrift Critique Adjudication Status"',
        'description: "Governed status, evidence, and next validation gates for every public critique of the AffineDrift scientific framework."',
        "---",
        "",
        "<!-- DO NOT EDIT. Generated by scripts/generate_claim_critique_ledger.py.",
        f"     Ledger SHA-256: {digest} -->",
        "",
        "## AffineDrift Critique Adjudication Status",
        "",
        "This generated view replaces the former hand-maintained defense plan. "
        "An **Open** entry has no protected adjudication evidence. A **Responded** entry records a bounded response but does not claim the critique is resolved.",
        "",
        "| Critique ID | Critique | Severity | Status | Rationale | Evidence / Next Gate |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        adjudication = row.get("adjudication")
        if isinstance(adjudication, dict):
            rationale = str(adjudication["rationale"])
            evidence = "; ".join(
                f"[{Path(str(path)).name}](../{path})" for path in adjudication["evidence_paths"]
            )
            gate = str(adjudication["next_gate"])
            evidence_and_gate = f"{evidence}; {html.escape(gate)}"
        else:
            rationale = str(defaults["open_rationale"])
            evidence_and_gate = "No verified evidence; next: " + html.escape(
                str(defaults["open_next_gate"])
            )
        lines.append(
            f"| `{row['critique_id']}` | [{html.escape(str(row['title']))}]({Path(str(row['source_path'])).name}) "
            f"| {str(row['severity']).title()} | {str(row['status']).title()} "
            f"| {html.escape(rationale)} | {evidence_and_gate} |"
        )
    lines.append("")
    return "\n".join(lines)


def _render_annotation(page: str, rows: list[dict[str, object]], digest: str) -> str:
    lines = [
        "<!-- DO NOT EDIT. Generated by scripts/generate_claim_critique_ledger.py.",
        f"     Ledger SHA-256: {digest} -->",
        "",
        '::: {.callout-caution collapse="true"}',
        "## Governed Critiques for This Page",
        "",
        "These entries remain visible until evidence-backed adjudication changes their governed status.",
        "",
    ]
    for row in rows:
        lines.append(
            f"- **{str(row['status']).title()} / {str(row['severity']).title()}:** "
            f"[{html.escape(str(row['title']))}]({_route(str(row['source_path']))}) "
            f"(`{row['critique_id']}`)"
        )
    lines.extend(["", ":::", ""])
    return "\n".join(lines)


def _search_projection(rows: list[dict[str, object]], claims_path: Path, digest: str) -> str:
    claim_registry = _json(claims_path)
    if not isinstance(claim_registry, dict) or not isinstance(claim_registry.get("pages"), list):
        raise LedgerContractError("Claim registry pages must be a list")
    records: list[dict[str, object]] = []
    for page in claim_registry["pages"]:
        if not isinstance(page, dict) or not isinstance(page.get("claims"), list):
            raise LedgerContractError("Claim registry page is invalid")
        for claim in page["claims"]:
            if not isinstance(claim, dict):
                raise LedgerContractError("Claim registry claim is invalid")
            records.append(
                {
                    "id": claim["claim_id"],
                    "kind": "claim",
                    "route": _route(str(page["source_path"])),
                    "status": claim["critique_status"],
                    "title": claim["title"],
                }
            )
    for row in rows:
        records.append(
            {
                "affected_routes": [
                    _route(str(page)) for page in _list_field(row, "affected_pages")
                ],
                "id": row["critique_id"],
                "kind": "critique",
                "related_claim_ids": row["related_claim_ids"],
                "route": _route(str(row["source_path"])),
                "severity": row["severity"],
                "status": row["status"],
                "title": row["title"],
            }
        )
    projection = {
        "ledger_sha256": digest,
        "records": sorted(records, key=lambda record: (str(record["kind"]), str(record["id"]))),
        "schema_version": "1.0.0",
    }
    return json.dumps(projection, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _expected_outputs(
    ledger: dict[str, object], claims_path: Path, root: Path, digest: str
) -> dict[Path, str]:
    rows = _status_rows(ledger, root)
    by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        for page in _list_field(row, "affected_pages"):
            by_page[str(page)].append(row)
    annotation_root = root / "articles/_generated/trust/critique-annotations"
    outputs = {
        root / "critiques/_generated/critique-status.qmd": _render_status(rows, digest),
        root / "critiques/DEFENSE_STRATEGY.md": _render_defense(rows, ledger, digest),
        root
        / "data/trust/generated/claim_critique_search.json": _search_projection(
            rows, claims_path, digest
        ),
    }
    for page, page_rows in sorted(by_page.items()):
        outputs[annotation_root / f"{Path(page).stem}.qmd"] = _render_annotation(
            page, page_rows, digest
        )
    return outputs


def generate(
    ledger_path: Path = DEFAULT_LEDGER,
    schema_path: Path = DEFAULT_SCHEMA,
    claims_path: Path = DEFAULT_CLAIMS,
    root: Path = ROOT,
    *,
    check: bool = False,
) -> list[Path]:
    """Generate public status, defense, page annotations, and search projection."""
    ledger_bytes = ledger_path.read_bytes()
    digest = hashlib.sha256(ledger_bytes).hexdigest()
    ledger = load_ledger(ledger_path, schema_path, claims_path, root)
    outputs = _expected_outputs(ledger, claims_path, root, digest)
    annotation_root = root / "articles/_generated/trust/critique-annotations"
    expected_annotations = {path for path in outputs if path.parent == annotation_root}
    actual_annotations = set(annotation_root.glob("*.qmd")) if annotation_root.is_dir() else set()
    stale = actual_annotations - expected_annotations
    if stale:
        if check:
            raise LedgerContractError(
                "Stale generated annotation(s): " + ", ".join(str(path) for path in sorted(stale))
            )
        for path in stale:
            path.unlink()

    for path, expected in outputs.items():
        if check:
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                raise LedgerContractError(f"Generated ledger surface is stale: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8", newline="\n")
    return sorted(outputs)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--claims", type=Path, default=DEFAULT_CLAIMS)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        outputs = generate(
            args.ledger,
            args.schema,
            args.claims,
            args.root,
            check=args.check,
        )
    except LedgerContractError as exc:
        print(f"claim/critique ledger contract failed: {exc}", file=sys.stderr)
        return 1
    action = "verified" if args.check else "generated"
    print(f"{action} {len(outputs)} claim/critique ledger surface(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
