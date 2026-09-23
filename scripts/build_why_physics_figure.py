"""Reproduce Chapter 1's manufactured retained-hinge/released-mass illustration."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

# This high-speed example separates normal acceleration from power; it is not a golfer fit.
RADIUS = 1.25  # m
SPEED = 40.0  # m/s
GRAVITY_M_S2 = 9.81  # m/s^2
DURATION = 0.06  # s
SAMPLES = 601


def trajectory_data() -> dict[str, NDArray[np.float64]]:
    """Return SI-unit trajectories for identical initial states and two constraints.

    The retained model is an undriven, fixed-length pendulum. The released model
    removes the tether without an impulse. Both ignore drag and use uniform gravity.
    """
    time = np.linspace(0.0, DURATION, SAMPLES)
    solution = solve_ivp(
        lambda _time, state: [state[1], -GRAVITY_M_S2 / RADIUS * np.sin(state[0])],
        (0.0, DURATION),
        [0.0, SPEED / RADIUS],
        t_eval=time,
        rtol=1e-11,
        atol=1e-12,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    angle = solution.y[0]
    retained = RADIUS * np.column_stack((np.sin(angle), -np.cos(angle)))
    released = np.column_stack((SPEED * time, -RADIUS - GRAVITY_M_S2 * time**2 / 2))
    return {"time": time, "retained": retained, "released": released}


def build_figure(output_dir: Path) -> None:
    """Write readable SVG/PDF companions; create the requested directory if absent."""
    data = trajectory_data()
    output_dir.mkdir(parents=True, exist_ok=True)
    with plt.rc_context({"font.size": 12, "svg.hashsalt": "why-physics-v1"}):
        fig, axis = plt.subplots(figsize=(8.0, 5.4), layout="constrained")
        for key, label, color, style in (
            ("retained", "Hinge Retained, Zero Drive Torque", "#17619c", "-"),
            ("released", "Tether Removed, No Impulse", "#a83a00", "--"),
        ):
            xy = data[key]
            axis.plot(xy[:, 0], xy[:, 1], style, color=color, linewidth=2.5, label=label)
            axis.scatter(xy[::100, 0], xy[::100, 1], color=color, s=22)
        axis.plot([0, 0], [0, -RADIUS], ":", color="#555555", linewidth=1.5)
        axis.scatter([0], [0], marker="s", color="black", zorder=4)
        axis.annotate("Fixed Pivot", (0, 0), xytext=(-0.32, 0.21))
        axis.annotate(
            "Same Initial Position and Velocity",
            (0, -RADIUS),
            xytext=(0.10, -0.87),
            arrowprops={"arrowstyle": "->"},
        )
        axis.set(
            xlabel="Horizontal Position (m)",
            ylabel="Vertical Position (m)",
            title="Same Initial State, Different Retained Constraints",
            xlim=(-0.4, 2.55),
            ylim=(-1.65, 0.65),
            aspect="equal",
        )
        axis.grid(alpha=0.25)
        axis.legend(loc="lower center", bbox_to_anchor=(0.5, -0.43), frameon=False)
        # Freeze the same bytes before and after Git's cross-platform newline handling.
        with (output_dir / "why_physics_release.svg").open(
            "w", encoding="utf-8", newline="\n"
        ) as svg:
            fig.savefig(svg, format="svg", metadata={"Date": None})
        fig.savefig(output_dir / "why_physics_release.pdf", metadata={"CreationDate": None})
        plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    build_figure(parser.parse_args().output_dir)
