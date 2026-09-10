"""Reproduce Chapter 3 geometry and independently testable manufactured examples."""

import json
from importlib import import_module
from pathlib import Path

import matplotlib
import numpy as np
from scipy.linalg import eigh

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc

AFFINE = import_module("docs.development.technical-review.build_affine_structure_figures")
ROOT = Path(__file__).resolve().parents[3]
FIGURES = ROOT / "articles/The_Physics_of_Golf/figures"
LENGTH_SECOND = 1.0  # m; distal endpoint, distinct from the 0.5 m COM distance.


def radial(angle: float) -> np.ndarray:
    """Return the unit direction measured counterclockwise from downward vertical."""
    return np.array([np.sin(angle), -np.cos(angle)])


def tangent(angle: float) -> np.ndarray:
    """Differentiate radial direction with respect to the declared angle."""
    return np.array([np.cos(angle), np.sin(angle)])


def endpoint(q: np.ndarray) -> np.ndarray:
    """Locate the distal endpoint in the fixed inertial plane, in metres."""
    return AFFINE.LENGTH_FIRST * radial(q[0]) + LENGTH_SECOND * radial(q.sum())


def endpoint_jacobian(q: np.ndarray) -> np.ndarray:
    """Map relative coordinate rates to inertial endpoint velocity."""
    distal = LENGTH_SECOND * tangent(q.sum())
    return np.column_stack((AFFINE.LENGTH_FIRST * tangent(q[0]) + distal, distal))


def endpoint_acceleration(
    q: np.ndarray, velocity: np.ndarray, acceleration: np.ndarray
) -> np.ndarray:
    """Include both tangential acceleration and the normal curvature terms."""
    curvature = -AFFINE.LENGTH_FIRST * velocity[0] ** 2 * radial(
        q[0]
    ) - LENGTH_SECOND * velocity.sum() ** 2 * radial(q.sum())
    return endpoint_jacobian(q) @ acceleration + curvature


def potential(q: np.ndarray) -> float:
    """Use the pivot-height datum with inertial vertical positive upward."""
    return float(
        -AFFINE.GRAVITY_M_S2
        * (AFFINE.GRAVITY_FIRST * np.cos(q[0]) + AFFINE.GRAVITY_SECOND * np.cos(q.sum()))
    )


def energy(q: np.ndarray, velocity: np.ndarray) -> float:
    """Return kinetic plus gravitational potential energy of the declared two bodies."""
    mass = AFFINE.operators(q, velocity)[0]
    return float(0.5 * velocity @ mass @ velocity + potential(q))


def coriolis_matrix(q: np.ndarray, velocity: np.ndarray) -> np.ndarray:
    """Use the Christoffel factorization, with skew-symmetric mass_dot minus 2C."""
    first, second = velocity
    return AFFINE.B * np.sin(q[1]) * np.array([[-second, -first - second], [first, 0]])


def gravity_stiffness() -> np.ndarray:
    """Linearize the restoring gradient at both links hanging downward."""
    distal = AFFINE.GRAVITY_SECOND
    return AFFINE.GRAVITY_M_S2 * np.array(
        [[AFFINE.GRAVITY_FIRST + distal, distal], [distal, distal]]
    )


def small_oscillation_frequencies() -> np.ndarray:
    """Return positive natural angular frequencies of the conservative linearization."""
    mass = AFFINE.operators(np.zeros(2), np.zeros(2))[0]
    return np.sqrt(eigh(gravity_stiffness(), mass, eigvals_only=True))


def example_report() -> dict:
    """Compute instantaneous examples without describing them as measured golf data."""
    q, velocity = np.deg2rad([0.0, -5.0]), np.array([10.0, 9.0])
    mass, bias, gravity = AFFINE.operators(q, velocity)
    zero_input = np.linalg.solve(mass, -bias - gravity)
    torque = np.array([5.0, 0.0])
    driven = np.linalg.solve(mass, torque - bias - gravity)
    top = np.deg2rad([150.0, -70.0])
    return {
        "authority": "Manufactured rigid planar model; not a measured golfer or impact collision",
        "mass_kg_m2": mass.tolist(),
        "bias_N_m": bias.tolist(),
        "potential_gradient_N_m": gravity.tolist(),
        "zero_input_acceleration_rad_s2": zero_input.tolist(),
        "five_N_m_proximal_acceleration_rad_s2": driven.tolist(),
        "endpoint_velocity_m_s": (endpoint_jacobian(q) @ velocity).tolist(),
        "zero_input_endpoint_acceleration_m_s2": endpoint_acceleration(
            q, velocity, zero_input
        ).tolist(),
        "free_distal_effective_inertia_kg_m2": float(mass[0, 0] - mass[0, 1] ** 2 / mass[1, 1]),
        "total_kinetic_energy_J": float(0.5 * velocity @ mass @ velocity),
        "top_to_downward_gravity_work_J": potential(top) - potential(np.zeros(2)),
        "top_physical_gravity_torque_N_m": (-AFFINE.operators(top, np.zeros(2))[2]).tolist(),
        "rigid_rotation_normal_acceleration_in_g": 10.47**2 * 1.35 / AFFINE.GRAVITY_M_S2,
        "small_oscillation_angular_frequencies_rad_s": small_oscillation_frequencies().tolist(),
    }


def draw_geometry(axis: plt.Axes) -> None:
    """Construct link positions, COMs and angle arcs from one explicit geometry."""
    q = np.deg2rad([55.0, -65.0])
    hinge = AFFINE.LENGTH_FIRST * radial(q[0])
    tip = endpoint(q)
    center1 = AFFINE.COM_FIRST * radial(q[0])
    center2 = hinge + AFFINE.COM_SECOND * radial(q.sum())
    axis.plot([0, hinge[0]], [0, hinge[1]], color="#176a9a", linewidth=5)
    axis.plot([hinge[0], tip[0]], [hinge[1], tip[1]], color="#994a1f", linewidth=5)
    axis.scatter(*np.column_stack((center1, center2)), s=70, color="black", zorder=5)
    axis.plot([0, 0], [0, -0.4], "--", color="gray")
    extension = hinge + 0.35 * radial(q[0])
    axis.plot([hinge[0], extension[0]], [hinge[1], extension[1]], "--", color="gray")
    axis.add_patch(Arc((0, 0), 0.3, 0.3, theta1=-90, theta2=-35, color="#176a9a"))
    axis.add_patch(Arc(hinge, 0.3, 0.3, theta1=-100, theta2=-35, color="#994a1f"))
    for point, text, offset in (
        (np.zeros(2), "Fixed Pivot O", (-0.23, 0.06)),
        (center1, "COM 1", (-0.22, -0.02)),
        (center2, "COM 2", (0.05, 0.01)),
        (hinge, "Hinge H", (0.07, 0.04)),
        (tip, "Endpoint P", (-0.11, -0.07)),
    ):
        axis.text(*(point + offset), text, fontsize=10)
    axis.text(0.02, -0.2, "q₁ = +55°", fontsize=10)
    axis.text(0.42, -0.4, "q₂ = −65°", fontsize=10)
    axis.set(
        xlabel="Horizontal Position (m)",
        ylabel="Vertical Position (m)",
        title="Declared Two-Link Geometry",
        xlim=(-0.35, 0.78),
        ylim=(-1.35, 0.15),
    )
    axis.set_aspect("equal")


def main() -> None:
    """Write the shared vector geometry and canonical numerical evidence."""
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none"})
    figure, axis = plt.subplots(figsize=(7, 8), constrained_layout=True)
    draw_geometry(axis)
    for extension in ("svg", "pdf"):
        figure.savefig(FIGURES / f"double_pendulum_verified.{extension}", facecolor="white")
    Path(__file__).with_name("double-pendulum-numerics.json").write_text(
        json.dumps(example_report(), indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
