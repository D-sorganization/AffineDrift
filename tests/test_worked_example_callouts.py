"""Recompute the numbers in each `.callout-example` worked example from src/.

Issue #4511 adopts a `.callout-example` convention (given data, steps, result)
and requires at least eight worked examples -- one in each theory part, plus
DCR, ZTCF and superposition -- whose numbers are reproducible from src/. Each
callout claims "checked against this page", so every test below parses the
callout's own Given and Result lines out of the .qmd source and compares them
against values recomputed from src/, instead of hard-coding constants that
could silently drift from what the page actually says.
"""

import re
from pathlib import Path

import numpy as np
import pytest

from src.affine_control.dynamics import (
    constrained_affine_fields,
    double_pendulum_coriolis,
    double_pendulum_mass_matrix,
    spatial_inertia,
)
from src.affine_control.golf_model import SEGMENTS, GolfModel
from src.affine_control.reachability import constant_additive_drift_interval
from src.tangent_models.examples import SimplePendulum

ARTICLES_DIR = Path(__file__).resolve().parent.parent / "articles"

WORKED_EXAMPLE_PAGES = (
    "theory-part1.qmd",
    "theory-part2.qmd",
    "theory-part3.qmd",
    "theory-part4.qmd",
    "theory-part5.qmd",
    "drift-control-ratio.qmd",
    "zero-torque-counterfactual.qmd",
    "superposition.qmd",
)

_NUMBER_RE = re.compile(r"-?\d+\.?\d*")


def _callout_block(page: str) -> str:
    """Return the body of the single `.callout-example` div on `page`."""
    text = (ARTICLES_DIR / page).read_text(encoding="utf-8")
    match = re.search(r"::: \{\.callout-example\}(.*?)\n:::", text, re.S)
    assert match, f"no .callout-example block found in {page}"
    return match.group(1)


def _field(block: str, label: str) -> str:
    """Return the single-paragraph text following `**<label>:**` in a callout."""
    match = re.search(rf"\*\*{label}:\*\*(.*?)\n\n", block, re.S)
    assert match, f"no **{label}:** paragraph found in callout block"
    return match.group(1)


def _capture(pattern: str, text: str) -> str:
    match = re.search(pattern, text)
    assert match, f"pattern {pattern!r} not found in {text!r}"
    return match.group(1)


def _numbers(s: str) -> list[str]:
    """Pull decimal number tokens out of a LaTeX comma list, keeping their precision."""
    return _NUMBER_RE.findall(s)


def _fractions(s: str) -> list[float]:
    """Parse a comma list that may contain LaTeX fractions such as `1/3`."""
    values = []
    for token in s.split(","):
        token = token.strip()
        if "/" in token:
            num, den = token.split("/")
            values.append(float(num) / float(den))
        else:
            values.append(float(_NUMBER_RE.search(token).group()))
    return values


def _assert_token_matches(computed: float, token: str) -> None:
    """Compare a recomputed value against a displayed token at its own precision."""
    places = len(token.split(".")[1]) if "." in token else 0
    atol = 0.5 * 10 ** (-places) if places else 0.5
    assert float(computed) == pytest.approx(float(token), abs=atol)


def _assert_tokens_match(computed, tokens: list[str]) -> None:
    assert len(computed) == len(tokens)
    for value, token in zip(computed, tokens, strict=True):
        _assert_token_matches(value, token)


def test_at_least_eight_worked_example_callouts_are_published():
    pages_with_callout = [
        page
        for page in WORKED_EXAMPLE_PAGES
        if "{.callout-example}" in (ARTICLES_DIR / page).read_text(encoding="utf-8")
    ]
    assert len(pages_with_callout) >= 8


def test_theory_part1_spatial_inertia():
    block = _callout_block("theory-part1.qmd")
    given = _field(block, "Given")
    result = _field(block, "Result")

    mass = float(_capture(r"m=(-?\d+\.?\d*)", given))
    com = [float(v) for v in _numbers(_capture(r"c=\(([^)]*)\)", given))]
    inertia_diag = [
        float(v) for v in _numbers(_capture(r"I_c=\\operatorname\{diag\}\(([^)]*)\)", given))
    ]

    spatial = spatial_inertia(mass, np.array(com), np.diag(inertia_diag))
    computed = np.diag(spatial[:3, :3])

    result_tokens = _numbers(_capture(r"M_\{1:3,1:3\}\)=\(([^)]*)\)", result))
    _assert_tokens_match(computed, result_tokens)


def test_theory_part2_pointwise_ztcf_sample():
    block = _callout_block("theory-part2.qmd")
    given = _field(block, "Given")
    result = _field(block, "Result")

    q_deg = [float(v) for v in _numbers(_capture(r"\$q=\(([^)]*)\)\$", given))]
    qd = [float(v) for v in _numbers(_capture(r"\\dot q=\(([^)]*)\)", given))]

    computed = SEGMENTS.drift_acceleration(np.deg2rad(q_deg), np.array(qd))

    result_tokens = _numbers(_capture(r"f\(x\(t_b\)\)\\approx\(([^)]*)\)", result))
    _assert_tokens_match(computed, result_tokens)


def test_theory_part3_constrained_acceleration_map():
    block = _callout_block("theory-part3.qmd")
    given = _field(block, "Given")
    result = _field(block, "Result")

    mass_diag = [
        float(v) for v in _numbers(_capture(r"M=\\operatorname\{diag\}\(([^)]*)\)", given))
    ]
    jacobian = [float(v) for v in _numbers(_capture(r"J=\(([^)]*)\)", given))]
    delta_u = [float(v) for v in _numbers(_capture(r"\\delta u=\(([^)]*)\)", given))]

    drift, field = constrained_affine_fields(
        mass_matrix=np.diag(mass_diag),
        bias=np.array([0.0, 0.0]),
        input_matrix=np.eye(2),
        constraint_jacobian=np.array([jacobian]),
        constraint_bias=np.array([0.0]),
    )
    delta_a = field @ np.array(delta_u)

    drift_tokens = _numbers(_capture(r"drift \$=\(([^)]*)\)\$", result))
    _assert_tokens_match(drift, drift_tokens)

    delta_a_expected = _fractions(_capture(r"\\delta a=\(([^)]*)\)", result))
    np.testing.assert_allclose(delta_a, delta_a_expected, atol=1e-9)


def test_theory_part4_rigid_pendulum():
    block = _callout_block("theory-part4.qmd")
    given = _field(block, "Given")
    result = _field(block, "Result")

    mass = float(_capture(r"m=(-?\d+\.?\d*)", given))
    length = float(_capture(r"L=(-?\d+\.?\d*)", given))
    gravity = float(_capture(r"g=(-?\d+\.?\d*)", given))
    theta = float(_capture(r"\\theta=(-?\d+\.?\d*)", given))
    theta_dot = float(_capture(r"\\dot\\theta=(-?\d+\.?\d*)", given))

    pendulum = SimplePendulum(m=mass, L=length, g=gravity)
    state = np.array([theta, theta_dot])
    control = np.array([0.0])

    xdot = pendulum.dynamics(state, control)
    xdot_tokens = _numbers(_capture(r"\\dot x=\(([^)]*)\)", result))
    _assert_tokens_match(xdot, xdot_tokens)

    a_matrix, b_matrix = pendulum.linearize(state, control)

    a_content = _capture(r"A=\\begin\{bmatrix\}(.*?)\\end\{bmatrix\}", result)
    a_rows = [row.split("&") for row in a_content.split(r"\\")]
    for row_index, row_tokens in enumerate(a_rows):
        _assert_tokens_match(a_matrix[row_index], row_tokens)

    b_content = _capture(r"B=\\begin\{bmatrix\}(.*?)\\end\{bmatrix\}", result)
    b_tokens = b_content.split(r"\\")
    _assert_tokens_match(b_matrix[:, 0], b_tokens)


def test_theory_part5_forward_ztcf_trajectory():
    block = _callout_block("theory-part5.qmd")
    given = _field(block, "Given")
    result = _field(block, "Result")

    q_deg = [float(v) for v in _numbers(_capture(r"\$q=\(([^)]*)\)\$", given))]
    qd = [float(v) for v in _numbers(_capture(r"\\dot q=\(([^)]*)\)", given))]
    duration = float(_capture(r"for \$(-?\d+\.?\d*)\$ s", given))
    steps = int(_capture(r"in \$(\d+)\$ steps", given))

    trajectory = SEGMENTS.ztcf_trajectory(
        np.deg2rad(q_deg), np.array(qd), duration=duration, steps=steps
    )
    start_speed = trajectory[0][3]
    end_speed = trajectory[-1][3]
    pct_change = 100.0 * (end_speed / start_speed - 1.0)

    start_token = _capture(r"from \$(-?\d+\.?\d*)\$ m/s", result)
    end_token = _capture(r"to \$(-?\d+\.?\d*)\$ m/s", result)
    pct_token = _capture(r"a \$(-?\d+\.?\d*)\\%\$ change", result)

    _assert_token_matches(start_speed, start_token)
    _assert_token_matches(end_speed, end_token)
    _assert_token_matches(pct_change, pct_token)


def test_dcr_reachable_width_independent_of_drift():
    block = _callout_block("drift-control-ratio.qmd")
    given = _field(block, "Given")
    result = _field(block, "Result")

    x0 = float(_capture(r"x_0=(-?\d+\.?\d*)", given))
    u_bar = float(_capture(r"\\bar u=(-?\d+\.?\d*)", given))
    horizon = float(_capture(r"T=(-?\d+\.?\d*)", given))
    d1 = float(_capture(r"compare \$d=(-?\d+\.?\d*)\$", given))
    d2 = float(_capture(r"against \$d=(-?\d+\.?\d*)\$", given))

    zero_drift = constant_additive_drift_interval(x0, d1, u_bar, horizon)
    high_drift = constant_additive_drift_interval(x0, d2, u_bar, horizon)

    interval1_tokens = _numbers(_capture(r"d=0\\Rightarrow\[([^\]]*)\]", result))
    interval2_tokens = _numbers(_capture(r"d=100\\Rightarrow\[([^\]]*)\]", result))
    _assert_tokens_match(zero_drift, interval1_tokens)
    _assert_tokens_match(high_drift, interval2_tokens)

    width_token = _capture(r"width stays \$(-?\d+\.?\d*)\$", result)
    _assert_token_matches(zero_drift[1] - zero_drift[0], width_token)
    _assert_token_matches(high_drift[1] - high_drift[0], width_token)


def test_ztcf_pointwise_sample_at_rest():
    block = _callout_block("zero-torque-counterfactual.qmd")
    given = _field(block, "Given")
    result = _field(block, "Result")

    q = [float(v) for v in _numbers(_capture(r"\$q=\(([^)]*)\)\$", given))]
    qd = [float(v) for v in _numbers(_capture(r"\\dot q=\(([^)]*)\)", given))]

    model = GolfModel()
    computed = model.drift_acceleration(np.array(q), np.array(qd))

    result_tokens = _numbers(_capture(r"f\(x\)\\approx\(([^)]*)\)", result))
    _assert_tokens_match(computed, result_tokens)


def test_superposition_theorem_double_pendulum():
    block = _callout_block("superposition.qmd")
    given = _field(block, "Given")
    result = _field(block, "Result")

    assert "gravity" in given.lower(), "Given line must state whether gravity is included"

    common = float(_capture(r"m_1=m_2=l_1=l_2=(-?\d+\.?\d*)", given))
    q = [float(v) for v in _numbers(_capture(r"\$q=\(([^)]*)\)\$", given))]
    qd = [float(v) for v in _numbers(_capture(r"\\dot q=\(([^)]*)\)", given))]
    tau1 = [float(v) for v in _numbers(_capture(r"\\tau_1=\(([^)]*)\)", given))]
    tau2 = [float(v) for v in _numbers(_capture(r"\\tau_2=\(([^)]*)\)", given))]

    mass_matrix = double_pendulum_mass_matrix(np.array(q), common, common, common, common)
    bias = double_pendulum_coriolis(np.array(q), np.array(qd), common, common, common) @ np.array(
        qd
    )

    def phi(tau: list[float]) -> np.ndarray:
        return np.linalg.solve(mass_matrix, np.asarray(tau, dtype=float) - bias)

    baseline = phi([0.0, 0.0])
    phi_tau1 = phi(tau1)
    phi_tau2 = phi(tau2)
    combined = phi([tau1[0] + tau2[0], tau1[1] + tau2[1]])

    _assert_tokens_match(baseline, _numbers(_capture(r"\\Phi\(0\)=\(([^)]*)\)", result)))
    _assert_tokens_match(phi_tau1, _numbers(_capture(r"\\Phi\(\\tau_1\)=\(([^)]*)\)", result)))
    _assert_tokens_match(phi_tau2, _numbers(_capture(r"\\Phi\(\\tau_2\)=\(([^)]*)\)", result)))
    _assert_tokens_match(
        combined, _numbers(_capture(r"\\Phi\(\\tau_1\+\\tau_2\)=\(([^)]*)\)", result))
    )
    np.testing.assert_allclose(phi_tau1 + phi_tau2 - baseline, combined, atol=1e-9)
