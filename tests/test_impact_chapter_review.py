"""Manufactured geometry and impulse checks for impact chapter review #4842."""

import re
from pathlib import Path

import numpy as np
import pytest

CHAPTER = (
    Path(__file__).resolve().parents[1]
    / "articles/Launch_Monitor_Technology_Review/sections/03-impact-physics.tex"
)


def test_launch_diagram_matches_its_declared_weight() -> None:
    """The drawn launch angle must agree with the displayed manufactured rule."""
    source = CHAPTER.read_text(encoding="utf-8")
    match = re.search(r"8\.6\*cos\(([-\d.]+)\)", source)
    assert match is not None
    assert float(match[1]) == pytest.approx(0.76 * -2.0 + 0.24 * -6.0)


def test_gear_equation_has_no_hundredfold_scaling_error() -> None:
    """Protect the cited mph/inch/rpm conversion from the old extra factor."""
    source = CHAPTER.read_text(encoding="utf-8")
    equation = source.split(r"\label{eq:gear}", 1)[1].split(r"\end{equation}", 1)[0]
    assert r"\times 100" not in equation
    assert "16.4" in equation


def test_gear_unit_conversion_matches_independent_si_calculation() -> None:
    """Check units of the historical heuristic, not its physical accuracy."""
    speed = 150.0 * 1609.344 / 3600.0
    depth, offset = 1.42 * 0.0254, 0.25 * 0.0254
    inertia, mass, radius = 5100e-7, 0.046, 0.043 / 2.0
    head_increment = offset * mass * speed / inertia
    rpm = head_increment * depth / radius * 60.0 / (2.0 * np.pi)
    imperial = 58830.0 * 150.0 * 1.42 * 0.25 / 5100.0
    assert rpm == pytest.approx(imperial, rel=0.002)
    assert rpm == pytest.approx(16.4 * 150.0 * 0.25, rel=0.002)
    assert rpm < 620.0


def test_coupled_gear_impulse_satisfies_restitution_and_sticking() -> None:
    """Independent body updates verify the two-by-two contact mobility solve."""
    mass, head_mass, radius, head_inertia = 0.04593, 0.2, 0.02135, 0.0005
    ball_inertia = 0.4 * mass * radius**2
    depth, offset, speed, restitution = 0.04, 0.01, 45.0, 0.83
    normal, tangent = np.eye(3)[[0, 2]]  # Forward/up/right basis.
    head_arm, ball_arm = depth * normal + offset * tangent, -radius * normal
    mobility = np.array(
        [
            [1 / mass + 1 / head_mass + offset**2 / head_inertia, -depth * offset / head_inertia],
            [
                -depth * offset / head_inertia,
                1 / mass + 1 / head_mass + radius**2 / ball_inertia + depth**2 / head_inertia,
            ],
        ]
    )
    components = np.linalg.solve(mobility, [(1 + restitution) * speed, 0.0])
    impulse = components[0] * normal + components[1] * tangent
    ball_velocity = impulse / mass
    head_velocity = speed * normal - impulse / head_mass
    ball_spin = np.cross(ball_arm, impulse) / ball_inertia
    head_spin = -np.cross(head_arm, impulse) / head_inertia
    relative = (
        ball_velocity
        + np.cross(ball_spin, ball_arm)
        - head_velocity
        - np.cross(head_spin, head_arm)
    )
    assert relative @ normal == pytest.approx(restitution * speed)
    assert relative @ tangent == pytest.approx(0.0, abs=1e-12)
    assert abs(components[1]) < 0.3 * components[0]  # Feasible sticking candidate.
    np.testing.assert_allclose(
        mass * ball_velocity + head_mass * head_velocity, head_mass * speed * normal
    )
    angular = (
        np.cross(head_arm - ball_arm, impulse) + ball_inertia * ball_spin + head_inertia * head_spin
    )
    np.testing.assert_allclose(angular, 0.0, atol=1e-14)
    final_energy = (
        mass * (ball_velocity @ ball_velocity)
        + head_mass * (head_velocity @ head_velocity)
        + ball_inertia * (ball_spin @ ball_spin)
        + head_inertia * (head_spin @ head_spin)
    ) / 2
    assert final_energy <= head_mass * speed**2 / 2
    # Matching contact speeds does not equate face speed to R times ball spin:
    # ball translation and head tangential recoil are also present.
    face_tangent_speed = (head_velocity + np.cross(head_spin, head_arm)) @ tangent
    assert not np.isclose(abs(face_tangent_speed), radius * np.linalg.norm(ball_spin))


def test_fixed_inclined_plane_path_is_conditional_geometry() -> None:
    """A tangent in the declared plane yields the descending-strike example."""
    inclination, attack = np.deg2rad([60.0, -5.0])
    path = np.arcsin(-np.tan(attack) / np.tan(inclination))
    velocity = np.array(
        [np.cos(attack) * np.cos(path), np.sin(attack), np.cos(attack) * np.sin(path)]
    )
    plane_normal = np.array([0.0, np.cos(inclination), np.sin(inclination)])
    assert velocity @ plane_normal == pytest.approx(0.0, abs=1e-14)
    assert np.rad2deg(path) == pytest.approx(2.895333787723421, abs=1e-5)


def test_chapter_removes_universal_instrument_and_speed_verdicts() -> None:
    """Guard the original unqualified inference rather than a writing style."""
    source = CHAPTER.read_text(encoding="utf-8")
    assert "Every launch monitor embeds a model" not in source
    assert "loft-appropriate ceiling indicates a measurement error" not in source
    assert "optical impact-location\nadd-on" not in source
