"""Reproduce the declared oscillator response and pressure-boundary diagrams."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402 -- select the headless backend first
import numpy as np  # noqa: E402 -- group scientific imports after backend selection
from matplotlib.axes import Axes  # noqa: E402 -- select the headless backend first
from matplotlib.figure import Figure  # noqa: E402 -- select the headless backend first
from matplotlib.patches import Arc, Circle  # noqa: E402 -- select the headless backend first

OUTPUT = Path(__file__).resolve().parents[3] / "articles/The_Physics_of_Golf/figures"
COLORS = ["#145c86", "#974817"]
MASS = 1.0
STIFFNESS = 5000.0
DAMPING = (200.0, 54.0)


def save(figure: Figure, name: str) -> None:
    """Save print and web vectors with stable paths for mathematical lettering."""
    for extension in ("pdf", "svg"):
        path = OUTPUT / f"{name}.{extension}"
        figure.savefig(path)
        if extension == "svg":
            text = path.read_text(encoding="utf-8")
            path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n")
    plt.close(figure)


def draw_response() -> None:
    """Plot exact zero-velocity releases and base-to-tissue harmonic magnitudes."""
    figure, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), constrained_layout=True)
    time = np.linspace(0, 0.3, 1000)
    frequency = np.geomspace(0.1, 200, 1000)
    omega = 2 * np.pi * frequency
    for damping, color in zip(DAMPING, COLORS, strict=True):
        first, second = np.roots([MASS, damping, STIFFNESS]).astype(complex)
        release = (
            (-second * np.exp(first * time) + first * np.exp(second * time)) / (first - second)
        ).real
        response = (STIFFNESS + 1j * damping * omega) / (
            STIFFNESS - MASS * omega**2 + 1j * damping * omega
        )
        ratio = damping / (2 * np.sqrt(STIFFNESS * MASS))
        label = f"c = {damping:.0f}; ζ = {ratio:.3f}"
        style = "-" if damping == DAMPING[0] else "--"
        axes[0].plot(time, release, color=color, linestyle=style, label=label)
        axes[1].semilogx(frequency, np.abs(response), color=color, linestyle=style)
    axes[0].set(
        title="Fixed-Base Release",
        xlabel="Time (s)",
        ylabel="Relative Displacement / Initial Value",
    )
    axes[0].axhline(0, color="#777777", linewidth=0.6)
    axes[0].legend(fontsize=8.5, loc="upper right")
    axes[1].set(
        title="Prescribed-Base Oscillation",
        xlabel="Excitation Frequency (Hz)",
        ylabel=r"Displacement Ratio $|X_w/X_r|$",
    )
    axes[1].axvline(
        np.sqrt(STIFFNESS / MASS) / (2 * np.pi), color="#777777", linestyle=":", linewidth=0.8
    )
    axes[1].text(
        0.035,
        0.08,
        "Dotted: undamped natural frequency",
        fontsize=8,
        transform=axes[1].transAxes,
        va="top",
    )
    for axis in axes:
        axis.grid(alpha=0.2)
    figure.supxlabel("m = 1 kg; k = 5000 N/m; c in N s/m. Teaching parameters.", fontsize=9)
    save(figure, "soft_tissue_response")


def traction(axis: Axes, angle: float, color: str) -> None:
    """Draw an outward traction at one boundary location."""
    direction = np.array([np.cos(angle), np.sin(angle)])
    axis.annotate(
        "",
        1.35 * direction,
        direction,
        arrowprops={"arrowstyle": "->", "color": color, "linewidth": 1.3},
    )


def draw_pressure() -> None:
    """Distinguish a cap resultant from a complete closed-boundary balance."""
    figure, axes = plt.subplots(1, 2, figsize=(7.2, 3.8), constrained_layout=True)
    cap, closed = axes
    cap.add_patch(Arc((0, 0), 2, 2, theta1=0, theta2=180, color=COLORS[0], linewidth=2))
    cap.plot([-1, 1], [0, 0], linestyle="--", color="#777777")
    for angle in np.linspace(0.12, np.pi - 0.12, 7):
        traction(cap, angle, COLORS[0])
    cap.text(0, 0.45, "Uniform Δp", ha="center", fontsize=11)
    cap.text(0, -0.28, r"Projected Disk: $A=\pi R^2$", ha="center", fontsize=10)
    cap.text(0, -0.65, r"Cap Resultant: $F_z=\Delta p\,\pi R^2$", ha="center", fontsize=10)
    cap.text(
        0,
        -1.08,
        "Curved area is twice the projected area.\nNormals point in different directions.",
        ha="center",
        fontsize=9,
    )
    cap.set_title("Hemispherical Cap (Section)", fontsize=11)
    closed.add_patch(Circle((0, 0), 1, fill=False, color=COLORS[1], linewidth=2))
    for angle in np.linspace(0, 2 * np.pi, 12, endpoint=False):
        traction(closed, angle, COLORS[1])
    closed.text(0, 0.12, "Uniform Pressure\nClosed Boundary", ha="center", va="center", fontsize=10)
    closed.text(
        0, -1.7, "Net Force = 0; Net Moment = 0\nLocal Wall Loads Remain", ha="center", fontsize=10
    )
    closed.set_title("Complete Boundary (Section)", fontsize=11)
    for axis in axes:
        axis.set(xlim=(-1.65, 1.65), ylim=(-1.95, 1.65), aspect="equal")
        axis.axis("off")
    figure.supxlabel(
        "Ideal pressure geometry; wall tension and attachments require separate force balance.",
        fontsize=8.5,
    )
    save(figure, "soft_tissue_pressure")


if __name__ == "__main__":
    plt.rcParams.update({"font.size": 10, "svg.fonttype": "path", "pdf.fonttype": 42})
    draw_response()
    draw_pressure()
