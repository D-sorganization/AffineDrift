"""Independent accounting and counterexamples for the strokes-gained article."""

import json
from importlib import import_module
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest
from numpy.typing import ArrayLike


@pytest.fixture
def model() -> ModuleType:
    return import_module("scripts.build_strokes_gained_examples")


@pytest.mark.parametrize(
    ("values", "costs", "message"),
    [
        ([2, 0], [1, 1], "boundary"),
        ([[2, 0]], [1], "boundary"),
        ([2, np.nan], [1], "finite"),
        ([2, 0], [np.inf], "finite"),
        ([2, 0], [-1], "nonnegative"),
    ],
)
def test_invalid_counted_transitions_rejected(
    model: ModuleType, values: ArrayLike, costs: ArrayLike, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        model.shot_gains(values, costs)


@pytest.mark.parametrize(
    ("transition", "costs", "message"),
    [
        ([[0]], [1, 1], "match"),
        ([], [], "match"),
        ([[np.nan]], [1], "finite"),
        ([[0]], [np.inf], "finite"),
        ([[-0.1]], [1], "substochastic"),
        ([[1.1]], [1], "substochastic"),
        ([[0]], [-1], "nonnegative"),
        ([[0, 1], [1, 0]], [1, 1], "spectral radius"),
    ],
)
def test_nonphysical_or_nonabsorbing_policy_rejected(
    model: ModuleType, transition: ArrayLike, costs: ArrayLike, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        model.policy_value(transition, costs)


@pytest.mark.parametrize("costs", [(1,), (1, -1), (1, np.nan)])
def test_invalid_intervention_costs_rejected(model: ModuleType, costs: tuple) -> None:
    with pytest.raises(ValueError):
        model.intervention_change(costs, ([1], [1]), ([2], [1]))


def test_distribution_shape_and_mixture_domain_are_enforced(model: ModuleType) -> None:
    with pytest.raises(ValueError, match="matching vectors"):
        model.expected_value([1], [1, 2])
    with pytest.raises(ValueError, match="defined only"):
        model.mixture_value(3)


def _assert_report_matches(actual: object, expected: object) -> None:
    """Keep JSON structure exact while allowing final-digit numerical roundoff."""
    assert type(actual) is type(expected)
    if isinstance(expected, dict):
        assert actual.keys() == expected.keys()
        for key, value in expected.items():
            _assert_report_matches(actual[key], value)
    elif isinstance(expected, list):
        assert len(actual) == len(expected)
        for observed, desired in zip(actual, expected, strict=True):
            _assert_report_matches(observed, desired)
    elif isinstance(expected, float):
        assert np.isfinite(actual) and np.isfinite(expected)
        # Far tighter than the article's displayed precision; accommodates the
        # observed Windows/Linux exp differences without weakening input checks.
        np.testing.assert_allclose(actual, expected, rtol=1e-13, atol=1e-14)
    else:
        assert actual == expected


@pytest.mark.integration
def test_published_numerical_artifact_reproduces_with_declared_precision(model: ModuleType) -> None:
    artifact = Path("reports/technical-review/strokes-gained-numerics.json")
    published = json.loads(artifact.read_bytes())
    # Preserve the exact stored serialization separately from numerical agreement.
    assert artifact.read_bytes() == (json.dumps(published, indent=2) + "\n").encode("utf-8")
    computed = json.loads(json.dumps(model.report()))  # Normalize tuples to JSON arrays.
    _assert_report_matches(published, computed)


def test_report_comparison_accepts_observed_linux_roundoff() -> None:
    windows = {"slope": [0.07644508335301181, 0.6585739633128318]}
    linux = {"slope": [0.0764450833530117, 0.6585739633128317]}
    _assert_report_matches(windows, linux)


@pytest.mark.parametrize(
    "changed",
    [
        {"value": [0.0764451]},
        {"value": [float("nan")]},
        {"value": [float("inf")]},
        {"value": ["0.07644508335301181"]},
        {"value": [0.07644508335301181, 0.0]},
        {"renamed": [0.07644508335301181]},
        {"value": [0.07644508335301181], "extra": 0},
    ],
)
def test_report_comparison_rejects_changed_results_or_structure(changed: dict) -> None:
    with pytest.raises(AssertionError):
        _assert_report_matches(changed, {"value": [0.07644508335301181]})


@pytest.mark.parametrize("changed", [True, 1.0, 2, "1"])
def test_report_comparison_keeps_integer_inputs_exact(changed: object) -> None:
    with pytest.raises(AssertionError):
        _assert_report_matches({"count": changed}, {"count": 1})


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


def test_joint_intervention_includes_cost_distribution_and_continuation(model: ModuleType) -> None:
    result = model.intervention_change((1, 1.1), ([0.5, 0.5], [0.75, 0.25]), ([1.5, 2], [1.3, 1.9]))
    assert result["total"] == pytest.approx(2.75 - 2.55)
    assert result["immediate"] == pytest.approx(-0.1)
    assert result["distribution_old"] == pytest.approx(0.125)
    assert result["continuation_new"] == pytest.approx(0.175)
    # Reversing the attribution order changes the components, not their sum.
    alternative_distribution = np.dot([0.5, 0.5], [1.3, 1.9]) - np.dot([0.75, 0.25], [1.3, 1.9])
    alternative_continuation = np.dot([0.5, 0.5], [0.2, 0.1])
    assert alternative_distribution == pytest.approx(0.15)
    assert result[
        "immediate"
    ] + alternative_distribution + alternative_continuation == pytest.approx(result["total"])


def test_interaction_is_difference_between_combined_and_isolated_benefits() -> None:
    before, distribution_only, skill_only, combined = 2.75, 2.725, 2.6, 2.55
    combined_benefit = before - combined
    separate_benefits = (before - distribution_only) + (before - skill_only)
    assert combined_benefit - separate_benefits == pytest.approx(0.025)


def test_mean_preserving_spread_uses_conditional_mean_and_convexity() -> None:
    original = np.array([1.5, 2.5])
    spread = np.array([[1, 2], [2, 3]])
    np.testing.assert_allclose(spread.mean(axis=1), original)
    # A strictly convex toy continuation function yields a positive increase.
    assert np.mean(1 + 0.1 * spread**2) - np.mean(1 + 0.1 * original**2) == pytest.approx(0.025)
