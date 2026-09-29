"""Independent synthetic accounting examples for the whole-swing ledger."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "articles/proximal_distal_companion/chapters/ch29_whole_swing_ledger.qmd"
WRAPPER = ROOT / "articles/proximal-distal-a-journey-through-the-swing.qmd"


def test_stationary_contact_has_impulse_without_work() -> None:
    force, contact_velocity, duration = 100.0, 0.0, 0.1
    assert force * duration == 10.0
    assert force * contact_velocity * duration == 0.0
    assert force * 2.0 != force * contact_velocity  # COM pseudopower is a different quantity.


def test_wrench_point_transport_preserves_power_but_observer_change_does_not() -> None:
    force = np.array([0.0, 2.0, 0.0])
    moment = np.array([0.0, 0.0, 5.0])
    velocity = np.array([0.0, 3.0, 0.0])
    angular = np.array([0.0, 0.0, 4.0])
    offset = np.array([1.0, 0.0, 0.0])
    shifted_velocity = velocity + np.cross(angular, offset)
    shifted_moment = moment - np.cross(offset, force)
    original_power = force @ velocity + moment @ angular
    assert original_power == pytest.approx(26.0)
    assert force @ shifted_velocity + shifted_moment @ angular == pytest.approx(original_power)
    observer_speed = np.array([0.0, 1.0, 0.0])
    assert force @ (velocity - observer_speed) + moment @ angular == pytest.approx(24.0)


def test_flexible_contacts_can_have_zero_wrench_and_nonzero_power() -> None:
    positions = np.array([[-0.05, 0, 0], [0.05, 0, 0]])
    forces = np.array([[-10.0, 0, 0], [10.0, 0, 0]])
    velocities = np.array([[-0.2, 0, 0], [0.2, 0, 0]])
    assert np.sum(forces, axis=0) == pytest.approx(np.zeros(3))
    assert np.sum(np.cross(positions, forces), axis=0) == pytest.approx(np.zeros(3))
    assert np.sum(forces * velocities) == pytest.approx(4.0)


def test_elastic_return_is_internal_conversion_in_whole_system_ledger() -> None:
    stiffness, extension, extension_rate = 1000.0, 0.01, -0.1
    elastic_energy = stiffness * extension**2 / 2
    elastic_power = stiffness * extension * extension_rate
    kinetic_power = -elastic_power
    assert elastic_energy == pytest.approx(0.05)
    assert elastic_power == pytest.approx(-1.0)
    assert kinetic_power + elastic_power == 0.0


def test_negative_moment_component_does_not_determine_total_power() -> None:
    moment = np.array([-2.0, 3.0, 0.0])
    angular = np.array([1.0, 1.0, 0.0])
    assert moment[0] * angular[0] == -2.0
    assert moment @ angular == 1.0


def test_finite_removal_is_not_a_derivative_for_nonlinear_input_map() -> None:
    initial, final = 2.0, 0.0
    actual_change = final**2 - initial**2
    local_prediction = 2 * initial * (final - initial)
    assert actual_change == -4.0
    assert local_prediction == -8.0


def test_equal_net_first_order_channels_can_hide_different_internal_states() -> None:
    time, tau = 0.01, 0.018
    post = np.array([16.0, -6.0])
    persistent = post + (np.array([10.0, -4.0]) - post) * math.exp(-time / tau)
    reversal = post + (np.array([-4.0, 10.0]) - post) * math.exp(-time / tau)
    assert persistent.sum() == pytest.approx(reversal.sum())
    assert not np.allclose(persistent, reversal)
    zero_crossing = tau * math.log(20 / 16)
    assert zero_crossing == pytest.approx(0.0040165839)
    assert 16 - 20 * math.exp(-zero_crossing / tau) == pytest.approx(0.0)


def test_force_couple_collapse_requires_bounded_forces() -> None:
    separations = np.array([0.1, 0.01, 0.001])
    assert separations * 10 == pytest.approx([1.0, 0.1, 0.01])
    fixed_moment_forces = 1.0 / separations
    assert fixed_moment_forces == pytest.approx([10.0, 100.0, 1000.0])


def test_opening_ledger_counts_gravity_and_elastic_storage_once() -> None:
    hand_work, gravity_work, loss, storage_gain = 500.0 * 0.1, 3.0, 5.0, 8.0
    kinetic_gain = hand_work + gravity_work - loss - storage_gain
    assert kinetic_gain == pytest.approx(40.0)
    assert kinetic_gain + storage_gain - gravity_work == hand_work - loss
    subsequent_storage_change = -8.0
    assert -subsequent_storage_change - 2.0 == pytest.approx(6.0)


def test_point_mass_energy_does_not_use_directional_impact_effective_mass() -> None:
    masses = np.array([0.20, 0.22])
    assert 0.5 * masses * 45.0**2 == pytest.approx([202.5, 222.75])
    source = (CHAPTER.parent / "ch01_follow_the_energy.qmd").read_text(encoding="utf-8")
    assert "total kinetic energy" in source
    assert "must not be substituted for physical" in source
    assert "shaft\nreturn is internal conversion" in source


@pytest.mark.parametrize(
    "required",
    [
        "stationary no-slip contact",
        "strain energy remains stored energy",
        "finite same-state comparison",
        "bounded hand forces",
        "a1a613999eb0c744da96caa040941955eb210a21",
        "@marsan2019",
    ],
)
def test_chapter_preserves_accounting_and_evidence_boundaries(required: str) -> None:
    assert required in CHAPTER.read_text(encoding="utf-8")


def test_wrapper_does_not_imply_ground_is_a_universal_energy_source() -> None:
    source = WRAPPER.read_text(encoding="utf-8")
    assert "stationary ground contact" in source
    assert "complete measured treatment" not in source
    assert "future inputs or input laws" in source
