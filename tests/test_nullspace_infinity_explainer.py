"""Check the published null-space search example and its mathematical claims."""

from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def test_example_constraints_leave_a_line_with_a_unique_minimum() -> None:
    """Rank two leaves one free coordinate; the declared cost selects one point."""
    matrix = np.array([[1.0, 1.0, 1.0], [1.0, -1.0, 0.0]])
    target = np.array([1.0, 0.0])
    direction = np.array([1.0, 1.0, -2.0])
    minimum = np.full(3, 1.0 / 3.0)

    assert np.linalg.matrix_rank(matrix) == 2
    np.testing.assert_allclose(matrix @ direction, 0.0)
    np.testing.assert_allclose(matrix @ minimum, target)
    assert np.dot(direction, minimum) == 0.0
    assert np.dot(direction, direction) == 6.0

    for parameter in (0.0, 1.0 / 3.0, 0.5):
        point = np.array([parameter, parameter, 1.0 - 2.0 * parameter])
        np.testing.assert_allclose(matrix @ point, target)
        assert np.all(point >= 0.0)
        np.testing.assert_allclose(
            0.5 * np.dot(point, point), 3 * parameter**2 - 2 * parameter + 0.5
        )

    assert 100**3 // 100 == 100**2
    cube_covering_radius = 1.0 / (2 * (100 - 1))
    line_half_step = 0.5 / (2 * (100 - 1))
    line_covering_radius = np.max(np.abs(direction)) * line_half_step
    np.testing.assert_allclose(line_covering_radius, cube_covering_radius)


def test_null_space_article_links_to_published_explanation() -> None:
    """The detailed derivation links to an existing overview section."""
    overview = (ROOT / "articles/degrees-of-freedom-and-dimensionality.qmd").read_text(
        encoding="utf-8"
    )
    derivation = (ROOT / "articles/null-space-constraint-jacobian.qmd").read_text(encoding="utf-8")

    anchor = "infinite-solution-sets-and-finite-search"
    assert f"{{#{anchor}}}" in overview
    assert f"degrees-of-freedom-and-dimensionality.html#{anchor}" in derivation
