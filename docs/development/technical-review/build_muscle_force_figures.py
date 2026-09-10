"""Reproduce the muscle chapter's declared curves and force network."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


def build_figures() -> None:
    """Write matching vector figures with explicit units and model scope."""
    destination = Path(__file__).resolve().parents[3] / "articles/The_Physics_of_Golf/figures"
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none"})
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.5), constrained_layout=True)
    length = np.linspace(0.5, 1.6, 400)
    axes[0].plot(length, np.exp(-(((length - 1) / 0.5) ** 2)), color="#185d85", label="Active fL")
    axes[0].plot(
        length,
        np.expm1(4 * np.maximum(length - 1, 0)) / np.expm1(2.4),
        "--",
        color="#b44c25",
        label="Passive fP",
    )
    axes[0].set(
        xlabel="Fiber length / optimal length", ylabel="Force multiplier", title="Length Curves"
    )
    k, ceiling = 0.4, 1.4
    c = (ceiling - 1) / (1 + 1 / k)
    shortening = np.linspace(0, 1, 300)
    lengthening = np.linspace(-1, 0, 300)
    axes[1].plot(
        lengthening,
        1 + (ceiling - 1) * -lengthening / (c - lengthening),
        "--",
        color="#b44c25",
        label="Lengthening",
    )
    axes[1].plot(
        shortening, (1 - shortening) / (1 + shortening / k), color="#185d85", label="Shortening"
    )
    axes[1].axhline(ceiling, color="#555", lw=0.8, ls=":")
    axes[1].set(
        xlabel="w = −fiber velocity / Vmax",
        ylabel="Force multiplier fV",
        title="Velocity Curve",
        ylim=(0, 1.5),
    )
    for ax in axes:
        ax.legend(fontsize=8, loc="lower left")
        ax.grid(alpha=0.2)
    for suffix in ("svg", "pdf"):
        fig.savefig(destination / f"muscle_force_curves.{suffix}", facecolor="white")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.1, 3.6), constrained_layout=True)
    ax.set(xlim=(0, 10), ylim=(0, 5))
    ax.axis("off")
    for x, y, width, height, label in [
        (0.4, 3.0, 2.2, 0.8, "Contractile\nCE"),
        (0.4, 1.7, 2.2, 0.8, "Passive\nPEE"),
        (3.6, 2.3, 2.0, 0.9, "Pennation\nprojection"),
        (6.3, 2.3, 1.4, 0.9, "Tendon\nSEE"),
        (8.4, 2.3, 1.3, 0.9, "Skeletal\npath"),
    ]:
        ax.add_patch(
            FancyBboxPatch(
                (x, y), width, height, boxstyle="round,pad=0.03", fc="#e8f2f8", ec="#185d85"
            )
        )
        ax.text(x + width / 2, y + height / 2, label, ha="center", va="center")
    ax.plot([0.2, 0.2, 0.4], [2.1, 3.4, 3.4], color="#185d85")
    ax.plot([0.2, 0.4], [2.1, 2.1], color="#185d85")
    ax.plot([2.6, 3.0, 3.0, 2.6], [3.4, 3.4, 2.1, 2.1], color="#185d85")
    for start, end in [
        ((3.0, 2.75), (3.6, 2.75)),
        ((5.6, 2.75), (6.3, 2.75)),
        ((7.7, 2.75), (8.4, 2.75)),
    ]:
        ax.add_patch(
            FancyArrowPatch(start, end, arrowstyle="->", mutation_scale=12, color="#185d85")
        )
    ax.text(5, 4.5, "Parallel Fiber Forces, Then a Series Tendon", ha="center", fontsize=12)
    ax.text(5, 1.05, r"$F_T=(F_{CE}+F_{PE})\cos\alpha$", ha="center", fontsize=13)
    ax.text(
        5, 0.35, "Fiber output = skeletal output + tendon storage rate", ha="center", fontsize=11
    )
    for suffix in ("svg", "pdf"):
        fig.savefig(destination / f"muscle_force_network.{suffix}", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    build_figures()
