"""Unit tests for the #5255 widget URL-hash state contract and schema."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "widget-url-state-v1.schema.json"
DCR_JS_PATH = REPO_ROOT / "js" / "dcr-visualizer.js"


def _run_node_eval(expr: str) -> dict[str, Any]:
    node_bin = shutil.which("node") or "/usr/bin/node"
    script = (
        f"const DV = require({json.dumps(str(DCR_JS_PATH))}); console.log(JSON.stringify({expr}));"
    )
    res = subprocess.run(  # noqa: S603
        [node_bin, "-e", script],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    data: dict[str, Any] = json.loads(res.stdout.strip())
    return data


def test_widget_url_state_schema_validates_envelope_and_rejects_invalid() -> None:
    """JSON schema enforces version 1, widget id pattern, and bounded numeric parameters."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    valid_payload = {
        "v": 1,
        "w": "dcr-visualizer",
        "p": {"x0": 1.5, "ubar": 2.0, "horizon": 1.0, "phase": 0.25},
    }
    assert list(validator.iter_errors(valid_payload)) == []

    wrong_version = {
        "v": 2,
        "w": "dcr-visualizer",
        "p": {"x0": 1.0, "ubar": 1.0, "horizon": 1.0, "phase": 0.5},
    }
    assert list(validator.iter_errors(wrong_version)) != []

    extra_prop = {
        "v": 1,
        "w": "dcr-visualizer",
        "p": {"x0": 1.0, "ubar": 1.0, "horizon": 1.0, "phase": 0.5, "extra": 1},
    }
    assert list(validator.iter_errors(extra_prop)) != []


def test_round_trip_encode_decode_in_dcr_visualizer() -> None:
    """Round-trip encodeWidgetStateHash -> decodeWidgetStateHash preserves widget state."""
    result = _run_node_eval(
        "(() => {"
        "  const input = {x0: -2.5, ubar: 3.25, horizon: 4.0, phase: 0.75};"
        "  const hash = DV.encodeWidgetStateHash(input);"
        "  const decoded = DV.decodeWidgetStateHash(hash);"
        "  return {hash, decoded};"
        "})()"
    )
    assert str(result["hash"]).startswith("#state=")
    decoded = result["decoded"]
    assert isinstance(decoded, dict)
    assert decoded["valid"] is True
    assert decoded["state"] == {"x0": -2.5, "ubar": 3.25, "horizon": 4.0, "phase": 0.75}


@pytest.mark.parametrize(
    "bad_hash_expr",
    [
        '"#state=%E0%A4%A"',
        '"#state={not-json"',
        '"#state=" + encodeURIComponent(JSON.stringify({v: 2, w: "dcr-visualizer", p: {x0: 1, ubar: 1, horizon: 1, phase: 0.5}}))',
        '"#state=" + encodeURIComponent(JSON.stringify({v: 1, w: "other-widget", p: {x0: 1, ubar: 1, horizon: 1, phase: 0.5}}))',
        '"#state=" + encodeURIComponent(JSON.stringify({v: 1, w: "dcr-visualizer", p: {x0: 0, ubar: 1, horizon: 1, phase: 0.5}}))',
        '"#state=" + encodeURIComponent(JSON.stringify({v: 1, w: "dcr-visualizer", p: {x0: 1, ubar: -1, horizon: 1, phase: 0.5}}))',
        '"#state=" + encodeURIComponent(JSON.stringify({v: 1, w: "dcr-visualizer", p: {x0: 1, ubar: 1, horizon: 1, phase: 1.5}}))',
        '"#state=" + "a".repeat(600)',
    ],
)
def test_malformed_and_oversized_hashes_rejected_without_throwing(bad_hash_expr: str) -> None:
    """Malformed, wrong-widget, out-of-bounds, and oversized hashes fall back to defaults."""
    result = _run_node_eval(f"DV.decodeWidgetStateHash({bad_hash_expr})")
    assert result["valid"] is False
    assert result["state"] == {"x0": 1, "ubar": 1, "horizon": 1, "phase": 0.5}
    assert isinstance(result["reason"], str) and len(result["reason"]) > 0
