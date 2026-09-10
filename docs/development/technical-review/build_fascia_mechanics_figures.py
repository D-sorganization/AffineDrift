"""Reproduce the chapter's manufactured standard-linear-solid response."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
FIGURES = ROOT / "articles/The_Physics_of_Golf/figures"
EQUILIBRIUM_MPA = 1.0
BRANCH_MPA = 4.0
RELAXATION_SECONDS = 0.05
STRAIN_AMPLITUDE = 0.02


def relaxation_panel(axis: plt.Axes) -> None:
    """Plot the exact response after an ideal imposed strain step."""
    time = np.linspace(0, 0.3, 501)
    stress = STRAIN_AMPLITUDE * (EQUILIBRIUM_MPA + BRANCH_MPA * np.exp(-time / RELAXATION_SECONDS))
    axis.plot(time, stress * 1000, color="#176a9a", linewidth=2)
    axis.axhline(20, color="#994a1f", linestyle="--", label="Equilibrium: 20 kPa")
    axis.scatter([0.05], [49.4303553], color="#176a9a", s=25)
    axis.annotate("49.43 kPa at 0.05 s", (0.05, 49.43), (0.10, 70), arrowprops={"arrowstyle": "->"})
    axis.set(
        title="Held Strain: Stress Relaxes", xlabel="Time After Step (s)", ylabel="Stress (kPa)"
    )
    axis.set_xlim(0, 0.3)
    axis.set_ylim(0, 110)
    axis.legend(loc="upper right", fontsize=9)
    axis.grid(alpha=0.2)


def cyclic_panel(axis: plt.Axes) -> None:
    """Plot steady harmonic cycles about a declared tensile bias."""
    phase = np.linspace(0, 2 * np.pi, 501)
    strain = STRAIN_AMPLITUDE * np.sin(phase)
    for frequency, color in ((1.0, "#994a1f"), (20.0, "#176a9a")):
        scaled = 2 * np.pi * frequency * RELAXATION_SECONDS
        storage = EQUILIBRIUM_MPA + BRANCH_MPA * scaled**2 / (1 + scaled**2)
        loss = BRANCH_MPA * scaled / (1 + scaled**2)
        stress = STRAIN_AMPLITUDE * (storage * np.sin(phase) + loss * np.cos(phase))
        axis.plot(strain * 100, stress * 1000, color=color, label=f"{frequency:g} Hz", linewidth=2)
        axis.annotate(
            "",
            (strain[71] * 100, stress[71] * 1000),
            (strain[50] * 100, stress[50] * 1000),
            arrowprops={"arrowstyle": "->", "color": color, "lw": 1.8},
        )
    axis.set(
        title="Cyclic Perturbation: Hysteresis",
        xlabel="Strain Change (%)",
        ylabel="Stress Change (kPa)",
    )
    axis.legend(loc="upper left", fontsize=9)
    axis.grid(alpha=0.2)


def build_fascia_mechanics() -> None:
    """Save vector outputs with fixed, explicit model parameters."""
    plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 10, "svg.fonttype": "none"})
    figure, axes = plt.subplots(1, 2, figsize=(10.5, 3.8))
    relaxation_panel(axes[0])
    cyclic_panel(axes[1])
    figure.suptitle("Manufactured Material Response; No Golf-Tissue Calibration")
    figure.tight_layout()
    for extension in ("svg", "pdf"):
        path = FIGURES / f"fascia_viscoelastic_memory.{extension}"
        figure.savefig(path, bbox_inches="tight")
        if extension == "svg":
            content = path.read_text(encoding="utf-8")
            path.write_bytes(
                ("\n".join(line.rstrip() for line in content.splitlines()) + "\n").encode()
            )
    figure.savefig(
        ROOT / "docs/development/technical-review/fascia-figure-preview.png",
        dpi=160,
        bbox_inches="tight",
    )
    plt.close(figure)


if __name__ == "__main__":
    build_fascia_mechanics()
