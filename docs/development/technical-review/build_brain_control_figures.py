"""Reproduce declared motor-control examples; none are measured golfer data."""

import json
from pathlib import Path

import matplotlib
import numpy as np
from scipy.optimize import lsq_linear

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
FIGURES = ROOT / "articles/The_Physics_of_Golf/figures"


def euler_prediction(state: np.ndarray, derivative: np.ndarray, step: float) -> np.ndarray:
    """Advance a state with a first-order, dimensionally consistent local step."""
    return state + step * derivative


def bounded_inverse_example() -> tuple[np.ndarray, np.ndarray]:
    """Return bounded least-squares input and desired-minus-achieved residual."""
    matrix = np.array([[0.0], [0.0], [1.0], [1.0]])
    desired = np.array([0.0, 1.0, 3.0, 0.0])
    result = lsq_linear(matrix, desired, bounds=(-1, 1), tol=1e-13)
    if not result.success:
        raise RuntimeError(result.message)
    return result.x, desired - matrix @ result.x


def activation_impulse(remaining: float, tau: float) -> float:
    """Integrate a unit step through a zero-initial-state first-order actuator."""
    if remaining < 0 or tau <= 0:
        raise ValueError("Remaining time must be nonnegative and time constant positive")
    return float(remaining + tau * np.expm1(-remaining / tau))


def projected_variances() -> list[float]:
    """Project equal marginal variances through a declared normalized sum output."""
    sensitivity = np.array([1.0, 1.0]) / np.sqrt(2)
    return [
        float(sensitivity @ (0.02**2 * np.array([[1, rho], [rho, 1]])) @ sensitivity)
        for rho in (0.0, -0.75, 0.9)
    ]


def delay_phase_degrees(frequency_hz: float, delay_seconds: float) -> float:
    """Return unwrapped phase from a pure delay, without other loop dynamics."""
    return -360 * frequency_hz * delay_seconds


def variational_free_energy(belief: np.ndarray, joint: np.ndarray) -> float:
    """Compute the finite-state variational identity for strictly positive inputs."""
    if not np.isclose(belief.sum(), 1) or np.any(belief <= 0) or np.any(joint <= 0):
        raise ValueError("Use a normalized positive belief and positive joint probabilities")
    return float(np.sum(belief * np.log(belief / joint)))


def draw_response(ax: plt.Axes) -> None:
    """Show how time remaining and activation jointly limit a declared response."""
    horizon = np.linspace(0, 0.15, 301)
    ax.plot(horizon * 1000, horizon * 1000, label="Instant Actuation", color="#176a9a")
    for tau, color in [(0.025, "#994a1f"), (0.05, "#704296")]:
        impulse = [activation_impulse(float(t), tau) for t in horizon]
        ax.plot(
            horizon * 1000,
            np.array(impulse) * 1000,
            label=f"Activation Time Constant {tau * 1000:.0f} ms",
            color=color,
        )
    ax.set(
        xlabel="Time Remaining After Delay (ms)",
        ylabel="Normalized Impulse (ms)",
        title="Available Time Is Not Instantaneous Authority",
    )
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)


def draw_nodes(ax: plt.Axes, nodes: dict[str, tuple[int, int, str]]) -> dict[str, plt.Text]:
    """Place labels before clipping connector arrows to their boundaries."""
    boxes = {}
    for key, (x, y, title) in nodes.items():
        label = (
            title.replace(" and ", "\nand ")
            .replace("Delayed Sensory ", "Delayed Sensory\n")
            .replace("Learning Across ", "Learning Across\n")
        )
        boxes[key] = ax.text(
            x,
            y,
            label,
            ha="center",
            va="center",
            fontsize=9,
            bbox={"boxstyle": "round,pad=0.6", "fc": "#eef4f8", "ec": "#176a9a"},
        )
    return boxes


def draw_architecture(ax: plt.Axes) -> None:
    """Draw functional roles, deliberately avoiding one-to-one neural assignments."""
    ax.set(xlim=(0, 10), ylim=(0, 7))
    ax.axis("off")
    nodes = {
        "goal": (2, 6, "Task, Context and Learned Policy"),
        "command": (2, 4, "Command and Activation"),
        "plant": (2, 2, "Body, Club and Contact"),
        "sense": (7, 2, "Delayed Sensory Observations"),
        "estimate": (7, 4, "State Estimate and Prediction"),
        "learn": (7, 6, "Learning Across Trials"),
    }
    boxes = draw_nodes(ax, nodes)
    ax.figure.canvas.draw()
    for start, end in [
        ("goal", "command"),
        ("command", "plant"),
        ("plant", "sense"),
        ("sense", "estimate"),
        ("estimate", "goal"),
        ("learn", "goal"),
        ("estimate", "learn"),
    ]:
        x1, y1, _ = nodes[start]
        x2, y2, _ = nodes[end]
        ax.annotate(
            "",
            (x2, y2),
            (x1, y1),
            arrowprops={
                "arrowstyle": "->",
                "patchA": boxes[start].get_bbox_patch(),
                "patchB": boxes[end].get_bbox_patch(),
                "shrinkA": 4,
                "shrinkB": 4,
            },
        )
    ax.annotate(
        "",
        (6, 4),
        (3, 4),
        arrowprops={"arrowstyle": "->", "linestyle": "dashed", "color": "#994a1f"},
    )
    ax.text(4.5, 4.35, "Command Copy", ha="center", fontsize=8)
    ax.text(5, 0.6, "Functional Connections; Not an Anatomical Wiring Map", ha="center", fontsize=9)
    ax.set_title("Preparation, Estimation and Feedback Interact")


def main() -> None:
    """Write the shared vector diagram and manufactured numerical report."""
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none"})
    fig, axes = plt.subplots(2, 1, figsize=(9, 10), constrained_layout=True)
    draw_architecture(axes[0])
    draw_response(axes[1])
    for extension in ("svg", "pdf"):
        fig.savefig(FIGURES / f"brain_control_verified.{extension}", facecolor="white")
    plt.close(fig)
    control, residual = bounded_inverse_example()
    report = {
        "authority": "Manufactured mathematical examples; no golfer calibration",
        "bounded_input": control.tolist(),
        "feasibility_residual": residual.tolist(),
        "normalized_impulse_seconds": {
            str(t): activation_impulse(t, 0.05) for t in (0.01, 0.04, 0.1)
        },
        "projected_variances": projected_variances(),
    }
    Path(__file__).with_name("brain-control-numerical-results.json").write_bytes(
        (json.dumps(report, indent=2) + "\n").encode()
    )


if __name__ == "__main__":
    main()
