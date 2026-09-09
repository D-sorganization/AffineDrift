"""Reproduce the textbook's interface ledger and passive two-rod trajectory."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402 -- select headless backend before pyplot
import numpy as np
from scipy.integrate import solve_ivp

from src.tools.energy_ledger_examples import rod_energy_ledger
from src.tools.lagrangian_examples import RodPair

OUTPUT = Path(__file__).resolve().parents[3] / "articles/The_Physics_of_Golf/figures"
BLUE = "#17658b"
RUST = "#a14520"


def save(figure: plt.Figure, stem: str) -> None:
    """Save identical vector layouts for print and web."""
    for extension in ("pdf", "svg"):
        path = OUTPUT / f"{stem}.{extension}"
        figure.savefig(path)
        if extension == "svg":
            lines = path.read_text(encoding="utf-8").splitlines()
            path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")
    plt.close(figure)


def interface_figure() -> None:
    """Show paired physical ledgers without implying a universal flow direction."""
    figure, axis = plt.subplots(figsize=(9.6, 4.2), layout="constrained")
    axis.axis("off")
    box = {"boxstyle": "round,pad=0.8", "facecolor": "#edf5f8", "edgecolor": BLUE}
    axis.text(
        0.22,
        0.68,
        "Arm Mechanical Energy\nBase Input − F · vH − n ωarm",
        ha="center",
        va="center",
        bbox=box,
        linespacing=1.8,
    )
    axis.text(
        0.78,
        0.68,
        "Club Mechanical Energy\nF · vH + n ωclub",
        ha="center",
        va="center",
        bbox=box,
        linespacing=1.8,
    )
    axis.annotate(
        "", (0.60, 0.44), (0.40, 0.44), arrowprops={"arrowstyle": "<->", "color": RUST, "lw": 2}
    )
    axis.text(
        0.5,
        0.34,
        "Signed Hinge-Force Power: F · vH\nDirection Depends on the State",
        ha="center",
        va="top",
        linespacing=1.6,
        color=RUST,
    )
    axis.text(
        0.5,
        0.08,
        "Combined Input: Base Power + n (ωclub − ωarm)\n"
        "Gravity Is Included in Each Body's Potential; No Dissipation Is Modeled",
        ha="center",
        va="center",
        linespacing=1.6,
    )
    axis.set_title("An Internal Force Transfers Energy; a Hinge Motor Can Also Supply It")
    save(figure, "energy_interface_ledger")


def passive_figure() -> None:
    """Integrate a specified free mechanism and display reversible transfer."""
    model, torques = RodPair(gravity=0), np.zeros(2)

    def derivative(_time: float, state: np.ndarray) -> np.ndarray:
        """Return absolute angular rates and accelerations for integration."""
        return np.r_[state[2:], model.acceleration(state, torques)]

    time = np.linspace(0, 2, 1001)
    result = solve_ivp(
        derivative, (0, 2), [0, -np.pi / 2, 2, 2], t_eval=time, rtol=1e-11, atol=1e-13
    )
    if not result.success:
        raise RuntimeError(result.message)
    ledgers = [rod_energy_ledger(model, state, torques) for state in result.y.T]
    energies = np.array([ledger.kinetic for ledger in ledgers])
    np.testing.assert_allclose(energies.sum(axis=1), 10 / 3, atol=2e-9, rtol=0)
    figure, axes = plt.subplots(1, 2, figsize=(9.6, 4.2), layout="constrained")
    axes[0].plot(time, energies[:, 0], color=BLUE, label="Inner Rod")
    axes[0].plot(time, energies[:, 1], color=RUST, label="Outer Rod")
    axes[0].axhline(10 / 3, color="gray", linestyle="--", label="Constant Total")
    axes[0].set(xlabel="Time (s)", ylabel="Kinetic Energy (J)", title="Redistribution Can Reverse")
    axes[0].legend(fontsize=9, loc="lower left")
    axes[1].plot(time, [ledger.force_power for ledger in ledgers], color=RUST)
    axes[1].axhline(0, color="gray", linewidth=0.8)
    axes[1].set(
        xlabel="Time (s)",
        ylabel="Power Into Outer Rod (W)",
        title="Positive and Negative Interface Power",
    )
    for axis in axes:
        axis.grid(alpha=0.18)
    figure.suptitle("Two Unit Rods: Fixed Base, Zero Gravity, No Motors or Losses")
    save(figure, "energy_passive_transfer")


def main() -> None:
    """Generate the paired teaching figures."""
    plt.rcParams.update({"font.size": 10, "svg.fonttype": "none"})
    interface_figure()
    passive_figure()


if __name__ == "__main__":
    main()
