"""Small Design-by-Contract primitives for mocap publication verification."""

from __future__ import annotations

import math
from typing import cast

PUBLICATION_SCHEMA_ID = "affinedrift/mocap-c3d-publication-compatibility/v1"
LOSS_SIDECAR_SCHEMA_ID = "affinedrift/mocap-c3d-loss-sidecar/v1"
STANDARD_CAMERA_CAPACITY = 7
STANDARD_MASK_MAX = (1 << STANDARD_CAMERA_CAPACITY) - 1
STANDARD_EVENT_HEADER_LIMIT = 18


class MocapC3DPublicationError(RuntimeError):
    """Raised when a publication package violates its fail-closed contract."""


def object_with_keys(value: object, label: str, keys: set[str]) -> dict[str, object]:
    """Require an object with exactly the declared fields."""

    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise MocapC3DPublicationError(f"{label} must be an object")
    result = cast(dict[str, object], value)
    actual = set(result)
    if actual != keys:
        raise MocapC3DPublicationError(
            f"{label} fields differ: missing={sorted(keys - actual)}, "
            f"extra={sorted(actual - keys)}"
        )
    return result


def array(value: object, label: str, *, allow_empty: bool = False) -> list[object]:
    """Require an array, optionally permitting an empty one."""

    if not isinstance(value, list) or (not value and not allow_empty):
        raise MocapC3DPublicationError(f"{label} must be an array")
    return cast(list[object], value)


def text(value: object, label: str) -> str:
    """Require nonblank text."""

    if not isinstance(value, str) or not value.strip():
        raise MocapC3DPublicationError(f"{label} must be a non-empty string")
    return value


def number(value: object, label: str) -> float:
    """Require a finite real number while rejecting booleans."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MocapC3DPublicationError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise MocapC3DPublicationError(f"{label} must be finite")
    return result


def integer(value: object, label: str, *, minimum: int = 0) -> int:
    """Require a bounded integer while rejecting booleans."""

    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise MocapC3DPublicationError(f"{label} must be an integer >= {minimum}")
    return value


def unique_texts(value: object, label: str) -> list[str]:
    """Require a nonempty ordered set of text identifiers."""

    texts = [text(item, f"{label} item") for item in array(value, label)]
    if len(texts) != len(set(texts)):
        raise MocapC3DPublicationError(f"{label} must contain unique values")
    return texts
