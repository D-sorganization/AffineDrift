"""Independent accounting and counterexamples for the strokes-gained article."""

from importlib import import_module
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest


@pytest.fixture
def model() -> ModuleType:
    return import_module("docs.development.technical-review.build_strokes_gained_examples")


@pytest.mark.parametrize("values", [[4.2, 2.8, 1.5, 0], [4.2, 7, -2, 0]])
def test_accounting_needs_no_optimal_or_correct_benchmark(model: ModuleType, values: list) -> None:
    gains = model.shot_gains(values, [1, 2, 1])
    assert sum(gains) == pytest.approx(0.2)


def test_omitted_penalty_breaks_score_reconciliation(model: ModuleType) -> None:
    assert sum(model.shot_gains([4.2, 2.8, 1.5, 0], [1, 1, 1])) == pytest.approx(1.2)
    assert sum(model.shot_gains([4.2, 2.8, 1.5, 0], [1, 2, 1])) == pytest.approx(0.2)


def test_category_transfer_preserves_entire_hole(model: ModuleType) -> None:
    for far, near in [(1.2, 1.1), (1.7, 1.4), (1.8, 1.75)]:
        result = model.category_change((1.5, 1.3), (far, near))
        assert result["approach"] == pytest.approx(0.2)
        assert result["putting"] == pytest.approx(far - near - 0.2)
        assert result["total"] == pytest.approx(far - near)


def test_within_putting_boundary_cancels_first_putt_credit(model: ModuleType) -> None:
    # Same starting putt; improve leave; final continuation belongs to putting too.
    old_first, new_first = 2.0 - 1.5 - 1, 2.0 - 1.3 - 1
    old_rest, new_rest = 1.5 - 1.7, 1.3 - 1.4
    assert new_first - old_first == pytest.approx(0.2)
    assert new_first + new_rest - old_first - old_rest == pytest.approx(0.3)


def test_lower_make_probability_does_not_order_proximity_benefits(model: ModuleType) -> None:
    result = model.slope_counterexample()
    assert result["poor_slope_close"] > result["good_slope_close"]
    assert result["poor_slope_far"] < result["good_slope_far"]
    assert result["poor_finite_benefit"] < result["good_finite_benefit"]
    for distance in np.linspace(0.01, 5, 100):
        assert np.exp(-1.2 * distance) < np.exp(-0.3 * distance)


def test_equal_mean_proximity_does_not_imply_equal_expected_score(model: ModuleType) -> None:
    assert np.dot([0.5, 0, 0.5], [1, 2, 3]) == np.dot([0, 1, 0], [1, 2, 3])
    assert model.expected_value([0.5, 0, 0.5], [1.1, 1.5, 2.1]) == pytest.approx(1.6)
    assert model.expected_value([0, 1, 0], [1.1, 1.5, 2.1]) == pytest.approx(1.5)


def test_policy_evaluation_solves_actual_chain_and_not_optimality(model: ModuleType) -> None:
    transition = np.array([[0, 1.0], [0, 0.25]])
    value = model.policy_value(transition, np.ones(2))
    np.testing.assert_allclose(value, [7 / 3, 4 / 3])
    np.testing.assert_allclose(value, 1 + transition @ value)
    # A different action at state 0 ends immediately: optimal cost 1, not 7/3.
    assert min(1.0, 1 + value[1]) == 1.0


def test_state_dependent_player_weights_contribute_to_gradient(model: ModuleType) -> None:
    distance, step = 1.5, 1e-5
    finite = model.mixture_value(distance + step) - model.mixture_value(distance - step)
    finite /= 2 * step
    assert finite == pytest.approx(0.28)
    assert finite != pytest.approx(0.15)  # Only the weighted individual slopes.


def test_distribution_can_change_mean_optimal_and_target_optimal_action(model: ModuleType) -> None:
    safe = model.expected_value([0, 1, 0], [3, 4, 7])
    aggressive = model.expected_value([0.6, 0, 0.4], [3, 4, 7])
    assert safe == 4
    assert aggressive == pytest.approx(4.6)
    assert np.dot([0.6, 0, 0.4], [1, 0, 0]) > np.dot([0, 1, 0], [1, 0, 0])


@pytest.mark.parametrize("probabilities", [[-0.1, 1.1], [0.3, 0.3], [float("nan"), 0]])
def test_invalid_distributions_rejected(model: ModuleType, probabilities: list) -> None:
    with pytest.raises(ValueError):
        model.expected_value(probabilities, [1, 2])


def test_article_states_accounting_conditions_and_distributional_estimand() -> None:
    source = Path("articles/strokes-gained-limitations.qmd").read_text(encoding="utf-8")
    for required in [
        "fixed benchmark",
        "category boundary",
        "policy evaluation",
        "exchangeability",
    ]:
        assert required in source
    assert "is generally false" not in source
    assert (
        "a causal model of the golfer's motion that does not depend on population averages"
        not in source
    )
