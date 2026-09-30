#!/usr/bin/env python3
"""Generate or verify the reader-facing Claim Ledger page (``evidence/claims.qmd``).

Builds one accessible card per registered claim from ``data/trust/claim_registry.json``,
joined with its related critiques from ``data/trust/claim_critique_ledger.json`` and the
pages that make it (its defining page plus any page carrying a matching
``data-trust-claim`` anchor). Also generates a small "See the Claim Ledger" link partial
for every page that makes a claim, so the claim's authoritative statement, falsifiers,
and open critiques are always one click away from the prose that states it.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import sys
from pathlib import Path
from typing import Any

from scripts.generate_claim_critique_ledger import (
    DEFAULT_CLAIMS as CRITIQUE_LEDGER_CLAIMS,
)
from scripts.generate_claim_critique_ledger import (
    DEFAULT_LEDGER,
    load_ledger,
    normalized_status,
)
from scripts.generate_claim_critique_ledger import (
    DEFAULT_SCHEMA as CRITIQUE_LEDGER_SCHEMA,
)
from scripts.generate_claim_critique_ledger import (
    _route as critique_route,
)
from scripts.generate_claim_critique_ledger import (
    _title as critique_title,
)
from scripts.generate_trust_panels import (
    DEFAULT_REGISTRY,
    load_registry,
)
from scripts.generate_trust_panels import (
    DEFAULT_SCHEMA as CLAIM_REGISTRY_SCHEMA,
)
from src.affine_control.evidence_presentation.projector import project_claim
from src.affine_control.evidence_presentation.renderer import render_evidence_badge

ROOT = Path(__file__).resolve().parent.parent
PARTIAL = ROOT / "_includes/generated/claims-ledger.qmd"
PAGE_LINKS_DIR = ROOT / "_includes/generated/claims-ledger"
CLAIMS_PAGE = "evidence/claims.qmd"

#: Directories whose .qmd files are scanned for ``data-trust-claim`` anchors,
#: mirroring ``src.tools.site_page_scan.CONTENT_DIRS`` plus ``evidence`` itself.
CONTENT_DIRS = ("articles", "pages", "resources", "models", "repositories", "books", "evidence")


class ClaimLedgerError(ValueError):
    """Raised when a claim-ledger artifact cannot be built or is stale."""


def _claim_anchor(claim: str) -> str:
    return f'data-trust-claim="{claim}"'


def _pages_making_claim(root: Path, claim_id: str, defining_page: str) -> list[str]:
    """Return every page that authors or cites *claim_id*, sorted for determinism."""
    pages = {defining_page}
    needle = _claim_anchor(claim_id)
    for content_dir in CONTENT_DIRS:
        base = root / content_dir
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.qmd")):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if needle in text:
                pages.add(path.relative_to(root).as_posix())
    return sorted(pages)


def _related_critiques(
    ledger: dict[str, object], root: Path, claim_id: str
) -> list[dict[str, object]]:
    """Return every ledger critique whose ``related_claim_ids`` names *claim_id*."""
    critiques = ledger.get("critiques")
    if not isinstance(critiques, list):
        raise ClaimLedgerError("Ledger critiques must be a list")
    rows: list[dict[str, object]] = []
    for raw in critiques:
        if not isinstance(raw, dict):
            raise ClaimLedgerError("Critique record must be an object")
        related = raw.get("related_claim_ids", [])
        if not isinstance(related, list) or claim_id not in related:
            continue
        source = str(raw["source_path"])
        rows.append(
            {
                "critique_id": str(raw["critique_id"]),
                "title": critique_title(root, source),
                "status": normalized_status(raw["disposition"]),
                "severity": str(raw["severity"]),
                "route": critique_route(source, "evidence"),
            }
        )
    return sorted(rows, key=lambda row: str(row["critique_id"]))


def build_claim_cards(root: Path = ROOT) -> list[dict[str, Any]]:
    """Project the governed claim registry into ledger-page card view models."""
    registry = load_registry(DEFAULT_REGISTRY, CLAIM_REGISTRY_SCHEMA)
    ledger = load_ledger(DEFAULT_LEDGER, CRITIQUE_LEDGER_SCHEMA, CRITIQUE_LEDGER_CLAIMS)

    pages = registry.get("pages")
    if not isinstance(pages, list):
        raise ClaimLedgerError("Claim registry pages must be a list")

    cards: list[dict[str, Any]] = []
    for page in pages:
        if not isinstance(page, dict):
            raise ClaimLedgerError("Claim registry page must be an object")
        defining_page = str(page["source_path"])
        claims = page.get("claims")
        if not isinstance(claims, list):
            raise ClaimLedgerError("Claim registry claims must be a list")
        for raw_claim in claims:
            if not isinstance(raw_claim, dict):
                raise ClaimLedgerError("Claim registry claim must be an object")
            claim_id = str(raw_claim["claim_id"])
            vm = project_claim(raw_claim)
            technical = raw_claim["technical_claim"]
            summary = raw_claim["accessible_summary"]
            falsifiers = raw_claim.get("falsifiers", [])
            if not isinstance(falsifiers, list):
                raise ClaimLedgerError(f"{claim_id} falsifiers must be a list")
            pages_for_claim = _pages_making_claim(root, claim_id, defining_page)
            cards.append(
                {
                    "claim_id": claim_id,
                    "title": vm.title,
                    "anchor": str(raw_claim["technical_anchor"]),
                    "plain_statement": str(summary["text"]),
                    "formal_statement": str(technical["text"]),
                    "formal_strength": str(technical["modal_strength"]),
                    "rung_label": vm.state_label,
                    "badge_html": render_evidence_badge(vm),
                    "falsifiers": [str(item) for item in falsifiers],
                    "critiques": _related_critiques(ledger, root, claim_id),
                    "pages": pages_for_claim,
                    "next_gate": str(raw_claim["next_validation_gate"]),
                    "source_url": vm.source_url,
                }
            )
    cards.sort(key=lambda card: str(card["claim_id"]))
    return cards


def _list_lines(items: list[str]) -> list[str]:
    if not items:
        return ["- None registered."]
    return [f"- {html.escape(item)}" for item in items]


def _critique_lines(critiques: list[dict[str, object]]) -> list[str]:
    if not critiques:
        return ["- No critiques are currently linked to this claim."]
    lines = []
    for item in critiques:
        lines.append(
            f"- **{str(item['status']).title()} / {str(item['severity']).title()}:** "
            f"[{html.escape(str(item['title']))}]({item['route']}) (`{item['critique_id']}`)"
        )
    return lines


def _page_lines(root: Path, card: dict[str, Any]) -> list[str]:
    lines = []
    for page in card["pages"]:
        title = critique_title(root, page)
        route = critique_route(page, "evidence")
        lines.append(f"- [{html.escape(title)}]({route})")
    return lines


def render_card(root: Path, card: dict[str, Any]) -> str:
    """Render one accessible, semantic claim card for the ledger page."""
    claim_id = html.escape(card["claim_id"])
    anchor = card["anchor"]
    title = html.escape(card["title"])
    aria = html.escape(f"Claim {claim_id}: {card['title']}. {card['rung_label']}.")
    lines = [
        f'::: {{.callout-note .claim-ledger-card role="region" aria-label="{aria}"}}',
        f"## {title} {{#{anchor}}}",
        "",
        card["badge_html"],
        "",
        f"**Claim ID:** `{claim_id}`",
        "",
        f"**Plain-language statement:** {html.escape(card['plain_statement'])}",
        "",
        f"**Formal statement ({html.escape(card['formal_strength'].title())}):** "
        f"{html.escape(card['formal_statement'])}",
        "",
        "**Falsifiers:**",
        "",
        *_list_lines(card["falsifiers"]),
        "",
        "**Critiques:**",
        "",
        *_critique_lines(card["critiques"]),
        "",
        "**Pages making this claim:**",
        "",
        *_page_lines(root, card),
        "",
        f"**Next validation gate:** {html.escape(card['next_gate'])}",
        "",
        ":::",
        "",
    ]
    return "\n".join(lines)


def render_ledger_partial(cards: list[dict[str, Any]], digest: str, root: Path = ROOT) -> str:
    """Render the deterministic, accessible claim-ledger Quarto partial."""
    lines = [
        "<!-- DO NOT EDIT. Generated by scripts/generate_claims_ledger.py.",
        f"     Claim registry + critique ledger SHA-256: {digest} -->",
        "",
    ]
    for card in cards:
        lines.append(render_card(root, card))
    return "\n".join(lines)


def render_page_link_partial(page: str, page_cards: list[dict[str, Any]], digest: str) -> str:
    """Render the small per-page 'see the Claim Ledger' include for *page*."""
    from_dir = str(Path(page).parent.as_posix()) if str(Path(page).parent) != "." else "."
    route_base = critique_route(CLAIMS_PAGE, from_dir)
    lines = [
        "<!-- DO NOT EDIT. Generated by scripts/generate_claims_ledger.py.",
        f"     Claim registry + critique ledger SHA-256: {digest} -->",
        "",
        '<div class="claims-ledger-link" role="note">',
        "",
        "This page's registered claim(s) are documented in the Claim Ledger:",
        "",
    ]
    for card in page_cards:
        anchor_route = f"{route_base}#{card['anchor']}"
        lines.append(f"- [{html.escape(card['title'])}]({anchor_route})")
    lines.extend(["", "</div>", ""])
    return "\n".join(lines)


def _digest() -> str:
    registry_bytes = DEFAULT_REGISTRY.read_bytes()
    ledger_bytes = DEFAULT_LEDGER.read_bytes()
    return hashlib.sha256(registry_bytes + ledger_bytes).hexdigest()


def _write_or_check(path: Path, content: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            raise ClaimLedgerError(f"Generated claim-ledger output is stale: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _expected_outputs(root: Path, digest: str) -> dict[Path, str]:
    cards = build_claim_cards(root)
    outputs: dict[Path, str] = {PARTIAL: render_ledger_partial(cards, digest, root)}

    by_page: dict[str, list[dict[str, Any]]] = {}
    for card in cards:
        for page in card["pages"]:
            by_page.setdefault(page, []).append(card)

    for page, page_cards in sorted(by_page.items()):
        output = PAGE_LINKS_DIR / f"{Path(page).stem}.qmd"
        outputs[output] = render_page_link_partial(page, page_cards, digest)
    return outputs


def generate(*, check: bool = False, root: Path = ROOT) -> list[Path]:
    """Generate or verify the claim-ledger partial and its per-page link includes."""
    digest = _digest()
    outputs = _expected_outputs(root, digest)

    expected_links = set(outputs) - {PARTIAL}
    actual_links = set(PAGE_LINKS_DIR.glob("*.qmd")) if PAGE_LINKS_DIR.is_dir() else set()
    stale_links = actual_links - expected_links
    if stale_links:
        if check:
            raise ClaimLedgerError(
                "Stale generated claim-ledger link(s): "
                + ", ".join(str(path) for path in sorted(stale_links))
            )
        for path in stale_links:
            path.unlink()

    for path, expected in outputs.items():
        _write_or_check(path, expected, check)
    return sorted(outputs)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when generated output is stale")
    args = parser.parse_args(argv)
    try:
        outputs = generate(check=args.check)
    except ClaimLedgerError as exc:
        print(f"claim-ledger contract failed: {exc}", file=sys.stderr)
        return 1
    action = "verified" if args.check else "generated"
    print(f"{action} {len(outputs)} claim-ledger surface(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
