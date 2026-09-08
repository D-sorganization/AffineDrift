"""Publication regressions for the impact/acoustics review (#4254)."""

from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles/technology-heavy-hit-impact-coupling.qmd"


@pytest.mark.content_lint
def test_review_retires_universal_claims_and_separates_impulse_from_sound() -> None:
    source = ARTICLE.read_text(encoding="utf-8")
    assert "Physics proves this is an illusion" not in source
    assert "for all physiological human-club configurations" not in source
    assert "sec-impact-prestress" in source
    assert "sec-impact-timescales" in source
    assert "mcnally2018shaftimpact" in source
    assert "_includes/impact-acoustics.qmd" in source


@pytest.mark.content_lint
def test_acoustic_treatment_has_radiation_and_causal_controls() -> None:
    source = (ROOT / "articles/_includes/impact-acoustics.qmd").read_text(encoding="utf-8")
    assert "sec-impact-acoustic-radiation" in source
    assert "level-matched" in source
    assert "matched-state" in source
    assert "guitar" in source


def test_longitudinal_speed_arithmetic_does_not_support_blanket_isolation() -> None:
    speeds = np.sqrt(np.array([90e9 / 1600, 150e9 / 1500]))
    np.testing.assert_allclose(speeds, [7500, 10000])
    np.testing.assert_allclose(2 * 1.15 / speeds * 1e6, [306.66666667, 230])
    assert np.all(2 * 1.15 / speeds < 450e-6)


def test_rigid_arm_example_has_no_second_lever_arm_division() -> None:
    added_mass = (4.5 * 0.65**2 / 3) / 1.8**2
    assert added_mass == pytest.approx(0.19560185185)


def test_directional_mass_is_not_projection_of_inverse_mobility() -> None:
    mobility = np.array([[5.0, 2.0, 0], [2.0, 6.0, 0], [0, 0, 7.0]])
    normal = np.array([1.0, 0, 0])
    free_tangent_mass = 1 / (normal @ mobility @ normal)
    constrained_tangent_mass = normal @ np.linalg.inv(mobility) @ normal
    assert free_tangent_mass == pytest.approx(0.2)
    assert constrained_tangent_mass > free_tangent_mass
