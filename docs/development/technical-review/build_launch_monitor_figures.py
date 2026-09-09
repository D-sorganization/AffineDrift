"""Reproduce the manufactured geometry figures for technical review #4309."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

root = Path(__file__).resolve().parents[3]
scratch = Path(__file__).parent
destination = root / "static/images"
plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "svg.fonttype": "path",
        "svg.hashsalt": "launch-monitor-4309",
    }
)
colors = ["#185f8c", "#a44810", "#246c4a"]


def save(fig: Figure, name: str) -> None:
    """Write a deterministic SVG and a PNG for independent visual inspection."""
    fig.savefig(destination / (name + ".svg"), metadata={"Date": None}, facecolor="white")
    fig.savefig(scratch / (name + ".png"), dpi=170, facecolor="white")
    path = destination / (name + ".svg")
    path.write_text(
        "\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n",
        encoding="utf-8",
    )
    plt.close(fig)


fig, axes = plt.subplots(1, 3, figsize=(9, 3.5), constrained_layout=True)
axes[0].set_title("Identical Image Lines")
for y in [-0.001, 0.001]:
    axes[0].plot([-0.002, 0.002], [y, y], color="#343a40", linewidth=2)
axes[0].set(
    xlim=(-0.0025, 0.0025),
    ylim=(-0.0017, 0.0017),
    xlabel="Normalized Image x",
    ylabel="Normalized Image y",
)
axes[0].ticklabel_format(style="sci", axis="both", scilimits=(0, 0))
sets = [
    np.array([[0.0, -0.001, 1.0], [0.0, 0.001, 1.0]]),
    np.array([[0.0, -0.000998, 0.998], [0.0, 0.001002, 1.002]]),
]
for number, (ax, points) in enumerate(zip(axes[1:], sets, strict=True)):
    points *= 0.002 / np.linalg.norm(points[1] - points[0])
    center = points.mean(axis=0)
    local = (points - center) * 1000
    ax.plot(local[:, 1], local[:, 2], "-o", color=colors[number], linewidth=2)
    normal = np.cross([1.0, 0.0, 0.0], points[1] - points[0])
    normal /= -np.linalg.norm(normal)
    ax.annotate(
        "",
        xy=(normal[1] * 0.65, normal[2] * 0.65),
        xytext=(0, 0),
        arrowprops={"arrowstyle": "->", "lw": 2, "color": colors[number]},
    )
    ax.text(-1.3, 1.18, f"Center Depth: {center[2]:.6f} m", fontsize=8)
    ax.text(-1.3, -1.28, "Groove Separation: 2 mm", fontsize=8)
    ax.set_title(["Plane A: 0°", "Plane B: 63.435°"][number])
    ax.set(
        xlim=(-1.4, 1.4),
        ylim=(-1.4, 1.4),
        xlabel="Lateral Offset (mm)",
        ylabel="Depth Offset (mm)",
        aspect="equal",
    )
for ax in axes:
    ax.grid(alpha=0.2)
    ax.spines[["top", "right"]].set_visible(False)
fig.suptitle("Same Image, Different Face Planes", fontsize=14)
save(fig, "launch-monitor-groove-ambiguity")

origin = np.array([2.0, 0.2, 0.1])
offsets = np.random.default_rng(4309).uniform(-0.05, 0.05, (30, 3))
sensors = [np.zeros(3), np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 1.0])]
matrices = []
for sensor in sensors:
    directions = origin + offsets - sensor
    directions /= np.linalg.norm(directions, axis=1)[:, None]
    matrices.append(np.column_stack((np.cross(offsets, directions), directions)))
scales = np.diag([20.0, 20.0, 20.0, 1.0, 1.0, 1.0])
fig, axes = plt.subplots(1, 3, figsize=(9, 3.4), constrained_layout=True, sharey=True)
for count, ax in enumerate(axes, 1):
    matrix = np.vstack(matrices[:count])
    values = np.linalg.svd(matrix @ scales / 0.01, compute_uv=False)
    rank = int(np.linalg.matrix_rank(matrix))
    for column, value in enumerate(values):
        if column < rank:
            ax.bar(column + 1, value, color=colors[count - 1], width=0.6)
        else:
            ax.text(column + 1, 0.0018, "0", ha="center", va="bottom", fontweight="bold")
    ax.set(yscale="log", ylim=(0.001, 10000), xticks=range(1, 7), xlabel="Singular-Value Index")
    ax.set_title(f"{count} " + ("Location" if count == 1 else "Locations") + f": Rank {rank}")
    ax.grid(axis="y", alpha=0.2)
    ax.spines[["top", "right"]].set_visible(False)
axes[0].set_ylabel("Scaled, Noise-Whitened Value")
fig.suptitle("Independent Viewing Locations Change Doppler Observability", fontsize=13)
save(fig, "launch-monitor-doppler-rank")
print("Two SVG figures and inspection PNGs written.")
