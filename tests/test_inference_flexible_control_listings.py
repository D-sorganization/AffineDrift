"""Independent benchmarks and failure contracts for three published listings."""

import re
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest

CHAPTERS = (
    Path(__file__).resolve().parents[1] / "articles/The_Geometry_of_Motion/Volume_III/chapters"
)


def listing(name: str) -> dict[str, Any]:
    source = (CHAPTERS / name).read_text(encoding="utf-8")
    blocks = re.findall(r"\\begin\{lstlisting\}[^\n]*\n(.*?)\\end\{lstlisting\}", source, re.S)
    namespace = {"__name__": "textbook_listing"}
    # Repository-owned listings at fixed paths, with no external input.
    # nosemgrep: python.lang.security.audit.exec-detected.exec-detected
    exec("\n".join(blocks), namespace)
    return namespace


@pytest.fixture
def inference() -> dict[str, Any]:
    return listing("ch08_inference.tex")


@pytest.fixture
def beam() -> dict[str, Any]:
    return listing("ch09_deformable_bodies.tex")


@pytest.fixture
def rotor() -> dict[str, Any]:
    return listing("ch10_control_theory_applications.tex")


def problem(ns: Any) -> Any:
    return ns["GaussianProblem"](
        np.array([[1.0], [3.0]]),
        lambda theta: np.full((2, 1), theta[0]),
        np.zeros(1),
        np.eye(1),
        np.eye(1),
    )


def test_gaussian_closed_form(inference: Any) -> None:
    result = inference["map_estimate"](problem(inference), np.zeros(1))
    np.testing.assert_allclose(result, [4 / 3], atol=1e-6)


@pytest.mark.parametrize("bad", [np.array([1.0, 3.0]), np.array([[np.nan], [3.0]])])
def test_gaussian_observation_contract(inference: Any, bad: Any) -> None:
    with pytest.raises(ValueError):
        inference["map_estimate"](replace(problem(inference), observations=bad), np.zeros(1))


def test_gaussian_prediction_shape(inference: Any) -> None:
    task = replace(problem(inference), forward_model=lambda theta: np.array([theta[0]]))
    with pytest.raises(ValueError):
        inference["map_estimate"](task, np.zeros(1))


@pytest.mark.parametrize("cov", [np.zeros((1, 1)), np.array([[-1.0]]), np.eye(2)])
def test_gaussian_covariance_contract(inference: Any, cov: Any) -> None:
    with pytest.raises(ValueError):
        inference["map_estimate"](replace(problem(inference), noise_cov=cov), np.zeros(1))


def test_gaussian_optimizer_failure(inference: Any) -> None:
    inference["minimize"] = lambda *args, **kwargs: SimpleNamespace(
        success=False, message="fixture"
    )
    with pytest.raises(RuntimeError):
        inference["map_estimate"](problem(inference), np.zeros(1))


def test_uniform_cantilever_and_clamped_modes(beam: Any) -> None:
    params = beam["BeamParameters"](1.0, 1.0, 1.0, 1.0)
    frequency, modes = beam["shaft_modal_analysis"](params, 24)
    exact = np.array([1.8751040687, 4.6940911330, 7.8547574382]) ** 2 / (2 * np.pi)
    np.testing.assert_allclose(frequency[:3], exact, rtol=3e-5)
    assert modes.shape == (50, 6)
    np.testing.assert_array_equal(modes[:2], np.zeros((2, 6)))


def test_beam_scaling_and_tip_mass(beam: Any) -> None:
    params = beam["BeamParameters"](1.0, 1.0, 1.0, 1.0)
    calc = beam["shaft_modal_analysis"]
    base = calc(params)[0]
    np.testing.assert_allclose(
        calc(replace(params, rigidity_root=4, rigidity_tip=4))[0], 2 * base, rtol=1e-7
    )
    np.testing.assert_allclose(calc(replace(params, length=2))[0], base / 4, rtol=1e-7)
    assert np.all(calc(replace(params, tip_mass=0.2))[0] <= base)


@pytest.mark.parametrize(
    "field,value",
    [("length", 0), ("rigidity_tip", -1), ("mass_per_length", np.nan), ("tip_mass", -1)],
)
def test_beam_parameter_contract(beam: Any, field: Any, value: Any) -> None:
    params = beam["BeamParameters"](1.0, 1.0, 1.0, 1.0)
    with pytest.raises(ValueError):
        beam["shaft_modal_analysis"](replace(params, **{field: value}))


def test_negative_eigenvalue_is_not_frequency(beam: Any) -> None:
    beam["eigh"] = lambda *args, **kwargs: (np.array([-1.0]), np.ones((4, 1)))
    with pytest.raises(ValueError):
        beam["shaft_modal_analysis"](beam["BeamParameters"](1, 1, 1, 1))


def test_rotor_constant_excitation_analytic(rotor: Any) -> None:
    params = rotor["RotorParameters"](2.0, 0.1, 20.0, 0.05)
    times = np.linspace(0, 0.5, 101)
    initial = np.array([0.3, -0.1, 0.2, 0.1])
    result = rotor["simulate_rotor"](lambda t: np.array([0.7, 0.3]), times, initial, params)
    activation = np.array([0.7, 0.3]) + (initial[2:] - [0.7, 0.3]) * np.exp(-times[:, None] / 0.05)
    np.testing.assert_allclose(result["a"], activation, atol=1e-8)
    velocity = -0.1 + 0.4 * times - 0.3 * 0.05 * (1 - np.exp(-times / 0.05))
    position = (
        0.3
        - 0.1 * times
        + 0.2 * times**2
        - 0.3 * 0.05 * (times - 0.05 * (1 - np.exp(-times / 0.05)))
    )
    np.testing.assert_allclose(result["q"], position, atol=1e-8)
    np.testing.assert_allclose(result["qdot"], velocity, atol=1e-8)
    np.testing.assert_allclose(result["tau"], 2 * (activation[:, 0] - activation[:, 1]), atol=1e-8)


@pytest.mark.parametrize("bad", [np.array([1.1, 0]), np.array([np.nan, 0]), np.zeros(3)])
def test_rotor_excitation_contract(rotor: Any, bad: Any) -> None:
    with pytest.raises(ValueError):
        rotor["simulate_rotor"](
            lambda t: bad, np.array([0, 0.1]), np.zeros(4), rotor["RotorParameters"](1, 1, 1, 0.1)
        )


def test_rotor_time_and_initial_contract(rotor: Any) -> None:
    params = rotor["RotorParameters"](1, 1, 1, 0.1)
    for times, initial in [
        (np.array([0, 0]), np.zeros(4)),
        (np.array([0, 1]), np.array([0, 0, -0.1, 0])),
    ]:
        with pytest.raises(ValueError):
            rotor["simulate_rotor"](lambda t: np.zeros(2), times, initial, params)


def test_rotor_solver_failure(rotor: Any) -> None:
    rotor["solve_ivp"] = lambda *args, **kwargs: SimpleNamespace(success=False, message="fixture")
    with pytest.raises(RuntimeError):
        rotor["simulate_rotor"](
            lambda t: np.zeros(2),
            np.array([0, 0.1]),
            np.zeros(4),
            rotor["RotorParameters"](1, 1, 1, 0.1),
        )


def test_correlated_gaussian_posterior(inference: Any) -> None:
    design = np.array([[1.0, 2.0], [3.0, 1.0]])
    noise = np.array([[0.5, 0.1], [0.1, 0.2]])
    prior = np.array([[2.0, 0.4], [0.4, 1.0]])
    mean = np.array([1.0, 2.0])
    observation = np.array([4.0, 7.5])
    precision = np.linalg.solve(prior, np.eye(2)) + design.T @ np.linalg.solve(noise, design)
    expected = np.linalg.solve(
        precision, np.linalg.solve(prior, mean) + design.T @ np.linalg.solve(noise, observation)
    )
    task = inference["GaussianProblem"](
        observation[None, :], lambda theta: (design @ theta)[None, :], mean, prior, noise
    )
    np.testing.assert_allclose(inference["map_estimate"](task, mean), expected, atol=2e-6)


def test_beam_modal_mass_and_static_compliance(beam: Any) -> None:
    params = beam["BeamParameters"](1, 1, 1, 1, 0.2)
    stiffness, mass = beam["beam_matrices"](params, 12)
    frequencies, modes = beam["shaft_modal_analysis"](params, 12)
    np.testing.assert_allclose(modes.T @ mass @ modes, np.eye(6), atol=1e-10)
    load = np.zeros(mass.shape[0] - 2)
    load[-2] = 0.001
    displacement = np.linalg.solve(stiffness[2:, 2:], load)
    np.testing.assert_allclose(displacement[-2], 0.001 / 3, rtol=1e-8)
    residual = (
        stiffness[2:, 2:] @ modes[2:] - mass[2:, 2:] @ modes[2:] * (2 * np.pi * frequencies) ** 2
    )
    assert np.linalg.norm(residual) / np.linalg.norm(stiffness[2:, 2:] @ modes[2:]) < 1e-8


def test_gaussian_bound_mode(inference: Any) -> None:
    task = replace(problem(inference), bounds=[(0, 1)])
    np.testing.assert_allclose(inference["map_estimate"](task, np.array([0.5])), [1])


def test_tip_mass_boundary_frequency(beam: Any) -> None:
    from scipy.optimize import brentq

    ratio = 0.2

    def characteristic(beta: float) -> float:
        return (
            1
            + np.cos(beta) * np.cosh(beta)
            + ratio * beta * (np.cos(beta) * np.sinh(beta) - np.sin(beta) * np.cosh(beta))
        )

    root = brentq(characteristic, 0.1, 1.8751040687)
    frequency = beam["shaft_modal_analysis"](beam["BeamParameters"](1, 1, 1, 1, ratio), 24)[0][0]
    np.testing.assert_allclose(frequency, root**2 / (2 * np.pi), rtol=2e-6)
