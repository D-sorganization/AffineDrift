"""Mathematical fixture test suite for multi-body dynamics and energy accounting."""

from pathlib import Path

import numpy as np
import pytest


def test_planar_rod_kinematics_and_power() -> None:
    """Verify manufactured planar rod kinematics, speed derivative, and wrench power."""
    mass: float = 3.0
    i_com: float = 1.0

    v_com = np.array([1.0, 0.0, 0.0], dtype=np.float64)
    a_com = np.array([-3.0, 0.0, 0.0], dtype=np.float64)
    omega = np.array([0.0, 0.0, 2.0], dtype=np.float64)
    alpha = np.array([0.0, 0.0, 4.0], dtype=np.float64)
    r = np.array([0.0, -1.0, 0.0], dtype=np.float64)

    # Endpoint velocity: v = v_COM + omega x r
    v_endpoint = v_com + np.cross(omega, r)
    # Endpoint acceleration: a = a_COM + alpha x r + omega x (omega x r)
    a_endpoint = a_com + np.cross(alpha, r) + np.cross(omega, np.cross(omega, r))

    # Speed derivative: d/dt ||v|| = (v . a) / ||v||
    speed = float(np.linalg.norm(v_endpoint))
    speed_deriv = float(np.dot(v_endpoint, a_endpoint) / speed)
    assert speed_deriv == pytest.approx(1.0)

    # Kinetic energy rate: d/dt T = m (v_COM . a_COM) + I (omega . alpha)
    trans_power = mass * float(np.dot(v_com, a_com))
    rot_power = i_com * float(np.dot(omega, alpha))
    kinetic_energy_rate = trans_power + rot_power
    assert kinetic_energy_rate == pytest.approx(-1.0)

    # Net wrench power: F . v_COM + M . omega
    net_force = mass * a_com
    net_moment = i_com * alpha
    wrench_power = float(np.dot(net_force, v_com) + np.dot(net_moment, omega))
    assert wrench_power == pytest.approx(-1.0)
    assert wrench_power == pytest.approx(kinetic_energy_rate)


def test_rotor_pair_segment_vs_actuator_power() -> None:
    """Verify segment power sign divergence from relative actuator power."""
    omega_prox: float = 3.0
    omega_dist: float = 1.0
    tau_dist: float = 2.0
    tau_prox: float = -2.0

    power_dist = tau_dist * omega_dist
    power_prox = tau_prox * omega_prox
    total_actuator_power = power_dist + power_prox

    assert power_dist == pytest.approx(2.0)
    assert power_prox == pytest.approx(-6.0)
    assert total_actuator_power == pytest.approx(-4.0)

    # Closed-form actuator power: tau * (omega_dist - omega_prox)
    actuator_relative_power = tau_dist * (omega_dist - omega_prox)
    assert actuator_relative_power == pytest.approx(-4.0)

    # Segment power on distal rotor is positive despite negative actuator power
    assert power_dist > 0.0
    assert total_actuator_power < 0.0


def test_flexible_club_energy_accounting() -> None:
    """Verify closed whole-club energy balance versus subsystem head accounting."""
    w_hand: float = 15.0
    w_aero: float = -2.0
    delta_u_shaft: float = -8.0  # Shaft strain energy released

    # Total external work on complete club
    w_ext = w_hand + w_aero
    delta_total_mech = w_ext
    assert delta_total_mech == pytest.approx(13.0)

    # delta(K + V) = W_ext - delta(U_shaft)
    delta_k_plus_v = w_ext - delta_u_shaft
    assert delta_k_plus_v == pytest.approx(21.0)

    # Energy ledger closure: delta(K + V) + delta(U_shaft) == W_ext
    assert (delta_k_plus_v + delta_u_shaft) == pytest.approx(delta_total_mech)

    # Falsely adding internal shaft strain return to total external mechanical work
    false_total_mech = delta_total_mech + abs(delta_u_shaft)
    assert false_total_mech == pytest.approx(21.0)
    assert false_total_mech != delta_total_mech

    # Shaft-excluded head subsystem
    delta_k_plus_v_shaft: float = 5.0
    delta_mech_shaft = delta_k_plus_v_shaft + delta_u_shaft
    w_interface = w_hand - delta_mech_shaft
    assert w_interface == pytest.approx(18.0)
    delta_k_plus_v_head = w_interface + w_aero
    assert delta_k_plus_v_head == pytest.approx(16.0)
    assert delta_k_plus_v_head + delta_mech_shaft == pytest.approx(delta_total_mech)

    # Ensure proximal hand work is not counted twice in head subsystem
    assert delta_k_plus_v_head != (w_hand + w_interface + w_aero)


def test_kinetic_energy_coordinate_mixing_invariance() -> None:
    """Verify kinetic energy invariance under coordinate mixing and cross-term omission."""
    v_phys = np.array([2.0, 1.0], dtype=np.float64)
    m_phys = np.array([1.0, 1.0], dtype=np.float64)

    # Physical kinetic energy: 0.5 * sum(m_i * v_i^2)
    t_phys = float(0.5 * np.sum(m_phys * (v_phys**2)))
    assert t_phys == pytest.approx(2.5)

    # Coordinate transformation: v = A @ q_dot
    q_dot = np.array([1.0, 1.0], dtype=np.float64)
    a_matrix = np.array([[1.0, 1.0], [0.0, 1.0]], dtype=np.float64)
    np.testing.assert_allclose(a_matrix @ q_dot, v_phys)

    # Generalized mass matrix: M = A^T @ A
    mass_matrix = a_matrix.T @ a_matrix
    t_gen = float(0.5 * q_dot.T @ mass_matrix @ q_dot)
    assert t_gen == pytest.approx(2.5)
    assert t_gen == pytest.approx(t_phys)

    # Diagonal coordinate-only tally vs cross-term
    t_diag = float(
        0.5 * (mass_matrix[0, 0] * (q_dot[0] ** 2) + mass_matrix[1, 1] * (q_dot[1] ** 2))
    )
    cross_term = float(mass_matrix[0, 1] * q_dot[0] * q_dot[1])

    assert t_diag == pytest.approx(1.5)
    assert cross_term == pytest.approx(1.0)
    assert (t_diag + cross_term) == pytest.approx(t_gen)


def test_whole_club_ledger_separates_internal_strain_conversion() -> None:
    """Prevent the published example from treating shaft release as external supply."""
    chapter = Path(__file__).resolve().parents[1] / (
        "articles/proximal_distal_companion/chapters/ch05_speed_energy_power.qmd"
    )
    text = chapter.read_text(encoding="utf-8")
    assert "full club-energy changes become roughly 38 and 21 joules" not in text
    assert "13 joules" in text and "strain energy" in text
    assert "relative angular velocity" in text


def test_counterfactual_lab_does_not_infer_cause_from_lost_ranking() -> None:
    """Numerical sensitivity and event rules remain possible explanations."""
    chapter = Path(__file__).resolve().parents[1] / (
        "articles/proximal_distal_companion/chapters/ch05_speed_energy_power.qmd"
    )
    text = chapter.read_text(encoding="utf-8")
    assert "original difference belonged to preparation or parameter choice" not in text
    assert "numerical" in text and "event" in text
    assert "/blob/main/" not in text
