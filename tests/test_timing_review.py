"""Manufactured timing identities and publication contracts, not human validation."""

import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure

from scripts import make_proximal_distal_companion_figures as figures


@pytest.mark.integration
def test_timing_provider_links_are_revision_bound() -> None:
    source = Path("articles/proximal_distal_companion/chapters/ch22_timing_state_question.qmd")
    links = re.findall(
        r"https://github\.com/D-sorganization/UpstreamDrift/[^)\s]+",
        source.read_text(encoding="utf-8"),
    )
    assert links
    assert all("/blob/85cce4d3307bb7ad3953d9fc6e583e370803515c/" in link for link in links)


@pytest.mark.integration
def test_clock_figure_declares_schematic_and_exact_scalar_events(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[Figure] = []
    monkeypatch.setattr(figures, "_save", lambda figure, _stem: captured.append(figure))
    figures.make_clock_state()
    figure = captured[0]
    try:
        labels = [text.get_text() for text in figure.texts]
        labels.extend(axis.get_title() for axis in figure.axes)
        wording = " ".join(labels).lower()
        assert "schematic" in wording and "one coordinate" in wording
        markers = figure.axes[1].collections
        assert len(markers) == 3
        coordinates = np.vstack([marker.get_offsets() for marker in markers])
        np.testing.assert_allclose(coordinates[:, 1], 0.6, atol=1e-12, rtol=0)
        assert np.all(np.diff(coordinates[:, 0]) > 0)
    finally:
        plt.close(figure)


def test_first_order_time_constant_differs_from_rise_time() -> None:
    time_constant = 0.035  # Seconds; not the 10-90% rise time.
    assert 1 - np.exp(-1) == pytest.approx(0.6321205588285577)
    crossing_times = -time_constant * np.log([0.9, 0.1])
    np.testing.assert_allclose(1 - np.exp(-crossing_times / time_constant), [0.1, 0.9])
    rise_time = np.diff(crossing_times).item()
    assert rise_time == pytest.approx(time_constant * np.log(9))
    assert rise_time == pytest.approx(0.07690286, abs=1e-8)


def test_filtered_torque_reversal_preserves_initial_load() -> None:
    time_constant = 0.035
    zero_time = time_constant * np.log(4 / 3)
    assert zero_time == pytest.approx(0.01006887, abs=1e-8)
    times = np.array([0, zero_time, 20 * time_constant])
    torques = 15 - 20 * np.exp(-times / time_constant)
    np.testing.assert_allclose(torques[:2], [-5, 0], atol=1e-12)
    assert torques[2] == pytest.approx(15, abs=1e-7)


def test_event_timing_error_depends_on_crossing_rate() -> None:
    angle_error = 0.002  # Radians; positive perturbation of the event function.
    rates = np.array([4.0, 0.04])  # rad/s near a nominal event at 0.2 s.
    nominal_time = 0.2
    perturbed_times = nominal_time - angle_error / rates
    np.testing.assert_allclose(perturbed_times - nominal_time, [-0.0005, -0.05])
    residuals = rates * (perturbed_times - nominal_time) + angle_error
    np.testing.assert_allclose(residuals, 0, atol=1e-14)


def test_grazing_event_can_disappear_or_split() -> None:
    # Dimensionless illustration g(s)=(s-0.2)^2+epsilon.
    positive_roots = np.roots([1, -0.4, 0.05])
    assert np.all(np.abs(positive_roots.imag) > 0.09)
    negative_roots = np.sort(np.roots([1, -0.4, 0.03]))
    np.testing.assert_allclose(negative_roots, [0.1, 0.3], atol=1e-14)
    np.testing.assert_allclose((negative_roots - 0.2) ** 2 - 0.01, 0, atol=1e-14)
    assert (0.2 - 0.2) ** 2 == 0  # Unperturbed double root.
    assert 2 * (0.2 - 0.2) == 0  # No nonzero-slope timing linearization here.


def test_normalized_phase_power_area_requires_duration_for_work() -> None:
    phase = np.linspace(0, 1, 101)
    power = 10 + 5 * phase  # Watts at each phase, not joules per phase.
    phase_area = np.trapezoid(power, phase)
    durations = np.array([0.2, 0.4])
    assert phase_area == pytest.approx(12.5)
    np.testing.assert_allclose(durations * phase_area, [2.5, 5.0])
    assert np.all(durations * phase_area != phase_area)
