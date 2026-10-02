"""Manufactured checks for model comparison; not provider or human validation."""

import re
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import binomtest


@pytest.mark.parametrize("extension,expected", [(0.01, 1.0), (-0.01, -1.0)])
def test_equal_reduced_state_does_not_determine_acceleration(
    extension: float, expected: float
) -> None:
    """An omitted spring extension changes the observed mass's acceleration."""
    mass = np.diag([1.0, 2.0])
    stiffness = 100.0 * np.array([[1.0, -1.0], [-1.0, 1.0]])
    position = np.array([0.0, extension])
    velocity = np.zeros(2)
    acceleration = np.linalg.solve(mass, -stiffness @ position)

    assert (position[0], velocity[0]) == (0.0, 0.0)
    assert acceleration[0] == pytest.approx(expected)
    assert acceleration[1] == pytest.approx(-expected / 2.0)
    assert np.sum(mass @ acceleration) == pytest.approx(0.0)


def test_resultant_wrench_does_not_capture_deformation_power() -> None:
    """Opposed axial forces can stretch a body with zero total force and moment."""
    position = np.array([[0.1, 0.0, 0.0], [-0.1, 0.0, 0.0]])
    force = np.array([[10.0, 0.0, 0.0], [-10.0, 0.0, 0.0]])
    velocity = np.array([[0.2, 0.0, 0.0], [-0.2, 0.0, 0.0]])
    resultant = np.sum(force, axis=0)
    moment = np.sum(np.cross(position, force), axis=0)
    np.testing.assert_allclose(resultant, np.zeros(3))
    np.testing.assert_allclose(moment, np.zeros(3))
    assert np.sum(force * velocity) == pytest.approx(4.0)
    assert np.dot(resultant, [0.3, -0.4, 0.1]) + np.dot(moment, [0.5, 0.0, -0.2]) == pytest.approx(
        0.0
    )


def test_ensemble_frequency_depends_on_declared_weighting() -> None:
    """Scenario weighting changes the fraction without changing any outcome."""
    signs = np.array([1, 1, 1, -1])
    supported = signs > 0
    assert np.mean(supported) == pytest.approx(0.75)
    assert np.average(supported, weights=[0.1, 0.1, 0.1, 0.7]) == pytest.approx(0.30)


def test_ninety_five_of_one_hundred_is_not_a_probability_guarantee() -> None:
    """Independent binomial sampling still leaves uncertainty about its probability."""
    interval = binomtest(95, 100).proportion_ci(confidence_level=0.95, method="wilson")
    assert interval.low == pytest.approx(0.888249530768, abs=1e-10)
    assert interval.high == pytest.approx(0.978456320846, abs=1e-10)
    assert interval.low < 0.95


def test_model_ladder_provider_links_are_revision_bound() -> None:
    """Provider assertions must retain their inspected immutable source revision."""
    text = Path("articles/proximal_distal_companion/chapters/ch19_model_ladder.qmd").read_text(
        encoding="utf-8"
    )
    links = re.findall(r"https://github\.com/D-sorganization/UpstreamDrift/[^)\s]+", text)
    assert len(links) == 3
    assert all("/blob/85cce4d3307bb7ad3953d9fc6e583e370803515c/" in link for link in links)


def test_model_ladder_figure_matches_its_model_comparison_subject() -> None:
    """A model-family figure must not silently substitute an evidence hierarchy."""
    text = Path(
        "articles/figures/proximal_distal_companion/fig_companion_evidence_ladder.svg"
    ).read_text(encoding="utf-8")
    assert "Shared Comparison Contract" in text
    assert "Biological Allocation" in text
    assert "Replicated" not in text
