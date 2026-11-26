"""Reserved notation symbol registry for later chapter checks (#5596).

``NOTATION.md`` stays the prose source. One row per glyph carries the meaning,
shape, sign, and forbidden roles that #5602 and #5597 can check.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from src.tools.agent_registries import validate_json_schema

ROOT = Path(__file__).resolve().parents[2]
SYMBOL_REGISTRY_PATH = ROOT / "data" / "agent" / "symbol_registry.json"
SCHEMA_PATH = ROOT / "schemas" / "notation-symbol-registry-v1.schema.json"
SCHEMA_ID = "affinedrift/notation-symbol-registry/v1"
_HEADING_RE = re.compile(r"\{#([^}]+)\}")


@dataclass(frozen=True)
class SymbolContract:
    """One reserved glyph. Optional JSON fields are None when omitted."""

    id: str
    symbol: str
    tex: str
    meaning: str
    shape: str
    source_anchor: str
    notation_witness: str
    unit: str | None = None
    frame: str | None = None
    sign: str | None = None
    notation_heading: str | None = None
    forbidden_roles: tuple[str, ...] = ()


@dataclass(frozen=True)
class SymbolRegistry:
    """Parsed registry. Invariant: one row per id and one row per symbol."""

    scope_note: str
    symbols: tuple[SymbolContract, ...]

    def reserved(self, symbol: str) -> SymbolContract:
        """Return the only contract for ``symbol``.

        Raises:
            ValueError: ``symbol`` is absent. Load rejects duplicates.
        """
        matches = [item for item in self.symbols if item.symbol == symbol]
        if len(matches) != 1:
            raise ValueError(f"symbol {symbol!r} must have exactly one reserved contract")
        return matches[0]


def _parse_json(text: str) -> dict[str, Any]:
    """Return a JSON object or raise ``ValueError``."""
    try:
        payload: object = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"symbol registry is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("symbol registry JSON must be an object")
    return cast(dict[str, Any], payload)


def _optional_str(value: object) -> str | None:
    """Return a string field, or None when the JSON omits it."""
    if value is None:
        return None
    return str(value)


def _forbidden(raw: dict[str, Any]) -> tuple[str, ...]:
    """Return forbidden role ids. The schema guarantees a list of strings."""
    roles = raw.get("forbidden_roles", [])
    if not isinstance(roles, list):
        raise ValueError("forbidden_roles must be a list")
    return tuple(str(role) for role in roles)


def _contract(raw: dict[str, Any]) -> SymbolContract:
    """Build one contract from a schema-valid row."""
    return SymbolContract(
        id=str(raw["id"]),
        symbol=str(raw["symbol"]),
        tex=str(raw["tex"]),
        meaning=str(raw["meaning"]),
        shape=str(raw["shape"]),
        source_anchor=str(raw["source_anchor"]),
        notation_witness=str(raw["notation_witness"]),
        unit=_optional_str(raw.get("unit")),
        frame=_optional_str(raw.get("frame")),
        sign=_optional_str(raw.get("sign")),
        notation_heading=_optional_str(raw.get("notation_heading")),
        forbidden_roles=_forbidden(raw),
    )


def _reject_duplicates(label: str, values: list[str]) -> None:
    """Raise when ``values`` repeats. ``label`` is ``id`` or ``symbol``."""
    seen: set[str] = set()
    for value in values:
        if value in seen:
            raise ValueError(f"duplicate {label}: {value}")
        seen.add(value)


def _registry_from_payload(payload: dict[str, Any]) -> SymbolRegistry:
    """Convert a schema-valid document into the immutable registry."""
    raw_symbols = payload["symbols"]
    if not isinstance(raw_symbols, list):
        raise ValueError("symbols must be a list")
    symbols = tuple(_contract(cast(dict[str, Any], row)) for row in raw_symbols)
    _reject_duplicates("id", [item.id for item in symbols])
    _reject_duplicates("symbol", [item.symbol for item in symbols])
    return SymbolRegistry(scope_note=str(payload["scope_note"]), symbols=symbols)


def load_symbol_registry(text: str, *, schema_path: Path = SCHEMA_PATH) -> SymbolRegistry:
    """Parse a v1 symbol-registry document.

    Preconditions:
        ``text`` is JSON for ``affinedrift/notation-symbol-registry/v1``.
        ``schema_path`` points at that JSON Schema.

    Postconditions:
        Ids and symbols are unique, and every row passed the schema.

    Raises:
        ValueError: Invalid JSON, another schema, a schema failure, or a
        repeated id or symbol.
    """
    payload = _parse_json(text)
    if payload.get("schema") != SCHEMA_ID:
        raise ValueError(f"unsupported symbol registry schema: {payload.get('schema')!r}")
    validate_json_schema(payload, schema_path, "symbol_registry.json")
    return _registry_from_payload(payload)


def _require_support(item: SymbolContract, notation: str, headings: set[str]) -> None:
    """Require the witness and, when set, the explicit ``{#heading}``."""
    if item.notation_witness not in notation:
        raise ValueError(f"symbol {item.symbol!r} witness is absent from NOTATION.md")
    heading = item.notation_heading
    if heading is not None and heading not in headings:
        raise ValueError(f"symbol {item.symbol!r} cites missing NOTATION heading {heading!r}")


def assert_matches_notation(registry: SymbolRegistry, notation: str) -> None:
    """Require each witness, and each explicit heading, to occur in NOTATION.md.

    Preconditions:
        ``notation`` is the full ``NOTATION.md`` text. Only ``{#id}`` anchors
        count as headings. Rows that omit ``notation_heading`` are witness-only.

    Raises:
        ValueError: A witness or an explicit heading is missing.
    """
    headings = set(_HEADING_RE.findall(notation))
    for item in registry.symbols:
        _require_support(item, notation, headings)
