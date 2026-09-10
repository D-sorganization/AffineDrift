"""Reproduce the chapter's manufactured covariance and trial-update figures."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def build_figures() -> None:
    """Write matching vector figures for the print and web editions."""
    destination = Path(__file__).resolve().parents[3] / "articles/The_Physics_of_Golf/figures"
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "svg.fonttype": "none"})
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.7), constrained_layout=True)
    theta = np.linspace(0, 2 * np.pi, 301)
    circle = np.vstack([np.cos(theta), np.sin(theta)])
    for ax, covariance, color, title in zip(
        axes,
        [np.array([[1, 0.9], [0.9, 1]]), np.array([[4, -3.8], [-3.8, 4]])],
        ["#b44c25", "#185d85"],
        ["A: Task Variance 3.8 deg²", "B: Task Variance 0.4 deg²"],
        strict=True,
    ):
        values, vectors = np.linalg.eigh(covariance)
        ellipse = vectors @ np.diag(np.sqrt(values)) @ circle
        ax.fill(*ellipse, color=color, alpha=0.25)
        ax.plot(*ellipse, color=color, lw=2)
        ax.plot([-3, 3], [3, -3], "--", color="#555", label="Zero task error")
        ax.set(
            xlim=(-3, 3),
            ylim=(-3, 3),
            xlabel="Joint deviation q₁ (deg)",
            ylabel="Joint deviation q₂ (deg)",
            title=title,
            aspect="equal",
        )
        ax.grid(alpha=0.2)
    axes[0].legend(loc="upper left", fontsize=8)
    for suffix in ("svg", "pdf"):
        fig.savefig(destination / f"motor_learning_covariance.{suffix}", facecolor="white")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.1, 3.9), constrained_layout=True)
    trials = np.arange(10)
    for gain, color, style in [
        (0.25, "#185d85", "o-"),
        (1.5, "#4a7929", "s--"),
        (2.1, "#b44c25", "^:"),
    ]:
        ax.plot(
            trials,
            4 * (1 - gain) ** trials,
            style,
            color=color,
            lw=2,
            markersize=4,
            label=f"b = {gain:g}",
        )
    ax.axhline(0, color="#777", lw=0.8)
    ax.set(
        xlabel="Trial index n",
        ylabel="Task error eₙ (arbitrary units)",
        title="A Larger Update Can Destabilize Learning",
    )
    ax.legend(ncol=3, loc="upper center")
    ax.grid(alpha=0.2)
    for suffix in ("svg", "pdf"):
        fig.savefig(destination / f"motor_learning_updates.{suffix}", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    build_figures()
