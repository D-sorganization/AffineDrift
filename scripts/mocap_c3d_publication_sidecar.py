"""Digest and contributor checks for C3D publication loss sidecars."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import cast

from scripts.mocap_c3d_publication_contract import (
    LOSS_SIDECAR_SCHEMA_ID,
    STANDARD_CAMERA_CAPACITY,
    MocapC3DPublicationError,
    array,
    integer,
    object_with_keys,
    text,
    unique_texts,
)

CanonicalPoints = dict[tuple[int, str], tuple[dict[str, object], list[str]]]


def _read_payload(value: object, fixture_dir: Path) -> dict[str, object]:
    reference = object_with_keys(
        value, "loss sidecar reference", {"path", "sha256", "bytes", "required"}
    )
    if reference["required"] is not True:
        raise MocapC3DPublicationError("loss sidecar must be required")
    relative = Path(text(reference["path"], "loss sidecar path"))
    if relative.name != str(relative) or relative.suffix != ".json":
        raise MocapC3DPublicationError("loss sidecar path must be a local JSON filename")
    payload = (fixture_dir / relative).read_bytes()
    expected_bytes = integer(reference["bytes"], "loss sidecar bytes", minimum=1)
    if len(payload) != expected_bytes:
        raise MocapC3DPublicationError("loss sidecar byte size differs")
    if hashlib.sha256(payload).hexdigest() != reference["sha256"]:
        raise MocapC3DPublicationError("loss sidecar SHA-256 differs")
    return cast(dict[str, object], json.loads(payload))


def _expected_overflow(canonical: CanonicalPoints, cameras: list[str]) -> list[str]:
    return [
        camera_id
        for camera_id in cameras[STANDARD_CAMERA_CAPACITY:]
        if any(camera_id in contributors for _, contributors in canonical.values())
    ]


def _verify_record(
    value: object, canonical: CanonicalPoints, cameras: list[str]
) -> tuple[int, str]:
    record = object_with_keys(
        value,
        "sidecar contributor",
        {
            "frame_index",
            "point_id",
            "canonical_camera_ids",
            "standard_mask_state",
            "standard_mask",
        },
    )
    key = (
        integer(record["frame_index"], "sidecar frame"),
        text(record["point_id"], "sidecar point"),
    )
    if key not in canonical or record["canonical_camera_ids"] != canonical[key][1]:
        raise MocapC3DPublicationError(
            "sidecar contributor identities differ from canonical evidence"
        )
    contributors = canonical[key][1]
    overflow = any(
        cameras.index(camera_id) >= STANDARD_CAMERA_CAPACITY for camera_id in contributors
    )
    expected_state = "unavailable_overflow" if overflow else "representable"
    expected_mask = (
        None if overflow else sum(1 << cameras.index(camera_id) for camera_id in contributors)
    )
    if record["standard_mask_state"] != expected_state:
        raise MocapC3DPublicationError("sidecar standard mask disposition differs")
    if record["standard_mask"] != expected_mask:
        raise MocapC3DPublicationError("sidecar standard mask disposition differs")
    return key


def load_and_verify_sidecar(
    reference: object,
    fixture_id: str,
    fixture_dir: Path,
    canonical: CanonicalPoints,
    cameras: list[str],
) -> tuple[dict[str, object], int]:
    """Read, digest-check, and bind one loss sidecar to canonical evidence."""

    sidecar = _read_payload(reference, fixture_dir)
    checked = object_with_keys(
        sidecar,
        "loss sidecar",
        {"schema", "fixture_id", "purpose", "camera_overflow", "contributors", "losses"},
    )
    if checked["schema"] != LOSS_SIDECAR_SCHEMA_ID:
        raise MocapC3DPublicationError("loss sidecar schema is unsupported")
    if checked["fixture_id"] != fixture_id:
        raise MocapC3DPublicationError("loss sidecar fixture id differs")
    text(checked["purpose"], "loss sidecar purpose")
    overflow = (
        unique_texts(checked["camera_overflow"], "camera overflow")
        if checked["camera_overflow"]
        else []
    )
    if overflow != _expected_overflow(canonical, cameras):
        raise MocapC3DPublicationError(
            "camera overflow must preserve every contributor beyond seven"
        )
    records = array(checked["contributors"], "sidecar contributors")
    if len(records) != len(canonical):
        raise MocapC3DPublicationError("sidecar must bind every canonical contributor record")
    keys = [_verify_record(record, canonical, cameras) for record in records]
    if len(keys) != len(set(keys)) or set(keys) != set(canonical):
        raise MocapC3DPublicationError("sidecar contributor keys must be exact and unique")
    return sidecar, len(overflow)
