"""Check plotted DCR quantities against declared models, not illustrative golf curves."""

from collections.abc import Callable, Iterator
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest
import sympy as sp
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse
from matplotlib.quiver import Quiver
from scipy.integrate import solve_ivp

from scripts.core_theory_figures import dcr

Builder = Callable[[Path], None]
Capture = Callable[[Builder], Figure]
BUILDERS = (
    dcr.build_dcr_vector_decomposition,
    dcr.build_dcr_reachability_tubes,
    dcr.build_dcr_swing_phases,
)


@pytest.fixture
def capture_plot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Capture]:
    """Inspect exactly the figure saved by each builder; clean up only those figures."""
    figures: list[Figure] = []
    original_close = plt.close

    def capture_close(figure: Figure | str | int | None = None) -> None:
        if isinstance(figure, Figure):
            figures.append(figure)
        else:
            original_close(figure)

    def build(builder: Builder) -> Figure:
        before = len(figures)
        builder(tmp_path / f"{builder.__name__}.svg")
        assert len(figures) == before + 1, "Builder must save and close exactly one figure"
        return figures[-1]

    monkeypatch.setattr(plt, "close", capture_close)
    try:
        yield build
    finally:
        for figure in figures:
            original_close(figure)


def _line(figure: Figure, label: str) -> Line2D:
    matches = [line for axis in figure.axes for line in axis.lines if line.get_label() == label]
    assert len(matches) == 1, f"Expected one declared {label!r} curve"
    return matches[0]


def test_input_and_total_ellipses_are_distinct_affine_images(capture_plot: Capture) -> None:
    figure = capture_plot(dcr.build_dcr_vector_decomposition)
    ellipses = [
        patch for axis in figure.axes for patch in axis.patches if isinstance(patch, Ellipse)
    ]
    assert len(ellipses) == 2, "Show input-only and translated total acceleration sets separately"
    ellipses.sort(key=lambda ellipse: ellipse.center[0])
    angles = np.linspace(0.0, 2 * np.pi, 73)
    unit_inputs = np.column_stack((np.cos(angles), np.sin(angles)))
    input_map = np.diag([1.0, 0.5])
    effects = unit_inputs @ input_map.T
    for ellipse, offset in zip(ellipses, ([0.0, 0.0], [2.0, 0.5]), strict=True):
        plotted = ellipse.get_patch_transform().transform(unit_inputs)
        np.testing.assert_allclose(plotted, effects + offset, atol=1e-12)
    assert np.linalg.svd(input_map, compute_uv=False)[0] == 1.0


def test_plotted_vectors_use_one_admissible_input_and_common_origin(capture_plot: Capture) -> None:
    figure = capture_plot(dcr.build_dcr_vector_decomposition)
    arrows = [item for axis in figure.axes for item in axis.collections if isinstance(item, Quiver)]
    assert len(arrows) == 3, "Draw drift, input contribution and their sum"
    drift = np.array([2.0, 0.5])
    used_input = np.array([-0.5, 0.5])
    assert np.linalg.norm(used_input) < 1.0
    contribution = np.diag([1.0, 0.5]) @ used_input
    expected = [(np.zeros(2), drift), (drift, contribution), (np.zeros(2), drift + contribution)]
    actual = [np.r_[arrow.get_offsets()[0], arrow.U[0], arrow.V[0]] for arrow in arrows]
    for origin, vector in expected:
        assert any(np.allclose(item, np.r_[origin, vector], atol=1e-12) for item in actual)


def test_speed_curves_follow_euler_lagrange_equations(capture_plot: Capture) -> None:
    figure = capture_plot(dcr.build_dcr_swing_phases)
    coordinate, speed, acceleration, control = sp.symbols("q v a u", real=True)
    lagrangian = sp.exp(2 * coordinate) * (speed**2 + 1) / 2
    momentum = sp.diff(lagrangian, speed)
    equation = sp.diff(momentum, coordinate) * speed + sp.diff(momentum, speed) * acceleration
    equation -= sp.diff(lagrangian, coordinate)
    derived = sp.solve(equation - control, acceleration)[0].subs(coordinate, 0)
    ratio = _line(figure, "DCR")
    samples = np.asarray(ratio.get_xdata(), dtype=float)
    assert samples.min() == 0.0 and samples.max() == 3.0
    drift = np.abs(sp.lambdify(speed, derived.subs(control, 0), "numpy")(samples))
    capacity = abs(float(sp.diff(derived, control)))
    np.testing.assert_allclose(ratio.get_ydata(), drift / capacity, atol=1e-12)
    np.testing.assert_allclose(_line(figure, "Drift Magnitude").get_ydata(), drift, atol=1e-12)
    np.testing.assert_allclose(_line(figure, "Available Capacity").get_ydata(), capacity)
    for value, expected in zip((0, 1, 2, 3), (1, 0, 3, 8), strict=True):
        selected = np.flatnonzero(np.isclose(samples, value, atol=1e-12))
        assert len(selected) == 1
        assert ratio.get_ydata()[selected[0]] == pytest.approx(expected)


@pytest.mark.parametrize(
    "projection",
    [
        (0, "Position", 1.0, "Upper"),
        (0, "Position", -1.0, "Lower"),
        (1, "Velocity", 1.0, "Upper"),
        (1, "Velocity", -1.0, "Lower"),
    ],
)
def test_endpoint_bounds_match_independent_constant_control_integration(
    capture_plot: Capture, projection: tuple[int, str, float, str]
) -> None:
    component, name, sign, bound = projection
    figure = capture_plot(dcr.build_dcr_reachability_tubes)
    assert len(figure.axes) == 2, "Position and velocity are separate marginal projections"
    line = _line(figure, f"{bound} {name} Bound")
    horizons = np.asarray(line.get_xdata(), dtype=float)
    assert horizons.min() == 0.0 and horizons.max() == 1.0
    solution = solve_ivp(
        lambda _time, state: [state[1], sign],
        (0.0, 1.0),
        [0.0, 0.0],
        t_eval=horizons,
        rtol=1e-10,
        atol=1e-12,
    )
    assert solution.success
    np.testing.assert_allclose(line.get_ydata(), solution.y[component], atol=1e-10)


@pytest.mark.parametrize("builder", BUILDERS)
def test_generators_preserve_shared_plot_settings(capture_plot: Capture, builder: Builder) -> None:
    """Scoped DCR generation must not alter other articles' figures in a full build."""
    before = dict(plt.rcParams)
    capture_plot(builder)
    assert dict(plt.rcParams) == before


@pytest.mark.parametrize("builder", BUILDERS)
def test_scientific_svg_output_is_reproducible(tmp_path: Path, builder: Builder) -> None:
    first, second = tmp_path / "first.svg", tmp_path / "second.svg"
    builder(first)
    builder(second)
    assert first.read_bytes() == second.read_bytes(), "Rebuilding must preserve declared evidence"
