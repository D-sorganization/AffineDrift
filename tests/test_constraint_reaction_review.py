"""Tests reviewing constraint reactions, redundancy, superposition, and links."""

import re
from pathlib import Path

import numpy as np
import pytest

from scripts.build_nullspace_examples import constraint_solve


@pytest.mark.parametrize("speed,valid_cord", [(1.0, False), (4.0, True)])
def test_circle_top_cord_reaction(speed: float, valid_cord: bool) -> None:
    """A bilateral circular guide can push; a taut cord must pull inward."""
    mass = 2.0 * np.eye(2)
    force = np.array([0.0, -19.62])
    jacobian = np.array([[0.0, 1.0]])
    curvature = np.array([speed**2])

    accel, lam = constraint_solve(mass, force, jacobian, curvature)
    expected_lam = 19.62 - 2.0 * speed**2
    assert np.isclose(lam[0], expected_lam)

    # Tensile cord requires inward pulling force (T = -lambda >= 0 along outward normal)
    tensile_cord = -lam[0] >= 0.0
    assert bool(tensile_cord) is valid_cord

    # Bilateral constraint remains algebraically satisfied
    assert np.allclose(mass @ accel, force + jacobian.T @ lam)
    assert np.allclose(jacobian @ accel + curvature, 0.0)


def test_redundant_jacobian_rows_and_multiplier_scaling() -> None:
    """Duplicated equations change multiplier allocations, not the net generalized load."""
    mass = 2.0 * np.eye(2)
    load = np.array([2.0, 4.0])
    accel = np.array([0.0, 2.0])
    jacobian = np.array([[1.0, 0.0], [2.0, 0.0]])
    gamma = np.zeros(2)

    # Dependent Jacobian rows must be rejected by solver
    with pytest.raises(ValueError):
        constraint_solve(mass, load, jacobian, gamma)

    # Independently verify balance and compatibility
    target_reaction = np.array([-2.0, 0.0])
    assert np.allclose(mass @ accel, load + target_reaction)
    assert np.allclose(jacobian @ accel + gamma, 0.0)

    # Distinct multipliers yield identical generalized reaction with unequal norms
    lam1 = np.array([-0.4, -0.8])
    lam2 = np.array([-2.0, 0.0])
    assert np.allclose(jacobian.T @ lam1, target_reaction)
    assert np.allclose(jacobian.T @ lam2, target_reaction)
    assert not np.isclose(np.linalg.norm(lam1), np.linalg.norm(lam2))

    # Scaling duplicate row from 2 to 20 alters minimum norm multiplier
    j_scaled = np.array([[1.0, 0.0], [20.0, 0.0]])
    lam_scaled = np.array([-2.0 / 401.0, -40.0 / 401.0])
    assert np.allclose(j_scaled.T @ lam_scaled, target_reaction)


def test_planar_grip_wrench_ambiguity() -> None:
    """Force cancellation can leave a couple; axial squeeze is wrench neutral."""
    g_wrench = np.array([[1.0, 0.0, 1.0, 0.0], [0.0, 1.0, 0.0, 1.0], [0.0, -0.1, 0.0, 0.1]])
    assert np.linalg.matrix_rank(g_wrench) == 3

    delta_axial = np.array([1.0, 0.0, -1.0, 0.0])
    delta_transverse = np.array([0.0, 1.0, 0.0, -1.0])

    # Opposing axial increments generate zero complete wrench
    wrench_axial = g_wrench @ delta_axial
    assert np.allclose(wrench_axial, 0.0)

    # Opposing transverse increments yield zero force but -0.2 Nm moment
    wrench_trans = g_wrench @ delta_transverse
    assert np.allclose(wrench_trans[:2], 0.0)
    assert np.isclose(wrench_trans[2], -0.2)


def test_affine_constraint_response_superposition() -> None:
    """Four fixed-state cases share a drift baseline that must be subtracted once."""
    mass = np.array([[2.0, 1.0], [1.0, 3.0]])
    jacobian = np.array([[1.0, 1.0]])
    gamma = np.array([0.7])
    f_base = np.array([1.0, -2.0])
    f_p = np.array([3.0, 0.0])
    f_d = np.array([0.0, 5.0])

    a_0, lam_0 = constraint_solve(mass, f_base, jacobian, gamma)
    a_p, lam_p = constraint_solve(mass, f_base + f_p, jacobian, gamma)
    a_d, lam_d = constraint_solve(mass, f_base + f_d, jacobian, gamma)
    a_all, lam_all = constraint_solve(mass, f_base + f_p + f_d, jacobian, gamma)

    # Affine response superposition: responseAll = responseP + responseD - responseZero
    assert np.allclose(a_all, a_p + a_d - a_0)
    assert np.allclose(lam_all, lam_p + lam_d - lam_0)

    # Naive sum fails
    assert not np.allclose(a_all, a_p + a_d)
    assert not np.allclose(lam_all, lam_p + lam_d)

    # Endpoint acceleration with shared drift obeys the same identity
    c_mat = np.array([[1.0, 2.0], [-1.0, 0.5]])
    c_vec = np.array([0.3, -0.4])
    ep_0 = c_mat @ a_0 + c_vec
    ep_p = c_mat @ a_p + c_vec
    ep_d = c_mat @ a_d + c_vec
    ep_all = c_mat @ a_all + c_vec

    assert np.allclose(ep_all, ep_p + ep_d - ep_0)


@pytest.mark.parametrize("stiffness", [100.0, 400.0, 1600.0])
def test_stiff_spring_limit_displacement_vs_force(stiffness: float) -> None:
    """Small displacement and energy do not ensure uniformly small reaction error."""
    mass = 1.0
    omega = np.sqrt(stiffness / mass)
    phases = np.array([0.0, np.pi / 2.0, np.pi])
    times = phases / omega

    deltas = np.cos(omega * times) / stiffness
    forces = -np.cos(omega * times)

    max_displacement = float(np.max(np.abs(deltas)))
    max_force = float(np.max(np.abs(forces)))
    energy = 0.5 * stiffness * (1.0 / stiffness) ** 2

    assert np.isclose(max_displacement, 1.0 / stiffness)
    assert np.isclose(max_force, 1.0)
    assert np.isclose(energy, 1.0 / (2.0 * stiffness))


@pytest.mark.integration
def test_chapter6_provider_links_pinned_commit() -> None:
    """All provider links must identify the exact inspected revision."""
    repo_root = Path(__file__).resolve().parents[1]
    content = (
        repo_root / "articles/proximal_distal_companion/chapters/ch06_constraints_push_back.qmd"
    ).read_text(encoding="utf-8")
    link_pattern = re.compile(r"https://github\.com/D-sorganization/UpstreamDrift/[^\s\)\"\'\>]+")
    links = link_pattern.findall(content)

    assert len(links) >= 3
    pinned_segment = "/blob/85cce4d3307bb7ad3953d9fc6e583e370803515c/"
    assert all(pinned_segment in url for url in links)
