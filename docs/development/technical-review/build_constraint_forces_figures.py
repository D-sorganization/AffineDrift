"""Reproduce manufactured Chapter 7 constraints, impulses and physical energies."""

import json
from importlib import import_module
from pathlib import Path

import matplotlib
import numpy as np
from scipy.integrate import solve_ivp

matplotlib.use("Agg")
import matplotlib.pyplot as plt

AFFINE = import_module("docs.development.technical-review.build_affine_structure_figures")
operators = AFFINE.operators
ROOT = Path(__file__).resolve().parents[3]
FIGURES = ROOT / "articles/The_Physics_of_Golf/figures"
INITIAL_ANGLES = np.deg2rad([45.0, 70.0])
TIME = np.linspace(0, 0.1, 201)


def constrained_acceleration(
    mass: np.ndarray, force: np.ndarray, jacobian: np.ndarray, gamma: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Solve a regular ideal mode; require SPD inertia and independent Jacobian rows."""
    inverse_normal = np.linalg.solve(mass, jacobian.T)
    free = np.linalg.solve(mass, force)
    reaction = np.linalg.solve(jacobian @ inverse_normal, -jacobian @ free - gamma)
    return free + inverse_normal @ reaction, reaction


def plastic_engagement(
    mass: np.ndarray, before: np.ndarray, jacobian: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Project an incoming velocity onto a newly engaged stationary ideal constraint."""
    inverse_normal = np.linalg.solve(mass, jacobian.T)
    impulse = np.linalg.solve(jacobian @ inverse_normal, -jacobian @ before)
    return before + inverse_normal @ impulse, impulse


def segment_kinetic(q: np.ndarray, velocity: np.ndarray) -> np.ndarray:
    """Compute each physical body's COM translation plus centroidal rotation energy."""
    first_rate, second_rate = velocity[0], velocity.sum()
    first_tangent = np.array([np.cos(q[0]), np.sin(q[0])])
    second_tangent = np.array([np.cos(q.sum()), np.sin(q.sum())])
    distal_com_velocity = (
        AFFINE.LENGTH_FIRST * first_rate * first_tangent
        + AFFINE.COM_SECOND * second_rate * second_tangent
    )
    first = 0.5 * (AFFINE.INERTIA_FIRST + AFFINE.MASS_FIRST * AFFINE.COM_FIRST**2)
    return np.array(
        [
            first * first_rate**2,
            0.5 * AFFINE.MASS_SECOND * (distal_com_velocity @ distal_com_velocity)
            + 0.5 * AFFINE.INERTIA_SECOND * second_rate**2,
        ]
    )


def total_energy(q: np.ndarray, velocity: np.ndarray) -> float:
    """Return full mechanical energy with a common downward-vertical potential datum."""
    potential = -AFFINE.GRAVITY_M_S2 * (
        AFFINE.GRAVITY_FIRST * np.cos(q[0]) + AFFINE.GRAVITY_SECOND * np.cos(q.sum())
    )
    return float(sum(segment_kinetic(q, velocity)) + potential)


def free_derivative(time: float, state: np.ndarray) -> np.ndarray:
    """Evolve two attached links with free relative rotation and zero applied torque."""
    mass, bias, gravity = operators(state[:2], state[2:])
    return np.r_[state[2:], np.linalg.solve(mass, -bias - gravity)]


def reduced_derivative(time: float, state: np.ndarray, tangent: np.ndarray) -> np.ndarray:
    """Use exact reduced coordinates so the stationary linear constraint cannot drift."""
    q, velocity = INITIAL_ANGLES + tangent * state[0], tangent * state[1]
    mass, bias, gravity = operators(q, velocity)
    acceleration = -(tangent @ (bias + gravity)) / (tangent @ mass @ tangent)
    return np.array([state[1], acceleration])


def trajectory(mode: str, refined: bool = False) -> np.ndarray:
    """Integrate free/guide from (8,-8), or the distinct relative lock from (8,0)."""
    if mode not in {"free", "guide", "lock"}:
        raise ValueError("mode must be free, guide or lock")
    tangent = np.array([1.0, -1.0]) if mode != "lock" else np.array([1.0, 0.0])
    initial = np.r_[INITIAL_ANGLES, 8 * tangent] if mode == "free" else [0.0, 8.0]
    solution = solve_ivp(
        free_derivative if mode == "free" else reduced_derivative,
        (TIME[0], TIME[-1]),
        initial,
        args=() if mode == "free" else (tangent,),
        method="DOP853",
        t_eval=TIME,
        rtol=1e-12 if refined else 1e-10,
        atol=1e-13 if refined else 1e-12,
        max_step=0.001 if refined else 0.002,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    if mode == "free":
        return solution.y.T
    angles = INITIAL_ANGLES + solution.y[0, :, None] * tangent
    rates = solution.y[1, :, None] * tangent
    return np.column_stack((angles, rates))


def instantaneous_report() -> dict:
    """Evaluate compatible guide reactions and explicitly impulsive incompatible capture."""
    velocity, jacobian = np.array([8.0, -8.0]), np.array([[1.0, 1.0]])
    mass, bias, gravity = operators(INITIAL_ANGLES, velocity)
    acceleration, reaction = constrained_acceleration(mass, -bias - gravity, jacobian, np.zeros(1))
    before = np.array([8.0, 12.0])
    after, impulse = plastic_engagement(mass, before, jacobian)
    return {
        "mass_kg_m2": mass.tolist(),
        "bias_N_m": bias.tolist(),
        "gravity_N_m": gravity.tolist(),
        "free_acceleration_rad_s2": np.linalg.solve(mass, -bias - gravity).tolist(),
        "guide_acceleration_rad_s2": acceleration.tolist(),
        "guide_multiplier_N_m": reaction.tolist(),
        "guide_coordinate_power_W": (velocity * reaction[0]).tolist(),
        "capture_velocity_before_rad_s": before.tolist(),
        "capture_velocity_after_rad_s": after.tolist(),
        "capture_impulse_N_m_s": impulse.tolist(),
        "capture_segment_kinetic_before_J": segment_kinetic(INITIAL_ANGLES, before).tolist(),
        "capture_segment_kinetic_after_J": segment_kinetic(INITIAL_ANGLES, after).tolist(),
    }


def example_report() -> dict:
    """Report integration convergence, energy and endpoints without biological inference."""
    records = {}
    for mode in ("free", "guide", "lock"):
        coarse, fine = trajectory(mode), trajectory(mode, True)
        energy = np.array([total_energy(row[:2], row[2:]) for row in fine])
        records[mode] = {
            "final_angles_deg": np.rad2deg(fine[-1, :2]).tolist(),
            "final_rates_rad_s": fine[-1, 2:].tolist(),
            "energy_range_J": float(np.ptp(energy)),
            "refinement_max_state_difference": float(np.max(np.abs(coarse - fine))),
        }
    return {
        "authority": "Manufactured two-link example; no golfer calibration or physiological inference",
        "instantaneous": instantaneous_report(),
        "trajectories": records,
    }


def draw_trajectories(axes: np.ndarray) -> None:
    """Compare attached free motion with a world-orientation guide from identical states."""
    for mode, color in (("free", "#176a9a"), ("guide", "#994a1f")):
        states = trajectory(mode, True)
        for index, label in enumerate(("First-Link Angle", "Relative Angle")):
            axes[0].plot(
                TIME,
                np.rad2deg(states[:, index]),
                color=color,
                linestyle="-" if index == 0 else "--",
                label=f"{mode.title()}: {label}",
            )
    states = trajectory("guide", True)
    reactions = []
    for row in states:
        mass, bias, gravity = operators(row[:2], row[2:])
        _, reaction = constrained_acceleration(
            mass, -bias - gravity, np.array([[1.0, 1.0]]), np.zeros(1)
        )
        reactions.append(reaction[0])
    axes[1].plot(TIME, reactions, color="#994a1f")
    axes[0].set(ylabel="Angle (Degrees)", title="Same Initial State, Different Constraint Modes")
    axes[0].legend(fontsize=9)
    axes[1].set(
        xlabel="Time (s)",
        ylabel="Guide Moment (N m)",
        title="Reaction of the World-Orientation Guide",
    )
    for axis in axes:
        axis.grid(alpha=0.2)


def main() -> None:
    """Write reproducible vector figures and the chapter's numerical evidence."""
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none"})
    figure, axes = plt.subplots(2, 1, figsize=(9, 8), constrained_layout=True)
    draw_trajectories(axes)
    for extension in ("svg", "pdf"):
        figure.savefig(FIGURES / f"constraint_forces_verified.{extension}", facecolor="white")
    report = Path(__file__).with_name("constraint-forces-numerics.json")
    report.write_text(json.dumps(example_report(), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
