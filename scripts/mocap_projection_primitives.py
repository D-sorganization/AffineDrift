"""Fail-closed field primitives shared by the markerless-mocap projection verifier."""

from __future__ import annotations

import re
from typing import cast

REVISION = re.compile(r"[0-9a-f]{40}")
DIGEST = re.compile(r"[0-9a-f]{64}")


class MocapProjectionError(RuntimeError):
    """Raised when public markerless-mocap evidence violates its contract."""


def _object(value: object, label: str, keys: set[str]) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise MocapProjectionError(f"{label} must be an object")
    result = cast(dict[str, object], value)
    actual = set(result)
    if actual != keys:
        raise MocapProjectionError(
            f"{label} fields differ: missing={sorted(keys - actual)}, extra={sorted(actual - keys)}"
        )
    return result


def _array(value: object, label: str) -> list[object]:
    if not isinstance(value, list) or not value:
        raise MocapProjectionError(f"{label} must be a non-empty array")
    return cast(list[object], value)


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MocapProjectionError(f"{label} must be a non-empty string")
    return value


def _boolean(value: object, label: str) -> bool:
    if type(value) is not bool:
        raise MocapProjectionError(f"{label} must be boolean")
    return value


def _integer(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise MocapProjectionError(f"{label} must be a non-negative integer")
    return value


def _matches(value: object, label: str, pattern: re.Pattern[str]) -> str:
    text = _text(value, label)
    if pattern.fullmatch(text) is None:
        raise MocapProjectionError(f"{label} is invalid")
    return text
