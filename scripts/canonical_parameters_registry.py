"""Load and render the canonical parameter registry (issue #5595)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "canonical_parameters.json"
PARAMETERS_MD = REPO_ROOT / "PARAMETERS.md"

REQUIRED_ENTRY_KEYS = frozenset(
    {
        "id",
        "category",
        "name",
        "symbol",
        "unit",
        "definition",
        "value",
        "value_kind",
        "source",
        "rule_or_standard",
        "chapters",
        "upstream",
        "affine_refs",
        "literal_checks",
    }
)


@dataclass(frozen=True)
class ParameterEntry:
    """One canonical parameter row."""

    raw: dict[str, Any]

    @property
    def entry_id(self) -> str:
        return str(self.raw["id"])


def load_registry(path: Path = DATA_PATH) -> dict[str, Any]:
    """Load and minimally validate the canonical parameter registry."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("canonical_parameters.json must be a JSON object")
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("canonical_parameters.json must list at least one entry")
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("each entry must be an object")
        missing = REQUIRED_ENTRY_KEYS - entry.keys()
        if missing:
            raise ValueError(f"entry {entry.get('id', '?')} missing keys: {sorted(missing)}")
    return payload


def _format_upstream(refs: list[dict[str, str]]) -> str:
    if not refs:
        return "—"
    return "; ".join(f"`{item['path']}` (`{item['symbol']}`)" for item in refs)


def _format_list(items: list[str]) -> str:
    return ", ".join(items) if items else "—"


def render_parameters_markdown(payload: dict[str, Any]) -> str:
    """Render PARAMETERS.md body from the registry (no duplicate H1)."""
    lines = [
        payload["scope_intro"],
        "",
        "| Parameter | Symbol | Unit | Definition | Value | Source | Rule / Standard | Chapters | UpstreamDrift |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in payload["entries"]:
        lines.append(
            "| {name} | ${symbol}$ | {unit} | {definition} | {value} | {source} | {rule} | {chapters} | {upstream} |".format(
                name=entry["name"],
                symbol=entry["symbol"],
                unit=entry["unit"],
                definition=entry["definition"],
                value=entry["value"],
                source=entry["source"],
                rule=entry["rule_or_standard"],
                chapters=_format_list(entry["chapters"]),
                upstream=_format_upstream(entry["upstream"]),
            )
        )
    lines.extend(
        [
            "",
            "## Usage",
            "",
            "- **Consistency**: Numerical examples must match these symbols, units, and sourced values unless a chapter explicitly declares a rounded teaching default listed in `data/canonical_parameters.json`.",
            "- **Provenance**: UpstreamDrift paths name shared constants in `D-sorganization/UpstreamDrift` at the fleet pin reviewed for the 2026-11-10 technical review.",
            "- **Checks**: `scripts/check_parameters.py` regenerates this table and flags literals that contradict the registry (with baseline allowances).",
            "",
        ]
    )
    return "\n".join(lines)


def stale_markers(payload: dict[str, Any]) -> list[dict[str, str]]:
    """Return stale pointer patterns that must not appear in PARAMETERS.md."""
    markers = payload.get("stale_markers", [])
    if not isinstance(markers, list):
        raise ValueError("stale_markers must be a list")
    return markers


def iter_literal_checks(payload: dict[str, Any]) -> list[tuple[ParameterEntry, dict[str, Any]]]:
    """Yield (entry, check) pairs for filesystem literal enforcement."""
    pairs: list[tuple[ParameterEntry, dict[str, Any]]] = []
    for entry in payload["entries"]:
        wrapped = ParameterEntry(raw=entry)
        for check in entry.get("literal_checks", []):
            if check:
                pairs.append((wrapped, check))
    return pairs


def match_literal(value_text: str, expected: float, tolerance: float) -> bool:
    """Return True when value_text is numerically within tolerance of expected."""
    return abs(float(value_text) - expected) <= tolerance


def compile_check_pattern(pattern: str) -> re.Pattern[str]:
    """Compile a literal-check regex with a capturing group for the value."""
    compiled = re.compile(pattern)
    if compiled.groups < 1:
        raise ValueError(f"literal check pattern must capture the value: {pattern}")
    return compiled
