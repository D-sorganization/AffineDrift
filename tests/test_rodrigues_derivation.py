"""Check both published skew-power cycles against direct matrix products."""

import re
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1] / "articles/The_Geometry_of_Motion"
EDITIONS = [
    ROOT / "Volume_0/chapters/ch06_exponential_coordinates.tex",
    ROOT / "quarto/vol0_ch06_exponential_coordinates.qmd",
]


@pytest.mark.parametrize("edition", EDITIONS, ids=["print", "web"])
def test_rodrigues_power_pattern_captures_alternating_signs(edition: Path) -> None:
    """Parse explicit published powers, then verify their signs numerically."""
    text = edition.read_text(encoding="utf-8")
    powers = re.findall(r"K\^([4-7])=(-?)K(?:\^([2]))?", text)
    assert {int(power) for power, _, _ in powers} == {4, 5, 6, 7}
    direction = np.array([1, 2, 3]) / np.sqrt(14)
    cross = np.cross(direction, np.eye(3)).T
    for power, sign, squared in powers:
        expected = np.linalg.matrix_power(cross, 2 if squared else 1)
        np.testing.assert_allclose(
            np.linalg.matrix_power(cross, int(power)),
            (-1 if sign else 1) * expected,
            atol=1e-14,
        )
