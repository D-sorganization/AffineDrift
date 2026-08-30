"""Fail-closed validation for downloaded companion manifests and schemas."""

from __future__ import annotations

import hashlib
import json
from typing import Any, cast

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

from .errors import AcquisitionError
from .models import (
    FetchResult,
    ImportRequest,
    LockRecord,
    ValidatedSnapshot,
    snapshot_tree_digest,
)
from .policy import ConsumerPolicy

PATH_KEYS = frozenset({"entry_point", "path", "source_path", "vendor_path"})


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise AcquisitionError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_json(payload: bytes, label: str) -> object:
    try:
        return json.loads(payload.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except AcquisitionError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AcquisitionError(f"invalid {label} JSON: {exc}") from exc


def _digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _validate_digest(payload: bytes, expected: str, label: str) -> None:
    if _digest(payload) != expected:
        raise AcquisitionError(f"{label} SHA-256 does not match the pinned digest")


def _validate_fetch(
    result: FetchResult,
    expected_url: str,
    request: ImportRequest,
    policy: ConsumerPolicy,
    approved_path: str,
) -> bytes:
    if result.requested_url != expected_url:
        raise AcquisitionError("transport returned evidence for a different requested URL")
    observed_urls = (*result.redirects, result.final_url)
    for observed_url in observed_urls:
        policy.validate_url(observed_url, request.source_commit, approved_path)
    if len(result.payload) > policy.max_payload_bytes:
        raise AcquisitionError("payload exceeds byte limit")
    return result.payload


def _validate_repository_path(value: str) -> None:
    parts = value.split("/")
    if (
        not value
        or value.startswith(("/", "\\"))
        or "\\" in value
        or ":" in parts[0]
        or any(part in {"", ".", ".."} for part in parts)
    ):
        raise AcquisitionError(f"unsafe repository path: {value}")


def _validate_paths(value: object, parent_key: str | None = None) -> None:
    if parent_key in PATH_KEYS and isinstance(value, str):
        _validate_repository_path(value)
    if isinstance(value, dict):
        for key, child in value.items():
            _validate_paths(child, str(key))
    elif isinstance(value, list):
        for child in value:
            _validate_paths(child, parent_key)


def _validate_schema(schema: object, policy: ConsumerPolicy) -> dict[str, object]:
    if not isinstance(schema, dict):
        raise AcquisitionError("provider schema must be a JSON object")
    if schema.get("$id") != policy.schema_id:
        raise AcquisitionError("provider schema ID does not match the pinned contract")
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise AcquisitionError(f"invalid provider schema: {exc.message}") from exc
    return cast(dict[str, object], schema)


def _validate_manifest(
    manifest: object,
    schema: dict[str, object],
    request: ImportRequest,
    policy: ConsumerPolicy,
) -> tuple[str, str]:
    _validate_paths(manifest)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(manifest), key=lambda error: list(error.absolute_path))
    if errors:
        location = "/".join(str(part) for part in errors[0].absolute_path) or "<root>"
        raise AcquisitionError(f"manifest schema violation at {location}: {errors[0].message}")
    if not isinstance(manifest, dict):
        raise AcquisitionError("validated manifest must be a JSON object")
    source = cast(dict[str, object], manifest["source"])
    if source["repository"] != policy.repository_url:
        raise AcquisitionError("embedded provider repository does not match the allowlist")
    if source["commit"] != request.source_commit:
        raise AcquisitionError("embedded source commit does not match the requested commit")
    publication = cast(dict[str, object], manifest["publication"])
    return str(source["repository"]), str(publication["state"])


def validate_downloads(
    request: ImportRequest,
    policy: ConsumerPolicy,
    manifest_result: FetchResult,
    schema_result: FetchResult,
) -> ValidatedSnapshot:
    """Validate all downloaded bytes and build their deterministic lock.

    Preconditions:
        ``policy.validate_request(request)`` succeeds and both results are bounded.
    Postconditions:
        Returned bytes match every digest, schema, provider, commit, and path contract.
    """
    manifest_bytes = _validate_fetch(
        manifest_result, request.manifest_url, request, policy, policy.manifest_path
    )
    schema_bytes = _validate_fetch(
        schema_result, request.schema_url, request, policy, policy.schema_path
    )
    _validate_digest(manifest_bytes, request.manifest_sha256, "manifest")
    _validate_digest(schema_bytes, request.schema_sha256, "schema")
    schema = _validate_schema(_load_json(schema_bytes, "schema"), policy)
    repository, publication_state = _validate_manifest(
        _load_json(manifest_bytes, "manifest"), schema, request, policy
    )
    snapshot_id = f"{request.source_commit}-{request.manifest_sha256[:16]}"
    lock = LockRecord(
        repository=repository,
        source_commit=request.source_commit,
        manifest_url=request.manifest_url,
        manifest_sha256=request.manifest_sha256,
        manifest_bytes=len(manifest_bytes),
        schema_url=request.schema_url,
        schema_sha256=request.schema_sha256,
        schema_bytes=len(schema_bytes),
        snapshot_id=snapshot_id,
        snapshot_tree_sha256=snapshot_tree_digest(request.manifest_sha256, request.schema_sha256),
        publication_state=cast(Any, publication_state),
    )
    return ValidatedSnapshot(manifest_bytes, schema_bytes, lock)
