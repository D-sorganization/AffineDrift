"""Shared constants and validation helpers for the RL funnel benchmark."""

from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt

from src.core.constants import GRAVITY_M_S2
from src.core.contracts import check_finite_array, require

STATE_DIM = 4
CONTROL_DIM = 2
DEFAULT_CONTROL_SATURATION = 50.0
PENDULUM_MASS_1_KG = 1.0
PENDULUM_MASS_2_KG = 1.0
PENDULUM_LINK_1_M = 0.5
PENDULUM_LINK_2_M = 0.5


def double_pendulum_mass_matrix(theta1: float, theta2: float) -> npt.NDArray[Any]:
    """Return the benchmark mass matrix for the two-link pendulum."""
    c12 = np.cos(theta1 - theta2)
    return np.array(
        [
            [
                (PENDULUM_MASS_1_KG + PENDULUM_MASS_2_KG) * PENDULUM_LINK_1_M**2,
                PENDULUM_MASS_2_KG * PENDULUM_LINK_1_M * PENDULUM_LINK_2_M * c12,
            ],
            [
                PENDULUM_MASS_2_KG * PENDULUM_LINK_1_M * PENDULUM_LINK_2_M * c12,
                PENDULUM_MASS_2_KG * PENDULUM_LINK_2_M**2,
            ],
        ]
    )


def validate_state_vector(x: npt.NDArray[Any], name: str) -> None:
    """Validate a 4D state vector for the benchmark system."""
    check_finite_array(x, name)
    require(x.shape == (STATE_DIM,), f"{name} must have shape ({STATE_DIM},)", x.shape)


def validate_time_span(t_span: tuple[float, float]) -> None:
    """Validate a simulation time span."""
    require(len(t_span) == 2, "t_span must contain exactly two endpoints", t_span)
    require(t_span[1] > t_span[0], "t_span end must exceed start", t_span)


def validate_weight_matrix(matrix: npt.NDArray[Any], shape: tuple[int, int], name: str) -> None:
    """Validate a quadratic cost weight matrix."""
    check_finite_array(matrix, name)
    require(matrix.shape == shape, f"{name} must have shape {shape}", matrix.shape)


def validate_reference_trajectory(t_ref: npt.NDArray[Any], x_ref: npt.NDArray[Any]) -> None:
    """Validate a reference time/state trajectory pair."""
    check_finite_array(t_ref, "t_ref")
    check_finite_array(x_ref, "x_ref")
    require(t_ref.ndim == 1, "t_ref must be one-dimensional", t_ref.ndim)
    require(len(t_ref) >= 2, "t_ref must contain at least two samples", len(t_ref))
    require(bool(np.all(np.diff(t_ref) > 0)), "t_ref must be strictly increasing")
    require(
        x_ref.shape == (STATE_DIM, len(t_ref)),
        "x_ref must have shape (4, len(t_ref))",
        x_ref.shape,
    )


__all__ = [
    "CONTROL_DIM",
    "DEFAULT_CONTROL_SATURATION",
    "GRAVITY_M_S2",
    "PENDULUM_LINK_1_M",
    "PENDULUM_LINK_2_M",
    "PENDULUM_MASS_1_KG",
    "PENDULUM_MASS_2_KG",
    "STATE_DIM",
    "double_pendulum_mass_matrix",
    "validate_reference_trajectory",
    "validate_state_vector",
    "validate_time_span",
    "validate_weight_matrix",
]
