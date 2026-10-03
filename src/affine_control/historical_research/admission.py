"""Strict versioned admission of hash-bound sanitized historical JSON."""

import hashlib
import json
import math
import re
from fractions import Fraction
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from .models import (
    MAX_BYTES,
    HistoricalResearchPackage,
    HistoricalResearchRecord,
    ResearchIdentity,
    SourceClock,
)

SCHEMA_ID = "urn:upstreamdrift:historical-player-research:v1"
SCHEMA_PATH = (
    Path(__file__).resolve().parents[3] / "schemas/historical-player-research-v1.schema.json"
)
LOCAL_PATH = re.compile(r"(?<![A-Za-z])[A-Za-z]:[/\\]|(?:^|\s)/(?:Users|home|tmp)/|\\\\")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate object keys before constructing research JSON."""
    keys = [name for name, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate JSON keys are forbidden")
    return dict(pairs)


def _constant(value: str) -> None:
    """Reject nonfinite constants during JSON decoding."""
    raise ValueError(f"Nonfinite JSON constant: {value}")


def load_research_json(payload: bytes) -> dict[str, Any]:
    """Decode bounded, duplicate-key-free UTF-8 research JSON."""
    if not isinstance(payload, bytes) or not 0 < len(payload) <= MAX_BYTES:
        raise ValueError("Research JSON must contain bounded immutable bytes")
    try:
        value = json.loads(
            payload.decode("utf-8"), object_pairs_hook=_unique_object, parse_constant=_constant
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid UTF-8 research JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("Research package must be an object")
    return value


def _sanitize(value: Any) -> None:
    """Reject host paths and nonfinite values throughout detached evidence."""
    if isinstance(value, str) and LOCAL_PATH.search(value):
        raise ValueError("Local paths are forbidden in sanitized research")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Research numbers must be finite")
    if isinstance(value, dict):
        for item in value.values():
            _sanitize(item)
    elif isinstance(value, list):
        for item in value:
            _sanitize(item)


def _clock(value: dict[str, Any]) -> SourceClock:
    """Decode the exact increasing source presentation interval."""
    times = [
        Fraction(value[key]["numerator"], value[key]["denominator"]) for key in ("start", "end")
    ]
    if times[1] <= times[0] or times[0] < 0:
        raise ValueError("Source presentation interval must increase and be nonnegative")
    return SourceClock(times[0], times[1], value["frame_count"])


def _validate_image_counts(value: dict[str, Any]) -> None:
    """Require optional observation counts to agree with the original frame clock.

    A subset of frames and observations is valid training evidence. Omitted
    counts retain the legacy v1 contract; this check adds no landmark assumptions.
    """
    counts = value.get("image_counts")
    if counts is None:
        return
    if counts["source_frame_count"] != value["source_clock"]["frame_count"]:
        raise ValueError("Image source frame count differs from the source clock")
    if counts["training_frame_count"] > counts["source_frame_count"]:
        raise ValueError("Training frame count exceeds original source coverage")
    if counts["training_observation_count"] > counts["dense_observation_count"]:
        raise ValueError("Training observation count exceeds dense evidence coverage")


def _records(values: list[dict[str, Any]]) -> tuple[HistoricalResearchRecord, ...]:
    """Build detached immutable records with consistent unique identities."""
    fits: set[str] = set()
    player_names: dict[str, str] = {}
    swing_owners: dict[str, str] = {}
    records = []
    for value in values:
        _validate_image_counts(value)
        fit_id = value["fit_id"]
        if fit_id in fits:
            raise ValueError("Duplicate fit identity")
        fits.add(fit_id)
        player_id, player_name = value["player_id"], value["player_name"]
        if player_id in player_names and player_names[player_id] != player_name:
            raise ValueError("Contradictory player identity")
        player_names[player_id] = player_name
        swing_id = value["swing_id"]
        if swing_id in swing_owners and swing_owners[swing_id] != player_id:
            raise ValueError("Contradictory swing ownership")
        swing_owners[swing_id] = player_id
        targets = [target["id"] for target in value["targets"]]
        if len(targets) != len(set(targets)):
            raise ValueError("Duplicate target identity")
        identity = ResearchIdentity(player_id, player_name, value["swing_id"], fit_id)
        copied = json.dumps(value, sort_keys=True, allow_nan=False).encode("utf-8")
        records.append(
            HistoricalResearchRecord(
                identity, value["producer_commit"], _clock(value["source_clock"]), copied
            )
        )
    return tuple(sorted(records, key=lambda record: record.identity.fit_id))


def validate_research_schema(schema_bytes: bytes) -> dict[str, Any]:
    """Require fetched schema semantics to equal the supported local contract."""
    schema = load_research_json(schema_bytes)
    approved = load_research_json(SCHEMA_PATH.read_bytes())
    if schema != approved:
        raise ValueError("Research schema differs from the supported versioned contract")
    return schema


def admit_package(
    payload: bytes,
    expected_sha256: str,
    expected_bytes: int,
    source_commit: str,
) -> HistoricalResearchPackage:
    """Verify exact bytes/source plus v1 semantics before constructing immutable records.

    This boundary grants local research display only. A target pass, computation
    or independent review cannot authorize publication or qualification promotion.
    """
    value = load_research_json(payload)
    digest = hashlib.sha256(payload).hexdigest()
    if digest != expected_sha256 or len(payload) != expected_bytes:
        raise ValueError("Research package hash or byte size differs from its pin")
    schema = validate_research_schema(SCHEMA_PATH.read_bytes())
    try:
        Draft202012Validator(schema).validate(value)
    except ValidationError as exc:
        raise ValueError(f"Historical research contract: {exc.message}") from exc
    if value["provider"]["source_commit"] != source_commit:
        raise ValueError("Provider source commit differs from its pin")
    expected_url = f"https://github.com/D-sorganization/UpstreamDrift/tree/{source_commit}"
    if value["provider"]["source_url"] != expected_url:
        raise ValueError("Provider reference is not bound to its exact source commit")
    _sanitize(value)
    return HistoricalResearchPackage(source_commit, digest, payload, _records(value["records"]))
