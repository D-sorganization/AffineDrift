"""Independent camera-mode and uncertainty checks for the public article."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles/markerless-mocap-camera-selection.qmd"
REGISTRY = ROOT / "data/markerless_mocap/camera_evidence_registry_v1.json"


@pytest.mark.parametrize(
    ("width", "height", "rate", "expected_gbps"),
    [
        (1440, 1080, 226, 2.8118016),
        (1920, 1200, 164, 3.022848),
        (1632, 1248, 225, 3.6661248),
        (1440, 1080, 166.3, 2.06903808),
    ],
)
def test_eight_bit_mode_payloads(
    width: int, height: int, rate: float, expected_gbps: float
) -> None:
    """Use image byte count rather than the interface's nominal line rate."""
    assert width * height * rate * 8 / 1e9 == pytest.approx(expected_gbps)


def test_lucid_old_mode_exceeds_link_even_without_overhead() -> None:
    old_payload = 1440 * 1080 * 226 * 8
    corrected_payload = 1440 * 1080 * 166.3 * 8
    assert old_payload > 2.5e9 > corrected_payload
    assert 8 * corrected_payload / 1e9 == pytest.approx(16.55230464)


def test_pixel_storage_is_distinct_from_adc_depth() -> None:
    pixels = 1440 * 1080
    packed_12 = pixels * 12 // 8
    container_16 = pixels * 2
    rgb8 = pixels * 3
    assert container_16 / packed_12 == pytest.approx(4 / 3)
    assert rgb8 / pixels == 3


def test_sampling_exposure_and_skew_have_different_time_scales() -> None:
    speed_px_s = 10_000
    assert speed_px_s / 200 == 50
    assert speed_px_s * 0.0001 == 1
    assert speed_px_s * 0.00005 == 0.5
    assert 40 * 15e-6 == pytest.approx(0.0006)


def test_rectified_depth_derivative_matches_finite_difference() -> None:
    focal_px, baseline_m, depth_m = 1000.0, 1.0, 4.0
    disparity = focal_px * baseline_m / depth_m
    epsilon = 1e-3
    derivative = (
        focal_px * baseline_m / (disparity + epsilon)
        - focal_px * baseline_m / (disparity - epsilon)
    ) / (2 * epsilon)
    assert derivative == pytest.approx(-(depth_m**2) / (focal_px * baseline_m))
    disparity_sigma = np.sqrt(2) * 0.5
    assert abs(derivative) * disparity_sigma == pytest.approx(0.0113137085)
    assert focal_px * baseline_m / (disparity + 10) - depth_m == pytest.approx(-0.1538461538)


def test_common_pixel_error_cancels_in_rectified_disparity() -> None:
    difference = np.array([1.0, -1.0])
    independent = 0.25 * np.eye(2)
    common = 0.25 * np.ones((2, 2))
    assert difference @ independent @ difference == pytest.approx(0.5)
    assert difference @ common @ difference == pytest.approx(0)


def test_derivative_noise_from_linear_stencils() -> None:
    dt, sigma = 1 / 200, 0.001
    velocity = np.array([-1, 0, 1]) / (2 * dt)
    acceleration = np.array([1, -2, 1]) / dt**2
    assert np.linalg.norm(velocity) * sigma == pytest.approx(0.1414213562)
    assert np.linalg.norm(acceleration) * sigma == pytest.approx(97.97958971)


@pytest.mark.parametrize(
    ("claim_id", "expected"),
    [
        ("lucid-frame-rate", 166.3),
        ("allied-frame-rate", 225),
        ("allied-resolution", "1632x1248"),
        ("basler-frame-rate", 164),
    ],
)
def test_registry_matches_reviewed_manufacturer_modes(claim_id: str, expected: str | float) -> None:
    claims = json.loads(REGISTRY.read_text(encoding="utf-8"))["claims"]
    assert next(c for c in claims if c["id"] == claim_id)["value"] == expected


def test_registry_does_not_transfer_sensor_or_lens_from_another_model() -> None:
    claims = {c["id"]: c for c in json.loads(REGISTRY.read_text(encoding="utf-8"))["claims"]}
    assert "IMX273" in claims["lucid-shutter"]["value"]
    assert "fisheye" not in claims["zed-lens"]["value"].lower()
    assert "Mono8" in claims["allied-frame-rate"]["limitations"]


def test_article_states_measurement_hypotheses_and_downstream_limits() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    for phrase in (
        "rectified stereo",
        "exposure midpoint",
        "cross-correlations",
        "calibration uncertainty",
        "inverse dynamics",
    ):
        assert phrase in text
    assert "required for full eight-camera rigs" not in text
    assert "maintaining full 226" not in text
