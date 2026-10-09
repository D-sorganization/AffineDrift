"""Generate the manufactured series-spring figure without site-time execution.

Run from the repository root with:
python -m scripts.build_passive_control_figure articles/figures/passive-control-energy.svg
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from src.affine_control.series_elastic_demo import (
    LoadStage,
    SeriesElasticParameters,
    SeriesElasticTrace,
    simulate_series_elastic,
)

# Manufactured force schedule in seconds/newtons; not identified human loads.
STAGES = (LoadStage(0.20, 100.0), LoadStage(0.05, 80.0), LoadStage(0.25, 0.0))
INITIAL_STATE = (0.02, 0.0)  # metres and metres/second


def _plot_trace(trace: SeriesElasticTrace) -> Figure:
    """Show storage and its independently integrated work/loss accounting."""
    figure, axes = plt.subplots(2, 1, figsize=(8, 7), sharex=True, layout="constrained")
    for values, label in (
        (trace.proximal_energy, "Proximal Spring"),
        (trace.distal_energy, "Distal Spring"),
        (trace.kinetic_energy, "Mass Kinetic Energy"),
    ):
        axes[0].plot(trace.time, values, label=label)
    axes[0].plot(trace.time, trace.energy, label="Total Storage", color="black")
    axes[0].set(ylabel="Energy (J)", title="Manufactured Series-Spring Energy")
    axes[1].plot(trace.time, trace.actuator_work, label="Actuator Work W")
    axes[1].plot(trace.time, trace.dissipated_energy, label="Dissipation D")
    axes[1].plot(trace.time, trace.energy - trace.energy[0], label="Storage Change")
    axes[1].plot(trace.time, trace.actuator_work - trace.dissipated_energy, "--", label="W - D")
    axes[1].set(xlabel="Time (s)", ylabel="Energy (J)")
    for axis in axes:
        elapsed = 0.0
        for stage in STAGES[:-1]:
            elapsed += stage.duration
            axis.axvline(elapsed, color="gray", linestyle=":")
        axis.legend(loc="best", ncol=2, fontsize=9)
        axis.grid(alpha=0.25)
    return figure


def build_figure(output: Path) -> None:
    """Write a reproducible SVG to output, creating its parent directory if needed."""
    trace = simulate_series_elastic(SeriesElasticParameters(), STAGES, INITIAL_STATE)
    output.parent.mkdir(parents=True, exist_ok=True)
    with plt.rc_context({"font.size": 11, "svg.fonttype": "none", "svg.hashsalt": "pdc-v1"}):
        figure = _plot_trace(trace)
        try:
            with output.open("w", encoding="utf-8", newline="\n") as stream:
                figure.savefig(stream, format="svg", metadata={"Date": None})
        finally:
            plt.close(figure)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    build_figure(parser.parse_args().output)
