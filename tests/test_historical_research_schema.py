"""Fetched schemas must preserve the supported contract independently of admission."""

import json

import pytest

from src.affine_control.historical_research import validate_research_schema
from src.affine_control.historical_research.admission import SCHEMA_PATH


def test_equivalent_schema_bytes_return_detached_supported_contract() -> None:
    original = json.loads(SCHEMA_PATH.read_bytes())
    reformatted = json.dumps(original, indent=1).encode()
    checked = validate_research_schema(reformatted)
    assert checked == original
    checked["properties"].clear()
    assert validate_research_schema(SCHEMA_PATH.read_bytes()) == original


def test_changed_schema_cannot_relax_rejected_qualification() -> None:
    changed = json.loads(SCHEMA_PATH.read_bytes())
    changed["properties"].clear()
    with pytest.raises(ValueError, match="supported versioned contract"):
        validate_research_schema(json.dumps(changed).encode())
