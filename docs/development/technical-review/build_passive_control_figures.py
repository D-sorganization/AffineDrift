"""Reproduce the chapter's manufactured damping-regime phase portraits."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[3]
FIGURES = ROOT / "articles/The_Physics_of_Golf/figures"


def build_damping_regimes() -> None:
    """Plot exact constant-coefficient trajectories with common physical axes."""
    plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 10, "svg.fonttype": "none"})
    time = np.linspace(0, 2, 801)
    initial = np.array([0.1, 0.0])
    figure, axes = plt.subplots(1, 3, figsize=(11, 3.6), sharex=True, sharey=True)
    for axis, damping, title in zip(
        axes,
        (5.0, 20.0, 50.0),
        ("Underdamped", "Critically Damped", "Overdamped"),
        strict=True,
    ):
        matrix = np.array([[0.0, 1.0], [-100.0, -damping]])
        trajectory = np.array([expm(matrix * t) @ initial for t in time])
        if damping == 20:
            exact = 0.1 * (1 + 10 * time) * np.exp(-10 * time)
            if not np.allclose(trajectory[:, 0], exact, atol=1e-12, rtol=1e-12):
                raise RuntimeError("Critical trajectory disagrees with its analytic solution.")
        axis.plot(trajectory[:, 0], trajectory[:, 1], color="#176a9a", linewidth=2)
        for start in (15, 45, 110):
            axis.annotate(
                "",
                xy=trajectory[start + 9],
                xytext=trajectory[start],
                arrowprops={"arrowstyle": "->", "color": "#a34d21", "lw": 1.6},
            )
        axis.scatter(*initial, color="#a34d21", s=22, zorder=3)
        axis.scatter(0, 0, color="black", s=14, zorder=3)
        axis.axhline(0, color="gray", linewidth=0.6)
        axis.axvline(0, color="gray", linewidth=0.6)
        axis.set_title(f"{title}\nD = {damping:g} N m s/rad")
        axis.set_xlabel("Position Error (rad)")
        axis.set_xlim(-0.06, 0.115)
        axis.set_xticks([-0.05, 0, 0.05, 0.1])
        axis.set_ylim(-0.75, 0.45)
        axis.grid(alpha=0.25)
    axes[0].set_ylabel("Velocity Error (rad/s)")
    figure.suptitle("Equal Inertia and Stiffness; Different Recovery Dynamics")
    figure.tight_layout()
    for extension in ("svg", "pdf"):
        figure.savefig(FIGURES / f"passive_damping_regimes.{extension}", bbox_inches="tight")
    svg = FIGURES / "passive_damping_regimes.svg"
    svg.write_text(
        "\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n",
        encoding="utf-8",
    )
    plt.close(figure)


if __name__ == "__main__":
    build_damping_regimes()
