"""Reproduce illustrative counterexamples; no fitted golfer data are used."""

import json
from pathlib import Path

import numpy as np
from numpy.typing import ArrayLike, NDArray


def shot_gains(values: ArrayLike, costs: ArrayLike) -> NDArray[np.float64]:
    """Return potential differences minus recorded costs, including penalties."""
    baseline, strokes = np.asarray(values, dtype=float), np.asarray(costs, dtype=float)
    if baseline.ndim != 1 or strokes.ndim != 1 or baseline.size != strokes.size + 1:
        raise ValueError("One more boundary value than transition costs is required")
    if not np.all(np.isfinite(baseline)) or not np.all(np.isfinite(strokes)):
        raise ValueError("Values and costs must be finite")
    if np.any(strokes < 0):
        raise ValueError("Recorded costs must be nonnegative")
    return baseline[:-1] - baseline[1:] - strokes


def expected_value(probabilities: ArrayLike, values: ArrayLike) -> float:
    """Evaluate a finite distribution with normalized nonnegative probabilities."""
    weights, outcomes = np.asarray(probabilities, dtype=float), np.asarray(values, dtype=float)
    if weights.ndim != 1 or weights.shape != outcomes.shape:
        raise ValueError("Probabilities and values must be matching vectors")
    if not np.all(np.isfinite(weights)) or not np.all(np.isfinite(outcomes)):
        raise ValueError("Inputs must be finite")
    if np.any(weights < 0) or not np.isclose(weights.sum(), 1):
        raise ValueError("Probabilities must be nonnegative and sum to one")
    return float(weights @ outcomes)


def category_change(benchmark: tuple, player: tuple) -> dict[str, float]:
    """Split a far-to-near approach change with unchanged continuation skill."""
    approach = benchmark[0] - benchmark[1]
    benefit = player[0] - player[1]
    return {"approach": approach, "putting": benefit - approach, "total": benefit}


def policy_value(transition: ArrayLike, costs: ArrayLike) -> NDArray[np.float64]:
    """Solve a proper finite absorbing chain's undiscounted cost-to-go."""
    matrix, cost = np.asarray(transition, dtype=float), np.asarray(costs, dtype=float)
    if cost.ndim != 1 or matrix.shape != (cost.size, cost.size) or not cost.size:
        raise ValueError("Transient transition matrix must match cost vector")
    if not np.all(np.isfinite(matrix)) or not np.all(np.isfinite(cost)):
        raise ValueError("Transition matrix and costs must be finite")
    if np.any(matrix < 0) or np.any(matrix.sum(axis=1) > 1) or np.any(cost < 0):
        raise ValueError("Use a substochastic matrix and nonnegative costs")
    if np.max(np.abs(np.linalg.eigvals(matrix))) >= 1:
        raise ValueError("Transient chain must have spectral radius below one")
    return np.linalg.solve(np.eye(cost.size) - matrix, cost)


def slope_counterexample() -> dict[str, float]:
    """Compare exponential make curves on positive distances in metres."""
    good_rate, poor_rate = 0.3, 1.2
    result = {}
    for label, rate in [("good", good_rate), ("poor", poor_rate)]:
        result[f"{label}_slope_close"] = float(rate * np.exp(-rate * 0.5))
        result[f"{label}_slope_far"] = float(rate * np.exp(-rate * 3))
        result[f"{label}_finite_benefit"] = float(np.exp(-rate * 2) - np.exp(-rate * 2.5))
    result["crossing_distance"] = float(np.log(poor_rate / good_rate) / (poor_rate - good_rate))
    return result


def mixture_value(distance: float) -> float:
    """Illustrate state-dependent player composition on the interval [1, 2]."""
    if not 1 <= distance <= 2:
        raise ValueError("This illustrative mixture is defined only on [1, 2]")
    weight = 0.8 - 0.2 * distance
    return weight * (1 + 0.1 * distance) + (1 - weight) * (1.5 + 0.2 * distance)


def report() -> dict:
    """Collect exact inputs and computed values for review and reproduction."""
    benchmark = (1.5, 1.3)
    players = {"A": (1.2, 1.1), "B": (1.7, 1.4), "C": (1.8, 1.75)}
    return {
        "authority": "Illustrative constructed examples; not empirical golfer estimates",
        "penalty": {
            "values": [4.2, 2.8, 1.5, 0],
            "costs": [1, 2, 1],
            "gains": shot_gains([4.2, 2.8, 1.5, 0], [1, 2, 1]).tolist(),
        },
        "category": {
            "benchmark_far_near": benchmark,
            "players_far_near": players,
            "changes": {name: category_change(benchmark, pair) for name, pair in players.items()},
        },
        "slope": slope_counterexample(),
        "same_mean": {
            "distance": [1, 2, 3],
            "value": [1.1, 1.5, 2.1],
            "deterministic": 1.5,
            "spread": expected_value([0.5, 0, 0.5], [1.1, 1.5, 2.1]),
        },
        "policy": {
            "transition": [[0, 1], [0, 0.25]],
            "cost": [1, 1],
            "value": policy_value([[0, 1], [0, 0.25]], [1, 1]).tolist(),
        },
        "mixture": {
            "distance": 1.5,
            "value": mixture_value(1.5),
            "weighted_slopes": 0.15,
            "composition_term": 0.13,
            "derivative": 0.28,
        },
        "tournament": {
            "scores": [3, 4, 7],
            "safe_probability": [0, 1, 0],
            "aggressive_probability": [0.6, 0, 0.4],
            "safe_mean": 4,
            "aggressive_mean": expected_value([0.6, 0, 0.4], [3, 4, 7]),
        },
    }


if __name__ == "__main__":
    destination = Path(__file__).with_name("strokes-gained-numerics.json")
    destination.write_text(json.dumps(report(), indent=2) + "\n", encoding="utf-8")
