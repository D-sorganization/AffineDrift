"""Tests for the quadratic_step listing extracted from Chapter 5 LaTeX source.

Validates the backward-pass quadratic step computation extracted directly
from the textbook LaTeX source listing against exact analytical solutions,
minimization optimality properties, and parameter validation specifications.
"""

import re
import sys
import types
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import pytest

MODULE_NAME = "quadratic_step_listing_module"
TEX_PATH = Path(__file__).resolve().parents[1] / Path(
    "articles/The_Geometry_of_Motion/Volume_V/chapters/ch05_trajectory_optimization.tex"
)
LISTING_PATTERN = re.compile(
    r"\\begin\{lstlisting\}(?:\[[^\]]*\])?(.*?"
    r"def\s+quadratic_step\s*\(.*?)"
    r"\\end\{lstlisting\}",
    re.DOTALL,
)


@pytest.fixture(scope="module")
def quadratic_step() -> Callable[..., dict[str, Any]]:
    """Extract, compile, register, and return quadratic_step from LaTeX."""
    content = TEX_PATH.read_text(encoding="utf-8")
    match = LISTING_PATTERN.search(content)
    assert match is not None, f"Listing with quadratic_step not found in {TEX_PATH}"
    code_str = match.group(1)

    code_obj = compile(
        code_str,
        str(TEX_PATH),
        "exec",
        dont_inherit=True,
    )
    mod = types.ModuleType(MODULE_NAME)
    mod.__file__ = str(TEX_PATH)
    sys.modules[MODULE_NAME] = mod

    # Listing execution of trusted repository-owned textbook code
    # nosemgrep: python.lang.security.audit.exec-detected.exec-detected
    exec(code_obj, mod.__dict__)

    fn = getattr(mod, "quadratic_step", None)
    assert callable(fn), "quadratic_step function not found in compiled module"
    return fn


def test_scalar_analytic_case(quadratic_step: Callable[..., dict[str, Any]]) -> None:
    """Verify exact analytical values for the 1D state / 1D control problem."""
    g = np.array([3.0, 4.0])
    h = np.array([[2.0, 1.0], [1.0, 2.0]])
    res = quadratic_step(g, h, 1)

    k_exp = np.array([-2.0])
    big_k_exp = np.array([[-0.5]])
    vg_exp = np.array([1.0])
    vh_exp = np.array([[1.5]])
    vo_exp = -4.0

    np.testing.assert_allclose(res["k"], k_exp, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(res["K"], big_k_exp, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(res["value_gradient"], vg_exp, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(res["value_hessian"], vh_exp, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(res["value_offset"], vo_exp, rtol=1e-12, atol=1e-12)


def test_manufactured_mixed_system(quadratic_step: Callable[..., dict[str, Any]]) -> None:
    """Verify quadratic stationarity and minimal value on n=2, m=2 problem."""
    n, m = 2, 2
    g = np.array([1.5, -2.0, 0.5, 3.0])
    h_xx = np.array([[-3.0, 1.0], [1.0, -2.0]])
    h_xu = np.array([[0.5, -1.0], [2.0, 0.2]])
    h_uu = np.array([[4.0, 1.0], [1.0, 3.0]])
    h = np.block([[h_xx, h_xu], [h_xu.T, h_uu]])

    res = quadratic_step(g, h, n)
    k, big_k = res["k"], res["K"]
    v_grad, v_hess, v_off = res["value_gradient"], res["value_hessian"], res["value_offset"]

    gu, hu_x, hu_u = g[n:], h[n:, :n], h[n:, n:]
    np.testing.assert_allclose(hu_u @ k + gu, np.zeros(m), rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(hu_u @ big_k + hu_x, np.zeros((m, n)), rtol=1e-12, atol=1e-12)

    dx_samples = np.array([[0.0, 0.0], [1.0, -0.5], [-2.0, 1.5], [0.3, 0.8]])
    opt_du = (big_k @ dx_samples.T).T + k
    z_opt = np.hstack([dx_samples, opt_du])

    q_full = np.einsum("bi,i->b", z_opt, g) + 0.5 * np.einsum("bi,ij,bj->b", z_opt, h, z_opt)
    q_red = (
        v_off
        + np.einsum("bi,i->b", dx_samples, v_grad)
        + 0.5 * np.einsum("bi,ij,bj->b", dx_samples, v_hess, dx_samples)
    )
    np.testing.assert_allclose(q_full, q_red, rtol=1e-12, atol=1e-12)

    delta_u = np.array([[0.1, -0.2], [-0.3, 0.05], [0.5, 0.5], [-0.1, 0.4]])
    z_pert = np.hstack([dx_samples, opt_du + delta_u])
    q_pert = np.einsum("bi,i->b", z_pert, g) + 0.5 * np.einsum("bi,ij,bj->b", z_pert, h, z_pert)
    delta_quad = 0.5 * np.einsum("bi,ij,bj->b", delta_u, hu_u, delta_u)
    np.testing.assert_allclose(q_pert - q_full, delta_quad, rtol=1e-12, atol=1e-12)
    assert np.all(q_pert > q_full)


INVALID_INPUTS = [
    (np.zeros(3), np.eye(3), True),
    (np.zeros(3), np.eye(3), False),
    (np.zeros(3), np.eye(3), 1.5),
    (np.zeros(3), np.eye(3), 0),
    (np.zeros(3), np.eye(3), 3),
    (np.zeros(3), np.eye(3), -1),
    (np.zeros((3, 1)), np.eye(3), 1),
    (np.zeros(3), np.eye(4), 1),
    (np.zeros(3), np.ones((3, 2)), 1),
    (np.zeros(3), np.ones((3, 3, 1)), 1),
    (np.array([1.0, np.nan, 2.0]), np.eye(3), 1),
    (np.array([1.0, np.inf, 2.0]), np.eye(3), 1),
    (np.zeros(3), np.array([[1.0, 0.0, np.nan], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]), 1),
    (np.zeros(3), np.array([[1.0, 2.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]), 1),
    (np.zeros(3), np.diag([1.0, 1.0, 0.0]), 1),
    (np.zeros(3), np.diag([1.0, 1.0, -1.0]), 1),
    (np.zeros(3), np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 2.0], [0.0, 2.0, 1.0]]), 1),
]


@pytest.mark.parametrize("g, h, n", INVALID_INPUTS)
def test_invalid_inputs_raise_value_error(
    quadratic_step: Callable[..., dict[str, Any]],
    g: Any,
    h: Any,
    n: Any,
) -> None:
    """Ensure invalid dimensions, types, non-finite values, and non-SPD Huu raise ValueError."""
    with pytest.raises(ValueError):
        quadratic_step(g, h, n)
