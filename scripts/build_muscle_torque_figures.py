"""Render the constructed Chapter 16 force-feasibility and power examples."""

from itertools import product
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from scipy.spatial import ConvexHull


def _plot_torque_set(axis: Axes) -> None:
    """Map the independently verified force box into its torque polygon."""
    moment_arms = np.array([[0.04, 0.02, -0.03], [0, 0.03, 0.02]])
    capacity = np.array([400, 300, 250])
    corners = np.array(list(product([0, 1], repeat=3))) * capacity
    torques = corners @ moment_arms.T
    hull = ConvexHull(torques)
    polygon = torques[hull.vertices]
    axis.fill(*polygon.T, color="#c7e0ef", label="Feasible Torque Set")
    closed = np.vstack([polygon, polygon[0]])
    axis.plot(*closed.T, color="#17608a", linewidth=1.8)
    axis.scatter([6.5, 22], [7, 14], color=["#17608a", "#a34716"], zorder=3)
    axis.annotate(
        "Feasible (6.5, 7)",
        (6.5, 7),
        xytext=(-4, 9.3),
        arrowprops={"arrowstyle": "->", "color": "#17608a"},
    )
    axis.annotate(
        "Infeasible (22, 14)",
        (22, 14),
        xytext=(1, 16.2),
        arrowprops={"arrowstyle": "->", "color": "#a34716"},
    )
    axis.set(
        xlabel="Coordinate 1 Torque (Nm)",
        ylabel="Coordinate 2 Torque (Nm)",
        title="Coupled Torque\nCapacity",
        yticks=[0, 5, 10, 15],
        ylim=(-1, 19),
        xlim=(-9, 26),
    )


def _plot_power(axis: Axes) -> None:
    """Compare coordinate powers at the two declared velocity pairs."""
    positions = np.arange(2)
    axis.bar(positions - 0.18, [12, 12], 0.36, label="Coordinate 1", color="#17608a")
    axis.bar(positions + 0.18, [-12, -36], 0.36, label="Coordinate 2", color="#a34716")
    axis.axhline(0, color="#555555", linewidth=0.8)
    axis.set(
        xticks=positions,
        xticklabels=["Speeds (2, −1)\nNet 0 W", "Speeds (2, −3)\nNet −24 W"],
        xlabel="Coordinate Speeds (rad/s)",
        ylabel="Power Delivered to Coordinate (W)",
        title="One Muscle,\nTwo Power Outcomes",
    )
    axis.legend(loc="lower left", fontsize=14)


def build_figures(destination: Path) -> None:
    """Save both publication formats of the constructed mechanics figure."""
    with plt.rc_context({"font.size": 16, "svg.fonttype": "none", "svg.hashsalt": "muscle"}):
        figure, axes = plt.subplots(1, 2, figsize=(10, 5.2), layout="constrained")
        _plot_torque_set(axes[0])
        _plot_power(axes[1])
        for axis in axes:
            axis.spines[["top", "right"]].set_visible(False)
        destination.mkdir(parents=True, exist_ok=True)
        for extension in ("svg", "pdf"):
            figure.savefig(
                destination / f"muscle_torque_feasibility.{extension}",
                metadata={"Creator": "AffineDrift; constructed Chapter 16 examples"},
            )
        plt.close(figure)
    svg_path = destination / "muscle_torque_feasibility.svg"
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_path.read_text(encoding="utf-8").splitlines())
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    build_figures(Path(__file__).resolve().parents[1] / "articles/The_Physics_of_Golf/figures")
