"""Independent constrained-energy examples and source conventions for #4860."""

import re
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    "articles/The_Physics_of_Golf/chapters/ch09b_passive_stabilization.tex",
    "articles/bosch_integration/golf_chapter/ch09b_passive_stabilization.tex",
    "articles/The_Physics_of_Golf/quarto/ch09b_passive_stabilization.qmd",
)


@pytest.mark.parametrize("offset, expected", ((0.8, 20.0), (0.5, -10.0)))
def test_exact_constrained_energy_recovers_preload_stiffness(
    offset: float, expected: float
) -> None:
    """Differentiate the curved feasible path; a straight tangent misses preload."""
    steps = np.array([0.001, 0.0005, 0.00025])
    # R = 1 m, kx = 100 N/m, ky = 40 N/m; U is even in theta.
    energies = 50 * (np.cos(steps) - offset) ** 2 + 20 * np.sin(steps) ** 2
    nominal = 50 * (1 - offset) ** 2
    estimates = 2 * (energies - nominal) / steps**2
    errors = np.abs(estimates - expected)
    assert np.all(np.diff(errors) < 0)
    assert errors[-1] < 1e-4
    multiplier = 100 * (1 - offset)
    assert 40 - multiplier == pytest.approx(expected)
    assert np.all(np.linalg.eigvalsh(np.diag([100, 40])) > 0)
    assert expected != 40  # Ambient tangent stiffness gives neither answer.


@pytest.mark.parametrize("basis_factor", (0.2, 3.0, -2.0))
def test_tangent_basis_scale_preserves_task_compliance(basis_factor: float) -> None:
    """Changing independent coordinates changes both Jacobian and stiffness."""
    task_jacobian = np.array([[1.0]]) * basis_factor
    stiffness = np.array([[20.0]]) * basis_factor**2
    compliance = task_jacobian @ np.linalg.solve(stiffness, task_jacobian.T)
    np.testing.assert_allclose(compliance, [[0.05]], atol=1e-14, rtol=0)
    tangent = np.array([[0.0], [basis_factor]])
    constraint = np.array([[1.0, 0.0]])
    np.testing.assert_allclose(constraint @ tangent, 0, atol=0)
    assert np.linalg.matrix_rank(tangent) == np.linalg.matrix_rank(constraint) == 1


@pytest.mark.content_lint
def test_maintained_print_copies_match() -> None:
    """A technical correction must reach both maintained print sources."""
    assert (ROOT / SOURCES[0]).read_bytes() == (ROOT / SOURCES[1]).read_bytes()


@pytest.mark.content_lint
@pytest.mark.parametrize("relative_path", SOURCES)
def test_chapter_discloses_the_reduction_and_constitutive_scope(relative_path: str) -> None:
    """Readers need the assumptions behind reaction-free local impedance."""
    content = " ".join((ROOT / relative_path).read_text(encoding="utf-8").split())
    for phrase in (
        "independent perturbation coordinates",
        "quasistatic constitutive approximation",
        "constraint-curvature term",
    ):
        assert phrase in content


@pytest.mark.content_lint
def test_quarto_display_math_has_no_paragraph_breaks() -> None:
    """A blank line inside dollar fences leaves literal delimiters in Pandoc output."""
    source = (ROOT / SOURCES[2]).read_text(encoding="utf-8")
    displays = re.findall(r"^\$\$\n(.*?)^\$\$", source, flags=re.MULTILINE | re.DOTALL)
    assert len(displays) == 12
    assert all("\n\n" not in display for display in displays)
