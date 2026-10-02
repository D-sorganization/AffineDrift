"""Manufactured synthesis identities and provenance, not golfer validation."""

from pathlib import Path

import numpy as np
import pytest


def test_rigid_body_kinematics_and_energy() -> None:
    """Verify kinetic energy symmetry and head velocity asymmetry for instantaneous states."""
    mass = 1.0
    izz = 0.25
    v_com = np.array([0.0, 2.0, 0.0])
    r_head = np.array([0.5, 0.0, 0.0])
    omega_pos = np.array([0.0, 0.0, 2.0])
    omega_neg = np.array([0.0, 0.0, -2.0])

    ke_trans = 0.5 * mass * float(np.dot(v_com, v_com))
    ke_rot_pos = 0.5 * izz * float(omega_pos[2] ** 2)
    ke_rot_neg = 0.5 * izz * float(omega_neg[2] ** 2)
    assert np.isclose(ke_trans + ke_rot_pos, 2.5)
    assert np.isclose(ke_trans + ke_rot_neg, 2.5)

    v_head_pos = v_com + np.cross(omega_pos, r_head)
    v_head_neg = v_com + np.cross(omega_neg, r_head)
    np.testing.assert_allclose(v_head_pos, [0.0, 3.0, 0.0])
    np.testing.assert_allclose(v_head_neg, [0.0, 1.0, 0.0])
    assert np.isclose(np.linalg.norm(v_head_pos), 3.0)
    assert np.isclose(np.linalg.norm(v_head_neg), 1.0)


def test_planar_hand_wrench_power_and_internal_forces() -> None:
    """Verify invariant wrench power and load redistribution with manufactured limits."""
    r1, r2 = np.array([0.0, 0.1, 0.0]), np.array([0.0, -0.1, 0.0])
    f1, f2 = np.array([10.0, 20.0, 0.0]), np.array([-10.0, 30.0, 0.0])
    v_com, omega = np.array([2.0, 1.0, 0.0]), np.array([0.0, 0.0, 3.0])

    res_f = f1 + f2
    res_m = np.cross(r1, f1) + np.cross(r2, f2)
    np.testing.assert_allclose(res_f, [0.0, 50.0, 0.0])
    np.testing.assert_allclose(res_m, [0.0, 0.0, -2.0])

    v1, v2 = v_com + np.cross(omega, r1), v_com + np.cross(omega, r2)
    np.testing.assert_allclose(v1, [1.7, 1.0, 0.0])
    np.testing.assert_allclose(v2, [2.3, 1.0, 0.0])

    p1, p2 = float(np.dot(f1, v1)), float(np.dot(f2, v2))
    wrench_p = float(np.dot(res_f, v_com) + np.dot(res_m, omega))
    assert np.isclose(p1, 37.0) and np.isclose(p2, 7.0)
    assert np.isclose(p1 + p2, 44.0) and np.isclose(wrench_p, 44.0)

    delta = np.array([0.0, 100.0, 0.0])
    f1_mod, f2_mod = f1 + delta, f2 - delta
    res_m_mod = np.cross(r1, f1_mod) + np.cross(r2, f2_mod)
    np.testing.assert_allclose(f1_mod + f2_mod, res_f)
    np.testing.assert_allclose(res_m_mod, res_m)

    p1_mod, p2_mod = float(np.dot(f1_mod, v1)), float(np.dot(f2_mod, v2))
    assert np.isclose(p1_mod, 137.0) and np.isclose(p2_mod, -93.0)
    assert np.isclose(p1_mod + p2_mod, 44.0)

    manufactured_limit = 50.0
    assert np.linalg.norm(f1) < manufactured_limit and np.linalg.norm(f2) < manufactured_limit
    assert np.linalg.norm(f1_mod) > manufactured_limit
    assert np.linalg.norm(f2_mod) > manufactured_limit


def test_pareto_claim_scope_vector_dominance() -> None:
    """Verify non-dominated baseline candidates and hypothetical dominating alternative."""
    cand_a = np.array([1.0, 4.0])
    cand_b = np.array([4.0, 1.0])
    untested = np.array([0.5, 0.5])

    a_dom_b = np.all(cand_a <= cand_b) and np.any(cand_a < cand_b)
    b_dom_a = np.all(cand_b <= cand_a) and np.any(cand_b < cand_a)
    u_dom_a = np.all(untested <= cand_a) and np.any(untested < cand_a)
    u_dom_b = np.all(untested <= cand_b) and np.any(untested < cand_b)

    assert not a_dom_b
    assert not b_dom_a
    assert u_dom_a
    assert u_dom_b


@pytest.mark.integration
def test_provenance_contract_markers() -> None:
    """Verify source document contains expected provenance identifiers and cross-references."""
    path = Path("articles/proximal_distal_companion/chapters/ch28_practical_synthesis.qmd")
    source = path.read_text(encoding="utf-8")
    prefix = (
        "https://github.com/D-sorganization/UpstreamDrift/blob/"
        "85cce4d3307bb7ad3953d9fc6e583e370803515c/"
        "docs/research/proximal_distal_energy_transfer/"
    )
    for suffix in ("chapters/_ch09_conclusions.qmd", "REVIEWER_WORKBENCH.md"):
        assert prefix + suffix in source
