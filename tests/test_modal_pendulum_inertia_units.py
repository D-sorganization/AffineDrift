"""Dimensional contracts for the flexible-pendulum foreshortening inertia."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

import pytest

ROOT = Path(__file__).resolve().parents[1]
EDITIONS = (
    "articles/theory-part4.qmd",
    "articles/drifter-manifesto.qmd",
    "articles/affine-nature-golf-swing.qmd",
)
CRITIQUE = "critiques/geometric_stiffness_omission.md"
DERIVATION = "src/tools/modal_pendulum_foreshortening.py"
LENGTH_SCALE = 2.0
MASS_SCALE = 3.0
SAMPLE_DEFLECTION_M = 0.02
QUADRATURE_DEGREE = 12
COEFFICIENT_TOLERANCE = 1e-9
AXIAL_DISPLACEMENT = r"u_{\mathrm{ax}}(s)"
AXIAL_POTENTIAL_ORDER = r"$O(\eta^2)$ axial gravity correction"
LINEAR_AXIAL_ORDER = r"$O(\eta)$ axial gravity correction"
CROSS_MASS_UNIT = r"0.397\ \mathrm{kg/m}"
MODAL_MASS_UNIT = r"0.317\ \mathrm{kg/m^2}"
OBSOLETE_CROSS_MASS_UNIT = r"0.397\ \mathrm{kg\,m}"


class _QuadratureModel(Protocol):
    """Attributes the foreshortening module must expose for a scaling check."""

    LENGTH: float
    DENSITY: float
    HEAD_MASS: float

    def quadrature_nodes(self, degree: int = 12) -> tuple[object, object]:
        """Return nodes and weights on the shaft."""

    def mass_from_quadrature(
        self, eta: float, theta: float, nodes: object, weights: object
    ) -> object:
        """Assemble the inertia matrix on the supplied mesh."""


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _quadrature_coefficients(model: _QuadratureModel) -> tuple[float, float]:
    """Return (β_B, β_A) extracted from the distributed mass matrix."""
    nodes, weights = model.quadrature_nodes(QUADRATURE_DEGREE)
    at_rest = model.mass_from_quadrature(0.0, 0.0, nodes, weights)
    deflected = model.mass_from_quadrature(SAMPLE_DEFLECTION_M, 0.0, nodes, weights)
    deflection_sq = SAMPLE_DEFLECTION_M**2
    cross = (float(at_rest[0, 1]) - float(deflected[0, 1])) / deflection_sq
    modal = (float(deflected[1, 1]) - float(at_rest[1, 1])) / deflection_sq
    return cross, modal


@pytest.mark.parametrize("relative", EDITIONS)
def test_published_editions_state_inertia_correction_units(relative: str) -> None:
    """β_B is linear density and β_A is mass per area; axial displacement is u_ax."""
    text = _read(relative)
    assert CROSS_MASS_UNIT in text
    assert MODAL_MASS_UNIT in text
    assert OBSOLETE_CROSS_MASS_UNIT not in text
    assert text.count(AXIAL_DISPLACEMENT) >= 3
    assert "$u(s)=" not in text
    assert AXIAL_POTENTIAL_ORDER in text
    assert LINEAR_AXIAL_ORDER not in text


def test_critique_uses_axial_symbol_and_quadratic_potential_order() -> None:
    """The resolved critique must not keep the torque symbol or the linear order."""
    text = _read(CRITIQUE)
    assert text.count(AXIAL_DISPLACEMENT) >= 2
    assert "$u(s)=" not in text
    assert AXIAL_POTENTIAL_ORDER in text
    assert LINEAR_AXIAL_ORDER not in text


def test_gradient_docstring_keeps_linear_axial_gravity_order() -> None:
    """The potential is O(η²); its displacement gradient remains O(η)."""
    assert "including O(η) axial gravity" in _read(DERIVATION)


def test_quadrature_inertia_corrections_scale_with_mass_and_length(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """β_B scales as mass/length and β_A as mass/length² under a similar shaft."""
    from src.tools import modal_pendulum_foreshortening as model

    baseline = _quadrature_coefficients(model)
    monkeypatch.setattr(model, "LENGTH", model.LENGTH * LENGTH_SCALE)
    monkeypatch.setattr(model, "DENSITY", model.DENSITY * MASS_SCALE / LENGTH_SCALE)
    monkeypatch.setattr(model, "HEAD_MASS", model.HEAD_MASS * MASS_SCALE)
    scaled = _quadrature_coefficients(model)
    mass_per_length = MASS_SCALE / LENGTH_SCALE
    assert scaled[0] == pytest.approx(baseline[0] * mass_per_length, rel=COEFFICIENT_TOLERANCE)
    assert scaled[1] == pytest.approx(
        baseline[1] * mass_per_length / LENGTH_SCALE, rel=COEFFICIENT_TOLERANCE
    )


def test_named_coefficients_match_quadrature_and_scale() -> None:
    """The derivation script's closed form carries the same dimensions as quadrature."""
    from src.tools.modal_pendulum_foreshortening import (
        DENSITY,
        HEAD_MASS,
        LENGTH,
        foreshortening_inertia_coefficients,
    )

    cross, modal = foreshortening_inertia_coefficients(LENGTH, DENSITY, HEAD_MASS)
    from src.tools import modal_pendulum_foreshortening as model

    quadrature = _quadrature_coefficients(model)
    assert cross == pytest.approx(quadrature[0], rel=COEFFICIENT_TOLERANCE)
    assert modal == pytest.approx(quadrature[1], rel=COEFFICIENT_TOLERANCE)
    scaled_cross, scaled_modal = foreshortening_inertia_coefficients(
        LENGTH * LENGTH_SCALE,
        DENSITY * MASS_SCALE / LENGTH_SCALE,
        HEAD_MASS * MASS_SCALE,
    )
    mass_per_length = MASS_SCALE / LENGTH_SCALE
    assert scaled_cross == pytest.approx(cross * mass_per_length, rel=COEFFICIENT_TOLERANCE)
    assert scaled_modal == pytest.approx(
        modal * mass_per_length / LENGTH_SCALE, rel=COEFFICIENT_TOLERANCE
    )


def test_coefficient_preconditions_reject_nonphysical_geometry() -> None:
    """Length must be positive and both masses must be non-negative."""
    from src.tools.modal_pendulum_foreshortening import foreshortening_inertia_coefficients

    with pytest.raises(ValueError, match="length"):
        foreshortening_inertia_coefficients(0.0, 0.1, 0.2)
    with pytest.raises(ValueError, match="density"):
        foreshortening_inertia_coefficients(1.1, -0.1, 0.2)
    with pytest.raises(ValueError, match="head_mass"):
        foreshortening_inertia_coefficients(1.1, 0.1, -0.2)
