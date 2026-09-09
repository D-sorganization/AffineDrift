"""Independent counterexamples for interdisciplinary chapter #4313."""

from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad, solve_ivp

BOOK = Path(__file__).resolve().parents[1] / "articles/The_Physics_of_Golf"
SOURCES = [BOOK / "chapters/ch13_interdisciplinary.tex", BOOK / "quarto/ch13_interdisciplinary.qmd"]


@pytest.mark.parametrize("velocity", [0.0, 10.0, 100.0])
def test_constant_inertia_gain_does_not_decay_with_speed(velocity: float) -> None:
    inertia, horizon, torque = 0.05, 0.1, 0.5
    endpoints = []
    for applied in [0.0, torque]:
        solution = solve_ivp(
            lambda _t, x, applied=applied: [x[1], applied / inertia],
            (0.0, horizon),
            [0.0, velocity],
            rtol=1e-11,
            atol=1e-12,
        )
        endpoints.append(solution.y[:, -1])
    assert endpoints[1] - endpoints[0] == pytest.approx([0.05, 1.0], abs=1e-10)


def test_baseline_feedback_changes_zero_input_intervention() -> None:
    inertia, stiffness, q, residual = 0.05, 2.0, 0.1, 0.4
    original = (-stiffness * q + residual) / inertia
    new_drift, new_input = -stiffness * q / inertia, residual / inertia
    assert original == pytest.approx(new_drift + new_input)
    assert new_drift == pytest.approx(-4.0)
    assert new_drift != 0.0  # Zero residual is a spring policy, not zero torque.


@pytest.mark.parametrize("error,cost", [([0.1, -0.1], 0.28), ([0.2, 0.3], 0.12)])
def test_minimum_energy_uses_gramian_metric(error: list[float], cost: float) -> None:
    target = np.asarray(error)
    gramian = np.array([[1 / 3, 1 / 2], [1 / 2, 1]])
    multiplier = np.linalg.solve(gramian, target)

    def control(time: float) -> float:
        return float(np.array([1 - time, 1]) @ multiplier)

    endpoint = [quad(lambda t: (1 - t) * control(t), 0, 1)[0], quad(control, 0, 1)[0]]
    assert endpoint == pytest.approx(target)
    assert quad(lambda t: control(t) ** 2, 0, 1)[0] == pytest.approx(cost)
    assert target @ multiplier == pytest.approx(cost)


def test_closer_euclidean_endpoint_can_cost_more() -> None:
    errors = np.array([[0.1, -0.1], [0.2, 0.3]])
    inverse = np.array([[12, -6], [-6, 4]])
    assert np.linalg.norm(errors[0]) < np.linalg.norm(errors[1])
    assert errors[0] @ inverse @ errors[0] > errors[1] @ inverse @ errors[1]


def test_printed_optimal_controls_recover_both_endpoint_components() -> None:
    for intercept, slope, endpoint in [(0.8, -1.8, [0.1, -0.1]), (0.6, -0.6, [0.2, 0.3])]:
        position = intercept / 2 + slope / 6
        velocity = intercept + slope / 2
        assert [position, velocity] == pytest.approx(endpoint)
    for source in SOURCES:
        assert "0.8-1.8t" in source.read_text(encoding="utf-8")


def test_time_varying_stiffness_adds_stored_energy_at_fixed_position() -> None:
    displacement = 0.1
    initial_storage = 10 * displacement**2 / 2
    final_storage = 30 * displacement**2 / 2
    assert final_storage - initial_storage == pytest.approx(0.1)
    assert quad(lambda _t: 100 * displacement**2 / 2, 0, 0.2)[0] == pytest.approx(0.1)


def test_task_force_pullback_preserves_mechanical_power() -> None:
    jacobian = np.array([[1.0, 2.0, 0.0], [0.0, -1.0, 3.0]])
    rates, force = np.array([0.3, -0.4, 0.2]), np.array([2.0, -5.0])
    assert force @ (jacobian @ rates) == pytest.approx((jacobian.T @ force) @ rates)


def test_unobserved_input_can_hide_stiffness_even_with_complete_motion() -> None:
    time = np.linspace(0, 1, 101)
    position, acceleration = np.cos(time), -np.cos(time)
    stiffness_a, stiffness_b, inertia = 2.0, 8.0, 0.5
    force_a = inertia * acceleration + stiffness_a * position
    force_b = inertia * acceleration + stiffness_b * position
    assert force_b - force_a == pytest.approx((stiffness_b - stiffness_a) * position)
    assert (force_a - stiffness_a * position) / inertia == pytest.approx(acceleration)
    assert (force_b - stiffness_b * position) / inertia == pytest.approx(acceleration)


def test_equal_net_moments_do_not_identify_compressive_force() -> None:
    forces = np.array([[200.0, 100.0], [500.0, 400.0]])
    assert forces @ np.array([0.03, -0.03]) == pytest.approx([3.0, 3.0])
    assert forces.sum(axis=1) == pytest.approx([300.0, 900.0])


@pytest.mark.parametrize("angle", [0.0, 30.0, 45.0, 90.0])
def test_rotated_ply_stiffness_matches_tensor_transformation(angle: float) -> None:
    e1, e2, nu, shear = 135.0, 10.0, 0.3, 5.0
    compliance = np.array([[1 / e1, -nu / e1, 0], [-nu / e1, 1 / e2, 0], [0, 0, 1 / shear]])
    stiffness = np.linalg.inv(compliance)
    c, s = np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle))
    rotation = np.array([[c, -s], [s, c]])
    measured = []
    for strain in [np.array([[1.0, 0], [0, 0]]), np.array([[0, 0.5], [0.5, 0]])]:
        local = rotation.T @ strain @ rotation
        stress = stiffness @ np.array([local[0, 0], local[1, 1], 2 * local[0, 1]])
        global_stress = (
            rotation @ np.array([[stress[0], stress[2]], [stress[2], stress[1]]]) @ rotation.T
        )
        measured.append(global_stress)
    q11, q22, q12, q66 = stiffness[0, 0], stiffness[1, 1], stiffness[0, 1], stiffness[2, 2]
    expected_axial = q11 * c**4 + 2 * (q12 + 2 * q66) * s * s * c * c + q22 * s**4
    expected_shear = (q11 + q22 - 2 * q12 - 2 * q66) * s * s * c * c + q66 * (s**4 + c**4)
    assert measured[0][0, 0] == pytest.approx(expected_axial)
    assert measured[1][0, 1] == pytest.approx(expected_shear)


@pytest.mark.parametrize("restitution", [0.0, 0.5, 0.83, 1.0])
def test_collision_energy_is_not_restitution_or_smash_factor(restitution: float) -> None:
    mass_head, mass_ball, inbound = 0.2, 0.04593, 45.0
    head, ball = np.linalg.solve(
        [[mass_head, mass_ball], [-1, 1]],
        [mass_head * inbound, restitution * inbound],
    )
    assert ball / inbound == pytest.approx((1 + restitution) * mass_head / (mass_head + mass_ball))
    initial_energy = mass_head * inbound**2 / 2
    final_energy = (mass_head * head**2 + mass_ball * ball**2) / 2
    reduced_mass = mass_head * mass_ball / (mass_head + mass_ball)
    assert initial_energy - final_energy == pytest.approx(
        (1 - restitution**2) * reduced_mass * inbound**2 / 2, abs=1e-12
    )
    if restitution == 0.83:
        ball_fraction = mass_ball * ball**2 / (2 * initial_energy)
        assert ball_fraction == pytest.approx(0.50863425, abs=1e-8)
        assert ball_fraction != pytest.approx(restitution)


def test_publication_keeps_every_display_and_all_eight_worked_answers() -> None:
    tex, web = (source.read_text(encoding="utf-8") for source in SOURCES)
    assert tex.count(r"\[") == 22
    assert web.count("\n$$\n") == 44
    answers = tex.split(r"\section{Worked Answers}", 1)[1]
    exercises = tex.split(r"\section{Chapter Exercises}", 1)[1].split(r"\section{Worked Answers}")[
        0
    ]
    assert answers.count(r"\item ") == exercises.count(r"\item ") == 8


@pytest.mark.parametrize("source", SOURCES, ids=["print", "web"])
def test_both_editions_state_intervention_and_identification_limits(source: Path) -> None:
    text = source.read_text(encoding="utf-8")
    assert "Input Coordinates and the Meaning of Zero" in text
    assert "Minimum Effort Requires a Cost and a Horizon" in text
    assert "unobserved input" in text
    assert "Net Torque Is Not Tissue Load" in text


@pytest.mark.parametrize("source", SOURCES, ids=["print", "web"])
def test_both_editions_have_resolved_exercises_and_measured_evidence(source: Path) -> None:
    text = source.read_text(encoding="utf-8")
    assert "Worked Answers" in text
    for key in [
        "Pink1990Shoulder",
        "Arakawa2006Impact",
        "Robinson2024Injuries",
        "Roylance2000Laminates",
    ]:
        assert key in text
    assert "0.5086" in text
    assert "0.0581" in text
    assert "more aggressive hip rotation" not in text
