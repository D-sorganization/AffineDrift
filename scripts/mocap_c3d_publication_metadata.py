"""Metadata checks shared by the mocap/C3D publication verifier."""

from __future__ import annotations

import math
from typing import cast

from scripts.mocap_c3d_publication_contract import (
    LOSS_SIDECAR_SCHEMA_ID,
    MocapC3DPublicationError,
)
from scripts.mocap_c3d_publication_contract import array as _array
from scripts.mocap_c3d_publication_contract import number as _number
from scripts.mocap_c3d_publication_contract import object_with_keys as _object
from scripts.mocap_c3d_publication_contract import text as _text
from scripts.mocap_c3d_publication_contract import unique_texts as _unique_texts

OFFICIAL_SOURCE_IDS = {"c3d-user-guide", "ezc3d-primary"}
LOSS_DISPOSITIONS = {"preserved_in_sidecar", "rejected"}


def verify_sources(value: object) -> None:
    """Require the primary C3D and adapter sources used by this slice."""

    source_ids: set[str] = set()
    topics: set[str] = set()
    for index, item in enumerate(_array(value, "source traceability")):
        source = _object(
            item,
            f"source {index}",
            {"id", "title", "url", "accessed_on", "applies_to"},
        )
        source_id = _text(source["id"], f"source {index} id")
        if source_id in source_ids:
            raise MocapC3DPublicationError("source ids must be unique")
        source_ids.add(source_id)
        _text(source["title"], f"source {source_id} title")
        url = _text(source["url"], f"source {source_id} URL")
        if not url.startswith("https://"):
            raise MocapC3DPublicationError("source URLs must use HTTPS")
        if source["accessed_on"] != "2026-08-26":
            raise MocapC3DPublicationError("source access dates must match the review date")
        topics.update(_unique_texts(source["applies_to"], f"source {source_id} topics"))
    if source_ids != OFFICIAL_SOURCE_IDS:
        raise MocapC3DPublicationError("official C3D and EzC3D sources are both required")
    required_topics = {
        "fixed_point_rate",
        "integer_analog_ratio",
        "event_header_limit",
        "negative_residual_invalid",
        "seven_camera_mask",
    }
    if not required_topics.issubset(topics):
        raise MocapC3DPublicationError("source traceability omits a normative C3D limit")


def verify_coordinate_frame(value: object) -> None:
    """Require explicit axes, handedness, and SI source units."""

    frame = _object(
        value,
        "coordinate frame",
        {"frame_id", "handedness", "x_axis", "y_axis", "z_axis", "length_unit"},
    )
    _text(frame["frame_id"], "coordinate frame id")
    if frame["handedness"] not in {"right-handed", "left-handed"}:
        raise MocapC3DPublicationError("coordinate frame handedness is unsupported")
    axes = [
        _text(frame[name], f"coordinate frame {name}")
        for name in ("x_axis", "y_axis", "z_axis")
    ]
    if len(set(axes)) != 3:
        raise MocapC3DPublicationError("coordinate axes must have distinct meanings")
    if frame["length_unit"] != "m":
        raise MocapC3DPublicationError("canonical publication coordinates must use metres")


def verify_provenance(value: object) -> None:
    """Keep synthetic classification and method identity explicit."""

    provenance = _object(
        value,
        "provenance",
        {"source_kind", "method_id", "method_version", "human_subject_data", "claim_class"},
    )
    if provenance["source_kind"] != "sanitized_synthetic":
        raise MocapC3DPublicationError("fixture source must remain sanitized synthetic")
    if (
        provenance["human_subject_data"] is not False
        or provenance["claim_class"] != "model_scenario"
    ):
        raise MocapC3DPublicationError("fixture cannot claim human or observed evidence")
    _text(provenance["method_id"], "provenance method id")
    version = _text(provenance["method_version"], "provenance method version")
    parts = version.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise MocapC3DPublicationError("method version must be numeric semantic version")


def verify_projection_rates(
    value: object, point_rate: float, analog_rate: float, ratio: int
) -> None:
    """Ensure displayed C3D rates are the verified canonical rates."""

    projection = cast(dict[str, object], value)
    projected_point_rate = _number(projection.get("point_rate_hz"), "projected point rate")
    projected_analog_rate = _number(projection.get("analog_rate_hz"), "projected analog rate")
    projected_ratio = projection.get("analog_samples_per_point_frame")
    if not math.isclose(projected_point_rate, point_rate):
        raise MocapC3DPublicationError("projected point rate differs from canonical rate")
    if not math.isclose(projected_analog_rate, analog_rate) or projected_ratio != ratio:
        raise MocapC3DPublicationError(
            "projected analog rate/ratio differs from canonical timebase"
        )


def verify_losses(value: object, *, overflow: bool) -> int:
    """Require typed, unique, explicit loss dispositions."""

    sidecar = cast(dict[str, object], value)
    if sidecar.get("schema") != LOSS_SIDECAR_SCHEMA_ID:
        raise MocapC3DPublicationError("loss sidecar schema is unsupported")
    loss_ids: set[str] = set()
    for index, item in enumerate(_array(sidecar.get("losses"), "sidecar losses")):
        loss = _object(
            item,
            f"loss {index}",
            {"id", "path", "source_semantics", "c3d_semantics", "disposition", "detail"},
        )
        loss_id = _text(loss["id"], f"loss {index} id")
        if loss_id in loss_ids:
            raise MocapC3DPublicationError("loss ids must be unique")
        loss_ids.add(loss_id)
        for key in ("path", "source_semantics", "c3d_semantics", "detail"):
            _text(loss[key], f"loss {loss_id} {key}")
        if loss["disposition"] not in LOSS_DISPOSITIONS:
            raise MocapC3DPublicationError("loss disposition is unsupported")
    required = {
        "absolute-timestamp-origin",
        "point-confidence",
        "skeleton-topology",
        "processing-provenance",
    }
    if not required.issubset(loss_ids):
        raise MocapC3DPublicationError("sidecar omits a required semantic loss")
    if ("camera-mask-capacity" in loss_ids) != overflow:
        raise MocapC3DPublicationError("camera-mask-capacity loss must match actual overflow")
    return len(loss_ids)
