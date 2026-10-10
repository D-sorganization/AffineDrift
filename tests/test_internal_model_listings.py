"""Tests for internal models and responsibilities extracted from TeX listings.

Validates LinearPair and responsibilities functions extracted dynamically from
the textbook source listing in ch06_internal_models.tex.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from scipy.stats import multivariate_normal

TEX_REL_PATH = Path("articles/The_Geometry_of_Motion/Volume_IV/chapters/ch06_internal_models.tex")


def _load_tex_namespace() -> dict[str, Any]:
    """Extract and execute Python listings from the canonical TeX chapter."""
    repo_root = Path(__file__).resolve().parents[1]
    tex_path = repo_root / TEX_REL_PATH
    if not tex_path.is_file():
        pytest.fail(f"Required TeX source file not found at {tex_path}")

    content = tex_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"\\begin\{lstlisting\}\[language=Python[^\]]*\](.*?)(\\end\{lstlisting\})",
        re.DOTALL,
    )
    matches = pattern.findall(content)
    if not matches:
        pytest.fail(f"No Python lstlisting blocks found in {tex_path}")

    combined_code = "\n\n".join(m[0] for m in matches)
    namespace: dict[str, Any] = {"__name__": "listing_tests"}
    # Repository-owned listings at a fixed path, with no external input.
    # nosemgrep: python.lang.security.audit.exec-detected.exec-detected
    exec(compile(combined_code, str(tex_path), "exec", dont_inherit=True), namespace)

    required_symbols = ("LinearPair", "responsibilities")
    missing = [sym for sym in required_symbols if sym not in namespace]
    if missing:
        pytest.fail(f"Missing required extracted symbols from TeX: {missing}")

    return namespace


@pytest.fixture(scope="module")
def mod() -> dict[str, Any]:
    """Provide extracted TeX module namespace."""
    return _load_tex_namespace()


def test_linear_pair_validation_and_float_conversion(mod: dict[str, Any]) -> None:
    """Ensure shape validation and float casting on integer inputs."""
    linear_pair_cls = mod["LinearPair"]

    with pytest.raises(ValueError):
        linear_pair_cls(A=np.ones((2, 3)), B=np.ones((2, 1)))

    with pytest.raises(ValueError):
        linear_pair_cls(A=np.ones((2, 2)), B=np.ones((3, 1)))

    with pytest.raises(ValueError):
        linear_pair_cls(A=np.ones((0, 0)), B=np.ones((0, 1)))

    pair = linear_pair_cls(A=np.array([[0.5]]), B=np.array([[1.5]]))
    x_int = np.array([2], dtype=int)
    u_int = np.array([1], dtype=int)
    pred = pair.predict(x_int, u_int)
    assert isinstance(pred, np.ndarray)
    assert np.issubdtype(pred.dtype, np.floating)
    np.testing.assert_allclose(pred, np.array([2.5]))


def test_linear_pair_underactuated_lstsq(mod: dict[str, Any]) -> None:
    """Inverse must select minimal Euclidean norm u and retain nonzero residual."""
    linear_pair_cls = mod["LinearPair"]
    a_mat = np.eye(2)
    b_mat = np.array([[0.0], [1.0]])
    pair = linear_pair_cls(A=a_mat, B=b_mat)

    x_vec = np.array([0.0, 0.0])
    target = np.array([1.0, 2.0])
    command, residual = pair.inverse(x_vec, target)

    np.testing.assert_allclose(command, np.array([2.0]))
    np.testing.assert_allclose(residual, np.array([1.0, 0.0]))
    np.testing.assert_allclose(residual, target - pair.predict(x_vec, command))


def test_linear_pair_redundant_lstsq(mod: dict[str, Any]) -> None:
    """Inverse under redundant actuators picks minimal Euclidean norm solution."""
    linear_pair_cls = mod["LinearPair"]
    a_mat = np.array([[1.0]])
    b_mat = np.array([[1.0, 1.0]])
    pair = linear_pair_cls(A=a_mat, B=b_mat)

    x_vec = np.array([0.0])
    target = np.array([2.0])
    command, residual = pair.inverse(x_vec, target)

    np.testing.assert_allclose(command, np.array([1.0, 1.0]))
    np.testing.assert_allclose(residual, np.array([0.0]), atol=1e-12)


def test_linear_pair_predict_linear_and_input_immutable(mod: dict[str, Any]) -> None:
    """Verify linear superposition and immutability of input arrays."""
    linear_pair_cls = mod["LinearPair"]
    a_mat = np.array([[1.0, 2.0], [0.0, 1.0]])
    b_mat = np.array([[1.0], [0.5]])
    pair = linear_pair_cls(A=a_mat, B=b_mat)

    x1 = np.array([1.0, 2.0])
    x2 = np.array([0.5, -1.0])
    u1 = np.array([2.0])
    u2 = np.array([-0.5])

    x1_copy = x1.copy()
    u1_copy = u1.copy()
    pred_sum = pair.predict(x1 + x2, u1 + u2)
    pred_sep = pair.predict(x1, u1) + pair.predict(x2, u2)

    np.testing.assert_allclose(pred_sum, pred_sep)
    np.testing.assert_array_equal(x1, x1_copy)
    np.testing.assert_array_equal(u1, u1_copy)


def test_responsibilities_equal_error_different_variance(mod: dict[str, Any]) -> None:
    """Test posterior with equal error (0) and variances [1, 4] with equal priors."""
    calc_resp = mod["responsibilities"]
    preds = np.array([[0.0], [0.0]])
    obs = np.array([0.0])
    covs = np.array([[[1.0]], [[4.0]]])
    priors = np.array([0.5, 0.5])

    weights = calc_resp(preds, obs, covs, priors)
    expected = np.array([2.0 / 3.0, 1.0 / 3.0])
    np.testing.assert_allclose(weights, expected, rtol=1e-5)


def test_responsibilities_prior_only_equal_cov(mod: dict[str, Any]) -> None:
    """Identical predictions and covariances preserve the prior distribution."""
    calc_resp = mod["responsibilities"]
    preds = np.array([[1.0], [1.0]])
    obs = np.array([1.0])
    covs = np.array([[[2.0]], [[2.0]]])
    priors = np.array([0.8, 0.2])

    weights = calc_resp(preds, obs, covs, priors)
    np.testing.assert_allclose(weights, priors, rtol=1e-5)


def test_responsibilities_scalar_analytic_residual(mod: dict[str, Any]) -> None:
    """Check against analytic scalar Gaussian likelihood odds ratio."""
    calc_resp = mod["responsibilities"]
    preds = np.array([[0.0], [1.0]])
    obs = np.array([0.0])
    covs = np.array([[[1.0]], [[1.0]]])
    priors = np.array([0.5, 0.5])

    weights = calc_resp(preds, obs, covs, priors)
    p0 = np.exp(-0.5 * 0.0)
    p1 = np.exp(-0.5 * 1.0)
    expected = np.array([p0 / (p0 + p1), p1 / (p0 + p1)])
    np.testing.assert_allclose(weights, expected, rtol=1e-5)


def test_responsibilities_extreme_residual_no_underflow(mod: dict[str, Any]) -> None:
    """Very large residual magnitude should not result in NaN underflow."""
    calc_resp = mod["responsibilities"]
    preds = np.array([[10000.0], [10002.0]])
    obs = np.array([0.0])
    covs = np.array([[[1.0]], [[1.0]]])
    priors = np.array([0.5, 0.5])

    weights = calc_resp(preds, obs, covs, priors)
    assert not np.any(np.isnan(weights))
    np.testing.assert_allclose(np.sum(weights), 1.0)
    assert weights[0] > weights[1]


def test_responsibilities_correlated_2d_oracle(mod: dict[str, Any]) -> None:
    """Compare normalized posterior against scipy multivariate_normal oracle."""
    calc_resp = mod["responsibilities"]
    preds = np.array([[1.0, 0.5], [-0.5, 1.2]])
    obs = np.array([0.2, 0.1])
    cov0 = np.array([[2.0, 0.4], [0.4, 1.5]])
    cov1 = np.array([[1.0, -0.2], [-0.2, 3.0]])
    covs = np.stack([cov0, cov1])
    priors = np.array([0.3, 0.7])

    weights = calc_resp(preds, obs, covs, priors)

    ll0 = multivariate_normal.logpdf(obs, mean=preds[0], cov=cov0)
    ll1 = multivariate_normal.logpdf(obs, mean=preds[1], cov=cov1)
    unnorm = np.array([np.exp(ll0) * priors[0], np.exp(ll1) * priors[1]])
    oracle_weights = unnorm / np.sum(unnorm)

    np.testing.assert_allclose(weights, oracle_weights, rtol=1e-5)


def test_responsibilities_rejects_asymmetric_and_non_spd(mod: dict[str, Any]) -> None:
    """Covariances must be symmetric and strictly positive-definite."""
    calc_resp = mod["responsibilities"]
    preds = np.array([[0.0, 0.0]])
    obs = np.array([0.0, 0.0])
    priors = np.array([1.0])

    asym_cov = np.array([[[1.0, 0.5], [0.0, 1.0]]])
    with pytest.raises(ValueError):
        calc_resp(preds, obs, asym_cov, priors)

    non_spd_cov = np.array([[[-1.0, 0.0], [0.0, 1.0]]])
    with pytest.raises(ValueError):
        calc_resp(preds, obs, non_spd_cov, priors)


def test_responsibilities_rejects_invalid_priors_and_shapes(mod: dict[str, Any]) -> None:
    """Reject unnormalized, non-positive, or non-finite prior vectors and bad shapes."""
    calc_resp = mod["responsibilities"]
    preds = np.array([[0.0], [1.0]])
    obs = np.array([0.0])
    covs = np.array([[[1.0]], [[1.0]]])

    with pytest.raises(ValueError):
        calc_resp(preds, obs, covs, np.array([0.4, 0.4]))

    with pytest.raises(ValueError):
        calc_resp(preds, obs, covs, np.array([-0.2, 1.2]))

    with pytest.raises(ValueError):
        calc_resp(preds, obs, covs, np.array([0.0, 1.0]))

    with pytest.raises(ValueError):
        calc_resp(np.array([[0.0]]), obs, covs, np.array([1.0]))


def test_inverse_mixture_counterexample(mod: dict[str, Any]) -> None:
    """Convex combination of inverse controls fails to produce target on mixed plants."""
    linear_pair_cls = mod["LinearPair"]
    pair1 = linear_pair_cls(A=np.array([[0.0]]), B=np.array([[1.0]]))
    pair2 = linear_pair_cls(A=np.array([[0.0]]), B=np.array([[10.0]]))

    x_zero = np.array([0.0])
    target = np.array([10.0])
    u1, _ = pair1.inverse(x_zero, target)
    u2, _ = pair2.inverse(x_zero, target)

    u_blend = 0.5 * u1 + 0.5 * u2
    np.testing.assert_allclose(u_blend, np.array([5.5]))

    achieved_plant2 = pair2.predict(x_zero, u_blend)
    np.testing.assert_allclose(achieved_plant2, np.array([55.0]))
    assert not np.allclose(achieved_plant2, target)


@pytest.mark.parametrize("bad", [np.array([np.nan]), np.array([np.inf]), np.zeros(2)])
def test_linear_pair_rejects_invalid_vectors(mod: dict[str, Any], bad: np.ndarray) -> None:
    """Reject malformed state, command and target vectors at their boundary."""
    pair = mod["LinearPair"](A=np.eye(1), B=np.eye(1))
    with pytest.raises(ValueError):
        pair.predict(bad, np.zeros(1))
    with pytest.raises(ValueError):
        pair.predict(np.zeros(1), bad)
    with pytest.raises(ValueError):
        pair.inverse(np.zeros(1), bad)


@pytest.mark.parametrize("field", ["predictions", "observation", "covariances", "priors"])
def test_responsibilities_rejects_nonfinite(mod: dict[str, Any], field: str) -> None:
    """All measured quantities and probability parameters must be finite."""
    arguments = {
        "predictions": np.zeros((1, 1)),
        "observation": np.zeros(1),
        "covariances": np.ones((1, 1, 1)),
        "priors": np.ones(1),
    }
    arguments[field].flat[0] = np.nan
    with pytest.raises(ValueError):
        mod["responsibilities"](**arguments)
