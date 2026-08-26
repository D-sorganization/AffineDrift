#!/usr/bin/env python3
"""Verify AffineDrift's source-only mocap/C3D publication fixtures."""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from scripts.mocap_c3d_publication_contract import (
    PUBLICATION_SCHEMA_ID,
    STANDARD_CAMERA_CAPACITY,
    STANDARD_EVENT_HEADER_LIMIT,
    STANDARD_MASK_MAX,
    MocapC3DPublicationError,
)
from scripts.mocap_c3d_publication_contract import array as _array
from scripts.mocap_c3d_publication_contract import integer as _integer
from scripts.mocap_c3d_publication_contract import number as _number
from scripts.mocap_c3d_publication_contract import object_with_keys as _object
from scripts.mocap_c3d_publication_contract import text as _text
from scripts.mocap_c3d_publication_contract import unique_texts as _unique_texts
from scripts.mocap_c3d_publication_metadata import (
    verify_coordinate_frame,
    verify_losses,
    verify_projection_rates,
    verify_provenance,
    verify_sources,
)
from scripts.mocap_c3d_publication_sidecar import load_and_verify_sidecar

TOP_LEVEL_KEYS = {
    "schema",
    "fixture_id",
    "classification",
    "authority",
    "dependencies",
    "source_traceability",
    "coordinate_frame",
    "timebase",
    "cameras",
    "skeleton",
    "frames",
    "events",
    "analog",
    "provenance",
    "c3d_projection",
    "loss_sidecar",
    "limitations",
}


@dataclass(frozen=True)
class PublicationSummary:
    """Deterministic evidence counts and dependency state for one fixture."""

    fixture_id: str
    camera_count: int
    frame_count: int
    point_count: int
    analog_sample_count: int
    loss_count: int
    overflow_count: int
    representable_mask: int | None
    tools_m1_protected_revision: str | None
    tools_m9_protected_revision: str | None


def _verify_authority(value: object) -> None:
    authority = _object(
        value,
        "authority",
        {
            "repository",
            "scope",
            "runtime_authority",
            "binary_c3d_present",
            "unknown_metadata_policy",
        },
    )
    if authority["repository"] != "D-sorganization/AffineDrift":
        raise MocapC3DPublicationError("AffineDrift must remain publication authority")
    if authority["scope"] != "sanitized publication compatibility and pedagogy only":
        raise MocapC3DPublicationError("authority scope must remain publication-only")
    if authority["runtime_authority"] is not False or authority["binary_c3d_present"] is not False:
        raise MocapC3DPublicationError("fixture cannot claim runtime authority or a binary C3D")
    if authority["unknown_metadata_policy"] != "reject":
        raise MocapC3DPublicationError("unknown metadata must be rejected explicitly")


def _verify_dependency(value: object, label: str, issue_number: int) -> None:
    dependency = _object(
        value, label, {"issue", "state", "protected_revision", "release", "schema_id"}
    )
    expected_issue = f"https://github.com/D-sorganization/Tools/issues/{issue_number}"
    if dependency["issue"] != expected_issue:
        raise MocapC3DPublicationError(f"{label} issue is not pinned to {expected_issue}")
    null_fields = ("protected_revision", "release", "schema_id")
    if dependency["state"] != "unavailable" or any(
        dependency[field] is not None for field in null_fields
    ):
        raise MocapC3DPublicationError(f"{label} must remain unavailable with null pins")


def _verify_dependencies(value: object) -> dict[str, object]:
    dependencies = _object(value, "dependencies", {"tools_m1", "tools_m9"})
    _verify_dependency(dependencies["tools_m1"], "Tools M1", 4710)
    _verify_dependency(dependencies["tools_m9"], "Tools M9", 4716)
    return dependencies


def _verify_timebase(value: object) -> tuple[float, float, int]:
    timebase = _object(
        value,
        "timebase",
        {
            "point_rate_hz",
            "analog_rate_hz",
            "analog_samples_per_point_frame",
            "timestamp_origin",
            "timestamp_unit",
        },
    )
    point_rate = _number(timebase["point_rate_hz"], "point rate")
    analog_rate = _number(timebase["analog_rate_hz"], "analog rate")
    ratio = _integer(timebase["analog_samples_per_point_frame"], "analog ratio", minimum=1)
    if point_rate <= 0 or analog_rate <= 0 or not math.isclose(analog_rate, point_rate * ratio):
        raise MocapC3DPublicationError("analog rate must be an integer multiple of point rate")
    if timebase["timestamp_unit"] != "ns":
        raise MocapC3DPublicationError("timestamp unit must be ns")
    _text(timebase["timestamp_origin"], "timestamp origin")
    return point_rate, analog_rate, ratio


def _verify_point(value: object, label: str, cameras: set[str]) -> tuple[str, list[str]]:
    point = _object(
        value, label, {"point_id", "xyz_m", "confidence", "residual", "valid", "contributors"}
    )
    point_id = _text(point["point_id"], f"{label} id")
    xyz = _array(point["xyz_m"], f"{label} xyz")
    if len(xyz) != 3:
        raise MocapC3DPublicationError(f"{label} xyz must have three components")
    for axis in xyz:
        _number(axis, f"{label} coordinate")
    confidence = _number(point["confidence"], f"{label} confidence")
    if not 0 <= confidence <= 1:
        raise MocapC3DPublicationError(f"{label} confidence must be on [0,1]")
    residual = _number(point["residual"], f"{label} residual")
    if residual < 0 and point["valid"] is not False:
        raise MocapC3DPublicationError("negative residual must mark the C3D point invalid")
    if residual >= 0 and point["valid"] is not True:
        raise MocapC3DPublicationError("nonnegative residual must mark the point valid")
    contributors = _unique_texts(point["contributors"], f"{label} contributors")
    if not set(contributors).issubset(cameras):
        raise MocapC3DPublicationError(f"{label} references an unknown camera")
    return point_id, contributors


def _verify_frames(
    value: object, point_rate: float, cameras: set[str]
) -> dict[tuple[int, str], tuple[dict[str, object], list[str]]]:
    frames = _array(value, "frames")
    points: dict[tuple[int, str], tuple[dict[str, object], list[str]]] = {}
    first_timestamp: int | None = None
    for expected_index, item in enumerate(frames):
        frame = _object(item, f"frame {expected_index}", {"frame_index", "timestamp_ns", "points"})
        if frame["frame_index"] != expected_index:
            raise MocapC3DPublicationError("frame indices must be contiguous from zero")
        timestamp = _integer(frame["timestamp_ns"], f"frame {expected_index} timestamp")
        first_timestamp = timestamp if first_timestamp is None else first_timestamp
        expected_timestamp = first_timestamp + round(expected_index * 1_000_000_000 / point_rate)
        if timestamp != expected_timestamp:
            raise MocapC3DPublicationError("fixed-rate timestamp does not match frame index")
        frame_ids: set[str] = set()
        for point_item in _array(frame["points"], f"frame {expected_index} points"):
            point_id, contributors = _verify_point(
                point_item, f"frame {expected_index} point", cameras
            )
            if point_id in frame_ids:
                raise MocapC3DPublicationError("point ids must be unique within a frame")
            frame_ids.add(point_id)
            points[(expected_index, point_id)] = (cast(dict[str, object], point_item), contributors)
    return points


def _verify_events(value: object) -> int:
    events = _array(value, "events", allow_empty=True)
    if len(events) > STANDARD_EVENT_HEADER_LIMIT:
        raise MocapC3DPublicationError("events exceed the 18-event header limit")
    for index, item in enumerate(events):
        event = _object(item, f"event {index}", {"label", "time_seconds", "context", "description"})
        _text(event["label"], f"event {index} label")
        _number(event["time_seconds"], f"event {index} time")
        if not isinstance(event["context"], str) or not isinstance(event["description"], str):
            raise MocapC3DPublicationError("event context and description must be strings")
    return len(events)


def _verify_analog(value: object, frame_count: int, ratio: int) -> int:
    analog = _object(
        value,
        "analog",
        {"channel_labels", "channel_units", "samples", "force_platforms"},
    )
    labels = _unique_texts(analog["channel_labels"], "analog labels")
    units = [_text(unit, "analog unit") for unit in _array(analog["channel_units"], "analog units")]
    if len(labels) != len(units):
        raise MocapC3DPublicationError("analog labels and units must have equal length")
    samples = _array(analog["samples"], "analog samples")
    if len(samples) != frame_count * ratio:
        raise MocapC3DPublicationError("analog sample count must equal frames times integer ratio")
    for sample in samples:
        values = _array(sample, "analog sample")
        if len(values) != len(labels):
            raise MocapC3DPublicationError("every analog sample must cover every channel")
        for value_item in values:
            _number(value_item, "analog value")
    _verify_force_platforms(analog["force_platforms"], len(labels))
    return len(samples)


def _verify_force_platforms(value: object, channel_count: int) -> None:
    for index, item in enumerate(_array(value, "force platforms", allow_empty=True)):
        plate = _object(
            item,
            f"force platform {index}",
            {"plate_id", "type_code", "channel_indices_zero_based", "corners_m", "origin_m"},
        )
        _text(plate["plate_id"], f"force platform {index} id")
        _integer(plate["type_code"], f"force platform {index} type", minimum=1)
        channels = plate["channel_indices_zero_based"]
        indices = [_integer(item, "force channel") for item in _array(channels, "force channels")]
        if len(indices) != len(set(indices)) or any(item >= channel_count for item in indices):
            raise MocapC3DPublicationError("force channel indices must be unique and in range")
        corners = _array(plate["corners_m"], "force corners")
        if len(corners) != 4:
            raise MocapC3DPublicationError("force platform must have four corners")
        for vector in [*corners, plate["origin_m"]]:
            if len(_array(vector, "force geometry vector")) != 3:
                raise MocapC3DPublicationError("force geometry vectors must have three components")


def _verify_skeleton(value: object, point_ids: set[str]) -> None:
    skeleton = _object(value, "skeleton", {"skeleton_id", "joint_ids", "bones"})
    _text(skeleton["skeleton_id"], "skeleton id")
    joints = set(_unique_texts(skeleton["joint_ids"], "skeleton joints"))
    if joints != point_ids:
        raise MocapC3DPublicationError("skeleton joints must equal published point ids")
    for item in _array(skeleton["bones"], "bones", allow_empty=True):
        bone = _object(item, "bone", {"parent", "child"})
        if bone["parent"] not in joints or bone["child"] not in joints:
            raise MocapC3DPublicationError("bone endpoints must reference skeleton joints")


def _verify_projection(
    value: object,
    canonical: dict[tuple[int, str], tuple[dict[str, object], list[str]]],
    cameras: list[str],
    point_rate: float,
    analog_rate: float,
    ratio: int,
) -> int | None:
    projection = _object(
        value,
        "C3D projection",
        {
            "state",
            "point_rate_hz",
            "point_units",
            "timestamp_semantics",
            "analog_rate_hz",
            "analog_samples_per_point_frame",
            "event_header_limit",
            "points",
            "independent_reader_qualification",
        },
    )
    if projection["state"] != "semantic_example_only" or projection["point_units"] != "mm":
        raise MocapC3DPublicationError("C3D projection must remain a millimetre semantic example")
    if projection["event_header_limit"] != STANDARD_EVENT_HEADER_LIMIT:
        raise MocapC3DPublicationError("C3D projection must preserve the 18-event header limit")
    verify_projection_rates(projection, point_rate, analog_rate, ratio)
    _verify_reader_unavailable(projection["independent_reader_qualification"])
    projected = _array(projection["points"], "projected points")
    if len(projected) != len(canonical):
        raise MocapC3DPublicationError("projection must cover every canonical point exactly once")
    seen: set[tuple[int, str]] = set()
    masks: set[int] = set()
    for item in projected:
        key, mask = _verify_projected_point(item, canonical, cameras)
        if key in seen:
            raise MocapC3DPublicationError("projected point keys must be unique")
        seen.add(key)
        if mask is not None:
            masks.add(mask)
    if seen != set(canonical):
        raise MocapC3DPublicationError("projection point keys differ from canonical points")
    return next(iter(masks)) if len(masks) == 1 else None


def _verify_reader_unavailable(value: object) -> None:
    reader = _object(
        value,
        "reader qualification",
        {"state", "readers", "corpus", "normalized_semantic_agreement"},
    )
    if reader["state"] != "unavailable" or reader["normalized_semantic_agreement"] is not None:
        raise MocapC3DPublicationError("independent reader qualification must remain unavailable")
    if reader["readers"] != [] or reader["corpus"] != []:
        raise MocapC3DPublicationError(
            "unqualified readers or corpus must not be named as evidence"
        )


def _verify_projected_point(
    value: object,
    canonical: dict[tuple[int, str], tuple[dict[str, object], list[str]]],
    cameras: list[str],
) -> tuple[tuple[int, str], int | None]:
    point = _object(
        value,
        "projected point",
        {"frame_index", "point_id", "xyz_mm", "residual", "contributor_mask"},
    )
    key = (
        _integer(point["frame_index"], "projected frame"),
        _text(point["point_id"], "projected id"),
    )
    if key not in canonical:
        raise MocapC3DPublicationError("projected point has no canonical source")
    source, contributors = canonical[key]
    expected_xyz = [
        _number(axis, "source coordinate") * 1000
        for axis in cast(list[object], source["xyz_m"])
    ]
    projected_xyz = [
        _number(axis, "projected coordinate")
        for axis in _array(point["xyz_mm"], "projected xyz")
    ]
    if len(projected_xyz) != 3 or any(
        not math.isclose(a, b)
        for a, b in zip(projected_xyz, expected_xyz, strict=True)
    ):
        raise MocapC3DPublicationError("projected coordinates must convert metres to millimetres")
    if not math.isclose(
        _number(point["residual"], "projected residual"),
        _number(source["residual"], "source residual"),
    ):
        raise MocapC3DPublicationError("projection must preserve residual semantics")
    mask = point["contributor_mask"]
    overflow = any(
        cameras.index(camera_id) >= STANDARD_CAMERA_CAPACITY
        for camera_id in contributors
    )
    if overflow:
        if mask is not None:
            raise MocapC3DPublicationError("overflow contributor mask must be unavailable")
        return key, None
    if isinstance(mask, bool) or not isinstance(mask, int) or not 0 <= mask <= STANDARD_MASK_MAX:
        raise MocapC3DPublicationError("contributor mask must be a seven-bit contributor mask")
    expected_mask = sum(1 << cameras.index(camera_id) for camera_id in contributors)
    if mask != expected_mask:
        raise MocapC3DPublicationError("contributor mask does not match canonical contributors")
    return key, mask


def verify_publication_package(
    source: Path | dict[str, Any], *, fixture_dir: Path | None = None
) -> PublicationSummary:
    """Verify one fixture and its digest-bound loss sidecar."""

    if isinstance(source, Path):
        data = cast(dict[str, Any], json.loads(source.read_text(encoding="utf-8")))
        fixture_dir = source.parent
    else:
        data = source
    if fixture_dir is None:
        raise MocapC3DPublicationError("fixture_dir is required for in-memory fixtures")
    fixture = _object(data, "fixture", TOP_LEVEL_KEYS)
    if fixture["schema"] != PUBLICATION_SCHEMA_ID or fixture["classification"] != "model_scenario":
        raise MocapC3DPublicationError("fixture schema/classification is unsupported")
    fixture_id = _text(fixture["fixture_id"], "fixture id")
    _verify_authority(fixture["authority"])
    dependencies = _verify_dependencies(fixture["dependencies"])
    verify_sources(fixture["source_traceability"])
    verify_coordinate_frame(fixture["coordinate_frame"])
    verify_provenance(fixture["provenance"])
    point_rate, analog_rate, ratio = _verify_timebase(fixture["timebase"])
    cameras = _unique_texts(fixture["cameras"], "cameras")
    canonical = _verify_frames(fixture["frames"], point_rate, set(cameras))
    frame_count = len(cast(list[object], fixture["frames"]))
    _verify_events(fixture["events"])
    sample_count = _verify_analog(fixture["analog"], frame_count, ratio)
    point_ids = {point_id for _, point_id in canonical}
    _verify_skeleton(fixture["skeleton"], point_ids)
    representable_mask = _verify_projection(
        fixture["c3d_projection"], canonical, cameras, point_rate, analog_rate, ratio
    )
    sidecar, overflow_count = load_and_verify_sidecar(
        fixture["loss_sidecar"], fixture_id, fixture_dir, canonical, cameras
    )
    loss_count = verify_losses(sidecar, overflow=overflow_count > 0)
    m1 = cast(dict[str, object], dependencies["tools_m1"])
    m9 = cast(dict[str, object], dependencies["tools_m9"])
    return PublicationSummary(
        fixture_id, len(cameras), frame_count, len(canonical), sample_count, loss_count,
        overflow_count, representable_mask, cast(str | None, m1["protected_revision"]),
        cast(str | None, m9["protected_revision"]),
    )


def main(argv: list[str] | None = None) -> int:
    """Verify paths from the command line."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixtures", nargs="+", type=Path)
    args = parser.parse_args(argv)
    try:
        for fixture in args.fixtures:
            summary = verify_publication_package(fixture)
            print(json.dumps(summary.__dict__, sort_keys=True))
    except (MocapC3DPublicationError, OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
