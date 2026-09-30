"""Independent mechanics checks for the bounded impact-optimality argument."""

from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "articles/impact-optimality-and-model-limits.qmd"


def _mass_matrix(
    proximal_inertia: float,
    arm_length: float,
    club: tuple[float, float, float, float],
    angle: float = 0.0,
) -> np.ndarray:
    """Assemble the relative-angle inertia for a rigid club with an axial COM."""
    mass, _length, com, inertia = club
    delta = inertia + mass * com**2
    coupling = mass * arm_length * com * np.cos(angle)
    return np.array(
        [
            [proximal_inertia + mass * arm_length**2 + delta + 2 * coupling, delta + coupling],
            [delta + coupling, delta],
        ]
    )


@pytest.mark.parametrize("angle", [-1.4, -0.3, 0.0, 0.9])
def test_mass_matrix_matches_separately_assembled_body_energies(angle: float) -> None:
    proximal_inertia, arm_length = 0.47, 0.65
    mass, length, com, inertia = club = (0.31, 1.143, 0.89, 0.043)
    rates = np.array([3.0, 11.0])
    club_rate = rates.sum()
    wrist_velocity = np.array([0.0, arm_length * rates[0]])
    com_velocity = wrist_velocity + com * club_rate * np.array([-np.sin(angle), np.cos(angle)])
    body_energy = (
        0.5 * proximal_inertia * rates[0] ** 2
        + 0.5 * mass * (com_velocity @ com_velocity)
        + 0.5 * inertia * club_rate**2
    )
    matrix = _mass_matrix(proximal_inertia, arm_length, club, angle)
    assert length > com  # The head location and COM are distinct inputs.
    assert 0.5 * rates @ matrix @ rates == pytest.approx(body_energy)


def test_normalized_optimum_respects_energy_and_bounds_every_sampled_direction() -> None:
    energy, arm_length, club_length = 120.0, 0.65, 1.143
    matrix = _mass_matrix(0.47, arm_length, (0.31, club_length, 0.89, 0.043))
    output = np.array([arm_length + club_length, club_length])
    direction = np.linalg.solve(matrix, output)
    optimum = np.sqrt(2 * energy / (output @ direction)) * direction
    assert 0.5 * optimum @ matrix @ optimum == pytest.approx(energy)
    assert output @ optimum == pytest.approx(np.sqrt(2 * energy * output @ direction))
    angles = np.linspace(0, 2 * np.pi, 1001)
    circle = np.array([np.cos(angles), np.sin(angles)])
    rates = np.sqrt(2 * energy) * np.linalg.solve(np.linalg.cholesky(matrix).T, circle)
    assert np.max(output @ rates) <= output @ optimum + 1e-10
    assert optimum[0] < 0


@pytest.mark.parametrize("proximal_inertia,mass", [(0.1, 0.238), (0.47, 0.5), (1.2, 0.31)])
def test_tip_mass_has_zero_optimal_hand_rate_only_with_positive_proximal_inertia(
    proximal_inertia: float, mass: float
) -> None:
    arm_length, club_length, energy = 0.65, 1.1, 120.0
    matrix = _mass_matrix(proximal_inertia, arm_length, (mass, club_length, club_length, 0))
    output = np.array([arm_length + club_length, club_length])
    direction = np.linalg.solve(matrix, output)
    optimum = np.sqrt(2 * energy / (output @ direction)) * direction
    assert optimum[0] == pytest.approx(0, abs=1e-12)
    assert output @ optimum == pytest.approx(np.sqrt(2 * energy / mass))
    rates = np.array([7.0, 4.0])
    assert 0.5 * rates @ matrix @ rates == pytest.approx(
        0.5 * proximal_inertia * rates[0] ** 2 + 0.5 * mass * (output @ rates) ** 2
    )
    degenerate = _mass_matrix(0.0, arm_length, (mass, club_length, club_length, 0))
    assert np.linalg.matrix_rank(degenerate) == 1


def test_distributed_coefficient_threshold_and_coupling_error_share_one_bracket() -> None:
    proximal_inertia, arm_length = 0.47, 0.65
    mass, length, com, inertia = club = (0.31, 1.143, 0.89, 0.043)
    matrix = _mass_matrix(proximal_inertia, arm_length, club)
    delta = inertia + mass * com**2
    bracket = inertia - mass * com * (length - com)
    determinant = np.linalg.det(matrix)
    assert determinant == pytest.approx(proximal_inertia * delta + mass * arm_length**2 * inertia)
    direction = np.linalg.solve(matrix, [arm_length + length, length])
    assert direction[0] == pytest.approx(arm_length * bracket / determinant)
    assert bracket == pytest.approx(-0.0268027)
    assert mass * com * (length - com) == pytest.approx(0.0698027)
    assert mass * com * (length - com) / inertia == pytest.approx(1.62331860465)
    equivalent_mass = delta / length**2
    assert equivalent_mass * arm_length * length - mass * arm_length * com == pytest.approx(
        arm_length * bracket / length
    )


def test_collinear_mass_support_bounds_the_formal_forward_rate_regime() -> None:
    locations = np.array([0.0, 0.2, 0.7, 1.143])
    masses = np.array([0.05, 0.02, 0.04, 0.20])
    length, mass = locations[-1], masses.sum()
    com = masses @ locations / mass
    inertia = masses @ (locations - com) ** 2
    bracket = inertia - mass * com * (length - com)
    assert bracket == pytest.approx(-(masses @ (locations * (length - locations))))
    assert bracket < 0
    # All mass at the two endpoints saturates the bound; interior mass does not.
    endpoint_masses, endpoints = np.array([0.05, 0.20]), np.array([0.0, length])
    endpoint_com = endpoint_masses @ endpoints / endpoint_masses.sum()
    endpoint_inertia = endpoint_masses @ (endpoints - endpoint_com) ** 2
    assert endpoint_inertia == pytest.approx(
        endpoint_masses.sum() * endpoint_com * (length - endpoint_com)
    )


def test_matching_grip_inertia_does_not_match_the_full_matrix() -> None:
    arm_length, model_length = 0.65, 1.1
    mass, com, inertia = 0.31, 0.867, 0.0551
    delta = inertia + mass * com**2
    equivalent_mass = delta / model_length**2
    actual = _mass_matrix(0.47, arm_length, (mass, model_length, com, inertia))
    equivalent = _mass_matrix(0.47, arm_length, (equivalent_mass, model_length, model_length, 0))
    assert delta == pytest.approx(0.28812359)
    assert equivalent_mass == pytest.approx(0.238118669421)
    assert mass * arm_length * com == pytest.approx(0.1747005)
    assert equivalent_mass * arm_length * model_length == pytest.approx(0.170254848636)
    assert actual[1, 1] == pytest.approx(equivalent[1, 1])
    assert actual[0, 1] != pytest.approx(equivalent[0, 1])
    assert actual[0, 0] != pytest.approx(equivalent[0, 0])
    assert 0.31 * model_length**2 == pytest.approx(0.3751)
    assert 0.50 * model_length**2 == pytest.approx(0.605)


def test_changing_the_grip_origin_changes_inertia_and_head_lever_arm() -> None:
    mass, com, inertia, length, offset = 0.31, 0.867, 0.0551, 1.143, 0.1
    butt_inertia = inertia + mass * com**2
    grip_inertia = inertia + mass * (com - offset) ** 2
    assert grip_inertia == pytest.approx(butt_inertia - 2 * offset * mass * com + mass * offset**2)
    assert grip_inertia < butt_inertia
    assert grip_inertia / (length - offset) ** 2 != pytest.approx(butt_inertia / length**2)


@pytest.mark.parametrize(
    "required,forbidden",
    [
        ("positive-definite", "Identically zero, for every parameter value"),
        ("0.0698027", "I_2 \\gtrsim 0.2"),
        ("one coefficient", "swings like the real club"),
        ("failure to find", "**no** | — | —"),
        ("heuristic", "five of six observables. The mechanisms and the outcome coincide"),
        ("eccentric", "removes the impossible braking"),
        ("moving pivot", "requires $L_1$ to shorten"),
        ("whole trajectories", "**Holding lag for its own sake is the one strategy"),
    ],
)
def test_article_retains_the_boundaries_that_prevent_overclaiming(
    required: str, forbidden: str
) -> None:
    source = " ".join(SOURCE.read_text(encoding="utf-8").split())
    assert required in source
    assert forbidden not in source


def test_workbench_summary_preserves_the_same_optimality_scope() -> None:
    source = (ROOT / "articles/proximal-distal-model-workbench.qmd").read_text(encoding="utf-8")
    assert "fixed-pose" in source
    assert "positive proximal inertia" in source
    assert "historical" in source
    assert "releasing the club requires reversing" not in source
    assert "zero* for every parameter value" not in source
