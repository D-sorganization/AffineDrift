"""Reproduce constructed constraint, grasp and controllability examples (#4371)."""

import argparse
import json
from pathlib import Path
from typing import TypedDict

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.integrate import quad_vec
from scipy.linalg import expm, null_space

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports/technical-review/nullspace-examples.json"
ARM_LENGTHS = (0.6, 0.5)  # Metres; a teaching linkage, not anatomical estimates.
GRIP_OFFSETS = np.array([[-0.1, 0.0], [0.1, 0.0]])
SHOULDERS = np.array([[-0.5, 0.0], [0.5, 0.0]])
HEAD_OFFSET = np.array([0.8, 0.0])


class ProjectorExample(TypedDict):
    """Dual force/velocity maps and one constrained response."""

    acceleration: list[float]
    reaction: list[float]
    velocity_projector: list[list[float]]
    force_projector: list[list[float]]
    force_to_acceleration: list[list[float]]


class MotionExample(TypedDict):
    """Acceleration, multiplier and reaction power in a declared state."""

    acceleration: list[float]
    reaction: list[float]
    reaction_power: float


class MovingExample(MotionExample):
    """Mechanical power balance for a moving guide."""

    applied_power: float
    kinetic_power: float


class SpringExample(TypedDict):
    """Reachability calculation for the exactly linear spring system."""

    horizon: float
    controllability: list[list[float]]
    gramian: list[list[float]]
    minimum_energy: float


class GraspExample(TypedDict):
    """Consistent planar configuration and the two distinct velocity maps."""

    configuration: list[float]
    closure: list[float]
    constraint_rank: int
    constraint_nullity: int
    stationary_head_nullity: int
    jacobian: list[list[float]]
    task_jacobian: list[list[float]]


class Examples(TypedDict):
    """JSON-compatible teaching record with explicit field meanings."""

    scope: str
    anisotropic: ProjectorExample
    circle: MotionExample
    moving_guide: MovingExample
    springs: SpringExample
    planar_grasp: GraspExample


def constraint_solve(
    mass: ArrayLike, force: ArrayLike, jacobian: ArrayLike, curvature: ArrayLike
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Solve M a = f + J.T lambda with J a + gamma = 0 at one declared state.

    Requires a finite symmetric positive-definite mass matrix and independent
    constraint rows. This smooth fixed-mode calculation does not enforce a
    contact force cone or simulate impacts.
    """
    metric, load = np.asarray(mass, dtype=float), np.asarray(force, dtype=float)
    rows, gamma = np.asarray(jacobian, dtype=float), np.asarray(curvature, dtype=float)
    if metric.ndim != 2 or metric.shape[0] != metric.shape[1] or metric.shape[0] == 0:
        raise ValueError("Mass metric must be nonempty and square")
    size = metric.shape[0]
    if rows.ndim != 2 or rows.shape[1] != size or rows.shape[0] == 0:
        raise ValueError("Constraint Jacobian must have one column per coordinate")
    if load.shape != (size,) or gamma.shape != (rows.shape[0],):
        raise ValueError("Force and curvature dimensions must match the model")
    if not all(np.all(np.isfinite(value)) for value in (metric, load, rows, gamma)):
        raise ValueError("All model values must be finite")
    if not np.allclose(metric, metric.T, rtol=1e-13, atol=1e-14):
        raise ValueError("Mass metric must be symmetric")
    if np.min(np.linalg.eigvalsh(metric)) <= 0:
        raise ValueError("Mass metric must be positive definite")
    if np.linalg.matrix_rank(rows) != rows.shape[0]:
        raise ValueError("This solver requires independent constraint rows")
    free_acceleration = np.linalg.solve(metric, load)
    inverse_mass_rows = np.linalg.solve(metric, rows.T)
    reaction = np.linalg.solve(rows @ inverse_mass_rows, -gamma - rows @ free_acceleration)
    return free_acceleration + inverse_mass_rows @ reaction, reaction


def rotation_frame(point: ArrayLike) -> NDArray[np.float64]:
    """Return a rotating orthonormal frame tangent to the plane z=0."""
    position = np.asarray(point, dtype=float)
    if position.shape != (3,) or not np.all(np.isfinite(position)):
        raise ValueError("Provide three finite Cartesian coordinates")
    cosine, sine = np.cos(position[0]), np.sin(position[0])
    return np.array([[cosine, -sine], [sine, cosine], [0.0, 0.0]])


def spring_system() -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Return the two unit-mass, unit-spring equations with only mass1 actuated."""
    stiffness = np.array([[2.0, -1.0], [-1.0, 2.0]])
    state_matrix = np.block([[np.zeros((2, 2)), np.eye(2)], [-stiffness, np.zeros((2, 2))]])
    return state_matrix, np.array([[0.0], [0.0], [1.0], [0.0]])


def _arm_endpoint(
    angles: NDArray[np.float64],
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Differentiate a planar two-link endpoint using relative elbow angle."""
    first, second = angles[0], angles.sum()
    proximal, distal = ARM_LENGTHS
    endpoint = proximal * np.array([np.cos(first), np.sin(first)])
    endpoint += distal * np.array([np.cos(second), np.sin(second)])
    derivative = np.array([-distal * np.sin(second), distal * np.cos(second)])
    return endpoint, np.column_stack([[-endpoint[1], endpoint[0]], derivative])


def _rotation(angle: float) -> NDArray[np.float64]:
    """Return the planar rotation mapping club-local vectors into world axes."""
    cosine, sine = np.cos(angle), np.sin(angle)
    return np.array([[cosine, -sine], [sine, cosine]])


def closed_chain(
    configuration: ArrayLike,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Return closure, closure Jacobian and club-point Jacobian for seven coordinates.

    Coordinates are left shoulder/elbow, right shoulder/elbow and club x/y/angle.
    Both grips constrain positions only; no anatomical wrist or ground model is
    implied. Lengths are metres and all angles are radians.
    """
    position = np.asarray(configuration, dtype=float)
    if position.shape != (7,) or not np.all(np.isfinite(position)):
        raise ValueError("Provide seven finite planar linkage coordinates")
    rotation = _rotation(float(position[-1]))
    closure, jacobian = np.zeros(4), np.zeros((4, 7))
    for index in range(2):
        row = slice(2 * index, 2 * index + 2)
        endpoint, arm_jacobian = _arm_endpoint(position[row])
        offset = rotation @ GRIP_OFFSETS[index]
        closure[row] = SHOULDERS[index] + endpoint - position[4:6] - offset
        jacobian[row, row] = arm_jacobian
        jacobian[row, 4:6] = -np.eye(2)
        jacobian[row, -1] = [offset[1], -offset[0]]
    head = rotation @ HEAD_OFFSET
    task_jacobian = np.zeros((2, 7))
    task_jacobian[:, 4:6] = np.eye(2)
    task_jacobian[:, -1] = [-head[1], head[0]]
    return closure, jacobian, task_jacobian


def _inverse_arm(endpoint: NDArray[np.float64]) -> NDArray[np.float64]:
    """Select the positive-elbow branch of a reachable constructed endpoint."""
    proximal, distal = ARM_LENGTHS
    cosine = (endpoint @ endpoint - proximal**2 - distal**2) / (2 * proximal * distal)
    if not -1 <= cosine <= 1:
        raise ValueError("Teaching endpoint is outside the two-link workspace")
    elbow = np.arccos(cosine)
    shoulder = np.arctan2(endpoint[1], endpoint[0]) - np.arctan2(
        distal * np.sin(elbow), proximal + distal * np.cos(elbow)
    )
    return np.array([shoulder, elbow])


def _anisotropic_example() -> ProjectorExample:
    """Compare velocity/force projectors under a non-isotropic mass metric."""
    mass, jacobian = np.array([[2.0, 1.0], [1.0, 3.0]]), np.array([[1.0, 1.0]])
    acceleration, reaction = constraint_solve(mass, [1, 0], jacobian, [0])
    inverse_mass_rows = np.linalg.solve(mass, jacobian.T)
    velocity_map = np.eye(2) - inverse_mass_rows @ np.linalg.solve(
        jacobian @ inverse_mass_rows, jacobian
    )
    force_map = velocity_map.T
    return {
        "acceleration": acceleration.tolist(),
        "reaction": reaction.tolist(),
        "velocity_projector": velocity_map.tolist(),
        "force_projector": force_map.tolist(),
        "force_to_acceleration": np.linalg.solve(mass, force_map).tolist(),
    }


def _circle_example() -> MotionExample:
    """Include centripetal acceleration at a unit-circle point under gravity."""
    acceleration, reaction = constraint_solve(2 * np.eye(2), [0, -19.62], [[1, 0]], [9])
    return {
        "acceleration": acceleration.tolist(),
        "reaction": reaction.tolist(),
        "reaction_power": 0.0,
    }


def _moving_example() -> MovingExample:
    """Account for reaction work when a two-kg particle follows x=t² at t=1."""
    acceleration, reaction = constraint_solve([[2]], [3], [[1]], [-2])
    velocity = 2.0
    return {
        "acceleration": acceleration.tolist(),
        "reaction": reaction.tolist(),
        "reaction_power": float(reaction[0] * velocity),
        "applied_power": 3 * velocity,
        "kinetic_power": float(2 * velocity * acceleration[0]),
    }


def _spring_example() -> SpringExample:
    """Compute finite-horizon input energy without imposing a force cap."""
    state_matrix, input_matrix = spring_system()
    horizon = 2.0

    def integrand(time: float) -> NDArray[np.float64]:
        response = expm(state_matrix * time) @ input_matrix
        return response @ response.T

    gramian, _ = quad_vec(integrand, 0, horizon, epsabs=1e-12, epsrel=1e-12)
    terminal = np.array([0.0, 1.0, 0.0, 0.0])
    controllability = np.column_stack(
        [np.linalg.matrix_power(state_matrix, power) @ input_matrix for power in range(4)]
    )
    return {
        "horizon": horizon,
        "controllability": controllability.tolist(),
        "gramian": gramian.tolist(),
        "minimum_energy": float(terminal @ np.linalg.solve(gramian, terminal)),
    }


def _grasp_example() -> GraspExample:
    """Construct a consistent closure pose and distinguish task/constraint kernels."""
    center = np.array([0.0, 0.5])
    angles = [_inverse_arm(center + GRIP_OFFSETS[i] - SHOULDERS[i]) for i in range(2)]
    configuration = np.r_[angles[0], angles[1], center, 0.0]
    closure, jacobian, task = closed_chain(configuration)
    return {
        "configuration": configuration.tolist(),
        "closure": closure.tolist(),
        "constraint_rank": int(np.linalg.matrix_rank(jacobian)),
        "constraint_nullity": int(null_space(jacobian).shape[1]),
        "stationary_head_nullity": int(null_space(np.vstack([jacobian, task])).shape[1]),
        "jacobian": jacobian.tolist(),
        "task_jacobian": task.tolist(),
    }


def make_examples() -> Examples:
    """Return deterministic teaching results, separate from empirical validation."""
    return {
        "scope": "Constructed examples; no fitted golfer data",
        "anisotropic": _anisotropic_example(),
        "circle": _circle_example(),
        "moving_guide": _moving_example(),
        "springs": _spring_example(),
        "planar_grasp": _grasp_example(),
    }


def main() -> None:
    """Write the reproducible record to an explicit path outside generated output."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    destination = parser.parse_args().output
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(make_examples(), indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    main()
