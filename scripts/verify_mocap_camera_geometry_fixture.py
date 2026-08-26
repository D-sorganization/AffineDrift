#!/usr/bin/env python3
"""Verify the pinned, synthetic camera-geometry teaching fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from scripts.mocap_camera_geometry_contract import (
    GEOMETRY_SCHEMA_ID,
    CameraGeometryFixtureError,
    CameraGeometrySummary,
    verify_camera_geometry_fixture,
)

__all__ = [
    "GEOMETRY_SCHEMA_ID",
    "CameraGeometryFixtureError",
    "CameraGeometrySummary",
    "verify_camera_geometry_fixture",
    "verify_fixture_file",
]


def verify_fixture_file(path: Path) -> CameraGeometrySummary:
    """Verify a fixture's sidecar SHA-256 pin before validating its content."""

    try:
        data = path.read_bytes()
        lock_path = path.with_suffix(path.suffix + ".sha256")
        lock_parts = lock_path.read_text(encoding="utf-8").strip().split()
    except OSError as error:
        raise CameraGeometryFixtureError(f"cannot read fixture or lock: {error}") from error
    if len(lock_parts) != 2 or lock_parts[1] != path.name:
        raise CameraGeometryFixtureError("fixture SHA-256 lock has invalid syntax")
    if hashlib.sha256(data).hexdigest() != lock_parts[0]:
        raise CameraGeometryFixtureError("fixture SHA-256 lock mismatch")
    try:
        value = json.loads(data)
    except json.JSONDecodeError as error:
        raise CameraGeometryFixtureError(f"fixture JSON is invalid: {error}") from error
    return verify_camera_geometry_fixture(value)


def main(argv: list[str] | None = None) -> int:
    """Run the fixture verifier CLI."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args(argv)
    try:
        summary = verify_fixture_file(args.fixture)
    except CameraGeometryFixtureError as error:
        sys.stderr.write(f"CAMERA GEOMETRY FIXTURE FAILED: {error}\n")
        return 1
    sys.stdout.write(
        "CAMERA GEOMETRY FIXTURE PASSED: "
        f"{summary.camera_count} cameras, {summary.observation_count} observations, "
        f"{summary.available_dependency_count}/{summary.dependency_count} dependencies available\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
