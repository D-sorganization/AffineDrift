"""Independent manufactured checks for the article's declared series topology."""

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from defusedxml import ElementTree
from scipy.linalg import expm

from src.affine_control.series_elastic_demo import (
    LoadStage,
    SeriesElasticParameters,
    simulate_series_elastic,
)

STAGES = (LoadStage(0.2, 100.0), LoadStage(0.05, 80.0), LoadStage(0.25, 0.0))


def test_massless_junction_and_initial_storage() -> None:
    """The previous independent junction position violated spring-force balance."""
    parameters = SeriesElasticParameters()
    trace = simulate_series_elastic(parameters, STAGES, (0.02, 0.0))
    assert parameters.effective_stiffness == pytest.approx(2500.0 / 3.0)
    assert trace.junction[0] == pytest.approx(1.0 / 300.0)
    np.testing.assert_allclose(
        parameters.proximal_stiffness * (trace.position - trace.junction),
        parameters.distal_stiffness * trace.junction,
        atol=1e-12,
    )
    assert trace.energy[0] == pytest.approx(1.0 / 6.0)
    assert parameters.damping_ratio == pytest.approx(np.sqrt(5.0 / 3.0))


def test_segmented_solution_matches_independent_matrix_exponential() -> None:
    """Compare every sampled state against an exact constant-force transition."""
    parameters = SeriesElasticParameters()
    trace = simulate_series_elastic(parameters, STAGES, (0.02, 0.0))
    matrix = np.array([[0.0, 1.0], [-2500.0 / 1.35, -50.0 / 0.45]])
    state = np.array([0.02, 0.0])
    start = 0.0
    expected_work = 0.0
    for stage in STAGES:
        end = start + stage.duration
        equilibrium = np.array([stage.force * 3.0 / 2500.0, 0.0])
        selected = np.flatnonzero((trace.time >= start) & (trace.time <= end))
        exact = np.array(
            [
                equilibrium + expm(matrix * (trace.time[i] - start)) @ (state - equilibrium)
                for i in selected
            ]
        )
        np.testing.assert_allclose(trace.position[selected], exact[:, 0], atol=2e-10)
        np.testing.assert_allclose(trace.velocity[selected], exact[:, 1], atol=2e-9)
        terminal = equilibrium + expm(matrix * stage.duration) @ (state - equilibrium)
        expected_work += stage.force * (terminal[0] - state[0])
        boundary = np.flatnonzero(np.isclose(trace.time, end, rtol=0.0, atol=1e-14))
        assert len(boundary) == 1
        assert trace.actuator_work[boundary[0]] == pytest.approx(expected_work, abs=2e-9)
        state, start = terminal, end
    assert np.all(np.diff(trace.time) > 0.0)
    assert trace.time[-1] == pytest.approx(0.5)


def test_work_storage_and_dissipation_close_without_energy_injection() -> None:
    """Storage follows the power balance; recoil cannot create total energy."""
    trace = simulate_series_elastic(SeriesElasticParameters(), STAGES, (0.02, 0.0))
    np.testing.assert_allclose(
        trace.energy - trace.energy[0],
        trace.actuator_work - trace.dissipated_energy,
        atol=3e-9,
    )
    assert np.all(np.diff(trace.dissipated_energy) >= -1e-12)
    released = trace.time >= 0.25
    assert np.all(np.diff(trace.energy[released]) <= 1e-10)
    np.testing.assert_allclose(trace.actuator_work[released], trace.actuator_work[released][0])
    assert np.max(trace.kinetic_energy[released]) > 0.0


def test_unforced_undamped_model_conserves_preload_energy() -> None:
    """Remove damping and input independently of the forced default example."""
    parameters = replace(SeriesElasticParameters(), damping=0.0)
    trace = simulate_series_elastic(parameters, (LoadStage(0.5, 0.0),), (0.02, 0.0))
    np.testing.assert_allclose(trace.energy, 1.0 / 6.0, atol=1e-9)
    np.testing.assert_array_equal(trace.actuator_work, 0.0)
    np.testing.assert_array_equal(trace.dissipated_energy, 0.0)


def test_nonzero_holding_force_can_have_zero_mechanical_work() -> None:
    """Zero power is not zero force or a claim about metabolic cost."""
    parameters = SeriesElasticParameters()
    force = 10.0
    initial = (force / parameters.effective_stiffness, 0.0)
    trace = simulate_series_elastic(parameters, (LoadStage(0.2, force),), initial)
    np.testing.assert_allclose(trace.position, initial[0], atol=1e-14)
    np.testing.assert_allclose(trace.velocity, 0.0, atol=1e-14)
    np.testing.assert_allclose(trace.actuator_work, 0.0, atol=1e-14)
    np.testing.assert_allclose(trace.force, force)


@pytest.mark.parametrize(
    "field,value",
    [
        ("mass", 0.0),
        ("damping", -1.0),
        ("proximal_stiffness", np.nan),
        ("distal_stiffness", -1.0),
        ("mass", np.inf),
    ],
)
def test_invalid_mechanical_parameters_are_rejected(field: str, value: float) -> None:
    """Reject singular or nonphysical parameters before calling the integrator."""
    with pytest.raises(ValueError):
        replace(SeriesElasticParameters(), **{field: value})


@pytest.mark.parametrize("duration,force", [(0.0, 0.0), (-1.0, 1.0), (0.2, np.nan)])
def test_invalid_load_stages_are_rejected(duration: float, force: float) -> None:
    """Every interval must have positive finite duration and finite force."""
    with pytest.raises(ValueError):
        LoadStage(duration, force)


def test_empty_schedule_and_nonfinite_initial_state_are_rejected() -> None:
    """An initial state and at least one force interval define the experiment."""
    parameters = SeriesElasticParameters()
    with pytest.raises(ValueError):
        simulate_series_elastic(parameters, (), (0.02, 0.0))
    with pytest.raises(ValueError):
        simulate_series_elastic(parameters, STAGES, (np.nan, 0.0))


def test_published_figure_is_reproducible_and_has_readable_labels(tmp_path: Path) -> None:
    """Generate portable SVG without a clock stamp or random element identifiers."""
    from scripts.build_passive_control_figure import build_figure

    target = tmp_path / "energy.svg"
    build_figure(target)
    first = target.read_bytes()
    build_figure(target)
    assert target.read_bytes() == first
    root = ElementTree.fromstring(first)
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    labels = set(root.itertext())
    assert {"Energy (J)", "Time (s)", "Actuator Work W", "Dissipation D", "W - D"} <= labels
    assert b"<dc:date>" not in first
