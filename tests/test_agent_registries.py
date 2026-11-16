"""Agent conventions and canonical-parameter registry contracts (#5596 slice 2)."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from scripts.check_agent_registries import main as check_agent_registries
from src.tools.agent_registries import (
    CONVENTIONS_PATH,
    CONVENTIONS_SCHEMA,
    load_conventions,
    validate_conventions_against_notation,
    validate_registry_documents,
)

ROOT = Path(__file__).resolve().parents[1]


def test_conventions_file_exists_and_loads() -> None:
    raw = json.loads(CONVENTIONS_PATH.read_text(encoding="utf-8"))
    assert raw["schema"] == CONVENTIONS_SCHEMA
    registry = load_conventions(CONVENTIONS_PATH.read_text(encoding="utf-8"))
    assert len(registry.items) >= 10


def test_conventions_validates_against_schema() -> None:
    payload = json.loads(CONVENTIONS_PATH.read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "schemas/agent-conventions-v1.schema.json").read_text())
    jsonschema.validate(payload, schema)


def test_canonical_parameters_validates_against_schema() -> None:
    payload = json.loads((ROOT / "data/canonical_parameters.json").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "schemas/canonical-parameters-v1.schema.json").read_text())
    jsonschema.validate(payload, schema)


def test_convention_ids_unique_and_html_anchors() -> None:
    payload = load_conventions(CONVENTIONS_PATH.read_text(encoding="utf-8"))
    ids = [item.id for item in payload.items]
    assert len(ids) == len(set(ids))
    for item in payload.items:
        assert item.source_anchor.startswith("/pages/")
        assert ".html" in item.source_anchor


def test_conventions_cover_rotation_frames_units_signs() -> None:
    payload = load_conventions(CONVENTIONS_PATH.read_text(encoding="utf-8"))
    categories = {item.category for item in payload.items}
    for required in {"rotation", "frame", "units", "sign", "control_affine"}:
        assert required in categories


def test_notation_cross_check_passes() -> None:
    notation = (ROOT / "NOTATION.md").read_text(encoding="utf-8")
    payload = load_conventions(CONVENTIONS_PATH.read_text(encoding="utf-8"))
    validate_conventions_against_notation(payload, notation)


def test_check_agent_registries_exit_zero() -> None:
    assert check_agent_registries(["--check"]) == 0


def test_validate_registry_documents_rejects_bad_schema() -> None:
    bad = {"schema": "wrong", "conventions": []}
    with pytest.raises(ValueError, match="schema"):
        validate_registry_documents(
            conventions_payload=bad,
            parameters_payload=json.loads(
                (ROOT / "data/canonical_parameters.json").read_text(encoding="utf-8")
            ),
            root=ROOT,
        )
