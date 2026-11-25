"""Load a closed-chain hand-load export and check its UpstreamDrift manifest."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import NoReturn, cast

from pydantic import BaseModel, ValidationError

from src.affine_control.closed_chain_hand_load_schema import (
    DOCUMENT_SCHEMA_VERSION,
    MANIFEST_SCHEMA_VERSION,
    ClosedChainHandLoadError,
    ClosedChainHandLoadRecord,
    UpstreamManifest,
    superposition_error,
)

logger = logging.getLogger(__name__)


def _reject(message: str) -> NoReturn:
    logger.error("%s", message)
    raise ClosedChainHandLoadError(message)


def _pairs(items: list[tuple[str, object]]) -> dict[str, object]:
    parsed: dict[str, object] = {}
    for key, value in items:
        if key in parsed:
            _reject(f"duplicate JSON key: {key}")
        parsed[key] = value
    return parsed


def _read_json(path: Path) -> dict[str, object]:
    """Read one duplicate-key-free JSON object."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs)
    except OSError as exc:
        _reject(f"unable to read {path.name}: {exc}")
    except json.JSONDecodeError as exc:
        _reject(f"invalid JSON in {path.name}: {exc}")
    if not isinstance(payload, dict):
        _reject(f"{path.name} must be a JSON object")
    return cast(dict[str, object], payload)


def _require_version(payload: dict[str, object], expected: str, label: str) -> None:
    if payload.get("schema_version") != expected:
        _reject(f"unknown {label} schema version: {payload.get('schema_version')!r}")


def _validation_message(exc: ValidationError) -> str:
    error = exc.errors()[0]
    location = ".".join(str(part) for part in error["loc"])
    return f"{location}: {error['msg']}" if location else str(error["msg"])


def _parse[ModelT: BaseModel](model: type[ModelT], payload: dict[str, object]) -> ModelT:
    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        _reject(_validation_message(exc))


def _require_provenance(record: ClosedChainHandLoadRecord, manifest: UpstreamManifest) -> None:
    left = record.provenance.model_dump()
    right = manifest.provenance.model_dump()
    for name, value in left.items():
        if value != right[name]:
            _reject(f"provenance mismatch: {name}")


def _require_superposition(record: ClosedChainHandLoadRecord) -> None:
    tolerance = record.superposition_tolerance
    for index, frame in enumerate(record.frames):
        message = superposition_error(frame, tolerance)
        if message is not None:
            _reject(f"frames[{index}] {message}")


def load_closed_chain_hand_load(
    document_path: Path, manifest_path: Path
) -> ClosedChainHandLoadRecord:
    """Load a document and require its SHA-256 provenance to match a manifest.

    Preconditions: both paths are UTF-8 JSON objects of the v1 schemas.
    Postconditions: numeric channels satisfy ZTCF + ZVCF = Total within tolerance,
    provenance matches, and ``UNAVAILABLE`` is preserved.
    """
    document = _read_json(document_path)
    manifest_payload = _read_json(manifest_path)
    _require_version(document, DOCUMENT_SCHEMA_VERSION, "document")
    _require_version(manifest_payload, MANIFEST_SCHEMA_VERSION, "manifest")
    record = _parse(ClosedChainHandLoadRecord, document)
    manifest = _parse(UpstreamManifest, manifest_payload)
    _require_provenance(record, manifest)
    _require_superposition(record)
    return record
