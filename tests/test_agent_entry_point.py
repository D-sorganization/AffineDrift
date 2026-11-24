"""Agent entry point and llms.txt coverage (#5596)."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from scripts.generate_agent_entry_point import main as generate_agent_entry_point
from src.tools.agent_entry_point import (
    LLMS_FULL_PATH,
    LLMS_PATH,
    MANIFEST_PATH,
    load_manifest,
    render_both,
)
from src.tools.symbol_references import parse_symbol_table

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
    assert "/pages/upstreamdrift-conventions.html" in llms
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


def test_symbol_registry_matches_notation_table_keys() -> None:
    """Every NOTATION.md registry row must appear in data/symbol_references.json (#5596)."""
    notation_keys = {ref.key for ref in parse_symbol_table((ROOT / "NOTATION.md").read_text())}
    payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    registry_keys = {entry["key"] for entry in payload["symbols"]}
    assert notation_keys == registry_keys
    assert len(registry_keys) >= 20


def test_llms_full_lists_canonical_parameters_json() -> None:
    manifest = load_manifest(MANIFEST_PATH.read_text(encoding="utf-8"))
    _, full = render_both(manifest)
    assert "`data/canonical_parameters.json`" in full


def test_llms_full_lists_agent_conventions_json() -> None:
    manifest = load_manifest(MANIFEST_PATH.read_text(encoding="utf-8"))
    _, full = render_both(manifest)
    assert "`data/agent/conventions.json`" in full
    assert "/pages/upstreamdrift-conventions.html" in full


@pytest.mark.parametrize(
    "route", ["/models/golf-model-maps.html", "/pages/upstreamdrift-engine-protocol.html"]
)
def test_agent_index_lists_model_maps_and_engine_protocol(route: str) -> None:
    """Expose the canonical model and engine references required by #5596."""
    manifest = load_manifest(MANIFEST_PATH.read_text(encoding="utf-8"))
    llms, full = render_both(manifest)
    assert route in llms
    assert route in full


def test_agent_index_has_unique_page_routes() -> None:
    """One canonical route carries all its source artifacts in one entry."""
    manifest = load_manifest(MANIFEST_PATH.read_text(encoding="utf-8"))
    paths = [page.path for section in manifest.sections for page in section.pages]
    assert len(paths) == len(set(paths))
    conventions = next(
        page
        for section in manifest.sections
        for page in section.pages
        if page.path == "/pages/upstreamdrift-conventions.html"
    )
    assert "data/agent/conventions.json" in conventions.artifacts
    assert "data/upstreamdrift/canonical_v2_page_contract.json" in conventions.artifacts


def test_agent_index_has_no_empty_heading() -> None:
    """Every generated section must contain links rather than another heading."""
    manifest = load_manifest(MANIFEST_PATH.read_text(encoding="utf-8"))
    llms, _ = render_both(manifest)
    assert "## Notation and Conventions\n\n##" not in llms


@pytest.mark.parametrize("other_section", [False, True])
def test_manifest_refuses_duplicate_routes(other_section: bool) -> None:
    """Reject ambiguous curated input before publishing either generated index."""
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    first_page = payload["sections"][0]["pages"][0]
    section = payload["sections"][1 if other_section else 0]
    section["pages"].append(first_page.copy())
    with pytest.raises(ValueError, match="duplicate page path"):
        load_manifest(json.dumps(payload))
