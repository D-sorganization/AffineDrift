"""Independent control-scaling checks and publication contracts for #4858."""

from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    "articles/The_Geometry_of_Motion/Volume_I/chapters/ch05_optimal_control.tex",
    "articles/The_Geometry_of_Motion/quarto/ch05_optimal_control.qmd",
)
HESSIAN = np.array([[4.0, 1.0], [1.0, 5.0]])
GRADIENT = np.array([0.5, 2.0])


@pytest.mark.parametrize("scales", ((1000.0, 1.0), (0.001, 3.0), (2.0, 7.0)))
@pytest.mark.parametrize("regularization", (0.1, 1.0, 10.0))
def test_quadratic_penalty_and_step_survive_input_unit_changes(
    scales: tuple[float, float], regularization: float
) -> None:
    """Transform the entire physical objective, then compare its minimizing step."""
    transform = np.diag(scales)
    metric = np.array([[2.0, 0.3], [0.3, 1.0]])
    physical_hessian = HESSIAN + regularization * metric
    physical_step = -np.linalg.solve(physical_hessian, GRADIENT)
    transformed_hessian = transform.T @ physical_hessian @ transform
    transformed_gradient = transform.T @ GRADIENT
    normalized_step = -np.linalg.solve(transformed_hessian, transformed_gradient)
    np.testing.assert_allclose(transform @ normalized_step, physical_step, atol=1e-13, rtol=0)
    physical_cost = GRADIENT @ physical_step + physical_step @ physical_hessian @ physical_step / 2
    normalized_cost = (
        transformed_gradient @ normalized_step
        + normalized_step @ transformed_hessian @ normalized_step / 2
    )
    assert normalized_cost == pytest.approx(physical_cost, abs=1e-13, rel=0)


def test_reusing_identity_after_rescaling_changes_the_physical_policy() -> None:
    """The same numeric damping parameter does not define the same physical penalty."""
    transform = np.diag([1000.0, 1.0])
    physical_step = -np.linalg.solve(HESSIAN + np.eye(2), GRADIENT)
    different_step = -transform @ np.linalg.solve(
        transform.T @ HESSIAN @ transform + np.eye(2), transform.T @ GRADIENT
    )
    np.testing.assert_allclose(physical_step, [-1 / 29, -19 / 58], atol=1e-14, rtol=0)
    assert np.linalg.norm(physical_step - different_step) > 0.005


@pytest.mark.content_lint
@pytest.mark.parametrize("relative_path", SOURCES)
@pytest.mark.parametrize(
    "contract",
    (
        "regularization metric",
        "twice continuously differentiable",
        "trial step fraction",
    ),
)
def test_paired_chapters_state_the_numerical_conventions(relative_path: str, contract: str) -> None:
    """Readers need the convention that makes the displayed local algorithm meaningful."""
    source = " ".join((ROOT / relative_path).read_text(encoding="utf-8").split())
    assert contract in source
