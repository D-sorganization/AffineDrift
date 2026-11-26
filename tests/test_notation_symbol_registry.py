"""Reserved notation symbol registry that later checks can query (Refs #5596).

#5602 and #5597 compare chapter glyphs with NOTATION.md. This registry is the
machine-readable contract for that comparison: one reserved row per glyph, with
the shape, sign, and forbidden roles the prose already fixes.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from scripts import check_agent_registries as registry_gate
from src.tools.notation_symbol_registry import (
    SYMBOL_REGISTRY_PATH,
    assert_matches_notation,
    load_symbol_registry,
)

ROOT_NOTATION = SYMBOL_REGISTRY_PATH.parents[2] / "NOTATION.md"
SCHEMA = "affinedrift/notation-symbol-registry/v1"
REQUIRED_SYMBOLS = frozenset({"f", "G", "g", "u", "M", "h", "B", "C", "J", "P_W", "N", "p"})


def _row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "id": "drift-f",
        "symbol": "f",
        "tex": "f(x)",
        "meaning": "Complete autonomous drift of the declared effective plant.",
        "shape": "vector field",
        "frame": "state",
        "source_anchor": "/pages/notation.html#drift-and-control",
        "notation_heading": "drift-and-control",
        "notation_witness": "Complete autonomous drift of the declared effective plant",
    }
    row.update(overrides)
    return row


def _document(symbols: list[dict[str, object]]) -> str:
    payload = {
        "schema": SCHEMA,
        "scope_note": "Reserved symbols later checks compare with NOTATION.md.",
        "symbols": symbols,
    }
    return json.dumps(payload)


def test_committed_registry_covers_reserved_symbols() -> None:
    registry = load_symbol_registry(SYMBOL_REGISTRY_PATH.read_text(encoding="utf-8"))
    assert REQUIRED_SYMBOLS <= {item.symbol for item in registry.symbols}


def test_committed_registry_matches_notation() -> None:
    registry = load_symbol_registry(SYMBOL_REGISTRY_PATH.read_text(encoding="utf-8"))
    assert_matches_notation(registry, ROOT_NOTATION.read_text(encoding="utf-8"))


def test_input_map_and_gravity_are_mutually_reserved() -> None:
    registry = load_symbol_registry(SYMBOL_REGISTRY_PATH.read_text(encoding="utf-8"))
    input_map = registry.reserved("G")
    gravity = registry.reserved("g")
    assert "input map" in input_map.meaning.lower()
    assert "gravity-load" in input_map.forbidden_roles
    assert "gravity" in gravity.meaning.lower()
    assert "input-map" in gravity.forbidden_roles


def test_null_basis_is_not_the_metric_projector() -> None:
    registry = load_symbol_registry(SYMBOL_REGISTRY_PATH.read_text(encoding="utf-8"))
    assert registry.reserved("N").shape == "matrix"
    assert "metric-projector" in registry.reserved("N").forbidden_roles
    assert registry.reserved("P_W").shape == "projector"
    assert registry.reserved("M").sign == "SPD"
    assert registry.reserved("h").shape == "vector"


def test_loader_rejects_invalid_json() -> None:
    with pytest.raises(ValueError, match="JSON"):
        load_symbol_registry("{")


def test_loader_rejects_non_object() -> None:
    with pytest.raises(ValueError, match="object"):
        load_symbol_registry("[]")


def test_loader_rejects_unknown_schema() -> None:
    payload: dict[str, Any] = json.loads(_document([_row()]))
    payload["schema"] = "affinedrift/notation-symbol-registry/v0"
    with pytest.raises(ValueError, match="schema"):
        load_symbol_registry(json.dumps(payload))


def test_loader_rejects_unknown_field() -> None:
    with pytest.raises(ValueError, match="JSON Schema"):
        load_symbol_registry(_document([_row(extra="nope")]))


def test_loader_rejects_duplicate_symbol() -> None:
    with pytest.raises(ValueError, match="duplicate symbol"):
        load_symbol_registry(_document([_row(), _row(id="drift-f-copy")]))


def test_loader_rejects_duplicate_id() -> None:
    with pytest.raises(ValueError, match="duplicate id"):
        load_symbol_registry(_document([_row(), _row(symbol="Q", tex="Q")]))


def test_reserved_rejects_an_unknown_symbol() -> None:
    registry = load_symbol_registry(_document([_row()]))
    with pytest.raises(ValueError, match="Q"):
        registry.reserved("Q")


def test_cross_check_rejects_a_missing_witness() -> None:
    registry = load_symbol_registry(_document([_row()]))
    with pytest.raises(ValueError, match="witness"):
        assert_matches_notation(registry, "{#drift-and-control}\n")


def test_cross_check_rejects_a_missing_heading() -> None:
    registry = load_symbol_registry(_document([_row()]))
    witness = str(_row()["notation_witness"])
    with pytest.raises(ValueError, match="heading"):
        assert_matches_notation(registry, witness)


def test_witness_only_row_does_not_require_a_heading() -> None:
    row = _row()
    del row["notation_heading"]
    registry = load_symbol_registry(_document([row]))
    assert_matches_notation(registry, str(row["notation_witness"]))


def test_registry_check_fails_when_the_file_is_missing(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(registry_gate, "SYMBOL_REGISTRY_PATH", tmp_path / "missing.json")
    assert registry_gate.main(["--check"]) == 1
