"""Reproduce the declared three-link examples using existing checked dynamics.

Run from the repository root with ``python -m docs.development.technical-review.
build_triple_pendulum_figures``. All parameters are manufactured, not golfer data.
"""

import json
from pathlib import Path

import matplotlib
import numpy as np
from scipy.integrate import solve_ivp

from src.affine_control.golf_model import GolfModel
from src.affine_control.rnea import PlanarChain, PlanarLink

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
FIGURES = ROOT / "articles/The_Physics_of_Golf/figures"
MODEL = GolfModel(masses=(2.0, 0.5, 0.2), lengths=(0.4, 0.3, 0.5), inertias=(0.05, 0.01, 0.01))
CHAIN = PlanarChain(
    tuple(
        PlanarLink(mass, length, length / 2, inertia)
        for mass, length, inertia in zip(MODEL.masses, MODEL.lengths, MODEL.inertias, strict=True)
    )
)
INITIAL_ANGLES = np.deg2rad([50.0, 80.0, 100.0])
INITIAL_VELOCITY = np.array([12.0, 20.0, 25.0])
DURATION_SECONDS = 0.05
LINK_COLORS = ("#176a9a", "#994a1f", "#704296")


def horizontal_angles(q: np.ndarray) -> np.ndarray:
    """Translate the chapter's downward-vertical origin to the library's +x origin."""
    return np.asarray(q) - np.array([np.pi / 2, 0.0, 0.0])


def derivative(time: float, state: np.ndarray) -> np.ndarray:
    """Return unforced rigid-chain dynamics; time is unused by this autonomous ODE."""
    q, velocity = horizontal_angles(state[:3]), state[3:]
    bias = CHAIN.inverse_dynamics(q, velocity, np.zeros(3))
    return np.concatenate([velocity, -np.linalg.solve(MODEL.rigid_mass_matrix(q), bias)])


def trajectory(refined: bool = False):
    """Integrate the same initial state on a fixed output grid at two accuracies."""
    return solve_ivp(
        derivative,
        (0, DURATION_SECONDS),
        np.concatenate([INITIAL_ANGLES, INITIAL_VELOCITY]),
        method="DOP853",
        t_eval=np.linspace(0, DURATION_SECONDS, 501),
        rtol=1e-12 if refined else 1e-10,
        atol=1e-13 if refined else 1e-12,
        max_step=0.0005 if refined else 0.001,
    )


def segment_energies(q: np.ndarray, velocity: np.ndarray) -> np.ndarray:
    """Include moving COM translation and each link's absolute angular velocity."""
    horizontal = horizontal_angles(q)
    angular = np.cumsum(velocity)
    linear = np.stack([MODEL.com_jacobian(horizontal, index) @ velocity for index in range(3)])
    return 0.5 * (
        np.array(MODEL.masses) * np.sum(linear**2, axis=1) + np.array(MODEL.inertias) * angular**2
    )


def total_energy(state: np.ndarray) -> float:
    """Return kinetic plus gravitational potential energy in joules."""
    return float(sum(segment_energies(state[:3], state[3:]))) + MODEL.potential_energy(
        horizontal_angles(state[:3])
    )


def release_accelerations(q: np.ndarray, velocity: np.ndarray) -> tuple:
    """Compare a compatible ideal q3 lock with its impulse-free removal.

    The multiplier is defined by M*a + bias = A.T*lambda, A = [0, 0, 1].
    """
    if velocity[2] != 0:
        raise ValueError("A locked relative wrist requires zero relative wrist velocity")
    horizontal = horizontal_angles(q)
    mass = MODEL.rigid_mass_matrix(horizontal)
    bias = CHAIN.inverse_dynamics(horizontal, velocity, np.zeros(3))
    axis = np.array([[0.0, 0.0, 1.0]])
    system = np.block([[mass, -axis.T], [axis, np.zeros((1, 1))]])
    locked = np.linalg.solve(system, np.concatenate([-bias, [0.0]]))
    return locked[:3], -np.linalg.solve(mass, bias), float(locked[3])


def numerical_report(solution) -> dict:
    """Collect the exact inputs and results used in the chapter and its exercises."""
    q = np.deg2rad([50.0, 90.0, 100.0])
    matrix = MODEL.rigid_mass_matrix(horizontal_angles(q))
    locked, free, reaction = release_accelerations(INITIAL_ANGLES, np.array([12.0, 20.0, 0.0]))
    energies = np.array([total_energy(state) for state in solution.y.T])
    samples = []
    for index in (0, 250, 500):
        state = solution.y[:, index]
        samples.append(
            {
                "time": float(solution.t[index]),
                "angles_degrees": np.rad2deg(state[:3]).tolist(),
                "relative_rates": state[3:].tolist(),
                "absolute_rates": np.cumsum(state[3:]).tolist(),
                "segment_kinetic_energy": segment_energies(state[:3], state[3:]).tolist(),
                "tip_speed": MODEL.clubhead_speed(horizontal_angles(state[:3]), state[3:]),
            }
        )
    return {
        "mass_matrix": matrix.tolist(),
        "inverse": np.linalg.inv(matrix).tolist(),
        "eigenvalues": np.linalg.eigvalsh(matrix).tolist(),
        "initial_acceleration": derivative(0, solution.y[:, 0])[3:].tolist(),
        "locked_acceleration": locked.tolist(),
        "released_acceleration": free.tolist(),
        "lock_reaction": reaction,
        "energy_range_joules": float(np.ptp(energies)),
        "refinement_max_state_difference": float(np.max(np.abs(solution.y - trajectory(True).y))),
        "samples": samples,
    }


def draw_configuration(axis: plt.Axes) -> None:
    """Show actual link directions and absolute angles without false relative arcs."""
    angles = np.cumsum(INITIAL_ANGLES)
    vectors = np.array(MODEL.lengths)[:, None] * np.stack([np.sin(angles), -np.cos(angles)], axis=1)
    points = np.vstack([np.zeros(2), np.cumsum(vectors, axis=0)])
    for index, color in enumerate(LINK_COLORS):
        pair = points[index : index + 2]
        axis.plot(pair[:, 0], pair[:, 1], "o-", color=color, lw=3)
        midpoint = pair.mean(axis=0)
        offset = (10, -10) if index == 1 else (8, 4)
        axis.annotate(f"Link {index + 1}", midpoint, xytext=offset, textcoords="offset points")
    axis.plot([0, 0], [0, -0.2], "k--", lw=1)
    axis.annotate(
        "Downward\nVertical",
        (0, -0.17),
        (0.08, -0.35),
        arrowprops={"arrowstyle": "->", "lw": 0.8},
        fontsize=8,
    )
    axis.set(
        title="Fixed-Pivot Three-Link Model", xlabel="Horizontal Position (m)", ylabel="Height (m)"
    )
    axis.set_aspect("equal")
    axis.set_xlim(-0.30, 0.80)
    axis.set_ylim(-0.40, 0.60)
    axis.text(
        0.03,
        0.97,
        "Relative q = (50°, 80°, 100°)\nAbsolute θ = (50°, 130°, 230°)",
        transform=axis.transAxes,
        va="top",
        fontsize=9,
    )


def build_figures() -> None:
    """Save a shared vector figure and the reproducible numeric audit."""
    solution = trajectory()
    if not solution.success:
        raise RuntimeError(solution.message)
    plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 10, "svg.fonttype": "none"})
    figure, axes = plt.subplots(1, 2, figsize=(10.5, 4.0))
    draw_configuration(axes[0])
    rates = np.cumsum(solution.y[3:], axis=0)
    for index, label in enumerate(("Upper Arm", "Forearm", "Club")):
        axes[1].plot(solution.t * 1000, rates[index], label=label, color=LINK_COLORS[index], lw=2)
    axes[1].set(
        title="Zero-Torque Absolute Angular Rates",
        xlabel="Time (ms)",
        ylabel="Angular Velocity (rad/s)",
    )
    axes[1].legend()
    axes[1].grid(alpha=0.2)
    figure.suptitle("Manufactured Rigid-Chain Example; No Golfer Calibration")
    figure.tight_layout()
    for extension in ("svg", "pdf"):
        figure.savefig(FIGURES / f"triple_pendulum_verified.{extension}", bbox_inches="tight")
    plt.close(figure)
    output = Path(__file__).with_name("triple-pendulum-numerical-results.json")
    output.write_bytes((json.dumps(numerical_report(solution), indent=2) + "\n").encode("utf-8"))


if __name__ == "__main__":
    build_figures()
