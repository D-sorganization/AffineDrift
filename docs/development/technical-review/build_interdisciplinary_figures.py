"""Reproduce the declared synthesis map and free two-mass collision calculation."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402 -- select the headless backend first
import numpy as np  # noqa: E402 -- group scientific imports after backend selection
from matplotlib.axes import Axes  # noqa: E402 -- select the headless backend first
from matplotlib.figure import Figure  # noqa: E402 -- select the headless backend first
from matplotlib.patches import FancyBboxPatch  # noqa: E402 -- select the headless backend first

OUTPUT = Path(__file__).resolve().parents[3] / "articles/The_Physics_of_Golf/figures"
MASS = 0.2
BALL_MASS = 0.04593
COLORS = ["#145c86", "#70428c", "#9b4e1a"]


def save(figure: Figure, name: str) -> None:
    """Save both editions with stable vector lettering."""
    for extension in ("pdf", "svg"):
        path = OUTPUT / f"{name}.{extension}"
        figure.savefig(path)
        if extension == "svg":
            text = path.read_text(encoding="utf-8")
            path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n")
    plt.close(figure)


def model_box(axis: Axes, index: int, label: str) -> None:
    """Draw one modeled stage and its forward connection."""
    left = 0.1 + 2 * index
    axis.add_patch(
        FancyBboxPatch(
            (left, 1.8),
            1.65,
            1.0,
            boxstyle="round,pad=0.04",
            facecolor="#eaf2f8",
            edgecolor=COLORS[0],
        )
    )
    axis.text(left + 0.825, 2.3, label, ha="center", va="center", fontsize=10.5)
    if index < 3:
        axis.annotate(
            "",
            (left + 1.96, 2.3),
            (left + 1.7, 2.3),
            arrowprops={"arrowstyle": "->", "color": COLORS[0]},
        )


def measurement_loop(axis: Axes) -> None:
    """Show observations and information for decisions separately."""
    axis.add_patch(
        FancyBboxPatch(
            (2, 0.25),
            5.5,
            0.75,
            boxstyle="round,pad=0.04",
            facecolor="#f3edf8",
            edgecolor=COLORS[1],
        )
    )
    axis.text(
        4.75,
        0.625,
        "Measurements and Analysis\nCalibration, Uncertainty, Identifiability",
        ha="center",
        va="center",
        fontsize=10.5,
    )
    for horizontal in (2.9, 4.9, 6.9):
        axis.annotate(
            "",
            (horizontal, 1.05),
            (horizontal, 1.72),
            arrowprops={"arrowstyle": "->", "color": COLORS[1]},
        )
    axis.annotate(
        "",
        (0.925, 1.74),
        (1.94, 0.625),
        arrowprops={
            "arrowstyle": "->",
            "color": COLORS[1],
            "connectionstyle": "angle,angleA=180,angleB=270",
        },
    )
    axis.text(0.15, 0.3, "Information\nfor Decisions", fontsize=10, color=COLORS[1])


def draw_map() -> None:
    """Distinguish the modeled process from observations and decisions."""
    figure, axis = plt.subplots(figsize=(7.2, 3.9), constrained_layout=True)
    axis.set(xlim=(0, 8), ylim=(0, 4))
    axis.axis("off")
    labels = [
        "Policy\nGoals, Estimates,\nCommands",
        "Body and Club\nActivation, Motion,\nGround and Grip",
        "Impact\nDelivery, Strike,\nContact Response",
        "Flight and Landing\nAir, Spin,\nSurface",
    ]
    for index, label in enumerate(labels):
        model_box(axis, index, label)
    axis.text(
        4,
        3.55,
        "Materials and Environment Enter the Physical Models",
        ha="center",
        fontsize=11,
        color="#713d12",
    )
    measurement_loop(axis)
    save(figure, "interdisciplinary_model_map")


def energy_curves(axis: Axes) -> None:
    """Plot the three energy fractions over restitution."""
    restitution = np.linspace(0, 1, 301)
    ball = MASS * BALL_MASS * (1 + restitution) ** 2 / (MASS + BALL_MASS) ** 2
    lost = (1 - restitution**2) * BALL_MASS / (MASS + BALL_MASS)
    head = ((MASS - restitution * BALL_MASS) / (MASS + BALL_MASS)) ** 2
    for value, label, color, style in zip(
        [ball, head, lost],
        ["Ball", "Other Mass", "Dissipated"],
        COLORS,
        ["-", "--", ":"],
        strict=True,
    ):
        axis.plot(restitution, value, label=label, color=color, ls=style, lw=2)
    axis.set(
        xlabel="Restitution e",
        ylabel="Initial Energy Fraction",
        ylim=(0, 1),
        title="Energy Is Partitioned",
    )
    axis.legend(fontsize=10)
    axis.grid(alpha=0.2)


def energy_example(axis: Axes) -> None:
    """Show the specified restitution example without equating e with energy."""
    selected = np.array(
        [
            MASS * BALL_MASS * 1.83**2 / (MASS + BALL_MASS) ** 2,
            ((MASS - 0.83 * BALL_MASS) / (MASS + BALL_MASS)) ** 2,
            (1 - 0.83**2) * BALL_MASS / (MASS + BALL_MASS),
        ]
    )
    bars = axis.bar(["Ball", "Other\nMass", "Lost"], selected, color=COLORS)
    axis.bar_label(bars, labels=[f"{value:.2%}" for value in selected], fontsize=10.5, padding=3)
    axis.set(ylim=(0, 0.7), ylabel="Initial Energy Fraction", title="Example: e = 0.83")


def draw_energy() -> None:
    """Compose the parameter sweep and the worked example."""
    figure, axes = plt.subplots(1, 2, figsize=(7.2, 3.8), constrained_layout=True)
    energy_curves(axes[0])
    energy_example(axes[1])
    for axis in axes:
        axis.title.set_fontsize(11)
        axis.xaxis.label.set_fontsize(10.5)
        axis.yaxis.label.set_fontsize(10.5)
        axis.tick_params(labelsize=10)
    save(figure, "interdisciplinary_collision_energy")


if __name__ == "__main__":
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "path", "font.size": 10})
    draw_map()
    draw_energy()
