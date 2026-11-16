"""Validate agent-facing convention and parameter registries (#5596)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
CONVENTIONS_PATH = ROOT / "data/agent/conventions.json"
PARAMETERS_PATH = ROOT / "data/canonical_parameters.json"
CONVENTIONS_SCHEMA = "affinedrift/agent-conventions/v1"
CONVENTIONS_SCHEMA_PATH = ROOT / "schemas/agent-conventions-v1.schema.json"
PARAMETERS_SCHEMA_PATH = ROOT / "schemas/canonical-parameters-v1.schema.json"

_CATEGORY_TO_NOTATION_SNIPPET: dict[str, str] = {
    "rotation": "Hamilton",
    "frame": "Site default target frame",
    "units": "SI",
    "sign": "Right-Hand Rule",
    "control_affine": "control-affine",
    "spatial_vectors": "angular blocks first",
}


@dataclass(frozen=True)
class ConventionEntry:
    """One machine-readable convention row."""

    id: str
    category: str
    name: str
    summary: str
    source_anchor: str
    frame: str | None = None
    sign: str | None = None
    unit: str | None = None


@dataclass(frozen=True)
class ConventionsRegistry:
    """Parsed conventions registry."""

    scope_note: str
    items: tuple[ConventionEntry, ...]
    sources: tuple[dict[str, str], ...]


def _load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_schema(instance: object, schema_path: Path, label: str) -> None:
    validator = Draft202012Validator(_load_schema(schema_path), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda err: list(err.absolute_path))
    if errors:
        detail = "; ".join(
            f"{'/'.join(str(part) for part in err.absolute_path) or '<root>'}: {err.message}"
            for err in errors
        )
        raise ValueError(f"{label} failed JSON Schema validation: {detail}")


def _entry(raw: dict[str, Any]) -> ConventionEntry:
    return ConventionEntry(
        id=str(raw["id"]),
        category=str(raw["category"]),
        name=str(raw["name"]),
        summary=str(raw["summary"]),
        source_anchor=str(raw["source_anchor"]),
        frame=str(raw["frame"]) if raw.get("frame") else None,
        sign=str(raw["sign"]) if raw.get("sign") else None,
        unit=str(raw["unit"]) if raw.get("unit") else None,
    )


def load_conventions(text: str) -> ConventionsRegistry:
    """Parse and minimally validate conventions JSON."""
    payload = json.loads(text)
    if payload.get("schema") != CONVENTIONS_SCHEMA:
        raise ValueError(f"unsupported conventions schema: {payload.get('schema')!r}")
    items = tuple(_entry(item) for item in payload["conventions"])
    if not items:
        raise ValueError("conventions must list at least one entry")
    ids = [item.id for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError("convention ids must be unique")
    sources = tuple(
        {
            "title": str(src["title"]),
            "source": str(src["source"]),
            "rendered": str(src["rendered"]),
        }
        for src in payload["sources"]
    )
    return ConventionsRegistry(
        scope_note=str(payload["scope_note"]),
        items=items,
        sources=sources,
    )


def validate_conventions_against_notation(registry: ConventionsRegistry, notation: str) -> None:
    """Ensure each category still appears in NOTATION.md prose (drift guard)."""
    for category, snippet in _CATEGORY_TO_NOTATION_SNIPPET.items():
        if not any(item.category == category for item in registry.items):
            raise ValueError(f"conventions missing category {category!r}")
        if snippet not in notation:
            raise ValueError(f"NOTATION.md no longer mentions {snippet!r} for {category}")


def _anchor_id(source_anchor: str) -> str | None:
    match = re.search(r"#(.+)$", source_anchor)
    return match.group(1) if match else None


def validate_convention_anchor_ids(notation: str, registry: ConventionsRegistry) -> None:
    """Require contract heading ids cited by conventions to remain in NOTATION.md."""
    explicit = set(re.findall(r"\{#([^}]+)\}", notation))
    for item in registry.items:
        anchor = _anchor_id(item.source_anchor)
        if not anchor or not item.source_anchor.startswith("/pages/notation.html"):
            continue
        if not (anchor.startswith("term-") or anchor == "drift-and-control"):
            continue
        if anchor not in explicit:
            raise ValueError(f"convention {item.id!r} cites missing NOTATION heading {anchor!r}")


def validate_registry_documents(
    *,
    conventions_payload: object,
    parameters_payload: object,
    root: Path = ROOT,
) -> None:
    """Validate both registries against JSON Schema and semantic contracts."""
    conv_schema = root / "schemas/agent-conventions-v1.schema.json"
    param_schema = root / "schemas/canonical-parameters-v1.schema.json"
    _validate_schema(conventions_payload, conv_schema, "conventions.json")
    _validate_schema(parameters_payload, param_schema, "canonical_parameters.json")
    registry = load_conventions(json.dumps(conventions_payload))
    notation = (root / "NOTATION.md").read_text(encoding="utf-8")
    validate_conventions_against_notation(registry, notation)
    validate_convention_anchor_ids(notation, registry)
