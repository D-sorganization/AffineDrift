"""Reproduce the spatial chapter's force/power and inertia-energy figures."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402 -- select a headless backend before pyplot
import numpy as np

OUTPUT = Path(__file__).resolve().parents[3] / "articles/The_Geometry_of_Motion/figures"
BLUE = "#17658b"
RUST = "#a14520"


def save(figure: plt.Figure, stem: str) -> None:
    """Save the same layout as vector print and web assets."""
    for extension in ("pdf", "svg"):
        path = OUTPUT / f"{stem}.{extension}"
        figure.savefig(path)
        if extension == "svg":
            lines = path.read_text(encoding="utf-8").splitlines()
            path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")
    plt.close(figure)


def power_figure() -> None:
    """Show a reporting-origin shift with numerically invariant power."""
    figure, axes = plt.subplots(1, 2, figsize=(9.6, 4.2), layout="constrained")
    for index, axis in enumerate(axes):
        axis.plot([0, 0.2], [0, 0], "o-", color=BLUE, linewidth=3)
        axis.annotate("A", (0, 0), xytext=(-0.01, -0.06))
        axis.annotate("B", (0.2, 0), xytext=(0.2, -0.06))
        axis.annotate(
            "", (0.2, 0.23), (0.2, 0), arrowprops={"arrowstyle": "->", "color": RUST, "lw": 2}
        )
        axis.text(0.22, 0.15, "Force: 10 N", color=RUST)
        axis.text(0.04, -0.12, "Origin Separation: 0.2 m")
        if index == 0:
            axis.set_title("Report About B")
            statement = "Moment: 0 N m\nLinear y Velocity: 2 m/s\nPower: 10 × 2 = 20 W"
        else:
            axis.set_title("Report About A")
            statement = (
                "Moment: +2 N m About z\nLinear y Block: 1.4 m/s\nPower: 2 × 3 + 10 × 1.4 = 20 W"
            )
        axis.text(-0.03, -0.23, statement, va="top", linespacing=1.6)
        axis.set(xlim=(-0.06, 0.53), ylim=(-0.47, 0.32), aspect="equal")
        axis.axis("off")
    figure.suptitle("One Force and One Rigid Motion: Angular Speed +3 rad/s About z")
    save(figure, "spatial_wrench_power")


def energy_figure() -> None:
    """Compare physical energy and configuration-dependent joint inertia."""
    figure, axes = plt.subplots(1, 2, figsize=(9.6, 4.4), layout="constrained")
    speed = np.linspace(-0.7, 0.1, 401)
    translation = (speed + 0.3) ** 2
    axes[0].plot(speed, translation, color=BLUE, label="Point Mass: Central J = 0")
    axes[0].plot(speed, translation + 0.05, color=RUST, label="Extended Body: J = 0.1 kg m²")
    axes[0].axvline(-0.3, color="gray", linestyle=":")
    axes[0].set(
        xlabel="Origin y Velocity (m/s)",
        ylabel="Kinetic Energy (J)",
        title="Energy Depends on the Mass Distribution",
    )
    axes[0].legend(fontsize=8, loc="upper center")
    axes[0].text(
        0.5,
        0.5,
        "m = 2 kg; c = (0.3, 0, 0) m\nAngular Velocity: (0, 0, 1) rad/s",
        transform=axes[0].transAxes,
        fontsize=8,
        ha="center",
    )
    angle = np.linspace(-np.pi, np.pi, 401)
    axes[1].plot(angle, 0.6175 + 0.3 * np.cos(angle), color=BLUE, label="M₁₁")
    axes[1].plot(angle, 0.0675 + 0.15 * np.cos(angle), color=RUST, label="M₁₂ = M₂₁")
    axes[1].axhline(0.0675, color="gray", linestyle="--", label="M₂₂")
    axes[1].set(
        xlabel="Relative Elbow Angle (rad)",
        ylabel="Joint Inertia Entry (kg m²)",
        title="Articulation Changes the Joint Mass Matrix",
    )
    axes[1].legend(fontsize=9)
    for axis in axes:
        axis.grid(alpha=0.18)
    save(figure, "spatial_inertia_energy")


def main() -> None:
    """Generate both figures using the chapter's declared teaching values."""
    plt.rcParams.update({"font.size": 10, "svg.fonttype": "none"})
    power_figure()
    energy_figure()


if __name__ == "__main__":
    main()
