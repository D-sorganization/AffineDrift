"""Independent energy, memory and coupling controls for the fascia chapter."""

from pathlib import Path

import numpy as np
import pytest
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "articles/The_Physics_of_Golf"


def test_original_area_example_uses_square_centimetres() -> None:
    area = 10 * (1e-2) ** 2
    volume = area * 0.1
    energy = 0.5 * 1e6 * 0.05**2 * volume
    club_energy = 0.5 * 0.2 * 50**2
    assert volume == pytest.approx(1e-4)
    assert energy == pytest.approx(0.125)
    assert 100 * energy / club_energy == pytest.approx(0.05)


def test_sheet_example_and_exercise_are_separate_geometries() -> None:
    sheet_volume = 0.1 * 0.1 * 0.001
    assert 0.5 * 50e6 * 0.02**2 * sheet_volume == pytest.approx(0.1)
    exercise_volume = 0.1 * 0.1 * 0.05
    exercise_energy = 0.5 * 1e6 * 0.05**2 * exercise_volume
    assert exercise_energy == pytest.approx(0.625)
    assert 100 * exercise_energy / 250 == pytest.approx(0.25)


def test_stiffness_comparison_reverses_with_loading_condition() -> None:
    low, high = 1e6, 5e6
    strain, stress = 0.02, 2e4
    assert 0.5 * high * strain**2 > 0.5 * low * strain**2
    assert stress**2 / (2 * high) < stress**2 / (2 * low)


def test_nonlinear_secant_and_tangent_moduli_differ() -> None:
    strain, base, stiffening = sp.symbols("epsilon E b", positive=True)
    secant = base * (1 + stiffening * strain**2)
    stress = secant * strain
    energy = sp.integrate(stress, strain)
    assert sp.diff(energy, strain) == stress.expand()
    assert sp.simplify(sp.diff(stress, strain) - base * (1 + 3 * stiffening * strain**2)) == 0
    assert sp.simplify(energy - secant * strain**2 / 2) != 0


def test_kelvin_ramp_stores_same_energy_but_dissipates_more_when_faster() -> None:
    modulus, viscosity, strain = 2e6, 1e4, 0.02
    stored = 0.5 * modulus * strain**2
    assert stored == 400
    slow_loss = viscosity * strain**2 / 1.0
    fast_loss = viscosity * strain**2 / 0.1
    assert slow_loss == 4
    assert fast_loss == 40


def test_standard_linear_solid_has_nonnegative_dissipation() -> None:
    strain, memory, rate = sp.symbols("epsilon z v", real=True)
    equilibrium, branch, relaxation = sp.symbols("Einf E1 tau", positive=True)
    storage = equilibrium * strain**2 / 2 + branch * (strain - memory) ** 2 / 2
    stress = sp.diff(storage, strain)
    memory_rate = (strain - memory) / relaxation
    storage_rate = stress * rate + sp.diff(storage, memory) * memory_rate
    loss = sp.simplify(stress * rate - storage_rate)
    assert sp.simplify(loss - branch * (strain - memory) ** 2 / relaxation) == 0


def test_relaxation_has_a_finite_equilibrium_spring() -> None:
    equilibrium, branch, strain = 1e6, 4e6, 0.02
    initial = (equilibrium + branch) * strain
    after_one_time_constant = (equilibrium + branch / np.e) * strain
    assert initial == pytest.approx(1e5)
    assert after_one_time_constant == pytest.approx(49430.3552937)
    assert equilibrium * strain == 2e4
    assert initial > after_one_time_constant > equilibrium * strain


def test_internal_tissue_force_preserves_virtual_power() -> None:
    length_jacobian = np.array([[0.03, -0.02], [0.01, 0.04]])
    joint_velocity = np.array([2.0, -3.0])
    tension = np.array([100.0, 50.0])
    joint_force = -length_jacobian.T @ tension
    length_rate = length_jacobian @ joint_velocity
    assert joint_force @ joint_velocity == pytest.approx(-tension @ length_rate)


def test_harmonic_material_response_satisfies_memory_equation() -> None:
    time, frequency, relaxation = sp.symbols("t w tau", positive=True)
    strain = sp.sin(frequency * time)
    memory = (strain - frequency * relaxation * sp.cos(frequency * time)) / (
        1 + frequency**2 * relaxation**2
    )
    assert sp.simplify(sp.diff(memory, time) - (strain - memory) / relaxation) == 0
    branch_stress = sp.simplify(strain - memory)
    expected = (
        frequency**2 * relaxation**2 * strain + frequency * relaxation * sp.cos(frequency * time)
    ) / (1 + frequency**2 * relaxation**2)
    assert sp.simplify(branch_stress - expected) == 0


def test_coupling_resists_relative_motion_without_resisting_common_motion() -> None:
    stiffness = 100 * np.array([[1, -1], [-1, 1]])
    assert np.linalg.eigvalsh(stiffness) == pytest.approx([0, 200])
    assert stiffness @ np.ones(2) == pytest.approx([0, 0])


def test_coupling_changes_task_capacity_in_different_directions() -> None:
    coupling = np.array([[1.0, 0.5], [0.5, 1.0]])
    common, relative = np.array([1.0, 1.0]), np.array([1.0, -1.0])
    assert np.abs(common @ coupling).sum() == 3
    assert np.abs(relative @ coupling).sum() == 1
    assert np.abs(common).sum() == np.abs(relative).sum() == 2
    assert np.linalg.det(coupling) == pytest.approx(0.75)


@pytest.mark.parametrize("relative_path", ["chapters/ch12_fascia.tex", "quarto/ch12_fascia.qmd"])
def test_chapter_replaces_absolute_claims_with_reproducible_mechanics(relative_path: str) -> None:
    text = (CHAPTER / relative_path).read_text(encoding="utf-8")
    for invalid in (
        "Fascia does not contract.",
        "Collagen is almost purely stiff (not elastic)",
        "meridians are anatomical fiction",
        "control authority is reduced because",
    ):
        assert invalid not in text
    for required in ("0.125", "myofibroblasts", "internal state", "fixed stress", "0.625"):
        assert required in text
    assert text.count("Answer") >= 8
