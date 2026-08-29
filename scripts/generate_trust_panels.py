#!/usr/bin/env python3
"""Validate scientific-trust metadata and generate deterministic Quarto panels."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = REPO_ROOT / "data/trust/claim_registry.json"
DEFAULT_SCHEMA = REPO_ROOT / "schemas/trust-metadata-v1.schema.json"
DEFAULT_OUTPUT = REPO_ROOT / "articles/_generated/trust"

STRENGTH = {"hypothesis": 0, "bounded": 1, "supported": 2, "established": 3}
AMPLIFICATION_TERMS = frozenset(
    {
        "always",
        "causal",
        "cause",
        "causes",
        "exact",
        "exactly",
        "locked-in",
        "optimal",
        "prove",
        "proves",
        "universal",
    }
)
PERCENTAGE = re.compile(r"(?<![\w.])\d+(?:\.\d+)?\s*%")
TOKEN = re.compile(r"[a-z]+(?:-[a-z]+)?")
CLAUSE_BOUNDARY = re.compile(r"[.!?;,:]|\b(?:although|and|but|however|yet)\b")
NEGATION_TERMS = frozenset({"cannot", "never", "no", "not", "without"})
NEGATED_CONTRACTION = re.compile(
    r"\b(?:are|ca|could|did|does|do|is|should|was|were|will|wo|would)n['’]t\b"
)


class TrustContractError(ValueError):
    """Raised when trust metadata or a generated panel violates its contract."""


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TrustContractError(f"Cannot load JSON contract {path}: {exc}") from exc


def validate_registry(registry: object, schema_path: Path = DEFAULT_SCHEMA) -> None:
    """Validate one registry against the strict v1 schema and semantic contracts."""
    schema = _json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(registry), key=lambda error: list(error.absolute_path))
    if errors:
        rendered = "; ".join(
            f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
            for error in errors
        )
        raise TrustContractError(rendered)

    if not isinstance(registry, dict):
        raise TrustContractError("Registry must be an object")
    pages = registry.get("pages")
    if not isinstance(pages, list):
        raise TrustContractError("Registry pages must be a list")

    page_ids: set[str] = set()
    claim_ids: set[str] = set()
    for page in pages:
        if not isinstance(page, dict):
            raise TrustContractError("Each page must be an object")
        page_id = str(page["page_id"])
        if page_id in page_ids:
            raise TrustContractError(f"Duplicate page_id: {page_id}")
        page_ids.add(page_id)
        claims = page["claims"]
        if not isinstance(claims, list):
            raise TrustContractError(f"Claims for {page_id} must be a list")
        for claim in claims:
            if not isinstance(claim, dict):
                raise TrustContractError(f"Claim on {page_id} must be an object")
            claim_id = str(claim["claim_id"])
            if claim_id in claim_ids:
                raise TrustContractError(f"Duplicate claim_id: {claim_id}")
            claim_ids.add(claim_id)
            validate_non_amplification(claim)


def load_registry(
    registry_path: Path = DEFAULT_REGISTRY,
    schema_path: Path = DEFAULT_SCHEMA,
) -> dict[str, object]:
    """Load and validate the canonical registry."""
    registry = _json(registry_path)
    validate_registry(registry, schema_path)
    if not isinstance(registry, dict):
        raise TrustContractError("Registry must be an object")
    return registry


def _claim_part(claim: dict[str, object], key: str) -> dict[str, object]:
    value = claim.get(key)
    if not isinstance(value, dict):
        raise TrustContractError(f"{claim.get('claim_id', '<unknown>')} {key} must be an object")
    return value


def validate_non_amplification(claim: dict[str, object]) -> None:
    """Reject a plain-language summary that is stronger than its technical claim."""
    technical = _claim_part(claim, "technical_claim")
    summary = _claim_part(claim, "accessible_summary")
    validate_accessible_text(
        technical_text=str(technical.get("text", "")),
        accessible_text=str(summary.get("text", "")),
        technical_strength=str(technical.get("modal_strength", "")),
        accessible_strength=str(summary.get("modal_strength", "")),
    )


def validate_accessible_text(
    technical_text: str,
    accessible_text: str,
    technical_strength: str,
    accessible_strength: str,
) -> None:
    """Enforce modal, high-risk-term, and percentage non-amplification."""

    if technical_strength not in STRENGTH or accessible_strength not in STRENGTH:
        raise TrustContractError("Unknown modal strength")
    if STRENGTH[accessible_strength] > STRENGTH[technical_strength]:
        raise TrustContractError(
            f"summary strength {accessible_strength} exceeds technical strength {technical_strength}"
        )

    technical_terms = _assertive_amplification_terms(technical_text)
    summary_terms = _assertive_amplification_terms(accessible_text)
    extra_terms = sorted(summary_terms - technical_terms)
    if extra_terms:
        raise TrustContractError(f"summary adds amplification term(s): {', '.join(extra_terms)}")

    technical_percentages = set(PERCENTAGE.findall(technical_text))
    summary_percentages = set(PERCENTAGE.findall(accessible_text))
    extra_percentages = sorted(summary_percentages - technical_percentages)
    if extra_percentages:
        raise TrustContractError(
            f"summary adds percentage(s) absent from technical claim: {', '.join(extra_percentages)}"
        )


def _assertive_amplification_terms(text: str) -> set[str]:
    """Return high-risk terms used affirmatively within simple prose clauses."""
    assertive: set[str] = set()
    normalized = NEGATED_CONTRACTION.sub(" not ", text.casefold())
    for clause in CLAUSE_BOUNDARY.split(normalized):
        tokens = TOKEN.findall(clause)
        terms = AMPLIFICATION_TERMS.intersection(tokens)
        if terms and not NEGATION_TERMS.intersection(tokens):
            assertive.update(terms)
    return assertive


def _label(value: object) -> str:
    return str(value).replace("_", " ").title()


def _markdown_list(values: object) -> str:
    if not isinstance(values, list):
        raise TrustContractError("Expected a list while rendering a trust panel")
    return "\n".join(f"- {html.escape(str(value))}" for value in values)


def _unknown_fields(claim: dict[str, object]) -> list[str]:
    unknown: list[str] = []
    if claim.get("evidence_class") == "unknown":
        unknown.append("evidence class")
    if claim.get("critique_status") == "unknown":
        unknown.append("critique status")
    uncertainty = _claim_part(claim, "uncertainty")
    if uncertainty.get("status") == "unknown":
        unknown.append("uncertainty")
    return unknown


def render_page_panel(page: dict[str, object], registry_sha256: str) -> str:
    """Render one page's claims as a semantic Quarto fragment."""
    page_id = html.escape(str(page["page_id"]))
    claims = page.get("claims")
    if not isinstance(claims, list) or not claims:
        raise TrustContractError(f"{page_id} has no claims")

    lines = [
        "<!-- DO NOT EDIT. Generated by scripts/generate_trust_panels.py.",
        f"     Registry SHA-256: {registry_sha256} -->",
        "",
        f'::: {{.scientific-trust-panel role="region" aria-labelledby="trust-panel-{page_id}"}}',
        f"## Scientific Trust Panel {{#trust-panel-{page_id}}}",
        "",
    ]

    for claim_index, raw_claim in enumerate(claims):
        if not isinstance(raw_claim, dict):
            raise TrustContractError(f"Claim {claim_index} on {page_id} must be an object")
        claim = raw_claim
        unknown = _unknown_fields(claim)
        qualification = (
            f"Unqualified — unknown {', '.join(unknown)}" if unknown else "Governed — scope-bounded"
        )
        technical = _claim_part(claim, "technical_claim")
        summary = _claim_part(claim, "accessible_summary")
        uncertainty = _claim_part(claim, "uncertainty")
        software = claim.get("software_provenance")
        if not isinstance(software, list):
            raise TrustContractError("software_provenance must be a list")
        software_lines = []
        for item in software:
            if not isinstance(item, dict):
                raise TrustContractError("software_provenance item must be an object")
            software_lines.append(
                f"{item['repository']}@{item['commit']} — {item['path']} "
                f"(SHA-256 {item['sha256']})"
            )

        lines.extend(
            [
                f"### {html.escape(str(claim['title']))}",
                "",
                f"**Qualification:** {html.escape(qualification)}",
                "",
                f"**Claim ID:** `{html.escape(str(claim['claim_id']))}`  ",
                f"**Evidence class:** {_label(claim['evidence_class'])}  ",
                f"**Critique status:** {_label(claim['critique_status'])}  ",
                f"**Reviewed:** {html.escape(str(claim['reviewed_on']))} at "
                f"`{html.escape(str(claim['review_commit']))}`",
                "",
                "**Plain-language summary:** "
                f"[{html.escape(str(summary['text']))}](#{html.escape(str(claim['technical_anchor']))})",
                "",
                f"**Technical claim ({_label(technical['modal_strength'])}):** "
                f"{html.escape(str(technical['text']))}",
                "",
                f"**Population:** {html.escape(str(claim['population']))}",
                "",
                "**Valid conditions:**",
                "",
                _markdown_list(claim["valid_conditions"]),
                "",
                f"**Uncertainty ({_label(uncertainty['status'])}):** "
                f"{html.escape(str(uncertainty['statement']))}",
                "",
                "**Limitations:**",
                "",
                _markdown_list(claim["limitations"]),
                "",
                "**Falsifier:**",
                "",
                _markdown_list(claim["falsifiers"]),
                "",
                "**Software provenance:**",
                "",
                _markdown_list(software_lines),
                "",
                f"**Data provenance:** {html.escape(str(claim['data_provenance']))}",
                "",
                f"**Next validation gate:** {html.escape(str(claim['next_validation_gate']))}",
                "",
            ]
        )

    lines.extend([":::", ""])
    return "\n".join(lines)


def generate(
    registry_path: Path = DEFAULT_REGISTRY,
    schema_path: Path = DEFAULT_SCHEMA,
    output_dir: Path = DEFAULT_OUTPUT,
    *,
    check: bool = False,
) -> list[Path]:
    """Generate all panels, or fail if committed panels are stale in check mode."""
    registry_bytes = registry_path.read_bytes()
    registry_sha256 = hashlib.sha256(registry_bytes).hexdigest()
    registry = load_registry(registry_path, schema_path)
    pages = registry.get("pages")
    if not isinstance(pages, list):
        raise TrustContractError("Registry pages must be a list")

    outputs: list[Path] = []
    for raw_page in sorted(pages, key=lambda item: str(item["page_id"])):
        if not isinstance(raw_page, dict):
            raise TrustContractError("Page must be an object")
        output = output_dir / f"{raw_page['page_id']}.qmd"
        expected = render_page_panel(raw_page, registry_sha256)
        outputs.append(output)
        if check:
            if not output.is_file() or output.read_text(encoding="utf-8") != expected:
                raise TrustContractError(f"Generated trust panel is stale: {output}")
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(expected, encoding="utf-8", newline="\n")
    return outputs


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when generated panels are stale")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    try:
        outputs = generate(args.registry, args.schema, args.output, check=args.check)
    except TrustContractError as exc:
        print(f"trust-panel contract failed: {exc}", file=sys.stderr)
        return 1
    action = "verified" if args.check else "generated"
    print(f"{action} {len(outputs)} scientific trust panel(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
