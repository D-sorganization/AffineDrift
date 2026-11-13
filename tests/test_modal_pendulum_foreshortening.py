"""Unit checks for the foreshortened planar modal pendulum model."""

import numpy as np

from src.tools.modal_pendulum_foreshortening import (
    GEOMETRIC_STIFFENING_RATIO,
    J0,
    A,
    mass,
)


def test_pinned_inertia_at_zero_deflection_matches_classical_values() -> None:
    matrix = mass(0.0)
    assert matrix[0, 0] == J0
    np.testing.assert_allclose(matrix, mass(1e-12), atol=1e-10)


def test_geometric_stiffening_reduces_spin_inertia_at_nonzero_deflection() -> None:
    assert mass(0.05)[0, 0] < J0
    reduction = J0 - mass(0.05)[0, 0]
    np.testing.assert_allclose(reduction, GEOMETRIC_STIFFENING_RATIO * A * 0.05**2, rtol=1e-10)
