"""Schema validation tests for schemas/asset-manifest-v1.schema.json (issue #5251)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "asset-manifest-v1.schema.json"
MANIFEST_PATH = REPO_ROOT / "articles" / "shot_pattern_analysis" / "asset_manifest.json"
SPEC_DOC_PATH = REPO_ROOT / "docs" / "audits" / "asset-manifest-provenance-spec-5251.md"


def _load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_current_asset_manifest_validates_against_schema() -> None:
    """Current articles/shot_pattern_analysis/asset_manifest.json must validate without changes."""
    schema = _load_schema()
    manifest = _load_manifest()
    jsonschema.validate(instance=manifest, schema=schema)


def test_optional_provenance_fields_validate_when_well_formed() -> None:
    """Optional provenance fields validate at both top-level and per-asset level."""
    schema = _load_schema()
    manifest = copy.deepcopy(_load_manifest())
    manifest["producer_repo_sha"] = "f3e83ea8aa754d93ea29b8d176a36fa3d4004a7d"
    manifest["tools_contract_version"] = "1.2.0"
    manifest["input_sha256"] = "a" * 64
    manifest["solver_config_sha256"] = "b" * 64

    manifest["assets"][0]["producer_repo_sha"] = "f3e83ea8aa754d93ea29b8d176a36fa3d4004a7d"
    manifest["assets"][0]["tools_contract_version"] = "1.2.0"
    manifest["assets"][0]["input_sha256"] = "c" * 64
    manifest["assets"][0]["solver_config_sha256"] = "d" * 64

    jsonschema.validate(instance=manifest, schema=schema)


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("producer_repo_sha", "not-a-40-char-hex-sha"),
        ("producer_repo_sha", "F" * 40),
        ("producer_repo_sha", "a" * 39),
        ("input_sha256", "malformed-sha256"),
        ("input_sha256", "A" * 64),
        ("input_sha256", "0" * 63),
        ("solver_config_sha256", "bad-solver-config-sha"),
        ("solver_config_sha256", "g" * 64),
        ("study_source_commit", "short-commit"),
        ("study_report_sha256", "short-sha256"),
        ("tools_contract_version", "not a version"),
    ],
)
def test_fixture_with_malformed_top_level_sha_or_version_fails(
    field: str,
    bad_value: str,
) -> None:
    """Any malformed SHA or contract version at top level must fail schema validation."""
    schema = _load_schema()
    fixture = copy.deepcopy(_load_manifest())
    fixture[field] = bad_value

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=fixture, schema=schema)


@pytest.mark.parametrize(
    ("asset_field", "bad_value"),
    [
        ("sha256", "malformed-asset-sha256"),
        ("source_commit", "malformed-source-commit"),
        ("producer_repo_sha", "12345"),
        ("input_sha256", "xyz"),
        ("solver_config_sha256", "0123456789"),
        ("tools_contract_version", "v1"),
    ],
)
def test_fixture_with_malformed_asset_level_sha_or_version_fails(
    asset_field: str,
    bad_value: str,
) -> None:
    """Any malformed SHA or contract version on an asset entry must fail validation."""
    schema = _load_schema()
    fixture = copy.deepcopy(_load_manifest())
    fixture["assets"][0][asset_field] = bad_value

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=fixture, schema=schema)


def test_undeclared_property_fails_closed() -> None:
    """Schema must reject undeclared properties at top level and in asset entries."""
    schema = _load_schema()
    fixture = copy.deepcopy(_load_manifest())
    fixture["undeclared_field"] = "unexpected"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=fixture, schema=schema)

    asset_fixture = copy.deepcopy(_load_manifest())
    asset_fixture["assets"][0]["undeclared_asset_field"] = "unexpected"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=asset_fixture, schema=schema)


def test_provenance_spec_doc_lists_fields_and_current_assets() -> None:
    """Specification document must describe the four provenance fields and candidate assets."""
    text = SPEC_DOC_PATH.read_text(encoding="utf-8")
    for field in (
        "producer_repo_sha",
        "tools_contract_version",
        "input_sha256",
        "solver_config_sha256",
    ):
        assert field in text

    for asset_ref in (
        "articles/shot_pattern_analysis/asset_manifest.json",
        "articles/proximal_distal_energy_transfer/source_manifest.json",
        "articles/forward_dynamics_matching/source_manifest.json",
    ):
        assert asset_ref in text
