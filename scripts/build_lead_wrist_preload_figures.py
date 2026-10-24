"""Write the firm-lead-wrist preload numbers and figures from the ported models (#5134).

Usage: ``python3 -m scripts.build_lead_wrist_preload_figures``. Rewrites
``data/lead_wrist_preload/results.json`` and the four SVG figures under
``articles/figures/lead_wrist_preload/``. Output is deterministic.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from src.tools import lead_wrist_preload_models as models

ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR = ROOT / "articles/figures/lead_wrist_preload"
DESIRED, PERSIST, REVERSE = "#444444", "#17608a", "#a34716"
MS = 1000.0
# Kurtzer, Pruszynski and Scott (2009): R1 20-45 ms, R2/3 45-100 ms after a perturbation.
REFLEX_WINDOWS_MS = (
    ("Earliest Stretch Response (R1)", 20.0, 45.0),
    ("Long-Latency (R2/3)", 45.0, 100.0),
)
# Illustrative contact duration used in impact-mechanics-and-ball-flight.qmd; not a constant.
ILLUSTRATIVE_CONTACT_MS = 0.45


def _save(figure: Figure, stem: str) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    figure.savefig(FIGURE_DIR / f"{stem}.svg", metadata={"Date": None})
    plt.close(figure)


def _plot_pair(axis: Axes, traces: tuple[dict[str, Any], ...], title: str) -> None:
    for trace, colour, label in zip(
        traces, (PERSIST, REVERSE), ("Persistent", "Reversal"), strict=True
    ):
        after = trace["time_s"] >= 0.0
        time_ms = trace["time_s"][after] * MS
        axis.plot(
            time_ms,
            trace["transmitted_net_nm"][after],
            color=colour,
            lw=2.2,
            label=(f"{label}: J = {trace['error_impulse_nms']:.4f} N m s"),
        )
    axis.plot(
        time_ms, trace["desired_net_nm"][after], color=DESIRED, ls="--", lw=1.4, label="Desired"
    )
    axis.set(title=title, xlabel="Time After Transition (ms)", ylabel="Net Torque (N m)")
    axis.legend(loc="lower right", fontsize=9)


def figure_two_models() -> None:
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.2), layout="constrained", sharey=True)
    dead = tuple(
        models.simulate_dead_zone(program, models.DEAD_ZONE_CHANNEL, preloaded=True)
        for program in (models.PERSISTENT, models.REVERSAL)
    )
    muscle = tuple(models.simulate_muscle(p) for p in (models.PERSISTENT, models.REVERSAL))
    _plot_pair(axes[0], dead, "Dead-Zone Transmission Model")
    _plot_pair(axes[1], muscle, "Reduced Muscle Model (0.2 ms Step)")
    _save(figure, "fig_preload_two_models")


def figure_robustness(results: dict[str, Any]) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.2), layout="constrained")
    for key, colour, label in (
        ("muscle_step_audit", PERSIST, "Net Target 10 N m"),
        ("muscle_step_audit_net_14", REVERSE, "Net Target 14 N m"),
    ):
        audit = results[key]
        steps_ms = [step * MS for step in audit["step_s"]]
        axes[0].plot(steps_ms, audit["difference_nms"], "o-", color=colour, label=label)
    axes[0].axhline(0.0, color=DESIRED, lw=0.8)
    axes[0].set(
        xscale="log",
        xlabel="Integration Step (ms)",
        ylabel="J(Reversal) − J(Persistent) (N m s)",
        title="Muscle Model: Gap Versus Step Size",
    )
    axes[0].legend(fontsize=9)
    grid = results["dead_zone_sensitivity"]["difference_nms"]
    widths = list(models.SENSITIVITY_DEAD_ZONES_RAD)
    for column, time_constant in enumerate(models.SENSITIVITY_TIME_CONSTANTS_S):
        axes[1].plot(
            widths, [row[column] for row in grid], "o-", label=f"T = {time_constant * MS:.0f} ms"
        )
    axes[1].set(
        xlabel="Dead-Zone Half-Width (rad)",
        ylabel="J(Reversal) − J(Persistent) (N m s)",
        title="Dead-Zone Model: Gap Versus Dead-Zone Width",
    )
    axes[1].legend(fontsize=9)
    _save(figure, "fig_preload_robustness")


def figure_internal_wrench() -> None:
    figure, axis = plt.subplots(figsize=(9, 3.4), layout="constrained")
    arm, wrist = models.PERSISTENT.arm_post_nm, models.PERSISTENT.wrist_post_nm
    rows = (
        (
            2.0,
            (
                (0.0, arm, PERSIST, f"Arm Drive {arm:+.0f}"),
                (0.0, wrist, REVERSE, f"Lead-Wrist Resistance {wrist:+.0f}"),
            ),
        ),
        (1.0, ((0.0, arm + wrist, DESIRED, f"Net on Club {arm + wrist:+.0f}"),)),
        (
            0.0,
            (
                (0.0, -wrist, "#7a7a7a", f"Internal Pair {-wrist:+.0f}"),
                (0.0, wrist, "#7a7a7a", f"{wrist:+.0f}"),
            ),
        ),
    )
    for height, arrows in rows:
        for offset, (start, length, colour, label) in enumerate(arrows):
            y = height + 0.18 * offset
            axis.annotate(
                "",
                (start + length, y),
                (start, y),
                arrowprops={"arrowstyle": "-|>", "color": colour, "lw": 2.5},
            )
            axis.text(start + length, y + 0.08, label, color=colour, ha="center", fontsize=10)
    axis.axvline(0.0, color=DESIRED, lw=0.8)
    axis.set(
        xlim=(-9, 19),
        ylim=(-0.4, 2.7),
        xlabel="Torque About the Grip (N m)",
        yticks=[0, 1, 2],
        yticklabels=["Cancels on Club", "Club Feels", "Two Channels"],
    )
    axis.set_title("Same Net Torque, Different Internal Load (Persistent Program After Transition)")
    _save(figure, "fig_internal_wrench")


def figure_timescales(results: dict[str, Any]) -> None:
    figure, axis = plt.subplots(figsize=(9, 3.6), layout="constrained")
    gaps = results["dead_zone"]["complete_role_reversal_preloaded"]
    points = (
        ("Illustrative Contact Duration", ILLUSTRATIVE_CONTACT_MS, DESIRED),
        ("Shaft Axial Round Trip (Assumed Steel)", results["shaft_round_trip_s"] * MS, DESIRED),
        ("Modeled Arm Gap (Dead Zone)", gaps["arm_gap_s"] * MS, REVERSE),
        ("Modeled Wrist Gap (Dead Zone)", gaps["wrist_gap_s"] * MS, REVERSE),
    )
    labels = [label for label, _value, _colour in points] + [
        name for name, _lo, _hi in REFLEX_WINDOWS_MS
    ]
    for row, (_label, value, colour) in enumerate(points):
        axis.plot([value], [row], "o", color=colour, ms=8)
        axis.text(value * 1.15, row, f"{value:.3g} ms", va="center", fontsize=9)
    for row, (_name, low, high) in enumerate(REFLEX_WINDOWS_MS, start=len(points)):
        axis.plot([low, high], [row, row], color=PERSIST, lw=6, solid_capstyle="butt")
    axis.set(
        xscale="log",
        xlim=(0.1, 300),
        xlabel="Time (ms, Log Scale)",
        yticks=range(len(labels)),
        yticklabels=labels,
        title="Contact Is Over Long Before Any Feedback Can Act",
    )
    axis.invert_yaxis()
    _save(figure, "fig_impact_timescales")


def main() -> None:
    """Regenerate the results document and all four figures."""
    models.write_results()
    results = models.build_results()
    with plt.rc_context({"font.size": 11, "svg.fonttype": "none", "svg.hashsalt": "lead-wrist"}):
        figure_two_models()
        figure_robustness(results)
        figure_internal_wrench()
        figure_timescales(results)


if __name__ == "__main__":
    main()
