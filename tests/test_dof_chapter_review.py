"""Execute the printed reaching example and verify its independent predictions."""

import re
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from numpy.testing import assert_allclose

CHAPTER = (
    Path(__file__).resolve().parents[1]
    / "articles/The_Geometry_of_Motion/Volume_IV/chapters/ch01_dof_problem.tex"
)


@pytest.fixture(scope="module")
def example() -> dict[str, Any]:
    """The checked implementation is exactly the code presented to the reader."""
    source = CHAPTER.read_text(encoding="utf-8")
    blocks = re.findall(r"\\begin\{lstlisting\}[^\n]*\n(.*?)\\end\{lstlisting\}", source, re.S)
    namespace: dict[str, Any] = {}
    for index, block in enumerate(blocks):
        exec(compile(block, f"chapter1-listing-{index}", "exec"), namespace)
    return namespace


def test_printed_jacobian_matches_cartesian_finite_differences(example: dict[str, Any]) -> None:
    """Transport through the three links agrees with independently displaced endpoints."""
    angles = np.array([0.5, 1.2, -0.3])
    lengths = np.array([0.3, 0.25, 0.2])
    endpoint = example["planar_endpoint"]
    jacobian = example["planar_jacobian"](angles, lengths)
    step = 1e-6
    plus = endpoint(angles + step * np.eye(3), lengths)
    minus = endpoint(angles - step * np.eye(3), lengths)
    assert_allclose(jacobian, ((plus - minus) / (2 * step)).T, rtol=1e-8, atol=1e-10)


def test_printed_anisotropic_and_isotropic_examples(example: dict[str, Any]) -> None:
    """Known sample covariance separates a 9:1 construction from an isotropic control."""
    result = example["result"]
    assert result.rank == 2
    assert result.variance_null == pytest.approx(0.0009)
    assert result.variance_task == pytest.approx(0.0001)
    assert result.ratio == pytest.approx(9.0)
    assert example["isotropic"].ratio == pytest.approx(1.0)
    assert example["null_step_linear_error"] < 1e-14
    assert 0 < example["null_step_actual_error"] < 0.001
