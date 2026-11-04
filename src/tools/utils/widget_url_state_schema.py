"""Widget URL-hash state schema loader and validator (#5255).

Loads and enforces schemas/widgets/widget-url-state-v1.schema.json for single-widget
URL-hash state envelopes (#state=<urlencoded-json>).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from src.core.contracts import require

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPO_ROOT / "schemas" / "widgets" / "widget-url-state-v1.schema.json"
MAX_HASH_LENGTH = 512


def load_widget_url_state_schema(schema_path: Path | None = None) -> dict[str, Any]:
    """Load the widget URL-hash state v1 JSON schema."""
    target_path = schema_path or SCHEMA_PATH
    require(target_path.is_file(), f"Widget URL state schema not found: {target_path}")
    loaded = json.loads(target_path.read_text(encoding="utf-8"))
    require(isinstance(loaded, dict), "Schema must be a JSON object")
    require("$id" in loaded, "Schema must declare $id")
    data: dict[str, Any] = loaded
    return data


def validate_widget_url_state_payload(
    payload: dict[str, Any],
    *,
    schema_path: Path | None = None,
) -> list[str]:
    """Validate a decoded widget URL-hash envelope against the v1 schema.

    Returns a list of validation error messages (empty when valid).
    """
    require(isinstance(payload, dict), "payload must be a mapping")
    schema = load_widget_url_state_schema(schema_path)
    validator = jsonschema.Draft202012Validator(schema)
    errors: list[str] = []
    for err in validator.iter_errors(payload):
        field = ".".join(str(p) for p in err.path) if err.path else "root"
        errors.append(f"{field}: {err.message}")
    return errors
