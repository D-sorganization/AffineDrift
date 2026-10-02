"""System boundary and energy ledger regression fixtures.

Manufactured mechanics regression suite covering virtual power, observer boosts,
contact-pair dissipation, self-equilibrated deformation power, actuator energy ledgers,
gravitational potential vs. external work accounting, and recoil impulse expansions.
"""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray

GRAVITY_M_S2 = 9.81


def test_rigid_body_resultant_power_and_reference_shift() -> None:
    """Assumption: Velocity field satisfies rigid kinematics v(r) = v0 + omega x (r - r0).

    Verifies that resultant wrench power equals the sum of point load powers, and
    that shifting the wrench reduction reference point leaves total power invariant.
    """
    positions = np.array([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 3.0]])
    forces = np.array([[10.0, 0.0, 0.0], [0.0, -5.0, 0.0], [2.0, 3.0, 4.0]])

    ref_point_a = np.array([0.0, 0.0, 0.0])
    v_a = np.array([1.0, 2.0, 3.0])
    omega = np.array([0.5, -1.0, 2.0])

    v_points = v_a + np.cross(omega, positions - ref_point_a)
    power_point_sum = float(np.sum([np.dot(f, v) for f, v in zip(forces, v_points, strict=True)]))

    resultant_force = np.sum(forces, axis=0)
    moment_a = np.sum(
        [np.cross(r - ref_point_a, f) for r, f in zip(positions, forces, strict=True)],
        axis=0,
    )
    power_wrench_a = float(np.dot(resultant_force, v_a) + np.dot(moment_a, omega))

    assert np.isclose(power_point_sum, power_wrench_a)

    ref_point_b = np.array([4.0, -1.0, 2.0])
    v_b = v_a + np.cross(omega, ref_point_b - ref_point_a)
    moment_b = np.sum(
        [np.cross(r - ref_point_b, f) for r, f in zip(positions, forces, strict=True)],
        axis=0,
    )
    power_wrench_b = float(np.dot(resultant_force, v_b) + np.dot(moment_b, omega))

    assert np.isclose(power_wrench_a, power_wrench_b)


@pytest.mark.parametrize(
    "boost_velocity",
    [
        np.array([2.0, 0.0, 0.0]),
        np.array([0.0, -3.0, 1.5]),
        np.array([1.0, 4.0, -2.0]),
    ],
)
def test_nonrotating_observer_boost_power_shift(
    boost_velocity: NDArray[np.float64],
) -> None:
    """Assumption: Observer transformation is a constant nonrotating velocity boost v' = v - U.

    Verifies that total power changes by -(R . U) for a general wrench, and remains
    strictly invariant under any boost when the resultant force vanishes (pure couple).
    """
    forces = np.array([[5.0, 1.0, -2.0], [3.0, -4.0, 0.0]])
    velocities = np.array([[2.0, 0.0, 1.0], [-1.0, 3.0, 2.0]])

    power_base = float(np.sum([np.dot(f, v) for f, v in zip(forces, velocities, strict=True)]))
    boosted_velocities = velocities - boost_velocity
    power_boosted = float(
        np.sum([np.dot(f, v) for f, v in zip(forces, boosted_velocities, strict=True)])
    )

    resultant_force = np.sum(forces, axis=0)
    expected_shift = -float(np.dot(resultant_force, boost_velocity))
    assert np.isclose(power_boosted - power_base, expected_shift)

    couple_positions = np.array([[-1.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    couple_forces = np.array([[0.0, -2.0, 0.0], [0.0, 2.0, 0.0]])
    omega = np.array([0.0, 0.0, 3.0])
    couple_velocities = np.cross(omega, couple_positions)

    couple_resultant_force = np.sum(couple_forces, axis=0)
    couple_resultant_moment = np.sum(
        [np.cross(r, f) for r, f in zip(couple_positions, couple_forces, strict=True)],
        axis=0,
    )
    assert np.allclose(couple_resultant_force, 0.0)
    assert np.allclose(couple_resultant_moment, np.array([0.0, 0.0, 4.0]))

    couple_power_base = float(
        np.sum([np.dot(f, v) for f, v in zip(couple_forces, couple_velocities, strict=True)])
    )
    couple_boosted_velocities = couple_velocities - boost_velocity
    couple_power_boosted = float(
        np.sum(
            [np.dot(f, v) for f, v in zip(couple_forces, couple_boosted_velocities, strict=True)]
        )
    )
    assert np.isclose(couple_power_base, 12.0)
    assert np.isclose(couple_power_boosted, 12.0)
    assert np.isclose(couple_power_boosted, couple_power_base)


def test_contact_force_pair_at_coincident_position() -> None:
    """Assumption: Contact interaction satisfies Newton's third law at a coincident contact point.

    Verifies power cancellation for sticking (v1 == v2), exact dissipation of -12 W
    for tangential sliding with specified vectors, and zero power for relative velocity
    perpendicular to the contact force.
    """
    force_on_1 = np.array([-4.0, 0.0, 10.0])
    force_on_2 = -force_on_1

    v_stick = np.array([5.0, 1.0, 0.0])
    power_stick = float(np.dot(force_on_1, v_stick) + np.dot(force_on_2, v_stick))
    assert np.isclose(power_stick, 0.0)

    v1_slide = np.array([5.0, 1.0, 0.0])
    v2_slide = np.array([2.0, 1.0, 0.0])
    power_1 = float(np.dot(force_on_1, v1_slide))
    power_2 = float(np.dot(force_on_2, v2_slide))
    total_sliding_power = power_1 + power_2

    assert np.isclose(power_1, -20.0)
    assert np.isclose(power_2, 8.0)
    assert np.isclose(total_sliding_power, -12.0)

    v_rel_perp = np.array([0.0, 4.0, 0.0])
    v2_perp = v1_slide - v_rel_perp
    power_perp = float(np.dot(force_on_1, v1_slide) + np.dot(force_on_2, v2_perp))
    assert np.isclose(power_perp, 0.0)


def test_self_equilibrated_loads_deformation_and_rigid_motion() -> None:
    """Assumption: Equal and opposite outward point forces form a self-equilibrated system.

    Verifies that outward loads yield zero resultant wrench, 2 W deformation power under
    unit outward velocities, 0 W for null loads, and 0 W under rigid translation or rotation.
    """
    pos_1 = np.array([-1.0, 0.0, 0.0])
    pos_2 = np.array([1.0, 0.0, 0.0])
    f_1 = np.array([-1.0, 0.0, 0.0])
    f_2 = np.array([1.0, 0.0, 0.0])

    resultant_force = f_1 + f_2
    resultant_torque = np.cross(pos_1, f_1) + np.cross(pos_2, f_2)
    assert np.allclose(resultant_force, 0.0)
    assert np.allclose(resultant_torque, 0.0)

    v1_outward = np.array([-1.0, 0.0, 0.0])
    v2_outward = np.array([1.0, 0.0, 0.0])
    power_deform = float(np.dot(f_1, v1_outward) + np.dot(f_2, v2_outward))
    assert np.isclose(power_deform, 2.0)

    power_zero_loads = float(np.dot(np.zeros(3), v1_outward) + np.dot(np.zeros(3), v2_outward))
    assert np.isclose(power_zero_loads, 0.0)

    v_common_trans = np.array([3.0, -2.0, 5.0])
    power_rigid_trans = float(np.dot(f_1, v_common_trans) + np.dot(f_2, v_common_trans))
    assert np.isclose(power_rigid_trans, 0.0)

    omega_rigid = np.array([0.0, 0.0, 3.0])
    v1_rot = np.cross(omega_rigid, pos_1)
    v2_rot = np.cross(omega_rigid, pos_2)
    power_rigid_rot = float(np.dot(f_1, v1_rot) + np.dot(f_2, v2_rot))
    assert np.isclose(power_rigid_rot, 0.0)


def test_two_mass_supported_and_free_actuation_energy() -> None:
    """Assumption: 1D zero-gravity motion driven by a constant internal repulsive actuator.

    For unilateral support: support does zero work, Newton time integration gives final
    velocity, yielding K_tot = 20 J, COM K = 10 J, and reservoir Delta E = -20 J.
    For free pair: isolated internal forces conserve center-of-mass momentum at zero.
    """
    m1: float = 2.0
    m2: float = 2.0
    actuator_force: float = 40.0
    displacement_2: float = 0.5

    a2 = actuator_force / m2
    t_end = np.sqrt(2.0 * displacement_2 / a2)
    v2_end = a2 * t_end

    k1_end = 0.0
    k2_end = 0.5 * m2 * (v2_end**2)
    total_k = k1_end + k2_end
    assert np.isclose(total_k, 20.0)

    v_com = (m1 * 0.0 + m2 * v2_end) / (m1 + m2)
    com_k = 0.5 * (m1 + m2) * (v_com**2)
    assert np.isclose(com_k, 10.0)

    support_force = actuator_force
    supported_mass_displacement = 0.0
    assert np.isclose(support_force - actuator_force, 0.0)

    support_work = support_force * supported_mass_displacement
    internal_reservoir_delta = -actuator_force * displacement_2
    assert np.isclose(support_work, 0.0)
    assert np.isclose(internal_reservoir_delta, -20.0)
    assert np.isclose(total_k + internal_reservoir_delta, 0.0)

    com_displacement = (m1 * supported_mass_displacement + m2 * displacement_2) / (m1 + m2)
    com_pseudowork = support_force * com_displacement
    assert np.isclose(com_pseudowork, 10.0)
    assert np.isclose(com_pseudowork, com_k)

    delta_p1_free = -actuator_force * t_end
    delta_p2_free = actuator_force * t_end
    p_com_free = delta_p1_free + delta_p2_free
    assert np.isclose(p_com_free, 0.0)


def test_gravity_potential_versus_external_power_ledgers() -> None:
    """Assumption: Constant vertical gravity field g; motion in 1D vertical freefall.

    Verifies that treating gravity as an external force (Ledger A) or as potential energy
    (Ledger B) both balance independently, while double counting produces a non-zero residual.
    """
    mass: float = 2.5
    y0: float = 20.0
    v0: float = -3.0
    duration: float = 1.0

    v1 = v0 - GRAVITY_M_S2 * duration
    y1 = y0 + v0 * duration - 0.5 * GRAVITY_M_S2 * (duration**2)

    k0 = 0.5 * mass * (v0**2)
    k1 = 0.5 * mass * (v1**2)
    delta_k = k1 - k0

    work_gravity_ext = -mass * GRAVITY_M_S2 * (y1 - y0)
    ledger_a_residual = delta_k - work_gravity_ext
    assert np.isclose(ledger_a_residual, 0.0)

    v_pot_0 = mass * GRAVITY_M_S2 * y0
    v_pot_1 = mass * GRAVITY_M_S2 * y1
    delta_v_pot = v_pot_1 - v_pot_0
    ledger_b_residual = delta_k + delta_v_pot
    assert np.isclose(ledger_b_residual, 0.0)

    double_count_residual = delta_k + delta_v_pot - work_gravity_ext
    assert not np.isclose(double_count_residual, 0.0)
    assert np.isclose(double_count_residual, -work_gravity_ext)


@pytest.mark.parametrize(
    ("mass", "v_init", "impulse"),
    [
        (2.0, np.array([3.0, 0.0, 0.0]), np.array([4.0, 0.0, 0.0])),
        (4.0, np.array([1.0, -2.0, 0.5]), np.array([0.0, 2.0, -1.0])),
        (8.0, np.array([-2.0, 1.5, 0.0]), np.array([1.0, -0.5, 3.0])),
    ],
)
def test_finite_mass_recoil_kinetic_energy_formula(
    mass: float,
    v_init: NDArray[np.float64],
    impulse: NDArray[np.float64],
) -> None:
    """Assumption: Total impulse J delivered over an interval to a point mass M with initial velocity V.

    Verifies Delta K = V . J + (J . J) / (2 M) against explicit 1/2 M (V_final^2 - V_init^2),
    not requiring an instantaneous impulse.
    """
    v_final = v_init + impulse / mass
    k_init = 0.5 * mass * float(np.dot(v_init, v_init))
    k_final = 0.5 * mass * float(np.dot(v_final, v_final))
    delta_k_direct = k_final - k_init

    linear_term = float(np.dot(v_init, impulse))
    recoil_term = float(np.dot(impulse, impulse)) / (2.0 * mass)
    delta_k_formula = linear_term + recoil_term

    assert np.isclose(delta_k_direct, delta_k_formula)


def test_bounded_impulse_large_mass_retains_linear_term() -> None:
    """Assumption: Total impulse J delivered over an interval to mass M with fixed initial velocity V.

    Verifies that the quadratic recoil term (J . J) / (2 M) vanishes while the linear
    coupling term V . J remains finite and is not erased, not requiring an instantaneous impulse.
    """
    v_init = Fraction(5, 1)
    impulse = Fraction(2, 1)
    linear_term = v_init * impulse
    assert linear_term == Fraction(10, 1)

    masses = [10, 1000, 1000000, 1000000000]
    differences: list[Fraction] = []

    for mass in masses:
        m = Fraction(mass, 1)
        v_final = v_init + impulse / m
        k_init = Fraction(1, 2) * m * (v_init**2)
        k_final = Fraction(1, 2) * m * (v_final**2)
        delta_k = k_final - k_init
        diff = delta_k - linear_term
        differences.append(diff)

    assert differences == [Fraction(2, mass) for mass in masses]
    for diff, mass in zip(differences, masses, strict=True):
        assert diff == Fraction(2, mass)
    for i in range(len(differences) - 1):
        assert differences[i] > differences[i + 1]
    assert linear_term != Fraction(0, 1)
    assert linear_term == Fraction(10, 1)


@pytest.fixture
def chapter_source() -> str:
    """Read the canonical explanation whose numerical examples this fixture checks."""
    root = Path(__file__).resolve().parents[1]
    return (
        root / "articles/proximal_distal_companion/chapters/ch02_choose_the_system.qmd"
    ).read_text(encoding="utf-8")


def test_chapter_distinguishes_contact_work_from_com_work(chapter_source: str) -> None:
    """Keep both power definitions present so the stationary-support example is auditable."""
    compact = "".join(chapter_source.split())
    assert (
        r"P_{\mathrm{contact}}=\mathbf F\cdot\mathbf v_{\mathrm{contact}}".replace(" ", "")
        in compact
    )
    assert r"\frac{dK_G}{dt}=\mathbf F_{\mathrm{ext}}\cdot\mathbf v_G".replace(" ", "") in compact


def test_chapter_bounds_observer_power_invariance(chapter_source: str) -> None:
    """An observer boost must remain distinct from a rigid-point reporting change."""
    compact = "".join(chapter_source.split())
    assert r"P'=P-\mathbf R\cdot\mathbf U".replace(" ", "") in compact
    assert "nonrotating" in chapter_source.lower()


def test_chapter_retains_contact_and_gravity_ledgers(chapter_source: str) -> None:
    """Protect the load-relative-motion and single-count gravity equations."""
    compact = "".join(chapter_source.split())
    assert r"P_1+P_2=\mathbf F\cdot(\mathbf v_1-\mathbf v_2)".replace(" ", "") in compact
    assert r"P_g=-\dot U_g".replace(" ", "") in compact


def test_chapter_provider_evidence_is_pinned(chapter_source: str) -> None:
    """Reader links must identify the reviewed provider revision, not mutable main."""
    assert "UpstreamDrift/blob/main/" not in chapter_source
    assert chapter_source.count("85cce4d3307bb7ad3953d9fc6e583e370803515c") >= 2
