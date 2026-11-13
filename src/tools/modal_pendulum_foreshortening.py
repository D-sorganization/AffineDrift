"""Planar modal pendulum with inextensible foreshortening (Part 4 benchmark)."""

from __future__ import annotations

import numpy as np
from numpy.polynomial.legendre import leggauss

LENGTH = 1.1
DENSITY = 0.1
HEAD_MASS = 0.2
PIVOT_INERTIA = 0.4
GRAVITY_M_S2 = 9.81
STIFFNESS = 2500.0
DAMPING = 0.8

A = DENSITY * LENGTH / 5 + HEAD_MASS
B = DENSITY * LENGTH**2 / 4 + HEAD_MASS * LENGTH
J0 = PIVOT_INERTIA + DENSITY * LENGTH**3 / 3 + HEAD_MASS * LENGTH**2
P = DENSITY * LENGTH**2 / 2 + HEAD_MASS * LENGTH
Q = DENSITY * LENGTH / 3 + HEAD_MASS

# Quadrature-verified foreshortening corrections (φ = (s/L)², u = ½∫φ'² η²).
CROSS_MASS_ETA2 = 0.3969696969696956
MODAL_MASS_ETA2 = 0.31693558966287
GEOMETRIC_STIFFENING_RATIO = 1.0 / 3.0


def phi(arc: float) -> float:
    """Return the trial shape value φ(s)."""
    return (arc / LENGTH) ** 2


def foreshorten_density(arc: float) -> float:
    """Return φ'(s)² weight in u(s) = ½∫₀ˢ φ'(ξ)² dξ η²."""
    return 4.0 * arc**3 / (3.0 * LENGTH**4)


def body_point(arc: float, eta: float) -> np.ndarray:
    """Return the body-frame placement with quadratic foreshortening."""
    axial = 0.5 * eta**2 * foreshorten_density(arc)
    return np.array([phi(arc) * eta, -(arc - axial)])


def mass(eta: float) -> np.ndarray:
    """Return the Hessian of the foreshortened planar kinetic energy."""
    inertial = J0 - GEOMETRIC_STIFFENING_RATIO * A * eta**2
    cross = B - CROSS_MASS_ETA2 * eta**2
    modal = A + MODAL_MASS_ETA2 * eta**2
    return np.array([[inertial, cross], [cross, modal]])


def mass_rate(eta: float, modal_rate: float) -> np.ndarray:
    """Return η̇ times the partial derivative of the inertia matrix."""
    scale = modal_rate
    return scale * np.array(
        [
            [-2.0 * GEOMETRIC_STIFFENING_RATIO * A * eta, -2.0 * CROSS_MASS_ETA2 * eta],
            [-2.0 * CROSS_MASS_ETA2 * eta, 2.0 * MODAL_MASS_ETA2 * eta],
        ]
    )


def potential(theta: float, eta: float) -> float:
    """Return gravity plus elastic potential with inextensible foreshortening."""
    nodes, weights = quadrature_nodes(12)
    return potential_from_quadrature(eta, theta, nodes, weights)


def gradient(theta: float, eta: float) -> np.ndarray:
    """Return the full potential gradient including O(η) axial gravity."""
    nodes, weights = quadrature_nodes(12)
    return _potential_gradient_quadrature(theta, eta, nodes, weights)


def velocity_bias(theta: float, eta: float, theta_rate: float, modal_rate: float) -> np.ndarray:
    """Return Christoffel velocity loads through quadratic foreshortening."""
    coupling = -2.0 * GEOMETRIC_STIFFENING_RATIO * A * eta * theta_rate * modal_rate
    modal_drag = -2.0 * CROSS_MASS_ETA2 * eta * modal_rate**2
    quadratic_coupling = 0.0236165869 * eta**2 * theta_rate * modal_rate
    centrifugal = GEOMETRIC_STIFFENING_RATIO * A * eta * theta_rate**2
    centrifugal_quadratic = -0.0118053739 * eta**2 * theta_rate**2
    modal_normal = MODAL_MASS_ETA2 * eta * modal_rate**2
    return np.array(
        [
            coupling + modal_drag + quadratic_coupling,
            centrifugal + centrifugal_quadratic + modal_normal,
        ]
    )


def acceleration(state: np.ndarray, torque: float) -> np.ndarray:
    """Solve the coupled force balance with foreshortened inertia and loads."""
    theta, eta, theta_rate, modal_rate = state
    inertial = mass(eta)
    load = velocity_bias(theta, eta, theta_rate, modal_rate) + gradient(theta, eta)
    load[1] += DAMPING * modal_rate
    return np.linalg.solve(inertial, np.array([torque, 0.0]) - load)


def quadrature_nodes(degree: int = 12) -> tuple[np.ndarray, np.ndarray]:
    """Return Gauss–Legendre nodes and weights on [0, L]."""
    nodes, weights = leggauss(degree)
    return (nodes + 1.0) * LENGTH / 2.0, weights * LENGTH / 2.0


def _rotation(theta: float) -> np.ndarray:
    """Return the planar rotation matrix for angle ``theta``."""
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    return np.array([[cos_t, -sin_t], [sin_t, cos_t]])


def mass_from_quadrature(
    eta: float, theta: float, nodes: np.ndarray, weights: np.ndarray
) -> np.ndarray:
    """Assemble the inertia matrix by integrating the distributed placement."""
    rotation = _rotation(theta)
    assembled = np.diag([PIVOT_INERTIA, 0.0])
    for arc, measure in zip(nodes, weights, strict=True):
        point = body_point(arc, eta)
        theta_column = rotation @ np.array([-point[1], point[0]])
        eta_column = rotation @ np.array([phi(arc), -eta * foreshorten_density(arc)])
        jacobian = np.column_stack([theta_column, eta_column])
        assembled += DENSITY * measure * jacobian.T @ jacobian
    point = body_point(LENGTH, eta)
    theta_column = rotation @ np.array([-point[1], point[0]])
    eta_column = rotation @ np.array([phi(LENGTH), -eta * foreshorten_density(LENGTH)])
    jacobian = np.column_stack([theta_column, eta_column])
    assembled += HEAD_MASS * jacobian.T @ jacobian
    return assembled


def potential_from_quadrature(
    eta: float, theta: float, nodes: np.ndarray, weights: np.ndarray
) -> float:
    """Integrate gravitational plus elastic potential from placement."""
    rotation = _rotation(theta)
    energy = 0.5 * STIFFNESS * eta**2
    for arc, measure in zip(nodes, weights, strict=True):
        world = rotation @ body_point(arc, eta)
        energy += DENSITY * measure * GRAVITY_M_S2 * world[1]
    world = rotation @ body_point(LENGTH, eta)
    energy += HEAD_MASS * GRAVITY_M_S2 * world[1]
    return energy


def christoffel_bias_from_quadrature(
    theta: float,
    eta: float,
    theta_rate: float,
    modal_rate: float,
    nodes: np.ndarray,
    weights: np.ndarray,
    eps: float = 1e-8,
) -> np.ndarray:
    """Return the velocity and potential bias by quadrature."""
    load = _potential_gradient_quadrature(theta, eta, nodes, weights)
    rates = np.array([theta_rate, modal_rate])
    for i in range(2):
        for j in range(2):
            for k in range(2):
                christoffel = _christoffel_symbol(i, j, k, theta, eta, nodes, weights, eps)
                load[i] += christoffel * rates[j] * rates[k]
    return load


def _potential_gradient_quadrature(
    theta: float, eta: float, nodes: np.ndarray, weights: np.ndarray, eps: float = 1e-7
) -> np.ndarray:
    """Central-difference gradient of the quadrature potential in ``(theta, eta)``."""
    return np.array(
        [
            (
                potential_from_quadrature(eta, theta + eps, nodes, weights)
                - potential_from_quadrature(eta, theta - eps, nodes, weights)
            )
            / (2.0 * eps),
            (
                potential_from_quadrature(eta + eps, theta, nodes, weights)
                - potential_from_quadrature(eta - eps, theta, nodes, weights)
            )
            / (2.0 * eps),
        ]
    )


def _mass_at(theta: float, eta: float, nodes: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """Return the inertia matrix at the given ``(theta, eta)`` configuration."""
    return mass_from_quadrature(eta, theta, nodes, weights)


def _christoffel_symbol(
    i: int,
    j: int,
    k: int,
    theta: float,
    eta: float,
    nodes: np.ndarray,
    weights: np.ndarray,
    eps: float,
) -> float:
    """Christoffel symbol Γ^k_ij for configuration metric derivatives."""

    def shift(angle_delta: float, modal_delta: float) -> np.ndarray:
        """Evaluate inertia after a finite shift in ``theta`` and ``eta``."""
        return _mass_at(theta + angle_delta, eta + modal_delta, nodes, weights)

    dM_ij_dk = (
        shift(eps if k == 0 else 0.0, eps if k == 1 else 0.0)[i, j]
        - shift(-(eps if k == 0 else 0.0), -(eps if k == 1 else 0.0))[i, j]
    ) / (2.0 * eps)
    dM_ik_dj = (
        shift(eps if j == 0 else 0.0, eps if j == 1 else 0.0)[i, k]
        - shift(-(eps if j == 0 else 0.0), -(eps if j == 1 else 0.0))[i, k]
    ) / (2.0 * eps)
    dM_jk_di = (
        shift(eps if i == 0 else 0.0, eps if i == 1 else 0.0)[j, k]
        - shift(-(eps if i == 0 else 0.0), -(eps if i == 1 else 0.0))[j, k]
    ) / (2.0 * eps)
    return float(0.5 * (dM_ij_dk + dM_ik_dj - dM_jk_di))


def arc_length_residual(eta: float, segments: int = 128) -> float:
    """Return |measured centerline length − L| with foreshortening."""
    if eta == 0.0:
        return 0.0
    arcs = np.linspace(0.0, LENGTH, segments)
    points = np.array([body_point(arc, eta) for arc in arcs])
    deltas = np.diff(points, axis=0)
    measured = float(np.sum(np.linalg.norm(deltas, axis=1)))
    return abs(measured - LENGTH)


def arc_length_without_foreshortening(eta: float, segments: int = 128) -> float:
    """Return |measured length − L| when axial foreshortening is omitted."""
    if eta == 0.0:
        return 0.0
    arcs = np.linspace(0.0, LENGTH, segments)
    points = np.array([np.array([phi(arc) * eta, -arc]) for arc in arcs])
    deltas = np.diff(points, axis=0)
    measured = float(np.sum(np.linalg.norm(deltas, axis=1)))
    return abs(measured - LENGTH)
