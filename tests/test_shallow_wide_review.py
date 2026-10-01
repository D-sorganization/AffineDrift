"""Execute the printed Chapter 4 examples and challenge their numerical contracts."""

import re
from pathlib import Path
from typing import Any

import numpy as np
import pytest

CHAPTER = (
    Path(__file__).resolve().parents[1]
    / "articles/The_Geometry_of_Motion/Volume_IV/chapters/ch04_shallow_wide.tex"
)


@pytest.fixture(scope="module")
def examples() -> dict[str, Any]:
    source = CHAPTER.read_text(encoding="utf-8")
    blocks = re.findall(r"\\begin\{lstlisting\}[^\n]*\n(.*?)\\end\{lstlisting\}", source, re.S)
    namespace: dict[str, Any] = {}
    for index, block in enumerate(blocks):
        exec(compile(block, f"chapter4-listing-{index}", "exec"), namespace)
    return namespace


def test_network_counts_and_common_signed_output(examples: dict[str, Any]) -> None:
    assert examples["parameter_count"](examples["deep_model"]) == 21960
    assert examples["parameter_count"](examples["wide_model"]) == 21958
    model = [(np.eye(2), np.zeros(2)), (-np.eye(2), np.zeros(2))]
    assert examples["forward"](model, np.ones(2)) == pytest.approx([-1.0, -1.0])
    assert examples["assumed_delays_ms"] == (50.0, 10.0)


@pytest.mark.parametrize(
    "data",
    [
        np.zeros((2, 3)),
        -np.ones((2, 3)),
        np.ones(3),
        np.empty((0, 2)),
        np.array([[np.nan]]),
        np.array([[np.inf]]),
    ],
)
def test_nmf_rejects_undefined_or_invalid_data(examples: dict[str, Any], data: np.ndarray) -> None:
    with pytest.raises(ValueError):
        examples["extract_synergies"](data, 1)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"n_synergies": 0},
        {"n_synergies": 1.5},
        {"n_synergies": True},
        {"max_iter": 0},
        {"max_iter": -1},
        {"max_iter": 1.5},
        {"tol": -1},
        {"tol": np.nan},
        {"tol": np.inf},
    ],
)
def test_nmf_rejects_invalid_options(examples: dict[str, Any], kwargs: dict[str, Any]) -> None:
    options = {"n_synergies": 1, **kwargs}
    with pytest.raises(ValueError):
        examples["extract_synergies"](np.ones((3, 2)), **options)


@pytest.mark.parametrize("scale", [1e-120, 1.0, 1e120])
def test_nmf_rank_one_reconstruction_and_scale(examples: dict[str, Any], scale: float) -> None:
    data = np.outer([0.0, 1.0, 2.0, 3.0], [1.0, 0.0, 2.0]) * scale
    weights, coefficients, score = examples["extract_synergies"](data, 1)
    assert weights.shape == (3, 1)
    assert coefficients.shape == (4, 1)
    assert np.all(np.isfinite(weights)) and np.all(np.isfinite(coefficients))
    assert np.all(weights >= 0) and np.all(coefficients >= 0)
    assert coefficients @ weights.T / scale == pytest.approx(data / scale, abs=1e-7)
    assert score == pytest.approx(1.0)


def test_nmf_is_reproducible_without_mutating_global_rng(examples: dict[str, Any]) -> None:
    state = np.random.get_state()
    data = np.arange(1.0, 13.0).reshape(4, 3)
    first = examples["extract_synergies"](data, 2)
    second = examples["extract_synergies"](data, 2)
    after = np.random.get_state()
    assert after[0] == state[0] and np.array_equal(after[1], state[1])
    assert after[2:] == state[2:]
    for left, right in zip(first, second, strict=True):
        assert left == pytest.approx(right)
    expected = 1 - np.sum((data - first[1] @ first[0].T) ** 2) / np.sum(data**2)
    assert first[2] == pytest.approx(expected)


def test_one_iteration_returns_a_finite_score(examples: dict[str, Any]) -> None:
    result = examples["extract_synergies"](np.ones((3, 2)), 1, max_iter=1)
    assert np.isfinite(result[2])


def test_factor_scaling_preserves_reconstruction_without_identifying_factors() -> None:
    weights = np.array([[1.0, 2.0], [3.0, 1.0]])
    coefficients = np.array([[2.0, 3.0], [1.0, 4.0]])
    scale = np.diag([2.0, 0.5])
    assert (weights @ scale) @ (np.linalg.inv(scale) @ coefficients) == pytest.approx(
        weights @ coefficients
    )


def test_position_only_compression_loses_damping_information() -> None:
    states = np.array([[1.0, -2.0], [1.0, 2.0]])
    assert states[0, 0] == states[1, 0]
    assert -3.0 * states[:, 1] == pytest.approx([6.0, -6.0])
