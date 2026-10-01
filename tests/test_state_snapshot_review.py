"""Independent state/observation counterexamples for companion Chapter 3."""

import matplotlib.pyplot as plt
import numpy as np
import pytest

from src.affine_control.dynamics import (
    double_pendulum_coriolis,
    double_pendulum_mass_matrix,
)


def test_state_figure_conditions_prediction_on_model_and_future_inputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from scripts import make_proximal_distal_companion_figures as figures

    captured = []
    monkeypatch.setattr(figures, "_save", lambda figure, stem: captured.append(figure))
    figures.make_state_map()
    try:
        labels = " ".join(text.get_text() for text in captured[0].axes[0].texts)
        assert "Model and Parameters" in labels
        assert "Future Inputs" in labels
        assert "Internal Variables" in labels
    finally:
        plt.close("all")


def test_global_velocity_reversal_preserves_quadratic_bias_not_momentum() -> None:
    q = np.array([0.8, -0.2])
    velocity = np.array([2.0, -3.0])
    mass = double_pendulum_mass_matrix(q, 1.0, 2.0, 1.2, 0.8)
    forward = double_pendulum_coriolis(q, velocity, 2.0, 1.2, 0.8) @ velocity
    reverse = double_pendulum_coriolis(q, -velocity, 2.0, 1.2, 0.8) @ -velocity
    coefficient = 0.5 * 2.0 * 1.2 * 0.8 * np.sin(1.0)
    np.testing.assert_allclose(forward, coefficient * np.array([9.0, -4.0]))
    np.testing.assert_allclose(reverse, forward)
    np.testing.assert_allclose(mass @ -velocity, -(mass @ velocity))
    torque = np.array([4.0, 1.0])
    assert torque @ velocity == 5.0 and torque @ -velocity == -5.0
    gravity = np.array([3.0, 2.0])
    acceleration = np.linalg.solve(mass, torque - forward - gravity)
    np.testing.assert_allclose(acceleration, np.linalg.solve(mass, torque - reverse - gravity))
    damping = np.diag([0.2, 0.3])
    assert not np.allclose(damping @ velocity, damping @ -velocity)


def test_single_valued_rhs_does_not_guarantee_unique_future() -> None:
    time = np.linspace(0, 2, 2001)
    start = 0.5
    delayed = np.maximum(time - start, 0) ** 2 / 4
    derivative = np.maximum(time - start, 0) / 2
    np.testing.assert_allclose(derivative, np.sqrt(delayed))
    zero = np.zeros_like(time)
    np.testing.assert_allclose(np.sqrt(zero), zero)
    assert delayed[0] == zero[0] == 0
    assert delayed[-1] > zero[-1]


def test_current_command_does_not_encode_pure_delay_history() -> None:
    delay = 0.1
    future_times = np.array([0.0, 0.05, 0.1])
    history_times = future_times - delay
    # Both histories and identical future commands equal zero at t=0.
    first_history = np.zeros_like(history_times)
    second_history = np.sin(np.pi * (history_times + delay) / delay)
    assert second_history[-1] == pytest.approx(0, abs=1e-15)
    assert first_history[-1] == 0
    assert second_history[1] == pytest.approx(1)
    assert first_history[1] == 0


def test_one_modal_observation_does_not_determine_elastic_energy() -> None:
    observation = np.array([1.0, 1.0])
    relaxed = np.zeros(2)
    deformed = np.array([1.0, -1.0])
    assert observation @ relaxed == observation @ deformed == 0
    assert 0.5 * relaxed @ relaxed == 0
    assert 0.5 * deformed @ deformed == 1
    # Observing only a sum is incomplete; full modal deformation fixes this energy.
    assert np.linalg.matrix_rank(observation[None, :]) == 1


def test_pointwise_nonlinear_intervention_is_defined_but_not_additive() -> None:
    baseline = 2.0 * 3.0
    remove_first = baseline - 0.0 * 3.0
    remove_second = baseline - 2.0 * 0.0
    remove_both = baseline - 0.0 * 0.0
    assert remove_first == remove_second == remove_both == 6.0
    assert remove_first + remove_second != remove_both
