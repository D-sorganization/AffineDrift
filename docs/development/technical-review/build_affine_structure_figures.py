"""Reproduce explicitly manufactured affine mechanics and control examples."""

import json
from pathlib import Path

import matplotlib
import numpy as np
from scipy.integrate import solve_ivp

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
FIGURES = ROOT / "articles/The_Physics_of_Golf/figures"
GRAVITY = 9.81
MASS_FIRST, MASS_SECOND = 2.5, 0.4
LENGTH_FIRST, COM_FIRST, COM_SECOND = 0.35, 0.175, 0.5
INERTIA_FIRST, INERTIA_SECOND = 0.025, 0.03
A = INERTIA_FIRST + MASS_FIRST * COM_FIRST**2 + MASS_SECOND * LENGTH_FIRST**2
D = INERTIA_SECOND + MASS_SECOND * COM_SECOND**2
B = MASS_SECOND * LENGTH_FIRST * COM_SECOND
GRAVITY_FIRST = MASS_FIRST * COM_FIRST + MASS_SECOND * LENGTH_FIRST
GRAVITY_SECOND = MASS_SECOND * COM_SECOND


def operators(q: np.ndarray, velocity: np.ndarray) -> tuple[np.ndarray, ...]:
    """Return complete mass, velocity bias and potential gradient for two links."""
    coupling = B * np.cos(q[1])
    mass = np.array([[A + D + 2 * coupling, D + coupling], [D + coupling, D]])
    bias = (
        B
        * np.sin(q[1])
        * np.array([-2 * velocity[0] * velocity[1] - velocity[1] ** 2, velocity[0] ** 2])
    )
    distal = GRAVITY_SECOND * GRAVITY * np.sin(q[0] + q[1])
    gravity = np.array([GRAVITY_FIRST * GRAVITY * np.sin(q[0]) + distal, distal])
    return mass, bias, gravity


def locked_derivative(time: float, state: np.ndarray) -> np.ndarray:
    """Reduced q2=0 dynamics, with zero proximal input and ideal lock reaction."""
    inertia = A + D + 2 * B
    restoring = GRAVITY * (GRAVITY_FIRST + GRAVITY_SECOND)
    return np.array([state[1], -restoring * np.sin(state[0]) / inertia])


def locked_trajectory(refined: bool = False):
    """Integrate the same reduced drift at two accuracy levels for comparison."""
    return solve_ivp(
        locked_derivative,
        (0, 2),
        [0.9, 0.0],
        method="DOP853",
        t_eval=np.linspace(0, 2, 801),
        rtol=1e-12 if refined else 1e-10,
        atol=1e-13 if refined else 1e-12,
        max_step=0.005 if refined else 0.01,
    )


def locked_energy(state: np.ndarray) -> np.ndarray:
    """Mechanical energy of the stationary-lock reduced system, in joules."""
    inertia = A + D + 2 * B
    restoring = GRAVITY * (GRAVITY_FIRST + GRAVITY_SECOND)
    return 0.5 * inertia * state[1] ** 2 - restoring * np.cos(state[0])


def minimum_energy_input(time: float | np.ndarray, rate: float) -> np.ndarray:
    """Optimal normalized input for z'=rate*z+u, z(0)=0 and z(1)=1."""
    gramian = np.expm1(2 * rate) / (2 * rate) if rate else 1.0
    return np.exp(rate * (1 - np.asarray(time))) / gramian


def draw_phase(ax: plt.Axes) -> None:
    """Draw normalized directions and a computed reduced-system integral curve."""
    angles, rates = np.meshgrid(np.linspace(-1.2, 1.2, 13), np.linspace(-4, 4, 13))
    restoring = GRAVITY * (GRAVITY_FIRST + GRAVITY_SECOND) / (A + D + 2 * B)
    accelerations = -restoring * np.sin(angles)
    magnitude = np.hypot(rates, accelerations)
    nonzero = magnitude > 1e-12
    ax.quiver(
        angles[nonzero],
        rates[nonzero],
        rates[nonzero] / magnitude[nonzero],
        accelerations[nonzero] / magnitude[nonzero],
        color="#176a9a",
        alpha=0.55,
        angles="xy",
        scale_units="xy",
        scale=6,
    )
    solution = locked_trajectory()
    ax.plot(solution.y[0], solution.y[1], color="#994a1f", label="Computed Zero-Input Orbit")
    ax.plot([0.9], [0], "o", color="#994a1f", label="Initial State")
    ax.set(
        xlabel="Angle / (1 rad)",
        ylabel="Angular Rate / (1 rad/s)",
        title="Reduced Drift With an Ideal Distal Lock",
        xlim=(-1.3, 1.3),
        ylim=(-4.2, 4.2),
    )
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)


def draw_timing(ax: plt.Axes) -> None:
    """Compare provably minimum-energy timing for different normalized plants."""
    time = np.linspace(0, 1, 201)
    for rate, color in [(-2, "#704296"), (0, "#176a9a"), (2, "#994a1f")]:
        ax.plot(time, minimum_energy_input(time, rate), color=color, label=f"Plant Rate a = {rate}")
    ax.set(
        xlabel="Normalized Time",
        ylabel="Normalized Input",
        title="Optimal Timing Depends on the Plant and Task",
    )
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)


def example_report() -> dict:
    """Report defined states without labelling them measured golf phases."""
    records = []
    for angles, rates in [
        ([0, 0], [0, 0]),
        ([45, 0], [0, 0]),
        ([150, -70], [0, 0]),
        ([140, -60], [5, 0]),
    ]:
        q, velocity = np.deg2rad(angles), np.array(rates, dtype=float)
        mass, bias, gravity = operators(q, velocity)
        drift = -np.linalg.solve(mass, bias + gravity)
        capacity = 30 * np.linalg.norm(np.linalg.inv(mass), 2)
        records.append(
            dict(
                angles_deg=angles,
                rates=rates,
                mass=mass.tolist(),
                bias=bias.tolist(),
                gravity=gravity.tolist(),
                drift_acceleration=drift.tolist(),
                acceleration_capacity=capacity,
                dcr_capacity=np.linalg.norm(drift) / capacity,
            )
        )
    solution = locked_trajectory(True)
    return {
        "authority": "Manufactured parameters and tasks; no golfer calibration",
        "states": records,
        "locked_energy_range_joules": float(np.ptp(locked_energy(solution.y))),
    }


def main() -> None:
    """Write the shared vector figure and its numerical evidence report."""
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none"})
    fig, axes = plt.subplots(2, 1, figsize=(9, 10), constrained_layout=True)
    draw_phase(axes[0])
    draw_timing(axes[1])
    for extension in ("svg", "pdf"):
        fig.savefig(FIGURES / f"affine_structure_verified.{extension}", facecolor="white")
    plt.close(fig)
    Path(__file__).with_name("affine-structure-numerical-results.json").write_bytes(
        (json.dumps(example_report(), indent=2) + "\n").encode()
    )


if __name__ == "__main__":
    main()
