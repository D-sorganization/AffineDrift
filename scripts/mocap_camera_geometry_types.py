"""Shared public types for the camera-geometry teaching contract."""

from __future__ import annotations

from dataclasses import dataclass


class CameraGeometryFixtureError(RuntimeError):
    """Raised when camera-geometry pedagogy violates its fail-closed contract."""


@dataclass(frozen=True)
class CameraGeometrySummary:
    """Deterministic evidence from one accepted synthetic fixture."""

    camera_count: int
    point_count: int
    observation_count: int
    dependency_count: int
    available_dependency_count: int
    calibration_authority_available: bool
    maximum_projection_error_px: float
    distortion_probe_pixel: tuple[float, float]
    stereo_depth_m: float
    stereo_depth_sigma_m: float
