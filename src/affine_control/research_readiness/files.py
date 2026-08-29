"""Bounded JSON and evidence-file operations for readiness validation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .errors import ResearchReadinessError

MAX_EVIDENCE_BYTES = 5_000_000


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Build a mapping while rejecting ambiguous duplicate JSON keys."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ResearchReadinessError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    """Load a JSON contract with duplicate-key and parse-error handling."""
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
    except ResearchReadinessError:
        raise
    except (OSError, json.JSONDecodeError) as exc:
        raise ResearchReadinessError(f"Cannot load JSON contract {path}: {exc}") from exc


def schema_errors(library: object, schema_path: Path) -> list[str]:
    """Return deterministic JSON Schema validation messages."""
    validator = Draft202012Validator(load_json(schema_path), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(library), key=lambda error: list(error.absolute_path))
    return [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in errors
    ]


def checked_file(root: Path, raw_path: object, label: str) -> Path:
    """Resolve a bounded regular evidence file below the repository root."""
    value = str(raw_path)
    parts = PurePosixPath(value).parts
    if not value or any(part in {".", ".."} for part in parts):
        raise ResearchReadinessError(f"Repository path traversal is forbidden: {value}")
    unresolved = root.joinpath(*parts)
    if unresolved.is_symlink():
        raise ResearchReadinessError(f"Symlink evidence is forbidden: {value}")
    candidate = unresolved.resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ResearchReadinessError(f"Repository path traversal is forbidden: {value}") from exc
    if not candidate.is_file():
        raise ResearchReadinessError(f"Missing {label}: {value}")
    if candidate.stat().st_size > MAX_EVIDENCE_BYTES:
        raise ResearchReadinessError(f"Oversized {label}: {value}")
    return candidate


def digest(path: Path) -> str:
    """Return the SHA-256 digest of one bounded evidence file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()
