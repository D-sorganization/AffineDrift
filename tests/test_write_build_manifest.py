"""Tests for scripts/write_build_manifest.py (#5319)."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from scripts.write_build_manifest import build_manifest, main

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas" / "build-manifest.schema.json").read_text(encoding="utf-8"))


def test_build_manifest_matches_schema() -> None:
    payload = build_manifest()
    jsonschema.validate(payload, SCHEMA)


def test_write_manifest_cli_writes_valid_json(tmp_path: Path) -> None:
    out = tmp_path / "build-manifest.json"
    assert main(["--out", str(out)]) == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    jsonschema.validate(payload, SCHEMA)
