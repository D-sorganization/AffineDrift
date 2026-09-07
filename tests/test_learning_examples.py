"""Check the textbook's learning examples independently of training assertions."""

import importlib
from dataclasses import fields
from typing import Any

import numpy as np
import pytest


@pytest.fixture(scope="module")
def example() -> Any:
    return importlib.import_module("src.tools.learning_examples")


def test_manual_backprop_matches_every_parameter_difference(example: Any) -> None:
    network = example.make_network(3, np.random.default_rng(41))
    features = np.array([[-0.8], [0.1], [0.7]])
    targets = features**2
    loss, gradient = example.loss_and_gradient(network, features, targets)
    expected = np.sum((example.predict(network, features) - targets) ** 2) / 6
    assert loss == pytest.approx(expected)
    step = 1e-6
    for field in fields(network):
        values = getattr(network, field.name)
        for index in np.ndindex(values.shape):
            original = values[index]
            values[index] = original + step
            upper = example.loss_and_gradient(network, features, targets)[0]
            values[index] = original - step
            lower = example.loss_and_gradient(network, features, targets)[0]
            values[index] = original
            numerical = (upper - lower) / (2 * step)
            assert getattr(gradient, field.name)[index] == pytest.approx(numerical, abs=1e-9)


@pytest.mark.parametrize("batch_size", [1, 3, 7, 20])
def test_epoch_reports_final_full_data_loss(example: Any, batch_size: int) -> None:
    network = example.make_network(4, np.random.default_rng(2))
    features = np.linspace(-1, 1, 7).reshape(-1, 1)
    dataset = example.Dataset(features, features**2)
    settings = example.TrainingSettings(batch_size, 0.03)
    reported = example.train_epoch(network, dataset, settings, np.random.default_rng(3))
    expected = np.sum((example.predict(network, features) - features**2) ** 2) / 14
    assert reported == pytest.approx(expected)
    assert np.isfinite(reported)


def test_oversized_batch_is_one_full_gradient_step(example: Any) -> None:
    network = example.make_network(3, np.random.default_rng(5))
    features = np.array([[-0.9], [-0.1], [0.4], [0.8]])
    targets = features**2
    _, gradient = example.loss_and_gradient(network, features, targets)
    expected = {field.name: getattr(network, field.name).copy() for field in fields(network)}
    example.train_epoch(
        network,
        example.Dataset(features, targets),
        example.TrainingSettings(8, 0.02),
        np.random.default_rng(6),
    )
    for field in fields(network):
        np.testing.assert_allclose(
            getattr(network, field.name),
            expected[field.name] - 0.02 * getattr(gradient, field.name),
        )


def test_demo_reproducibility_and_unseen_regression_points(example: Any) -> None:
    first = example.regression_demo()
    second = example.regression_demo()
    assert first == second
    assert first["final_train_loss"] < first["initial_train_loss"] / 10
    assert first["test_loss"] < 0.01


@pytest.mark.parametrize("width", [0, -1, 2.5, True])
def test_invalid_network_width(example: Any, width: Any) -> None:
    with pytest.raises(ValueError):
        example.make_network(width, np.random.default_rng(1))


@pytest.mark.parametrize(
    "features",
    [np.empty((0, 1)), np.ones(3), np.ones((3, 2)), np.array([[np.nan]]), np.array([[np.inf]])],
)
def test_invalid_features(example: Any, features: np.ndarray) -> None:
    network = example.make_network(2, np.random.default_rng(1))
    with pytest.raises(ValueError):
        example.predict(network, features)


@pytest.mark.parametrize("targets", [np.ones(2), np.ones((3, 1)), np.array([[0], [np.nan]])])
def test_invalid_targets(example: Any, targets: np.ndarray) -> None:
    network = example.make_network(2, np.random.default_rng(1))
    with pytest.raises(ValueError):
        example.loss_and_gradient(network, np.ones((2, 1)), targets)


@pytest.mark.parametrize(
    "batch,rate", [(0, 0.1), (2.5, 0.1), (True, 0.1), (2, 0), (2, -0.1), (2, np.inf), (2, np.nan)]
)
def test_invalid_training_settings(example: Any, batch: Any, rate: float) -> None:
    network = example.make_network(2, np.random.default_rng(1))
    dataset = example.Dataset(np.ones((2, 1)), np.zeros((2, 1)))
    with pytest.raises(ValueError):
        example.train_epoch(
            network, dataset, example.TrainingSettings(batch, rate), np.random.default_rng(1)
        )
