"""Fail-closed loading for the governed falsification atlas."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any, cast

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError

from .errors import AtlasValidationError
from .models import AtlasDocument, AtlasIndexes, AtlasPaths, AtlasRecord


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Construct a mapping while rejecting ambiguous duplicate JSON keys."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise AtlasValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_json(path: Path) -> dict[str, Any]:
    """Read one duplicate-key-free JSON object."""
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys
        )
    except AtlasValidationError:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AtlasValidationError(f"invalid JSON at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AtlasValidationError(f"JSON root must be an object: {path}")
    return cast(dict[str, Any], value)


def _sha256(path: Path) -> str:
    """Return the lowercase SHA-256 digest of exact file bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_schema(mapping: dict[str, Any], schema_path: Path) -> None:
    """Validate the editorial mapping against its strict Draft 2020-12 schema."""
    schema = _load_json(schema_path)
    try:
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(mapping)
    except (SchemaError, ValidationError) as exc:
        raise AtlasValidationError(f"atlas schema validation failed: {exc.message}") from exc


def _validate_digest(label: str, authority: dict[str, Any], path: Path) -> None:
    """Require one mapping authority pin to match the current exact bytes."""
    expected = cast(str, authority["sha256"])
    if _sha256(path) != expected:
        raise AtlasValidationError(f"{label} SHA-256 does not match the reviewed authority")


def _validate_authority_path(label: str, authority: dict[str, Any], path: Path, root: Path) -> None:
    """Require provenance metadata to name the bytes actually being read."""
    try:
        actual = path.relative_to(root).as_posix()
    except ValueError as exc:
        raise AtlasValidationError(f"{label} authority path is outside the repository") from exc
    if authority["path"] != actual:
        raise AtlasValidationError(f"{label} authority path does not match: {actual}")


def _indexed(items: object, key: str, label: str) -> dict[str, dict[str, Any]]:
    """Build a unique identifier index from a governed authority list."""
    if not isinstance(items, list):
        raise AtlasValidationError(f"{label} authority is missing its record list")
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get(key), str):
            raise AtlasValidationError(f"invalid {label} authority record")
        identifier = cast(str, item[key])
        if identifier in result:
            raise AtlasValidationError(f"duplicate {label} identifier: {identifier}")
        result[identifier] = cast(dict[str, Any], item)
    return result


def _validate_content_target(root: Path, record: dict[str, Any]) -> None:
    """Require a safe canonical chapter path containing the declared anchor."""
    raw_path = cast(str, record["chapter_path"])
    posix = PurePosixPath(raw_path)
    if posix.is_absolute() or ".." in posix.parts or "\\" in raw_path:
        raise AtlasValidationError(f"unsafe chapter path: {raw_path}")
    chapter = root.joinpath(*posix.parts)
    if not chapter.is_file():
        raise AtlasValidationError(f"missing chapter path: {raw_path}")
    anchor = cast(str, record["chapter_anchor"])
    if f"{{#{anchor}}}" not in chapter.read_text(encoding="utf-8"):
        raise AtlasValidationError(f"missing chapter anchor: {anchor}")


def _build_record(
    editorial: dict[str, Any],
    claim: dict[str, Any],
    critique: dict[str, Any],
    readiness: dict[str, Any],
) -> AtlasRecord:
    """Join one editorial question to authority-owned claim and critique fields."""
    workflow = cast(dict[str, Any], editorial["workflow"])
    links = cast(dict[str, Any], readiness["links"])
    release = cast(dict[str, str], links["validation_release"])
    return AtlasRecord(
        atlas_id=cast(str, editorial["atlas_id"]),
        theme=cast(str, editorial["theme"]),
        title=cast(str, editorial["title"]),
        claim_id=cast(str, claim["claim_id"]),
        claim=cast(str, claim["statement"]),
        evidence_state=cast(str, claim["adjudication_outcome"]),
        uncertainty=cast(str, claim["uncertainty_boundary"]),
        falsifier=cast(str, claim["falsifier"]),
        model_domain=cast(str, claim["model_domain"]),
        critique_id=cast(str, critique["critique_id"]),
        critique_state=cast(str, critique["disposition"]),
        critique_source_path=cast(str, critique["source_path"]),
        readiness_protocol_id=cast(str, readiness["protocol_id"]),
        readiness_title=cast(str, readiness["title"]),
        readiness_state=cast(str, readiness["state"]),
        readiness_evidence_origin=cast(str, readiness["evidence_origin"]),
        validation_release_state=release["status"],
        validation_release_next_gate=release["next_gate"],
        critique_question=cast(str, editorial["critique_question"]),
        alternative_mechanism=cast(str, editorial["alternative_mechanism"]),
        discriminating_measurement=cast(str, editorial["discriminating_measurement"]),
        chapter_path=cast(str, editorial["chapter_path"]),
        chapter_anchor=cast(str, editorial["chapter_anchor"]),
        workflow_state=cast(str, workflow["state"]),
        workflow_reason=cast(str, workflow["reason"]),
        provider_record_url=cast(str | None, workflow["provider_record_url"]),
        evidence_artifacts=tuple(cast(list[str], claim["evidence_artifacts"])),
    )


def _join_records(
    paths: AtlasPaths,
    mapping: dict[str, Any],
    indexes: AtlasIndexes,
) -> tuple[AtlasRecord, ...]:
    """Resolve all editorial references without copying scientific state."""
    records: list[AtlasRecord] = []
    atlas_ids: set[str] = set()
    themes: set[str] = set()
    for editorial in cast(list[dict[str, Any]], mapping["records"]):
        _validate_content_target(paths.root, editorial)
        atlas_id = cast(str, editorial["atlas_id"])
        theme = cast(str, editorial["theme"])
        if atlas_id in atlas_ids:
            raise AtlasValidationError(f"duplicate atlas identifier: {atlas_id}")
        if theme in themes:
            raise AtlasValidationError(f"duplicate atlas theme: {theme}")
        atlas_ids.add(atlas_id)
        themes.add(theme)
        claim_id = cast(str, editorial["claim_id"])
        critique_id = cast(str, editorial["critique_id"])
        readiness_id = cast(str, editorial["readiness_protocol_id"])
        if claim_id not in indexes.claims:
            raise AtlasValidationError(f"unknown claim identifier: {claim_id}")
        if critique_id not in indexes.critiques:
            raise AtlasValidationError(f"unknown critique identifier: {critique_id}")
        if readiness_id not in indexes.readiness:
            raise AtlasValidationError(f"unknown readiness protocol: {readiness_id}")
        records.append(
            _build_record(
                editorial,
                indexes.claims[claim_id],
                indexes.critiques[critique_id],
                indexes.readiness[readiness_id],
            )
        )
    return tuple(records)


def load_atlas(paths: AtlasPaths) -> AtlasDocument:
    """Load and join the complete fail-closed atlas authority graph."""
    mapping = _load_json(paths.mapping)
    _validate_schema(mapping, paths.schema)
    authorities = cast(dict[str, dict[str, Any]], mapping["authorities"])
    _validate_authority_path("claims", authorities["claims"], paths.claims, paths.root)
    _validate_authority_path("critiques", authorities["critiques"], paths.critiques, paths.root)
    _validate_authority_path(
        "source manifest",
        authorities["source_manifest"],
        paths.source_manifest,
        paths.root,
    )
    _validate_authority_path("readiness", authorities["readiness"], paths.readiness, paths.root)
    _validate_digest("claims", authorities["claims"], paths.claims)
    _validate_digest("critiques", authorities["critiques"], paths.critiques)
    _validate_digest("source manifest", authorities["source_manifest"], paths.source_manifest)
    _validate_digest("readiness", authorities["readiness"], paths.readiness)
    claim_doc = _load_json(paths.claims)
    critique_doc = _load_json(paths.critiques)
    readiness_doc = _load_json(paths.readiness)
    source = cast(dict[str, Any], _load_json(paths.source_manifest)["source"])
    indexes = AtlasIndexes(
        claims=_indexed(claim_doc.get("claims"), "claim_id", "claim"),
        critiques=_indexed(critique_doc.get("critiques"), "critique_id", "critique"),
        readiness=_indexed(readiness_doc.get("protocols"), "protocol_id", "readiness protocol"),
    )
    provider = cast(dict[str, str], mapping["provider_authority"])
    return AtlasDocument(
        schema_version=cast(str, mapping["schema_version"]),
        provider_state=provider["state"],
        provider_reason=provider["reason"],
        provider_tracking_issue=provider["tracking_issue"],
        source_repository=cast(str, source["repository"]),
        source_commit=cast(str, source["commit"]),
        source_root=cast(str, source["root"]),
        records=_join_records(paths, mapping, indexes),
    )
