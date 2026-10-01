"""Finite-ensemble counterexamples and archived Chapter 23 figure checks."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "data/illustrations/uncertainty_control_study.npz"


def test_tradeoff_figure_uses_all_eight_declared_candidates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from scripts import make_proximal_distal_companion_figures as figures

    captured = []
    monkeypatch.setattr(figures, "_save", lambda figure, stem: captured.append(figure))
    figures.make_speed_tradeoffs()
    try:
        points = np.concatenate([item.get_offsets() for item in captured[0].axes[0].collections])
        with np.load(ARCHIVE) as archive:
            held = archive["held_out_outputs"]
        expected = np.column_stack(
            (held[:, :, 1].mean(axis=1), np.quantile(held[:, :, 0], 0.1, axis=1))
        )
        assert points.shape == (8, 2)
        np.testing.assert_allclose(points, expected)
    finally:
        plt.close("all")


def test_six_case_tail_uses_two_extreme_order_statistics() -> None:
    with np.load(ARCHIVE) as archive:
        speed = archive["held_out_outputs"][:, :, 0]
    ordered = np.sort(speed, axis=1)
    np.testing.assert_allclose(np.quantile(speed, 0.1, axis=1), ordered[:, :2].mean(axis=1))
    assert np.quantile(speed[7], 0.1) == pytest.approx(4.706, abs=0.0005)
    assert np.quantile(speed[2], 0.1) == pytest.approx(4.417, abs=0.0005)


def test_candidate_nondominance_does_not_exclude_a_better_untested_policy() -> None:
    losses = np.array([[0, 2], [2, 0], [1, 1]])
    for index, row in enumerate(losses):
        others = np.delete(losses, index, axis=0)
        assert not np.any(np.all(others <= row, axis=1))
    untested = np.array([-1, -1])
    assert np.all(untested < losses)


def test_paired_difference_quantile_is_not_difference_of_quantiles() -> None:
    with np.load(ARCHIVE) as archive:
        speed = archive["held_out_outputs"][:, :, 0]
    paired = np.quantile(speed[7] - speed[2], 0.1)
    difference = np.quantile(speed[7], 0.1) - np.quantile(speed[2], 0.1)
    assert paired == pytest.approx(0.2711425032451831)
    assert difference != pytest.approx(paired)


def test_cvar_at_an_atom_includes_fraction_of_threshold_mass() -> None:
    losses = np.array([0.0, 0.0, 0.0, 10.0])
    # The convex piecewise-linear objective reaches a minimum at a loss breakpoint.
    breakpoints = np.unique(losses)
    objective = breakpoints + np.maximum(losses[:, None] - breakpoints, 0).mean(axis=0) / 0.5
    assert objective.min() == 5.0
    assert losses[losses > 0].mean() == 10.0
    # For eta<0 the objective is5-eta; for eta>10 it iseta. Neither improves5.
    assert 0.5 * (0 + 10) == objective.min()


def test_marginal_success_does_not_imply_the_same_joint_success() -> None:
    first = np.arange(10) != 0
    second = np.arange(10) != 1
    assert first.mean() == second.mean() == 0.9
    assert (first & second).mean() == 0.8


def test_dropping_a_failure_changes_tail_and_denominator() -> None:
    losses = np.array([1.0, 2.0, 2.0, 3.0, 100.0])
    retained = losses[:-1]
    assert np.quantile(losses, 0.8) > np.quantile(retained, 0.8)
    assert np.mean(losses > 50) == 0.2
    assert np.mean(retained > 50) == 0
