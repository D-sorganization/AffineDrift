"""Caveat block validation and HTML rendering helpers (WEB-03.4 #4509).

Provides:
- `validate_caveats_dict`: checks structure, required fields, and item non-emptiness.
- `format_evidence_level`: formats human-readable evidence level label.
- `render_caveats_html`: renders accessible HTML matching the standard caveat block.
"""

from __future__ import annotations

import html
from typing import Any

from src.core.contracts import ensure, require

EVIDENCE_LEVEL_MAP: dict[str, str] = {
    "mathematical-identity": "Theory (Mathematical Identity)",
    "mathematical_identity": "Theory (Mathematical Identity)",
    "manufactured-fixture": "Simulation (Manufactured Fixture)",
    "manufactured_synthetic": "Simulation (Manufactured Synthetic)",
    "qualified-simulation": "Simulation (Qualified Multi-Body)",
    "qualified_simulation": "Simulation (Qualified Multi-Body)",
    "measured-participant-result": "Empirical (Measured Human Data)",
    "pilot_bounded": "Empirical (Pilot Study)",
    "governed_dataset": "Empirical (Governed Dataset)",
    "collecting_locked": "Empirical (Collecting Locked)",
    "replicated-result": "Replicated Result",
    "bounded-application": "Bounded Application",
    "validated_evidence": "Validated Evidence",
    "published_claim": "Published Claim",
}


def format_evidence_level(raw_level: str | None, evidence_rung: str | None = None) -> str:
    """Format human-readable evidence level string."""
    if raw_level and raw_level.strip():
        return raw_level.strip()
    if evidence_rung and evidence_rung.strip():
        rung_key = evidence_rung.strip().lower()
        if rung_key in EVIDENCE_LEVEL_MAP:
            return EVIDENCE_LEVEL_MAP[rung_key]
        return evidence_rung.replace("-", " ").replace("_", " ").title()
    return "Theory"


def _validate_string_items(items: Any, field_name: str) -> list[str]:
    """Validate that items is a non-empty list of non-empty strings."""
    if not isinstance(items, list) or len(items) == 0:
        return [f"caveats.{field_name} must be a non-empty list of strings"]
    errs: list[str] = []
    for idx, item in enumerate(items):
        if not isinstance(item, str) or not item.strip():
            errs.append(f"caveats.{field_name}[{idx}] must be a non-empty string")
    return errs


def validate_caveats_dict(data: Any) -> list[str]:
    """Validate a parsed caveats mapping against domain contracts.

    Returns a list of error strings (empty if valid).
    """
    if not isinstance(data, dict):
        return ["caveats must be a dictionary / mapping"]

    errors: list[str] = []
    errors.extend(_validate_string_items(data.get("establishes"), "establishes"))
    errors.extend(_validate_string_items(data.get("does-not-establish"), "does-not-establish"))

    critiques = data.get("open-critiques")
    if critiques is not None:
        if not isinstance(critiques, list):
            errors.append("caveats.open-critiques must be a list of strings if provided")
        else:
            for idx, c in enumerate(critiques):
                if not isinstance(c, str) or not c.strip():
                    errors.append(f"caveats.open-critiques[{idx}] must be a non-empty string")

    next_gate = data.get("next-gate")
    if next_gate is not None and not isinstance(next_gate, str):
        errors.append("caveats.next-gate must be a string if provided")

    return errors


def render_caveats_html(data: dict[str, Any], evidence_rung: str | None = None) -> str:
    """Render a caveats mapping into accessible HTML matching the WEB-03.4 specification."""
    require(isinstance(data, dict), "data must be a dict")
    errs = validate_caveats_dict(data)
    require(not errs, f"Invalid caveats data: {errs}")

    evidence_level = format_evidence_level(data.get("evidence-level"), evidence_rung)
    establishes: list[str] = data.get("establishes", [])
    does_not: list[str] = data.get("does-not-establish", [])
    critiques: list[str] = data.get("open-critiques", [])
    next_gate: str | None = data.get("next-gate")

    est_items = "\n".join(f"      <li>{html.escape(item)}</li>" for item in establishes)
    does_not_items = "\n".join(f"      <li>{html.escape(item)}</li>" for item in does_not)

    critiques_html = ""
    if critiques:
        crit_items = "\n".join(f"      <li>{html.escape(c)}</li>" for c in critiques)
        critiques_html = f"""
    <div class="caveats-section caveats-critiques">
      <h3 class="caveats-subtitle">Open Critiques and Active Inquiries</h3>
      <ul class="caveats-list">
{crit_items}
      </ul>
    </div>"""

    next_gate_html = ""
    if next_gate and next_gate.strip():
        next_gate_html = f"""
    <div class="caveats-section caveats-next-gate">
      <h3 class="caveats-subtitle">Next Validation Gate</h3>
      <p class="caveats-gate-text">{html.escape(next_gate.strip())}</p>
    </div>"""

    out = f"""<div class="callout callout-style-simple callout-note no-icon callout-titled caveats-card what-this-shows-card" role="region" aria-label="What This Shows / What It Does Not Show">
  <div class="callout-header d-flex align-content-center">
    <div class="callout-icon-container">
      <i class="callout-icon no-icon"></i>
    </div>
    <div class="callout-title-container flex-fill">
      What This Shows / What It Does Not Show
    </div>
  </div>
  <div class="callout-body-container callout-body">
    <div class="caveats-section caveats-establishes">
      <h3 class="caveats-subtitle">What This Page Establishes (Evidence Level: {html.escape(evidence_level)})</h3>
      <ul class="caveats-list">
{est_items}
      </ul>
    </div>
    <div class="caveats-section caveats-does-not-establish">
      <h3 class="caveats-subtitle">What This Page Does Not Establish</h3>
      <ul class="caveats-list">
{does_not_items}
      </ul>
    </div>{critiques_html}{next_gate_html}
  </div>
</div>"""

    ensure(len(out) > 0, "Rendered HTML must not be empty")
    return out
