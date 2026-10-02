"""Manufactured kinematic examples; no participant or causal validation."""

import importlib
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure

from scripts import make_proximal_distal_companion_figures as base_figures


@pytest.mark.integration
def test_sequence_provider_links_are_revision_bound() -> None:
    text = Path(
        "articles/proximal_distal_companion/chapters/ch08_summation_of_speed.qmd"
    ).read_text(encoding="utf-8")
    links = re.findall(r"https://github\.com/D-sorganization/UpstreamDrift/[^)\s]+", text)
    assert links
    assert all("/blob/85cce4d3307bb7ad3953d9fc6e583e370803515c/" in link for link in links)


@pytest.mark.integration
def test_sequence_figure_declares_schematic_scale_without_coupling_measure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "make_proximal_distal_companion_figures", base_figures)
    figures = importlib.import_module("scripts.make_proximal_distal_companion_expanded_figures")
    captured: list[Figure] = []
    monkeypatch.setattr(figures, "_save", lambda figure, _stem: captured.append(figure))
    figures.make_sequence_overlap()
    figure = captured[0]
    try:
        axis = figure.axes[0]
        assert "Schematic" in axis.get_title()
        assert "Normalized" in axis.get_ylabel()
        assert not axis.patches  # No shaded interval presented as measured coupling.
        assert len(axis.lines) == 4
        for line in axis.lines:
            assert np.max(line.get_ydata()) == pytest.approx(1.0, abs=1e-3)
    finally:
        plt.close(figure)


@pytest.mark.parametrize("relative_rate", [3.0, -5.0])
def test_absolute_rotation_matches_endpoint_finite_difference(relative_rate: float) -> None:
    def position(time: float) -> np.ndarray:
        arm = 2.0 * time
        club = np.pi / 2.0 + (2.0 + relative_rate) * time
        return np.array([np.cos(arm) + np.cos(club), np.sin(arm) + np.sin(club)])

    step = 1e-6
    observed = (position(step) - position(-step)) / (2.0 * step)
    transport = np.array([0.0, 2.0, 0.0])
    radius = np.array([0.0, 1.0, 0.0])
    absolute = transport + np.cross([0.0, 0.0, 2.0 + relative_rate], radius)
    incorrect = transport + np.cross([0.0, 0.0, relative_rate], radius)
    np.testing.assert_allclose(observed, absolute[:2], atol=1e-9)
    assert not np.allclose(observed, incorrect[:2])


def test_signed_speed_partition_has_negative_term_and_energy_cross_term() -> None:
    # Jacobian-column contributions for q=(0, pi/2), qdot=(2, -5).
    terms = np.array([[-2.0, 2.0], [5.0, 0.0]])
    velocity = terms.sum(axis=0)
    speed = np.linalg.norm(velocity)
    contributions = terms @ (velocity / speed)
    assert contributions[0] == pytest.approx(-2.0 / np.sqrt(13.0))
    assert contributions[1] == pytest.approx(15.0 / np.sqrt(13.0))
    assert contributions.sum() == pytest.approx(speed)
    # Unit point mass: assigning energy from the two squared speeds misses the cross term.
    energy = 0.5 * np.dot(velocity, velocity)
    separate_squares = 0.5 * np.sum(terms * terms)
    assert energy == pytest.approx(6.5)
    assert separate_squares == pytest.approx(16.5)
    assert energy == pytest.approx(separate_squares + np.dot(terms[0], terms[1]))


def test_angular_speed_maximum_has_nonzero_angular_acceleration() -> None:
    def omega(time: float) -> np.ndarray:
        return (1.0 - time**2) * np.array([np.cos(time), np.sin(time), 0.0])

    step = 1e-6
    alpha = (omega(step) - omega(-step)) / (2.0 * step)
    np.testing.assert_allclose(alpha, [0.0, 1.0, 0.0], atol=1e-10)
    assert np.dot(omega(0.0), alpha) == pytest.approx(0.0)
    assert np.linalg.norm(omega(-0.1)) < np.linalg.norm(omega(0.0))
    assert np.linalg.norm(omega(0.1)) < np.linalg.norm(omega(0.0))
