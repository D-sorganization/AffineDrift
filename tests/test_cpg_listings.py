"""Tests for Matsuoka neural oscillator extracted from chapter 8 TeX listing."""

import math
import re
from pathlib import Path
from typing import Any

import numpy as np
import pytest

TEX_REL_PATH = Path("articles/The_Geometry_of_Motion/Volume_IV/chapters/ch08_cpg.tex")


def _load_extracted_namespace() -> dict[str, Any]:
    tex_path = Path(__file__).parents[1] / TEX_REL_PATH
    if not tex_path.is_file():
        pytest.fail(f"Missing TeX source file: {tex_path}")
    content = tex_path.read_text(encoding="utf-8")
    match = re.search(
        r"\\begin\{lstlisting\}(?:\[.*?\])?\r?\n(.*?)\\end\{lstlisting\}", content, re.DOTALL
    )
    if not match:
        pytest.fail(f"No lstlisting environment found in {tex_path}")
    code = match.group(1)
    compiled = compile(code, str(tex_path), "exec", dont_inherit=True)
    ns: dict[str, Any] = {"__name__": "example"}
    # Repository-owned listing at a fixed path, with no external input.
    # nosemgrep: python.lang.security.audit.exec-detected.exec-detected
    exec(compiled, ns)
    return ns


_EXTRACTED = _load_extracted_namespace()

if "MatsuokaParameters" not in _EXTRACTED or "MatsuokaOscillator" not in _EXTRACTED:
    pytest.fail("Missing MatsuokaParameters or MatsuokaOscillator in listing namespace")

MatsuokaParameters = _EXTRACTED["MatsuokaParameters"]
MatsuokaOscillator = _EXTRACTED["MatsuokaOscillator"]


def test_default_parameters_contract() -> None:
    p = MatsuokaParameters()
    assert p.tau == (0.1, 0.3)
    assert p.adaptation == 2.5
    assert p.inhibition == 2.0
    assert p.drive == 1.0


def test_symmetric_equilibrium_has_zero_derivative() -> None:
    param = MatsuokaParameters()
    equilibrium = param.drive / (1 + param.adaptation + param.inhibition)
    derivative = MatsuokaOscillator(param).dynamics(0, np.full(4, equilibrium))
    np.testing.assert_allclose(derivative, 0, atol=1e-13)


def test_rectification_suppresses_negative_rates() -> None:
    derivative = MatsuokaOscillator().dynamics(0, np.array([-1, 0, -2, 0]))
    np.testing.assert_allclose(derivative, [20, 0, 30, 0])


def test_time_scaling_preserves_state_curve() -> None:
    times = np.linspace(0, 0.4, 21)
    initial = np.array([0.1, 0, -0.1, 0])
    original = MatsuokaOscillator().simulate(times, initial)
    slow = MatsuokaOscillator(MatsuokaParameters(tau=(0.2, 0.6)))
    np.testing.assert_allclose(slow.simulate(2 * times, initial), original, atol=2e-7)


def test_scaled_drive_and_initial_preserve_time_dependence() -> None:
    times = np.linspace(0, 0.4, 21)
    initial = np.array([0.1, 0, -0.1, 0])
    original = MatsuokaOscillator().simulate(times, initial)
    scaled = MatsuokaOscillator(MatsuokaParameters(drive=3))
    np.testing.assert_allclose(scaled.simulate(times, 3 * initial), 3 * original, atol=2e-7)


def test_integration_failure_is_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    from types import SimpleNamespace

    def failed_solver(*args: Any, **kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(success=False)

    monkeypatch.setitem(_EXTRACTED, "solve_ivp", failed_solver)
    with pytest.raises(RuntimeError, match="failed"):
        MatsuokaOscillator().simulate(np.array([0, 1]), np.zeros(4))


@pytest.mark.parametrize("state", [np.zeros(3), np.array([0, 0, 0, np.nan])])
def test_dynamics_rejects_invalid_state(state: np.ndarray) -> None:
    with pytest.raises(ValueError):
        MatsuokaOscillator().dynamics(0, state)


def test_reject_tau_invalid_length_or_values() -> None:
    with pytest.raises((ValueError, TypeError)):
        MatsuokaParameters(tau=(0.1,))  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        MatsuokaParameters(tau=(-0.1, 0.2))
    with pytest.raises(ValueError):
        MatsuokaParameters(tau=(0.0, 0.2))
    with pytest.raises(ValueError):
        MatsuokaParameters(tau=(float("nan"), 0.2))


def test_reject_negative_or_nonfinite_scalars() -> None:
    with pytest.raises(ValueError):
        MatsuokaParameters(adaptation=-0.1)
    with pytest.raises(ValueError):
        MatsuokaParameters(inhibition=-1.0)
    with pytest.raises(ValueError):
        MatsuokaParameters(drive=-0.01)
    with pytest.raises(ValueError):
        MatsuokaParameters(drive=float("inf"))


def test_dynamics_returns_four_finite_floats() -> None:
    osc = MatsuokaOscillator()
    deriv = osc.dynamics(0.0, np.array([0.5, 0.2, 0.1, 0.0]))
    assert len(deriv) == 4
    assert np.isfinite(deriv).all()


def test_no_drive_zero_state_remains_zero() -> None:
    osc = MatsuokaOscillator(MatsuokaParameters(drive=0.0))
    zero_state = np.zeros(4, dtype=float)
    deriv = np.asarray(osc.dynamics(0.0, zero_state), dtype=float)
    np.testing.assert_allclose(deriv, np.zeros(4), atol=1e-12)


def test_independent_derivatives_calculation() -> None:
    p = MatsuokaParameters(tau=(0.2, 0.5), adaptation=2.0, inhibition=1.5, drive=1.0)
    osc = MatsuokaOscillator(p)
    state = np.array([1.0, 0.4, 0.6, 0.2])
    expected = np.array([-8.5, 1.2, -7.5, 0.8])
    actual = np.asarray(osc.dynamics(0.0, state), dtype=float)
    np.testing.assert_allclose(actual, expected, atol=1e-10)


def test_symmetric_state_produces_symmetric_derivatives() -> None:
    osc = MatsuokaOscillator(MatsuokaParameters(drive=1.0))
    symm_state = np.array([0.4, 0.2, 0.4, 0.2])
    deriv = np.asarray(osc.dynamics(0.0, symm_state), dtype=float)
    assert math.isclose(deriv[0], deriv[2], rel_tol=1e-9, abs_tol=1e-12)
    assert math.isclose(deriv[1], deriv[3], rel_tol=1e-9, abs_tol=1e-12)


def test_positive_homogeneity_when_drive_and_state_scaled() -> None:
    p1 = MatsuokaParameters(drive=1.0)
    p2 = MatsuokaParameters(drive=3.0)
    osc1, osc2 = MatsuokaOscillator(p1), MatsuokaOscillator(p2)
    state1 = np.array([0.5, 0.2, 0.3, 0.1])
    state2 = 3.0 * state1
    d1 = np.asarray(osc1.dynamics(0.0, state1), dtype=float)
    d2 = np.asarray(osc2.dynamics(0.0, state2), dtype=float)
    np.testing.assert_allclose(d2, 3.0 * d1, rtol=1e-10)


def test_common_tau_time_scaling() -> None:
    p_orig = MatsuokaParameters(tau=(0.1, 0.2))
    p_scaled = MatsuokaParameters(tau=(0.2, 0.4))
    osc1, osc2 = MatsuokaOscillator(p_orig), MatsuokaOscillator(p_scaled)
    state = np.array([0.6, 0.3, 0.2, 0.5])
    d1 = np.asarray(osc1.dynamics(0.0, state), dtype=float)
    d2 = np.asarray(osc2.dynamics(0.0, state), dtype=float)
    np.testing.assert_allclose(d1, 2.0 * d2, rtol=1e-10)


def test_simulate_shape_and_endpoint_included() -> None:
    osc = MatsuokaOscillator()
    t = np.linspace(0.0, 1.0, 11)
    init = np.array([0.1, 0.0, 0.0, 0.0])
    res = osc.simulate(t, init)
    assert res.shape == (4, 11)
    assert np.all(np.isfinite(res))
    np.testing.assert_allclose(res[:, 0], init, atol=1e-9)


def test_simulate_zero_drive_zero_initial_stays_zero() -> None:
    osc = MatsuokaOscillator(MatsuokaParameters(drive=0.0))
    t = np.linspace(0.0, 2.0, 21)
    res = osc.simulate(t, np.zeros(4))
    np.testing.assert_allclose(res, np.zeros((4, 21)), atol=1e-10)


def test_simulate_rejects_times_not_starting_at_zero() -> None:
    osc = MatsuokaOscillator()
    with pytest.raises(ValueError):
        osc.simulate(np.array([0.1, 0.2, 0.3]), np.zeros(4))


def test_simulate_rejects_times_not_strictly_increasing() -> None:
    osc = MatsuokaOscillator()
    with pytest.raises(ValueError):
        osc.simulate(np.array([0.0, 0.2, 0.2]), np.zeros(4))
    with pytest.raises(ValueError):
        osc.simulate(np.array([0.0, 0.3, 0.1]), np.zeros(4))


def test_simulate_rejects_times_length_less_than_two() -> None:
    osc = MatsuokaOscillator()
    with pytest.raises(ValueError):
        osc.simulate(np.array([0.0]), np.zeros(4))


def test_simulate_rejects_times_non_1d_or_nonfinite() -> None:
    osc = MatsuokaOscillator()
    with pytest.raises(ValueError):
        osc.simulate(np.array([[0.0, 0.1], [0.2, 0.3]]), np.zeros(4))
    with pytest.raises(ValueError):
        osc.simulate(np.array([0.0, float("nan")]), np.zeros(4))


def test_simulate_rejects_invalid_initial_state() -> None:
    osc = MatsuokaOscillator()
    t = np.array([0.0, 1.0])
    with pytest.raises(ValueError):
        osc.simulate(t, np.array([0.0, 1.0, 2.0]))
    with pytest.raises(ValueError):
        osc.simulate(t, np.array([0.0, 0.0, 0.0, float("inf")]))


def test_simulate_copies_initial_state_and_does_not_mutate() -> None:
    osc = MatsuokaOscillator()
    init = np.array([0.5, 0.1, 0.2, 0.3])
    init_copy = init.copy()
    res = osc.simulate(np.linspace(0.0, 0.5, 5), init)
    np.testing.assert_array_equal(init, init_copy)
    res[0, 0] = 999.0
    assert init[0] != 999.0


def test_symmetric_initial_state_yields_symmetric_trajectory() -> None:
    osc = MatsuokaOscillator()
    t = np.linspace(0.0, 0.5, 6)
    init = np.array([0.2, 0.1, 0.2, 0.1])
    res = osc.simulate(t, init)
    np.testing.assert_allclose(res[0, :], res[2, :], atol=1e-7)
    np.testing.assert_allclose(res[1, :], res[3, :], atol=1e-7)
