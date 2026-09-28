"""Independent manufactured checks for Volume III model-selection arguments (#4463)."""

from pathlib import Path

import numpy as np
import pytest

CHAPTER = Path(__file__).parents[1] / (
    "articles/The_Geometry_of_Motion/Volume_III/chapters/ch01_biology_vs_engineering.tex"
)


def test_mass_fractions_sum_and_toy_inventory() -> None:
    """Verify original chapter fraction discrepancy and balanced toy inventory."""
    central = 0.081 + 0.497
    unilateral = np.array([0.0271, 0.0162, 0.0061, 0.1416, 0.0433, 0.0137])
    one_row_sum = central + float(unilateral.sum())
    bilateral_sum = central + 2.0 * float(unilateral.sum())

    assert one_row_sum == pytest.approx(0.826, rel=1e-5)
    assert bilateral_sum == pytest.approx(1.074, rel=1e-5)
    assert abs(one_row_sum - 1.0) > 0.1 and abs(bilateral_sum - 1.0) > 0.05

    toy_central = 0.1 + 0.4
    toy_unilateral = np.array([0.05, 0.03, 0.02, 0.09, 0.04, 0.02])
    toy_bilateral = toy_central + 2.0 * float(toy_unilateral.sum())
    total_mass = 75.0 * toy_bilateral

    assert toy_bilateral == pytest.approx(1.0, rel=1e-6)
    assert total_mass == pytest.approx(75.0, rel=1e-6)


def test_center_of_mass_translation_invariance() -> None:
    """Verify COM position and translational invariance of internal geometry."""
    m1, m2 = 2.0, 1.0
    r1, r2 = np.array([0.2, 0.0, 0.0]), np.array([0.4, 0.15, 0.0])
    total_mass = m1 + m2
    com = (m1 * r1 + m2 * r2) / total_mass
    expected_com = np.array([4.0 / 15.0, 0.05, 0.0])
    assert np.allclose(com, expected_com, atol=1e-9)

    shift = np.array([-1.3, 2.7, 0.45])
    r1_s, r2_s = r1 + shift, r2 + shift
    com_s = (m1 * r1_s + m2 * r2_s) / total_mass
    assert np.allclose(com_s, com + shift, atol=1e-9)
    assert np.isclose(np.linalg.norm(r1_s - r2_s), np.linalg.norm(r1 - r2), atol=1e-9)
    assert np.isclose(np.linalg.norm(r1_s - com_s), np.linalg.norm(r1 - com), atol=1e-9)


def test_spatial_inertia_properties_and_kinetic_energy() -> None:
    """Verify spatial inertia symmetry, positive spectrum, and kinetic energy equivalence."""
    mass = 2.0
    c = np.array([0.1, -0.2, 0.3])
    i_c = np.diag([0.02, 0.03, 0.04])
    principal = np.linalg.eigvalsh(i_c)
    assert 2 * principal.max() <= principal.sum()
    skew_c = np.array([[0.0, -c[2], c[1]], [c[2], 0.0, -c[0]], [-c[1], c[0], 0.0]])

    m_spatial = np.block(
        [
            [i_c - mass * (skew_c @ skew_c), mass * skew_c],
            [-mass * skew_c, mass * np.eye(3)],
        ]
    )

    assert np.allclose(m_spatial, m_spatial.T, atol=1e-9)
    assert np.all(np.linalg.eigvalsh(m_spatial) > 0.0)

    omega = np.array([1.5, -2.0, 0.5])
    v_o = np.array([-1.2, 0.8, -0.4])
    twist = np.concatenate([omega, v_o])
    ke_matrix = 0.5 * twist @ (m_spatial @ twist)

    v_com = v_o + np.cross(omega, c)
    ke_independent = 0.5 * omega @ (i_c @ omega) + 0.5 * mass * float(np.dot(v_com, v_com))
    assert np.isclose(ke_matrix, ke_independent, rtol=1e-7)


def test_harmonic_compliance_resonance_and_high_freq_phase() -> None:
    """Verify dynamic compliance response across resonance and high-frequency phase lag."""
    m, k, b = 1.0, 100.0, 1.0
    omega_n = np.sqrt(k / m)
    zeta = b / (2.0 * np.sqrt(k * m))
    assert np.isclose(omega_n, 10.0, atol=1e-9)
    assert np.isclose(zeta, 0.05, atol=1e-9)

    def compliance(w: float) -> complex:
        """Return displacement per force for the manufactured linear oscillator."""
        return 1.0 / (k - m * w**2 + 1j * b * w)

    assert abs(k * compliance(1.0)) == pytest.approx(1.0, rel=0.02)
    assert abs(k * compliance(10.0)) == pytest.approx(10.0, rel=1e-5)
    assert abs(k * compliance(100.0)) == pytest.approx(0.0101, rel=1e-3)

    phase_hf = np.angle(compliance(100.0))
    assert abs(phase_hf) == pytest.approx(np.pi, rel=0.01)


def test_muscle_moment_arm_power_balance() -> None:
    """Verify power balance identity between joint and musculotendon coordinates."""
    r_matrix = np.array([[0.03, -0.03, 0.0], [0.0, 0.02, -0.02]])
    force = np.array([100.0, 80.0, 60.0])
    rates = np.array([2.0, -1.0])
    length_rates = -(r_matrix.T @ rates)

    joint_power = (r_matrix @ force) @ rates
    muscle_power = -force @ length_rates
    assert np.isclose(joint_power, muscle_power, atol=1e-9)


def test_redundant_actuator_equilibrium_and_task_jacobian_separation() -> None:
    """Verify feasible actuator force bounds and distinction from task Jacobian nullspace."""
    r_matrix = np.array([[1.0, 0.0, 1.0], [0.0, 1.0, 1.0]])
    load = np.array([3.0, 3.0])

    for t in [0.0, 1.5, 3.0]:
        f = np.array([3.0 - t, 3.0 - t, t])
        assert np.allclose(r_matrix @ f, load, atol=1e-9)
        assert np.all((f >= 0.0) & (f <= 3.0))

    for t_bad in [-0.5, 3.5]:
        f_bad = np.array([3.0 - t_bad, 3.0 - t_bad, t_bad])
        assert not np.all((f_bad >= 0.0) & (f_bad <= 3.0))

    _, _, vh_r = np.linalg.svd(r_matrix)
    r_null = vh_r[2] / vh_r[2, 2]
    assert np.allclose(r_null, np.array([-1.0, -1.0, 1.0]), atol=1e-9)

    j_task = np.array([[1.0, 1.0, 0.0], [0.0, 1.0, 1.0]])
    _, _, vh_j = np.linalg.svd(j_task)
    j_null = vh_j[2] / vh_j[2, 2]
    assert not np.allclose(
        np.outer(r_null, r_null) / (r_null @ r_null),
        np.outer(j_null, j_null) / (j_null @ j_null),
        atol=1e-9,
    )
    assert np.linalg.norm(r_matrix @ j_null) > 0.1


def test_activation_dynamics_piecewise_affine_identity() -> None:
    """Verify piecewise activation rates and breakdown of full-domain affine midpoint."""
    a = 0.5
    tau_act = 0.01 * (0.5 + 1.5 * a)
    tau_deact = 0.04 / (0.5 + 1.5 * a)

    def act_rate(u: float) -> float:
        """Evaluate the explicitly selected activation/deactivation branch."""
        tau = tau_act if u > a else tau_deact
        return (u - a) / tau

    assert act_rate(0.0) == pytest.approx(-15.625, rel=1e-5)
    assert act_rate(0.5) == pytest.approx(0.0, abs=1e-9)
    assert act_rate(1.0) == pytest.approx(40.0, rel=1e-5)

    midpoint_rate = act_rate(0.5 * (0.0 + 1.0))
    mean_rate = 0.5 * (act_rate(0.0) + act_rate(1.0))
    assert not np.isclose(midpoint_rate, mean_rate, atol=1.0)

    u_act1, u_act2 = 0.7, 0.9
    assert np.isclose(
        act_rate(0.5 * (u_act1 + u_act2)),
        0.5 * (act_rate(u_act1) + act_rate(u_act2)),
    )


def test_fixed_time_constant_activation_is_affine_in_excitation() -> None:
    """A chosen constant-time-constant model has an excitation-affine state derivative."""
    activation, time_constant = 0.5, 0.02
    excitation = np.array([0.0, 0.5, 1.0])
    derivative = (excitation - activation) / time_constant
    assert derivative[1] == pytest.approx((derivative[0] + derivative[2]) / 2)
    np.testing.assert_allclose(derivative, [-25, 0, 25])


@pytest.mark.parametrize(
    "obsolete",
    [
        "dependencies that have no analog in electric motors",
        "the system is effectively another rigid body",
        "de_leva_male_segments",
        "All differential geometry tools (Lie brackets, contraction metrics, etc.)",
        "This is the domain of software platforms",
        "Infinitely many muscle activation patterns",
    ],
)
def test_opening_chapter_removes_identified_false_generalizations(obsolete: str) -> None:
    """Prevent the specific unsupported claims identified by review #4463 from returning."""
    assert obsolete.casefold() not in CHAPTER.read_text(encoding="utf-8").casefold()
