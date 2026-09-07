"""Reproducible scalar-regression lesson; this is not a trained control policy."""

from dataclasses import dataclass, fields

import numpy as np
from numpy.typing import NDArray

type Array = NDArray[np.float64]
DEMO_SEED = 2026
DEMO_WIDTH = 12
DEMO_SAMPLES = 41
DEMO_EPOCHS = 1200
DEMO_BATCH_SIZE = 16
DEMO_LEARNING_RATE = 0.05


@dataclass
class Network:
    """Parameters of a one-input, tanh-hidden, one-output regression network."""

    input_weights: Array
    hidden_bias: Array
    output_weights: Array
    output_bias: Array


@dataclass(frozen=True)
class Dataset:
    """Column arrays of scalar inputs and targets with matching nonzero length."""

    features: Array
    targets: Array


@dataclass(frozen=True)
class TrainingSettings:
    """Positive mini-batch size and finite positive SGD learning rate."""

    batch_size: int
    learning_rate: float


def make_network(width: int, generator: np.random.Generator) -> Network:
    """Initialize a scalar network using the caller's random-number generator.

    Args:
        width: Positive integer count of hidden units.
        generator: Generator controlling reproducible initialization.

    Returns:
        Independently initialized trainable arrays; biases initially zero.
    """
    if type(width) is not int or width <= 0:
        raise ValueError("Hidden width must be a positive integer")
    return Network(
        generator.normal(size=(1, width)),
        np.zeros((1, width)),
        generator.normal(size=(width, 1)) / np.sqrt(width),
        np.zeros((1, 1)),
    )


def _validate_features(features: Array) -> None:
    """Reject empty, non-column or nonfinite regression inputs."""
    if features.ndim != 2 or features.shape[0] == 0 or features.shape[1] != 1:
        raise ValueError("Features must have shape (positive sample count, 1)")
    if not np.isfinite(features).all():
        raise ValueError("Features must be finite")


def predict(network: Network, features: Array) -> Array:
    """Evaluate scalar predictions for finite column inputs.

    Args:
        network: Parameters constructed by make_network.
        features: Nonempty finite array with one scalar input per row.

    Returns:
        One prediction per input, with the same column shape.
    """
    _validate_features(features)
    hidden = np.tanh(features @ network.input_weights + network.hidden_bias)
    return hidden @ network.output_weights + network.output_bias


def loss_and_gradient(network: Network, features: Array, targets: Array) -> tuple[float, Network]:
    """Compute half mean squared error and manual gradients without updates.

    Args:
        network: Parameters constructed by make_network.
        features: Finite nonempty scalar column inputs.
        targets: Finite column targets with exactly the same shape.

    Returns:
        Scalar loss and four gradients in the corresponding parameter shapes.
    """
    prediction = predict(network, features)
    if targets.shape != features.shape or not np.isfinite(targets).all():
        raise ValueError("Targets must be finite and match feature shape")
    hidden = np.tanh(features @ network.input_weights + network.hidden_bias)
    error = prediction - targets
    output_derivative = error / features.shape[0]
    hidden_derivative = (output_derivative @ network.output_weights.T) * (1 - hidden**2)
    gradient = Network(
        features.T @ hidden_derivative,
        hidden_derivative.sum(axis=0, keepdims=True),
        hidden.T @ output_derivative,
        output_derivative.sum(axis=0, keepdims=True),
    )
    return float(np.mean(error**2) / 2), gradient


def train_epoch(
    network: Network, dataset: Dataset, settings: TrainingSettings, generator: np.random.Generator
) -> float:
    """Mutate parameters through one shuffled epoch and report final full-data loss.

    Args:
        network: Network to update in place.
        dataset: Nonempty finite scalar input/target pairs.
        settings: Positive batch size and finite positive learning rate.
        generator: Generator used for the sample permutation.

    Returns:
        Full-dataset half MSE evaluated after every update has completed.
    """
    if type(settings.batch_size) is not int or settings.batch_size <= 0:
        raise ValueError("Batch size must be a positive integer")
    if not np.isfinite(settings.learning_rate) or settings.learning_rate <= 0:
        raise ValueError("Learning rate must be finite and positive")
    loss_and_gradient(network, dataset.features, dataset.targets)
    order = generator.permutation(dataset.features.shape[0])
    for start in range(0, len(order), settings.batch_size):
        selected = order[start : start + settings.batch_size]
        _, gradient = loss_and_gradient(
            network, dataset.features[selected], dataset.targets[selected]
        )
        for field in fields(network):
            getattr(network, field.name)[:] -= settings.learning_rate * getattr(
                gradient, field.name
            )
    return loss_and_gradient(network, dataset.features, dataset.targets)[0]


def regression_demo() -> dict[str, float]:
    """Fit x squared on [-1, 1] and evaluate at unseen interval midpoints.

    Returns:
        Deterministic initial/final training losses and midpoint test loss.
        These are scalar regression errors, not control-performance evidence.
    """
    generator = np.random.default_rng(DEMO_SEED)
    features = np.linspace(-1, 1, DEMO_SAMPLES).reshape(-1, 1)
    dataset = Dataset(features, features**2)
    network = make_network(DEMO_WIDTH, generator)
    settings = TrainingSettings(DEMO_BATCH_SIZE, DEMO_LEARNING_RATE)
    initial = loss_and_gradient(network, features, dataset.targets)[0]
    final = initial
    for _ in range(DEMO_EPOCHS):
        final = train_epoch(network, dataset, settings, generator)
    midpoints = (features[:-1] + features[1:]) / 2
    test_loss = loss_and_gradient(network, midpoints, midpoints**2)[0]
    return {"initial_train_loss": initial, "final_train_loss": final, "test_loss": test_loss}
