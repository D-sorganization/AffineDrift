"""Execute published pendulum and comparison listings against analytic contracts."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest

CHAPTERS = Path(__file__).resolve().parents[1] / "articles/The_Geometry_of_Motion/Volume_V/chapters"


def _load_listing(name: str) -> ModuleType:
    """Execute only fixed repository-owned Python examples, without external input."""
    path = CHAPTERS / name
    blocks = re.findall(
        r"\\begin\{lstlisting\}\[language=Python[^\n]*\]\n(.*?)\\end\{lstlisting\}",
        path.read_text(encoding="utf-8"),
        re.DOTALL,
    )
    assert blocks, f"No Python example in {path}"
    module = ModuleType(f"_platform_listing_{path.stem}")
    sys.modules[module.__name__] = module
    # Repository-owned listing at a fixed path, with no external input.
    # nosemgrep: python.lang.security.audit.exec-detected.exec-detected
    exec(compile("\n".join(blocks), str(path), "exec", dont_inherit=True), module.__dict__)
    return module


@pytest.fixture(scope="module")
def pendulum() -> ModuleType:
    """Load the actual platform chapter listing."""
    return _load_listing("ch01_platform_overview.tex")


@pytest.fixture(scope="module")
def metrics() -> ModuleType:
    """Load the actual engine comparison listing."""
    return _load_listing("ch02_engine_comparison.tex")


@pytest.mark.parametrize("field", ["mass", "length", "radius", "damping"])
@pytest.mark.parametrize("bad", [-1.0, np.nan, np.inf])
def test_physical_parameter_domain(pendulum: ModuleType, field: str, bad: float) -> None:
    """Reject nonphysical or nonfinite parameters before integration."""
    with pytest.raises(ValueError):
        pendulum.RodParameters(**{field: bad})


@pytest.mark.parametrize("field", ["mass", "length", "radius"])
def test_zero_body_parameter_rejected(pendulum: ModuleType, field: str) -> None:
    """A finite solid cylinder has positive mass and dimensions."""
    with pytest.raises(ValueError):
        pendulum.RodParameters(**{field: 0.0})


def test_pivot_inertia(pendulum: ModuleType) -> None:
    """The hinge inertia includes the COM-to-pivot parallel-axis term."""
    params = pendulum.RodParameters(mass=2.0, length=0.6, radius=0.1)
    expected = 2.0 * (0.6**2 + 3 * 0.1**2) / 12 + 2.0 * 0.3**2
    assert params.pivot_inertia == pytest.approx(expected)


@pytest.mark.parametrize(
    "times", [[], [0.0], [1.0, 2.0], [0.0, 0.0], [0.0, -1.0], [0.0, np.nan], [[0, 1]]]
)
def test_invalid_output_grid(pendulum: ModuleType, times: list) -> None:
    """Output includes an initial sample and strictly increasing finite times."""
    with pytest.raises(ValueError):
        pendulum.simulate_pendulum(pendulum.RodParameters(), (0.2, 0.0), np.array(times))


@pytest.mark.parametrize("initial", [(0.0,), (0.0, 0.0, 0.0), (np.nan, 0), (0, np.inf)])
def test_invalid_initial_state(pendulum: ModuleType, initial: tuple) -> None:
    """Initial angle and angular velocity must be finite scalars."""
    with pytest.raises(ValueError):
        pendulum.simulate_pendulum(pendulum.RodParameters(), initial, np.array([0.0, 1.0]))


@pytest.mark.parametrize("damping", [0.0, 0.05])
def test_energy_work_balance(pendulum: ModuleType, damping: float) -> None:
    """Energy plus integrated viscous loss is constant for this unforced model."""
    params = pendulum.RodParameters(damping=damping)
    times = np.linspace(0.0, 3.0, 121)
    result = pendulum.simulate_pendulum(params, (0.4, 0.2), times)
    assert set(result) == {"t", "q", "qd", "energy", "dissipated"}
    assert all(array.shape == times.shape for array in result.values())
    np.testing.assert_array_equal(result["t"], times)
    initial_energy = 0.5 * params.pivot_inertia * 0.2**2 + 4.905 * (1 - np.cos(0.4))
    assert result["energy"][0] == pytest.approx(initial_energy)
    np.testing.assert_allclose(result["energy"] + result["dissipated"], initial_energy, atol=2e-9)
    assert np.min(result["dissipated"]) >= -1e-12
    if damping == 0:
        np.testing.assert_array_equal(result["dissipated"], 0.0)
    else:
        assert result["energy"][-1] < initial_energy


def test_zero_energy_rest(pendulum: ModuleType) -> None:
    """Rest at the potential minimum needs no division by initial energy."""
    result = pendulum.simulate_pendulum(pendulum.RodParameters(), (0.0, 0.0), np.array([0.0, 1.0]))
    for key in ("q", "qd", "energy", "dissipated"):
        np.testing.assert_array_equal(result[key], 0.0)


def test_small_angle_frequency(pendulum: ModuleType) -> None:
    """An independent linear limit checks the gravitational sign and inertia."""
    params = pendulum.RodParameters(damping=0.0)
    times = np.linspace(0.0, 1.0, 101)
    result = pendulum.simulate_pendulum(params, (1e-5, 0.0), times)
    frequency = np.sqrt(4.905 / params.pivot_inertia)
    np.testing.assert_allclose(result["q"], 1e-5 * np.cos(frequency * times), atol=1e-11, rtol=0)


def test_solver_failure_surfaces(pendulum: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    """A failed integrator cannot masquerade as a valid trajectory."""
    monkeypatch.setattr(
        pendulum, "solve_ivp", lambda *args, **kwargs: SimpleNamespace(success=False)
    )
    with pytest.raises(RuntimeError):
        pendulum.simulate_pendulum(pendulum.RodParameters(), (0.1, 0.0), np.array([0.0, 1.0]))


def test_nonuniform_time_weighted_metric(metrics: ModuleType) -> None:
    """Trapezoidal time weighting differs from an unweighted sample mean."""
    times = np.array([0.0, 1.0, 3.0])
    actual = times[:, None]
    result = metrics.trajectory_errors(times, actual, np.zeros_like(actual), np.ones(1))
    assert result == pytest.approx({"rms": np.sqrt(3.5), "max": 3.0})
    assert result["rms"] != pytest.approx(np.sqrt(10.0 / 3.0))


def test_metric_units_and_time_origin(metrics: ModuleType) -> None:
    """Joint state rescaling and shifted timestamps preserve normalized errors."""
    times = np.array([0.0, 0.2, 1.0])
    actual = np.array([[1.0, 2.0], [2.0, 1.0], [0.0, 3.0]])
    reference = np.zeros_like(actual)
    scales = np.array([0.5, 2.0])
    first = metrics.trajectory_errors(times, actual, reference, scales)
    units = np.array([1000.0, 180.0 / np.pi])
    second = metrics.trajectory_errors(times + 7.0, actual * units, reference, scales * units)
    assert first == pytest.approx(second)


@pytest.mark.parametrize(
    "bad",
    [
        {"times": [0]},
        {"times": [0, 0]},
        {"times": [0, np.inf]},
        {"actual": [0, 1]},
        {"actual": [[0, 1], [0, 1]]},
        {"actual": [[np.nan], [0]]},
        {"reference": [[0]]},
        {"reference": [[0], [np.inf]]},
        {"scales": [0]},
        {"scales": [-1]},
        {"scales": [np.nan]},
        {"scales": [1, 2]},
    ],
)
def test_metric_contracts(metrics: ModuleType, bad: dict) -> None:
    """Reject incompatible state geometry, samples and normalization."""
    args = {"times": [0, 1], "actual": [[0], [0]], "reference": [[0], [0]], "scales": [1]}
    args.update(bad)
    with pytest.raises(ValueError):
        metrics.trajectory_errors(**args)
