"""Independent coordinate, feasibility, and reachability counterexamples."""

from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_joint_power_is_invariant_under_absolute_to_relative_angles() -> None:
    absolute_rates = np.array([2.0, 7.0])
    joint_torques = np.array([8.0, 3.0])
    absolute_from_relative = np.array([[1.0, 0.0], [1.0, 1.0]])
    relative_rates = np.linalg.solve(absolute_from_relative, absolute_rates)
    absolute_load = np.array([joint_torques[0] - joint_torques[1], joint_torques[1]])
    assert absolute_from_relative.T @ absolute_load == pytest.approx(joint_torques)
    assert absolute_load @ absolute_rates == pytest.approx(joint_torques @ relative_rates)


def test_positive_inertia_does_not_fix_coupling_acceleration_sign() -> None:
    accelerations = []
    for coupling in (-0.4, 0.4):
        mass = np.array([[2.0, coupling], [coupling, 1.0]])
        assert np.all(np.linalg.eigvalsh(mass) > 0)
        accelerations.append(-mass[1, 0] * -2.0 / mass[1, 1])
    assert accelerations == pytest.approx([-0.8, 0.8])


def test_annihilator_condition_does_not_enforce_torque_bounds() -> None:
    actuation = np.array([[1.0], [0.0]])
    load = np.array([10.0, 0.0])
    assert np.linalg.matrix_rank(actuation) == 1  # Full column rank.
    assert np.array([[0.0, 1.0]]) @ load == pytest.approx([0.0])
    required = np.linalg.lstsq(actuation, load, rcond=None)[0]
    assert abs(required[0]) > 1.0  # Infeasible with |u| <= 1.


def test_reviewed_editions_remove_unsupported_release_and_rank_claims() -> None:
    sources = [
        "articles/motion-control/chapter5.tex",
        "articles/motion-control/Control_Is_Motion_Complete.tex",
        "articles/The_Geometry_of_Motion/Volume_II/chapters/ch05_underactuation_and_passive_dyn.tex",
        "articles/The_Geometry_of_Motion/quarto/volume2_content.qmd",
    ]
    for relative in sources:
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert "matrix $\\Bmat$ is not full rank" not in source, relative
        assert "It is an optimal transfer of momentum" not in source, relative
        assert "Chow's Theorem / Orbit Theorem" not in source, relative
        assert "required input must also belong" in source, relative
