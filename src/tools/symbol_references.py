"""Equation symbol references for the WEB-11.6 symbol hover (#4584).

``NOTATION.md`` is the single source: a table between the
``SYMBOL-REFERENCES`` markers lists each hoverable symbol's key, TeX, plain
name and definition. :func:`parse_symbol_table` reads it and
:func:`render_registry` writes ``data/symbol_references.json``, which
``scripts/filters/symbol-hover.lua`` loads at render time.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTATION_PATH = ROOT / "NOTATION.md"
REGISTRY_PATH = ROOT / "data" / "symbol_references.json"
SCHEMA = "affinedrift/symbol-references/v1"
ANCHOR = "/pages/notation.html#equation-symbol-definitions"

_START = "<!-- SYMBOL-REFERENCES:START -->"
_END = "<!-- SYMBOL-REFERENCES:END -->"
#: Keys become CSS class suffixes and HTML attribute values, so keep them plain.
_KEY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")
_CODE_RE = re.compile(r"^`([^`]*)`$")
_TEX_RE = re.compile(r"^\$([^$]+)\$$")


@dataclass(frozen=True)
class SymbolReference:
    """One hoverable symbol: its key, TeX, plain-text name and definition."""

    key: str
    tex: str
    name: str
    definition: str


def _cells(row: str) -> list[str]:
    """Split one Markdown table row into stripped cell texts."""
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def _parse_row(row: str) -> SymbolReference:
    """Parse one symbol row; raises ``ValueError`` on any malformed cell."""
    cells = _cells(row)
    if len(cells) != 4:
        raise ValueError(f"symbol row must have four cells: {row!r}")
    if not all(cells):
        raise ValueError(f"symbol row has an empty cell: {row!r}")
    raw_key, raw_tex, name, definition = cells
    code = _CODE_RE.match(raw_key)
    key = code.group(1) if code else raw_key
    if not _KEY_RE.match(key):
        raise ValueError(f"symbol key must be alphanumeric and start with a letter: {key!r}")
    tex = _TEX_RE.match(raw_tex)
    if tex is None:
        raise ValueError(f"symbol cell must be inline TeX like $f(x)$: {raw_tex!r}")
    return SymbolReference(key, tex.group(1).strip(), name, definition)


def parse_symbol_table(text: str) -> tuple[SymbolReference, ...]:
    """Return the symbols between the markers, in document order.

    Raises ``ValueError`` if the markers are missing, the table has no rows, a
    row is malformed, or a key repeats.
    """
    start, end = text.find(_START), text.find(_END)
    if start < 0 or end < start:
        raise ValueError("NOTATION.md must contain the SYMBOL-REFERENCES markers")
    rows = [line for line in text[start + len(_START) : end].splitlines() if line.startswith("|")]
    body = [row for row in rows[2:] if not set(row) <= set("|-: ")]
    if not body:
        raise ValueError("symbol table has no symbol rows")
    refs = tuple(_parse_row(row) for row in body)
    keys = [ref.key for ref in refs]
    duplicates = sorted({key for key in keys if keys.count(key) > 1})
    if duplicates:
        raise ValueError(f"duplicate symbol keys: {duplicates}")
    return refs


def render_registry(refs: tuple[SymbolReference, ...]) -> str:
    """Deterministic JSON registry text with one trailing newline."""
    payload = {
        "schema": SCHEMA,
        "source": "NOTATION.md",
        "anchor": ANCHOR,
        "symbols": [
            {"key": r.key, "tex": r.tex, "name": r.name, "definition": r.definition} for r in refs
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
