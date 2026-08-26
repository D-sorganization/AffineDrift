"""Design-by-contract value validators for camera-geometry fixtures."""

from __future__ import annotations

import math
from typing import cast

from scripts.mocap_camera_geometry_types import CameraGeometryFixtureError


def object_with_keys(value: object, label: str, keys: set[str]) -> dict[str, object]:
    """Return an object only when its fields exactly match the contract."""

    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise CameraGeometryFixtureError(f"{label} must be an object")
    result = cast(dict[str, object], value)
    actual = set(result)
    if actual != keys:
        raise CameraGeometryFixtureError(
            f"{label} fields differ: missing={sorted(keys - actual)}, "
            f"extra={sorted(actual - keys)}"
        )
    return result


def nonempty_array(value: object, label: str, length: int | None = None) -> list[object]:
    """Return a non-empty array with an optional exact length."""

    if not isinstance(value, list) or not value:
        raise CameraGeometryFixtureError(f"{label} must be a non-empty array")
    result = cast(list[object], value)
    if length is not None and len(result) != length:
        raise CameraGeometryFixtureError(f"{label} must contain {length} values")
    return result


def nonempty_text(value: object, label: str) -> str:
    """Return a non-empty string."""

    if not isinstance(value, str) or not value.strip():
        raise CameraGeometryFixtureError(f"{label} must be a non-empty string")
    return value


def finite_number(value: object, label: str, *, positive: bool = False) -> float:
    """Return a finite number, optionally constrained to be positive."""

    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise CameraGeometryFixtureError(f"{label} must be finite")
    result = float(value)
    if positive and result <= 0.0:
        raise CameraGeometryFixtureError(f"{label} must be positive")
    return result


def numeric_vector(value: object, label: str, length: int) -> tuple[float, ...]:
    """Return a fixed-length finite numeric vector."""

    return tuple(
        finite_number(item, f"{label} item") for item in nonempty_array(value, label, length)
    )


def matrix3(value: object, label: str) -> tuple[tuple[float, ...], ...]:
    """Return a finite three-by-three numeric matrix."""

    rows = nonempty_array(value, label, 3)
    return tuple(numeric_vector(row, f"{label} row", 3) for row in rows)
