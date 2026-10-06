"""Generate or verify the WEB-08.2 signature graphic, "Drift Plus Control" (#4554).

The graphic is the phase plane of ``src.tangent_models.examples.SimplePendulum``,
an exactly control-affine system: ``x' = f(x) + G(x) u`` with ``x = (theta,
omega)``, ``f(x) = (omega, -(g/L) sin theta)`` and ``G(x) = (0, 1/(m L^2))``.
Every plotted number comes from that class: the faint field is the drift
``f``, the dashed curve is the zero-torque run, the solid curve the run under a
declared constant torque, and at one state of that run three head-to-tail
arrows show the drift ``f(x)``, the push ``G(x) u`` and their sum ``x'``.

The output is one inline SVG include whose colours come from CSS classes, so it
follows the site theme. Usage::

    python -m scripts.generate_signature_graphic          # write the include
    python -m scripts.generate_signature_graphic --check  # fail if it is stale
"""

from __future__ import annotations

import argparse
import logging
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from src.tangent_models.examples import SimplePendulum

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
INCLUDE_PATH = "_includes/generated/drift-plus-control.qmd"
GENERATOR = "python -m scripts.generate_signature_graphic"

#: Illustrative arm-and-club pendulum: 1 kg at 1 m under standard gravity.
PENDULUM = SimplePendulum(m=1.0, L=1.0)
#: Declared constant pivot torque, N m (illustrative, not a golfer measurement).
TORQUE = 5.0
#: Start at rest at the top of the backswing, rad.
THETA0 = -2.2
DT = 0.002
HORIZON = 1.0
#: The highlighted state is this far along the driven run, s.
MARK_TIME = 0.2
#: Arrows show the change of state over this interval, s.
ARROW_DT = 0.35

WIDTH, HEIGHT = 480, 340
PLOT = (24.0, 40.0, 464.0, 300.0)  # left, top, right, bottom in viewBox units
THETA_RANGE = (-math.pi, math.pi)
OMEGA_RANGE = (-3.0, 8.0)
FIELD_COLUMNS, FIELD_ROWS = 12, 6
FIELD_ARROW = 13.0


@dataclass(frozen=True)
class Scene:
    """Every model quantity the graphic draws."""

    passive: np.ndarray
    driven: np.ndarray
    mark: np.ndarray
    drift: np.ndarray
    push: np.ndarray


def _rk4(x: np.ndarray, u: float, dt: float) -> np.ndarray:
    """One classical Runge-Kutta step of ``PENDULUM.dynamics``."""
    k1 = PENDULUM.dynamics(x, u)
    k2 = PENDULUM.dynamics(x + 0.5 * dt * k1, u)
    k3 = PENDULUM.dynamics(x + 0.5 * dt * k2, u)
    k4 = PENDULUM.dynamics(x + dt * k3, u)
    return np.asarray(x + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0, dtype=float)


def trajectory(u: float) -> np.ndarray:
    """States from rest at ``THETA0`` under constant torque ``u`` until ``HORIZON``."""
    states = [np.array([THETA0, 0.0])]
    for _ in range(round(HORIZON / DT)):
        states.append(_rk4(states[-1], u, DT))
    return np.array(states)


def drift(x: np.ndarray) -> np.ndarray:
    """Drift ``f(x)``: the model's state velocity with zero input."""
    return np.asarray(PENDULUM.dynamics(x, 0.0), dtype=float)


def push(x: np.ndarray, u: float) -> np.ndarray:
    """Input term ``G(x) u``, the part of the state velocity the torque adds."""
    return np.asarray(PENDULUM.dynamics(x, u), dtype=float) - drift(x)


def build_scene() -> Scene:
    """Compute both runs and the head-to-tail arrows at the highlighted state."""
    driven = trajectory(TORQUE)
    mark = driven[round(MARK_TIME / DT)]
    return Scene(trajectory(0.0), driven, mark, drift(mark), push(mark, TORQUE))


def to_view(theta: float, omega: float) -> tuple[float, float]:
    """Map a phase-plane point to viewBox coordinates."""
    left, top, right, bottom = PLOT
    x = left + (theta - THETA_RANGE[0]) / (THETA_RANGE[1] - THETA_RANGE[0]) * (right - left)
    y = bottom - (omega - OMEGA_RANGE[0]) / (OMEGA_RANGE[1] - OMEGA_RANGE[0]) * (bottom - top)
    return x, y


def _visible(states: np.ndarray) -> np.ndarray:
    """The leading part of a run that stays inside the plotted window."""
    inside = (np.abs(states[:, 0]) <= THETA_RANGE[1]) & (np.abs(states[:, 1]) <= OMEGA_RANGE[1])
    end = int(np.argmin(inside)) if not inside.all() else len(states)
    return states[:end]


def _polyline(states: np.ndarray, css: str) -> str:
    """SVG polyline through every 5th state of a run."""
    points = " ".join("{:.1f},{:.1f}".format(*to_view(*s)) for s in _visible(states)[::5])
    return f'<polyline class="{css}" points="{points}"/>'


def _arrow(start: np.ndarray, delta: np.ndarray, css: str) -> str:
    """Arrow from ``start`` along the state change ``delta`` (phase-plane units)."""
    x1, y1 = to_view(*start)
    x2, y2 = to_view(*(start + delta))
    return (
        f'<line class="{css}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'marker-end="url(#{css}-head)"/>'
    )


def _field() -> str:
    """Faint unit-length arrows of the drift direction on a regular grid."""
    lines = []
    for i in range(FIELD_COLUMNS):
        for j in range(FIELD_ROWS):
            theta = THETA_RANGE[0] + (i + 0.5) * (THETA_RANGE[1] - THETA_RANGE[0]) / FIELD_COLUMNS
            omega = OMEGA_RANGE[0] + (j + 0.5) * (OMEGA_RANGE[1] - OMEGA_RANGE[0]) / FIELD_ROWS
            x, y = to_view(theta, omega)
            tip_x, tip_y = to_view(
                *(np.array([theta, omega]) + 0.01 * drift(np.array([theta, omega])))
            )
            dx, dy = tip_x - x, tip_y - y
            norm = math.hypot(dx, dy) or 1.0
            ux, uy = FIELD_ARROW * dx / norm, FIELD_ARROW * dy / norm
            lines.append(
                f'<line class="dpc-field" x1="{x - ux / 2:.1f}" y1="{y - uy / 2:.1f}" '
                f'x2="{x + ux / 2:.1f}" y2="{y + uy / 2:.1f}" marker-end="url(#dpc-field-head)"/>'
            )
    return "\n".join(lines)


def _marker(css: str, size: float) -> str:
    """Arrowhead marker whose fill follows the class of its path."""
    return (
        f'<marker id="{css}-head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="{size}" '
        f'markerHeight="{size}" orient="auto-start-reverse"><path class="{css}-head" '
        'd="M0,0 L10,5 L0,10 z"/></marker>'
    )


def long_description(scene: Scene) -> str:
    """Plain-text long description with the drawn numbers."""
    theta, omega = scene.mark
    return (
        "The horizontal axis is the pendulum angle from straight down, in radians; the "
        "vertical axis is its angular velocity, in radians per second. Faint arrows show "
        "the drift: the direction the model's state moves at each point with no torque. "
        f"Both runs start at rest at an angle of {THETA0} rad. The dashed curve is the "
        "zero-torque run, which follows the drift alone. The solid curve is the run under a "
        f"constant {TORQUE:g} N m pivot torque, which swings faster and further. At the "
        f"marked state, angle {theta:.2f} rad and angular velocity {omega:.2f} rad/s, three "
        f"arrows show the change over {ARROW_DT} s: the drift arrow "
        f"({scene.drift[0]:.2f}, {scene.drift[1]:.2f}) per second, the push arrow "
        f"(0, {scene.push[1]:.2f}) per second, which only changes angular velocity because "
        "torque acts on acceleration, and their sum, the state velocity the run actually has."
    )


def render_include(scene: Scene) -> str:
    """The embeddable figure: inline SVG, caption and long description."""
    left, top, right, bottom = PLOT
    head = scene.mark + ARROW_DT * scene.drift
    resultant = ARROW_DT * (scene.drift + scene.push)
    label_drift = to_view(*(scene.mark + 0.5 * ARROW_DT * scene.drift))
    label_push = to_view(*(head + 0.5 * ARROW_DT * scene.push))
    label_sum = to_view(*(scene.mark + resultant))
    zero_x, zero_y = to_view(0.0, 0.0)
    axes = (
        f'<line class="dpc-axis" x1="{left}" y1="{zero_y:.1f}" x2="{right}" y2="{zero_y:.1f}"/>'
        f'<line class="dpc-axis" x1="{zero_x:.1f}" y1="{top}" x2="{zero_x:.1f}" y2="{bottom}"/>'
    )
    svg = f"""<svg class="dpc-svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="dpc-title dpc-desc">
<title id="dpc-title">Drift plus control</title>
<desc id="dpc-desc">Phase plane of a pendulum model. A passive drift arrow and a torque push arrow add head to tail to give the state velocity.</desc>
<defs>{_marker("dpc-field", 4)}{_marker("dpc-drift", 5)}{_marker("dpc-push", 5)}{_marker("dpc-sum", 5)}</defs>
{_field()}
{axes}
{_polyline(scene.passive, "dpc-passive")}
{_polyline(scene.driven, "dpc-driven")}
{_arrow(scene.mark, resultant, "dpc-sum")}
{_arrow(scene.mark, ARROW_DT * scene.drift, "dpc-drift")}
{_arrow(head, ARROW_DT * scene.push, "dpc-push")}
<circle class="dpc-mark" cx="{to_view(*scene.mark)[0]:.1f}" cy="{to_view(*scene.mark)[1]:.1f}" r="4"/>
<text class="dpc-label dpc-label--drift" x="{label_drift[0] + 10:.1f}" y="{label_drift[1] + 22:.1f}">drift f(x)</text>
<text class="dpc-label dpc-label--push" x="{label_push[0] + 12:.1f}" y="{label_push[1] + 6:.1f}">push G(x)u</text>
<text class="dpc-label" x="{label_sum[0] - 10:.1f}" y="{label_sum[1]:.1f}" text-anchor="end">actual</text>
<text class="dpc-axis-label" x="{right}" y="{bottom + 30}" text-anchor="end">angle θ (rad)</text>
<text class="dpc-axis-label" x="{left}" y="{top - 16}">angular velocity ω (rad/s)</text>
</svg>"""
    return f"""<!-- DO NOT EDIT. Generated by {GENERATOR}. -->

```{{=html}}
<figure class="drift-plus-control" aria-describedby="dpc-long">
{svg}
<figcaption><strong>Drift plus control.</strong> At every state, the model's motion is a passive drift (blue) plus a push from the declared input (orange). Dashed: the same model with zero torque. Illustrative values from the pendulum model in <code>src/tangent_models/examples.py</code>; not a golfer measurement.</figcaption>
<details id="dpc-long">
<summary>Long description</summary>
<p>{long_description(scene)}</p>
</details>
</figure>
```
"""


def stale(root: Path = REPO_ROOT) -> bool:
    """True when the include on disk differs from a fresh render."""
    path = root / INCLUDE_PATH
    return not path.is_file() or path.read_text(encoding="utf-8") != render_include(build_scene())


def main(argv: list[str] | None = None) -> int:
    """Write the include, or with ``--check`` fail when it is stale."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the include is stale")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    if args.check:
        if stale():
            logger.error("Stale %s; run %s", INCLUDE_PATH, GENERATOR)
            return 1
        return 0
    path = REPO_ROOT / INCLUDE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_include(build_scene()), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
