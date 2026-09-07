"""Independent energy checks for the applications teaching model."""

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import eigvalsh, expm

from scripts.generate_worked_examples import render_ch08
from src.affine_control.golf_model import SEGMENTS, GolfModel

GRAVITY_M_S2 = 9.81


@pytest.mark.parametrize("mode", [0, 1])
def test_mode_amplitude_is_the_signed_tip_displacement(mode: int) -> None:
    values = SEGMENTS.mode_shape(mode, np.array([0.0, SEGMENTS.lengths[2]]))
    np.testing.assert_allclose(values, [0.0, 1.0], atol=1e-9)


def test_full_inertia_accounts_for_every_shaft_material_point() -> None:
    q = np.array([0.4, -0.7, 0.2])
    velocity = np.array([0.8, -0.5, 0.9, 0.06, -0.02])
    samples = 4001
    s = np.linspace(0.0, SEGMENTS.lengths[2], samples)
    angles = np.cumsum(q)
    normal = np.array([-np.sin(angles[-1]), np.cos(angles[-1])])
    handle_velocity = np.zeros(2)
    for index in range(2):
        handle_velocity += (
            SEGMENTS.lengths[index]
            * np.sum(velocity[: index + 1])
            * np.array([-np.sin(angles[index]), np.cos(angles[index])])
        )
    bending_rate = sum(SEGMENTS.mode_shape(mode, s) * velocity[3 + mode] for mode in range(2))
    material_velocity = handle_velocity[:, None] + normal[:, None] * (
        np.sum(velocity[:3]) * s + bending_rate
    )
    shaft_energy = (
        0.5
        * SEGMENTS.shaft_mass
        / SEGMENTS.lengths[2]
        * np.trapezoid(np.sum(material_velocity**2, axis=0), s)
    )
    rigid_energy = 0.5 * velocity[:3] @ SEGMENTS.rigid_mass_matrix(q) @ velocity[:3]
    assembled_energy = 0.5 * velocity @ SEGMENTS.full_mass_matrix(q, samples) @ velocity
    assert assembled_energy == pytest.approx(rigid_energy + shaft_energy, rel=1e-11)


def test_added_shaft_mass_changes_rotational_inertia() -> None:
    q = np.array([0.4, -0.7, 0.2])
    heavy = replace(SEGMENTS, shaft_mass=2 * SEGMENTS.shaft_mass)
    increment = heavy.full_mass_matrix(q) - SEGMENTS.full_mass_matrix(q)
    expected_distal = SEGMENTS.shaft_mass * SEGMENTS.lengths[2] ** 2 / 3
    assert increment[2, 2] == pytest.approx(expected_distal, rel=1e-6)
    assert np.linalg.eigvalsh(increment).min() > -1e-10


def test_a_light_carrier_does_not_make_a_positive_mass_shaft_indefinite() -> None:
    model = GolfModel(masses=(0.01, 0.01, 0.01), inertias=(0.001, 0.001, 0.001))
    assert np.linalg.eigvalsh(model.full_mass_matrix(np.zeros(3))).min() > 0


def test_rigid_counterfactual_preserves_its_declared_mechanical_energy() -> None:
    q = np.array([0.4, -0.7, 0.2])
    velocity = np.array([0.8, -0.5, 0.9])
    step = 1e-6
    mass = SEGMENTS.rigid_mass_matrix(q)
    mass_rate = (
        SEGMENTS.rigid_mass_matrix(q + step * velocity)
        - SEGMENTS.rigid_mass_matrix(q - step * velocity)
    ) / (2 * step)
    potential_rate = (
        SEGMENTS.potential_energy(q + step * velocity)
        - SEGMENTS.potential_energy(q - step * velocity)
    ) / (2 * step)
    energy_rate = (
        velocity @ mass @ SEGMENTS.drift_acceleration(q, velocity)
        + 0.5 * velocity @ mass_rate @ velocity
        + potential_rate
    )
    assert energy_rate == pytest.approx(0, abs=1e-7)


def test_modal_spring_is_symmetric_and_positive() -> None:
    stiffness = SEGMENTS.modal_stiffness()
    np.testing.assert_allclose(stiffness, stiffness.T, atol=1e-12)
    assert np.linalg.eigvalsh(stiffness).min() > 0


def test_generator_distinguishes_the_two_inertias_and_acceleration_units() -> None:
    fragment = render_ch08(SEGMENTS)
    assert r"\cheightFlexibleMqq" in fragment
    assert r"\rho_{\text{DCR}}" not in fragment
    assert r"\|a_{\mathrm{drift}}\|_2" in fragment


@pytest.mark.parametrize("extension", ["tex", "qmd"])
def test_both_editions_declare_model_and_evidence_boundaries(extension: str) -> None:
    root = Path(__file__).resolve().parents[1] / "articles/The_Geometry_of_Motion"
    folder = "Volume_I/chapters" if extension == "tex" else "quarto"
    source = (root / folder / f"ch08_applications.{extension}").read_text(encoding="utf-8")
    assert "A Rigid Counterfactual Is a Different Model" in source
    assert "A Position Pullback Has a Nullspace" in source
    assert "Quadratic Effort Is Not Propellant Consumption" in source
    assert "A Speed Schedule Requires Its Own Dynamics" in source
    assert r"observations within 15\%" not in source


@pytest.mark.parametrize("q", [np.zeros(3), np.array([0.4, -0.7, 0.2])])
def test_printed_rigid_inertia_matches_cartesian_assembly(q: np.ndarray) -> None:
    m1, m2, m3 = SEGMENTS.masses
    l1, l2, _ = SEGMENTS.lengths
    r1, r2, r3 = SEGMENTS.com_offsets()
    i1, i2, i3 = SEGMENTS.inertias
    a = i1 + i2 + i3 + m1 * r1**2 + m2 * (l1**2 + r2**2) + m3 * (l1**2 + l2**2 + r3**2)
    b = i2 + i3 + m2 * r2**2 + m3 * (l2**2 + r3**2)
    d = i3 + m3 * r3**2
    h = l1 * (m2 * r2 + m3 * l2) * np.cos(q[1])
    j = m3 * l1 * r3 * np.cos(q[1] + q[2])
    k = m3 * l2 * r3 * np.cos(q[2])
    displayed = np.array(
        [
            [a + 2 * (h + j + k), b + h + j + 2 * k, d + j + k],
            [b + h + j + 2 * k, b + 2 * k, d + k],
            [d + j + k, d + k, d],
        ]
    )
    np.testing.assert_allclose(displayed, SEGMENTS.rigid_mass_matrix(q), atol=1e-12)


def test_schur_solution_retains_the_nonzero_modal_bias() -> None:
    mass = SEGMENTS.full_mass_matrix(np.array([0.4, -0.7, 0.2]))
    a, c, d = mass[:3, :3], mass[:3, 3:], mass[3:, 3:]
    hq, heta = np.array([0.7, -0.2, 1.1]), np.array([0.03, -0.08])
    torque = np.array([0.9, -0.6, 0.1])
    gamma = -np.linalg.solve(d, c.T)
    qdd = np.linalg.solve(a + c @ gamma, torque - hq + c @ np.linalg.solve(d, heta))
    etadd = -np.linalg.solve(d, heta) + gamma @ qdd
    np.testing.assert_allclose(
        mass @ np.concatenate([qdd, etadd]), np.concatenate([torque - hq, -heta]), atol=1e-12
    )


def test_circle_inverse_kinematics_and_position_nullspace() -> None:
    for time in np.linspace(0, 2, 81):
        target = np.array([0.45 + 0.05 * np.cos(np.pi * time), 0.15 + 0.05 * np.sin(np.pi * time)])
        psi = np.pi / 4
        wrist = target - 0.3 * np.array([np.cos(psi), np.sin(psi)])
        q2 = np.arccos((wrist @ wrist - 0.18) / 0.18)
        q1 = np.arctan2(wrist[1], wrist[0]) - np.arctan2(np.sin(q2), 1 + np.cos(q2))
        angles = np.array([q1, q1 + q2, psi])
        tip = 0.3 * np.array([np.cos(angles).sum(), np.sin(angles).sum()])
        np.testing.assert_allclose(tip, target, atol=1e-12)
        jacobian = np.column_stack(
            [
                0.3 * np.array([-np.sin(angles[j:]).sum(), np.cos(angles[j:]).sum()])
                for j in range(3)
            ]
        )
        assert np.linalg.matrix_rank(jacobian.T @ jacobian) == 2
        assert np.linalg.matrix_rank(np.vstack([jacobian, np.ones(3)])) == 3


def test_exact_riccati_metric_rate_and_embedded_python() -> None:
    a = np.array([[0, 1], [0, 0]])
    b = np.array([[0], [1]])
    s = np.array([[np.sqrt(3), 1], [1, np.sqrt(3)]])
    k = b.T @ s
    closed = a - b @ k
    w = np.eye(2) + k.T @ k
    np.testing.assert_allclose(closed.T @ s + s @ closed, -w, atol=1e-12)
    assert eigvalsh(w, s)[0] == pytest.approx(np.sqrt(3) - 1 / np.sqrt(2))
    source = (
        Path(__file__).resolve().parents[1]
        / "articles/The_Geometry_of_Motion/quarto/ch08_applications.qmd"
    ).read_text(encoding="utf-8")
    example = source.split("```python\n", 1)[1].split("```", 1)[0]
    exec(compile(example, "applications_lqr_example", "exec"), {})


def test_orbit_frequency_reference_and_zero_order_hold() -> None:
    n = np.sqrt(3.98600435507e14 / (6.7e6) ** 3)
    assert 5457 < 2 * np.pi / n < 5459
    a = np.zeros((6, 6))
    a[:3, 3:] = np.eye(3)
    a[3:, :3] = np.diag([3 * n * n, 0, -n * n])
    a[3, 4], a[4, 3] = 2 * n, -2 * n
    b = np.vstack([np.zeros((3, 3)), np.eye(3)])
    for s in np.linspace(0, 1, 11):
        y = 1000 - 990 * (10 * s**3 - 15 * s**4 + 6 * s**5)
        yd = -990 * (30 * s**2 - 60 * s**3 + 30 * s**4) / 900
        ydd = -990 * (60 * s - 180 * s**2 + 120 * s**3) / 900**2
        state = np.array([0, y, 0, 0, yd, 0])
        control = np.array([-2 * n * yd, ydd, 0])
        np.testing.assert_allclose(a @ state + b @ control, [0, yd, 0, 0, ydd, 0], atol=1e-12)
    augmented = np.block([[a, b], [np.zeros((3, 9))]])
    hold = expm(augmented * 10)
    # Integrating a constant held input over two steps must equal one long hold.
    double = expm(augmented * 20)
    np.testing.assert_allclose(hold @ hold, double, atol=1e-12)


@pytest.mark.parametrize("speed", [2.0, 10.0, 25.0])
def test_constant_speed_schedule_preserves_declared_polynomial(speed: float) -> None:
    frequency, damping = 1.3, 0.8
    closed = np.array([[0, speed], [-(frequency**2) / speed, -2 * damping * frequency]])
    np.testing.assert_allclose(np.poly(closed), [1, 2 * damping * frequency, frequency**2])


def test_impact_time_sensitivity_includes_event_shift() -> None:
    # Falling particle: perturb both height and velocity, evaluate at its own ground event.
    height, velocity, gravity = 2.0, -1.0, GRAVITY_M_S2
    event = (velocity + np.sqrt(velocity**2 + 2 * gravity * height)) / gravity
    phi = np.array([[1, event], [0, 1]])
    field = np.array([velocity - gravity * event, -gravity])
    normal = np.array([1, 0])
    jacobian = (np.eye(2) - np.outer(field, normal) / (normal @ field)) @ phi
    step = 1e-6
    numerical = np.zeros((2, 2))
    for axis in range(2):
        results = []
        for sign in [-1, 1]:
            perturbed = np.array([height, velocity]) + sign * step * np.eye(2)[axis]
            impact_velocity = -np.sqrt(perturbed[1] ** 2 + 2 * gravity * perturbed[0])
            results.append(np.array([0, impact_velocity]))
        numerical[:, axis] = (results[1] - results[0]) / (2 * step)
    np.testing.assert_allclose(jacobian, numerical, atol=1e-8)


def test_reported_unforced_trajectory_converges_and_conserves_energy() -> None:
    q, qd = np.deg2rad([60, -30, -20]), np.array([12.0, -18.0, -25.0])
    trajectories = [
        SEGMENTS.ztcf_trajectory(q, qd, 0.1, steps) for steps in [50, 100, 200, 400, 800]
    ]
    ends = [np.concatenate([trajectory[-1][1], trajectory[-1][2]]) for trajectory in trajectories]
    coarse, fine = np.linalg.norm(ends[1] - ends[0]), np.linalg.norm(ends[2] - ends[1])
    assert fine < coarse / 5
    assert fine < 1e-5
    # Finite-difference force evaluation reaches its noise floor at small steps.
    assert np.linalg.norm(ends[4] - ends[3]) < 1e-7
    energy = [
        0.5 * velocity @ SEGMENTS.rigid_mass_matrix(position) @ velocity
        + SEGMENTS.potential_energy(position)
        for _, position, velocity, _ in trajectories[3]
    ]
    assert np.max(np.abs(np.asarray(energy) - energy[0])) / abs(energy[0]) < 1e-6
