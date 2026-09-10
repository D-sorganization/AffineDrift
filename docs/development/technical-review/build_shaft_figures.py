"""Reproduce the shaft chapter's declared static shape and driven oscillator."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm

DESTINATION = Path(__file__).resolve().parents[3] / "articles/The_Physics_of_Golf/figures"


def save_figure(figure: plt.Figure, name: str) -> None:
    """Write paired vector formats from the same plotted data."""
    for extension in ("pdf", "svg"):
        figure.savefig(DESTINATION / f"{name}.{extension}", facecolor="white")
    plt.close(figure)


def static_shape() -> None:
    """Plot a static admissible shape, explicitly not an exact vibration mode."""
    fraction = np.linspace(0, 1, 401)
    shape = (3 * fraction**2 - fraction**3) / 2
    figure, axes = plt.subplots(1, 2, figsize=(7.1, 3.1), constrained_layout=True)
    axes[0].plot(fraction, shape, color="#185d85", lw=2)
    axes[0].set(
        xlabel="Position z/L", ylabel="Deflection / tip deflection", title="Static Cantilever Shape"
    )
    axes[1].plot(fraction, 3 * fraction - 1.5 * fraction**2, color="#b44c25", lw=2)
    axes[1].set(
        xlabel="Position z/L", ylabel="Slope × L / tip deflection", title="Tip Slope Also Changes"
    )
    for axis in axes:
        axis.grid(alpha=0.2)
    save_figure(figure, "shaft_bending_shape")


def base_response() -> None:
    """Integrate the manufactured example and check an independent exponential."""
    amplitude, omega, mass, stiffness, damping = 0.02, np.pi / 0.2, 0.2, 80.0, 0.64
    times = np.linspace(0, 0.4, 801)
    solution = solve_ivp(
        lambda time, state: [
            state[1],
            -stiffness / mass * state[0]
            - damping / mass * state[1]
            + amplitude * omega**2 * np.sin(omega * time),
        ],
        (0, 0.4),
        [0, 0],
        t_eval=times,
        rtol=1e-11,
        atol=1e-13,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    matrix = np.array(
        [[0, 1, 0, 0], [-400, -3.2, amplitude * omega**2, 0], [0, 0, 0, omega], [0, 0, -omega, 0]]
    )
    for index in (100, 200, 400, 600, 800):
        np.testing.assert_allclose(
            solution.y[:, index], (expm(matrix * times[index]) @ [0, 0, 0, 1])[:2], atol=2e-11
        )
    plot_response(times, solution.y, (amplitude, omega))


def plot_response(times: np.ndarray, state: np.ndarray, forcing: tuple[float, float]) -> None:
    """Display prescribed, absolute and relative quantities with distinct labels."""
    amplitude, omega = forcing
    base = amplitude * np.sin(omega * times)
    base_velocity = amplitude * omega * np.cos(omega * times)
    figure, axes = plt.subplots(2, 1, figsize=(7.1, 4.8), constrained_layout=True, sharex=True)
    axes[0].plot(times, base, "--", color="#555555", label="Prescribed base / rigid head")
    axes[0].plot(times, base + state[0], color="#185d85", label="Flexible head")
    axes[0].set(ylabel="Position (m)", title="Prescribed-Base Teaching Response")
    axes[1].plot(times, base_velocity, "--", color="#555555", label="Base / rigid head velocity")
    axes[1].plot(times, base_velocity + state[1], color="#185d85", label="Absolute head velocity")
    axes[1].plot(times, state[1], ":", color="#b44c25", label="Relative deformation velocity")
    axes[1].set(xlabel="Time (s)", ylabel="Velocity (m/s)")
    for axis in axes:
        axis.legend(fontsize=8, loc="lower left")
        axis.grid(alpha=0.2)
        axis.axhline(0, color="#555555", lw=0.5)
    save_figure(figure, "shaft_base_response")


if __name__ == "__main__":
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none"})
    static_shape()
    base_response()
