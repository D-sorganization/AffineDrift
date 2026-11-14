"""Agent entry point and llms.txt coverage (#5596)."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from scripts.generate_agent_entry_point import main as generate_agent_entry_point
from src.tools.agent_entry_point import (
    LLMS_FULL_PATH,
    LLMS_PATH,
    MANIFEST_PATH,
    load_manifest,
    render_both,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/symbol-references-v2.schema.json"
REGISTRY_PATH = ROOT / "data/symbol_references.json"


def test_manifest_parses_with_required_sections() -> None:
    manifest = load_manifest(MANIFEST_PATH.read_text(encoding="utf-8"))
    names = {section.name for section in manifest.sections}
    assert "Notation, Conventions, and Parameters" in names
    assert "Programming Companion and Engine Protocol" in names


def test_llms_txt_lists_notation_glossary_and_companion() -> None:
    manifest = load_manifest(MANIFEST_PATH.read_text(encoding="utf-8"))
    llms, _ = render_both(manifest)
    assert "# AffineDrift" in llms
    assert "/pages/notation.html" in llms
    assert "/pages/glossary.html" in llms
    assert "/models/programming/engines.html" in llms
    assert "/data/symbol_references.json" in llms


def test_llms_full_includes_sources_and_artifacts() -> None:
    manifest = load_manifest(MANIFEST_PATH.read_text(encoding="utf-8"))
    _, full = render_both(manifest)
    assert "`pages/notation.qmd`" in full
    assert "`data/symbol_references.json`" in full
    assert "affinedrift/symbol-references/v2" in full


def test_generated_llms_files_match_renderer() -> None:
    manifest = load_manifest(MANIFEST_PATH.read_text(encoding="utf-8"))
    expected_llms, expected_full = render_both(manifest)
    assert LLMS_PATH.read_text(encoding="utf-8") == expected_llms
    assert LLMS_FULL_PATH.read_text(encoding="utf-8") == expected_full


def test_generate_agent_entry_point_check_passes() -> None:
    assert generate_agent_entry_point(["--check"]) == 0


def test_symbol_registry_matches_schema_v2() -> None:
    payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)


def test_symbol_registry_covers_issue_missing_keys() -> None:
    payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    keys = {entry["key"] for entry in payload["symbols"]}
    expected = {"h", "q", "qdot", "v", "tau", "J", "lam", "ad", "Ba", "W", "Uset"}
    assert expected <= keys
