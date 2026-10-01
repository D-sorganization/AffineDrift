"""Independent interpretation checks for the annotated launch-monitor references."""

from math import asin, degrees
from pathlib import Path
from statistics import median

import pytest

APPENDIX = (
    Path(__file__).resolve().parents[1]
    / "articles/Launch_Monitor_Technology_Review/sections/appendix-a-references.tex"
)


def test_median_centered_band_does_not_certify_zero_error_accuracy() -> None:
    # Synthetic measurement errors in degrees; no device performance is implied.
    errors = [2.5, 3.0, 3.5]
    bias = median(errors)
    assert sum(abs(error - bias) <= 1.0 for error in errors) == 3
    assert sum(abs(error) <= 1.0 for error in errors) == 0


def test_face_angle_inversion_has_twelve_percent_not_double_sensitivity() -> None:
    lower_weight_sensitivity = 1.0 / 0.76
    higher_weight_sensitivity = 1.0 / 0.85
    ratio = lower_weight_sensitivity / higher_weight_sensitivity
    assert lower_weight_sensitivity == pytest.approx(1.3157894736842106)
    assert higher_weight_sensitivity == pytest.approx(1.1764705882352942)
    assert (ratio - 1.0) * 100.0 == pytest.approx(11.8421052631579)
    assert ratio < 1.2


def test_bulge_angle_requires_local_curvature() -> None:
    # Ideal circular face sections: x is lateral displacement, not arc length.
    lateral_offset_m = 0.0127
    small_radius_angle = degrees(asin(lateral_offset_m / 0.25))
    large_radius_angle = degrees(asin(lateral_offset_m / 0.5))
    assert small_radius_angle > 2.0 > large_radius_angle


@pytest.mark.parametrize(
    "boundary",
    [
        "median difference",
        "TrackMan Pro IIIe",
        "does not establish permanent absence",
        "local face curvature",
        "do not establish the architecture shipped",
    ],
)
def test_reference_library_declares_source_scope(boundary: str) -> None:
    assert boundary in APPENDIX.read_text(encoding="utf-8")
