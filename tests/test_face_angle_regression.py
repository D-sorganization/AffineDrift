"""Check directional geometry without inventing a universal shot-curvature multiplier.

The former #2302 regression asserted unsupported 13--20 and 17--24 yard/degree
ranges. Issue #4307 separates an initial-direction calculation from the full
contact and aerodynamic response needed to predict final lateral error.
"""

import math
from pathlib import Path

import pytest


def test_face_gain_matches_ray_intersection_derivative() -> None:
    """Intersect perturbed launch rays with the plane 250 yards downrange."""
    downrange, face_weight, step_degrees = 250.0, 0.76, 1e-4
    launch = math.radians(face_weight * step_degrees)
    forward, lateral = math.cos(launch), math.sin(launch)
    plus = (downrange / forward) * lateral
    minus = (downrange / forward) * -lateral
    finite_gain = (plus - minus) / (2 * step_degrees)
    assert finite_gain == pytest.approx(downrange * face_weight * math.pi / 180)
    assert finite_gain == pytest.approx(3.316, abs=0.001)


def test_one_degree_launch_is_distinct_from_one_degree_face() -> None:
    """A local face weight changes the launch azimuth before flight begins."""
    downrange, face_weight = 250.0, 0.76
    launch_offset = downrange * math.tan(math.radians(1.0))
    face_offset = downrange * math.tan(math.radians(face_weight))
    assert launch_offset == pytest.approx(4.36377, abs=0.00001)
    assert face_offset < launch_offset


@pytest.mark.parametrize("directory,suffix", [("quarto", "qmd"), ("chapters", "tex")])
def test_ch31_rejects_unqualified_directional_sensitivity(directory: str, suffix: str) -> None:
    """Both editions retain the model boundary instead of an unsupported range."""
    root = Path(__file__).resolve().parents[1] / "articles/The_Physics_of_Golf"
    source = (root / directory / f"ch31_swing_plane_launch.{suffix}").read_text(encoding="utf-8")
    assert "60--70 yards per degree" not in source
    assert "65 yards per degree" not in source
    assert "13--20" not in source
    assert "Neither result includes curvature" in source
    assert "3.316" in source
