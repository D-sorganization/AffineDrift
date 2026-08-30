"""Pure functional renderers generating accessible, responsive HTML and Quarto components."""

from __future__ import annotations

import html
from collections.abc import Sequence

from src.affine_control.evidence_presentation.vocabulary import (
    EvidencePresentationViewModel,
)


def render_evidence_badge(vm: EvidencePresentationViewModel) -> str:
    """Render an inline, accessible badge for headers, cards, and listings."""
    escaped_id = html.escape(vm.entity_id, quote=True)
    escaped_badge = html.escape(vm.state_badge_class, quote=True)
    escaped_state = html.escape(vm.state_label, quote=True)
    escaped_aria = html.escape(vm.accessible_label, quote=True)

    return (
        f'<span class="badge evidence-badge {escaped_badge}" '
        f'data-entity-id="{escaped_id}" '
        f'role="status" '
        f'aria-label="{escaped_aria}">'
        f"{escaped_state}"
        f"</span>"
    )


def render_evidence_card(vm: EvidencePresentationViewModel) -> str:
    """Render an accessible evidence state card for monographs and workbenches."""
    badge = render_evidence_badge(vm)
    escaped_title = html.escape(vm.title, quote=True)
    escaped_aria = html.escape(vm.accessible_label, quote=True)
    escaped_gate = html.escape(vm.next_gate, quote=True)
    escaped_rev = html.escape(vm.source_revision, quote=True)
    escaped_origin = html.escape(vm.evidence_origin, quote=True)
    escaped_boundary = html.escape(vm.authority_boundary, quote=True)

    est_items = "".join(f"<li>{html.escape(item, quote=True)}</li>" for item in vm.establishes)
    not_est_items = "".join(
        f"<li>{html.escape(item, quote=True)}</li>" for item in vm.does_not_establish
    )
    limit_items = "".join(f"<li>{html.escape(item, quote=True)}</li>" for item in vm.limitations)

    card_header = (
        f'::: {{.callout-note .evidence-state-card appearance="simple" '
        f'role="region" aria-label="{escaped_aria}"}}\n'
        f"## Evidence & Verification State: {escaped_title} {badge}\n\n"
    )

    metadata_section = (
        '<div class="evidence-state-metadata">\n'
        f"<p><strong>Next Validation Gate:</strong> <code>{escaped_gate}</code> | "
        f"<strong>Evidence Origin:</strong> <code>{escaped_origin}</code></p>\n"
        f"<p><strong>Exact Source Revision:</strong> <code>{escaped_rev}</code></p>\n"
        f'<p class="evidence-boundary-note"><em>{escaped_boundary}</em></p>\n'
        "</div>\n"
    )

    return (
        card_header
        + '<div class="evidence-state-grid">\n'
        + '<div class="evidence-state-section establishes-section">\n'
        + "<strong>This establishes:</strong>\n<ul>\n"
        + est_items
        + "\n</ul>\n</div>\n\n"
        + '<div class="evidence-state-section does-not-establish-section">\n'
        + "<strong>This does not establish:</strong>\n<ul>\n"
        + not_est_items
        + "\n</ul>\n</div>\n\n"
        + '<div class="evidence-state-section limitations-section">\n'
        + "<strong>Governed limitations:</strong>\n<ul>\n"
        + limit_items
        + "\n</ul>\n</div>\n\n"
        + metadata_section
        + "</div>\n:::"
    )


def render_evidence_table(vms: Sequence[EvidencePresentationViewModel]) -> str:
    """Render a deterministic Markdown table of evidence states across multiple entities."""
    lines = [
        "| Entity / Claim | Tier | Reader-Facing State | Evidence Origin | Next Validation Gate |",
        "|---|---|---|---|---|",
    ]
    for vm in sorted(vms, key=lambda x: (x.tier, x.title.casefold())):
        anchor = f'<span id="evidence-{html.escape(vm.entity_id, quote=True)}"></span>'
        if vm.source_url:
            link = f"[{html.escape(vm.title, quote=True)}]({vm.source_url})"
        else:
            link = html.escape(vm.title, quote=True)
        lines.append(
            f"| {anchor}{link} | {vm.tier} | {vm.state_label} | "
            f"{vm.evidence_origin} | {vm.next_gate} |"
        )
    return "\n".join(lines)
