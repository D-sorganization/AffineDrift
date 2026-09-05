"""Independent geometric counterexamples for publication issue #4150."""

from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


def direction(azimuth: float, elevation: float) -> np.ndarray:
    """Return a unit vector in forward/up/right coordinates, angles in radians."""
    return np.array(
        [
            np.cos(elevation) * np.cos(azimuth),
            np.sin(elevation),
            np.cos(elevation) * np.sin(azimuth),
        ]
    )


def test_spin_loft_dot_product_retains_separate_elevations() -> None:
    face, path, loft, attack = np.deg2rad([30, 0, 40, 20])
    normal = direction(face, loft)
    velocity = direction(path, attack)
    exact = np.sin(loft) * np.sin(attack) + np.cos(loft) * np.cos(attack) * np.cos(face - path)
    np.testing.assert_allclose(normal @ velocity, exact)
    assert abs(exact - np.cos(face - path) * np.cos(loft - attack)) > 0.02


def test_normal_impulse_speed_has_one_cosine() -> None:
    obliqueness = np.deg2rad(30)
    velocity = direction(0, 0)
    normal = direction(0, obliqueness)
    ball = 1.488 * (velocity @ normal) * normal
    np.testing.assert_allclose(np.linalg.norm(ball), 1.488 * np.cos(obliqueness))
    np.testing.assert_allclose(ball @ velocity, 1.488 * np.cos(obliqueness) ** 2)


@pytest.mark.content_lint
def test_impact_reference_removes_false_exact_geometry_and_cor_classification() -> None:
    source = (ROOT / "articles/impact-mechanics-and-ball-flight.qmd").read_text(encoding="utf-8")
    assert "is the **apparent** COR" not in source
    assert "Whatever its published provenance, this is evidently the model in use" not in source
    assert r"\sin\lambda\sin\alpha" in source
