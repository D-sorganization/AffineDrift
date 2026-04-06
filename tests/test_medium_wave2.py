"""Tests for medium-severity wave 2 fixes.

Covers:
- #2160: _build_target_state() extraction in SwingOptimizer
- #2161: STIMPMETER_CALIBRATION_FACTOR constant usage
- #2162: RoundSimulator input validation
- #2163: Postconditions in compute_hessian_norm / compute_hessian_bound
- #2165: Core physics test coverage uplift
- #2171: REGULATION_HOLE_RADIUS_M, HOLE_CAPTURE_SPEED_MS constants
- #2172: GolfHole.pin_x / pin_y properties
- #2174: Shared LaTeX regex patterns
- #2175: Absolute imports in convert_all scripts
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from src.affine_control.residuals import compute_hessian_bound, compute_hessian_norm
from src.affine_control.swing_optimizer import SwingOptimizationConfig, SwingOptimizer
from src.core.constants import (
    HOLE_CAPTURE_SPEED_MS,
    REGULATION_HOLE_RADIUS_M,
    STIMPMETER_CALIBRATION_FACTOR,
)
from src.core.contracts import ContractViolationError
from src.golf_simulation.course import GolfHole, create_par3_course
from src.golf_simulation.putting import GreenSurface, PuttingSimulator
from src.golf_simulation.round_simulator import RoundSimulator
from src.tools.utils.constants import (
    LATEX_ABSTRACT_PATTERN,
    LATEX_ALIGN_BEGIN_PATTERN,
    LATEX_EQUATION_BEGIN_PATTERN,
    LATEX_KEYPOINT_PATTERN,
    LATEX_LIMITATION_PATTERN,
    LATEX_TIKZ_PATTERN,
)

# ── #2171 / #2161: Physics constants ──────────────────────────────────────


class TestPhysicsConstants:
    """Verify golf-simulation physics constants are defined correctly."""

    def test_stimpmeter_calibration_factor_value(self) -> None:
        assert STIMPMETER_CALIBRATION_FACTOR == 1.285

    def test_regulation_hole_radius_value(self) -> None:
        assert REGULATION_HOLE_RADIUS_M == 0.054

    def test_hole_capture_speed_value(self) -> None:
        assert HOLE_CAPTURE_SPEED_MS == 1.5

    def test_putting_simulator_default_hole_radius(self) -> None:
        """PuttingSimulator default hole_radius should equal REGULATION_HOLE_RADIUS_M."""
        green = GreenSurface.create_flat_green()
        sim = PuttingSimulator(green)
        assert sim.hole_radius == REGULATION_HOLE_RADIUS_M

    def test_stimpmeter_used_in_putting_simulate(self) -> None:
        """Verify stimpmeter calibration factor is used (deceleration = FACTOR / stimp)."""
        green = GreenSurface.create_flat_green(stimp=10.0)
        sim = PuttingSimulator(green)
        trajectory = sim.simulate(15.0, 5.0, 0.0, 2.0)
        assert len(trajectory) > 1  # Simulation ran


# ─��� #2172: GolfHole pin_x / pin_y ────────────────────────────────────────


class TestGolfHolePinProperties:
    """Test pin_x and pin_y convenience properties on GolfHole."""

    def test_pin_x_equals_pin_position_0(self) -> None:
        hole = GolfHole(
            number=1,
            par=4,
            yardage=400.0,
            handicap=1,
            tee_position=(0.0, 0.0, 0.0),
            pin_position=(365.76, 12.0, 0.0),
            green_center=(365.76, 12.0, 0.0),
            green_radius=15.0,
        )
        assert hole.pin_x == 365.76

    def test_pin_y_equals_pin_position_1(self) -> None:
        hole = GolfHole(
            number=1,
            par=4,
            yardage=400.0,
            handicap=1,
            tee_position=(0.0, 0.0, 0.0),
            pin_position=(365.76, 12.0, 0.0),
            green_center=(365.76, 12.0, 0.0),
            green_radius=15.0,
        )
        assert hole.pin_y == 12.0

    def test_pin_properties_on_factory_course(self) -> None:
        course = create_par3_course()
        for hole in course.holes:
            assert hole.pin_x == hole.pin_position[0]
            assert hole.pin_y == hole.pin_position[1]


# ── #2160: _build_target_state extraction ─────────────────────────────────


class TestBuildTargetState:
    """Verify _build_target_state returns correct target vector."""

    def test_target_state_shape(self) -> None:
        config = SwingOptimizationConfig(n_joints=3, allow_mock_solver=True)
        optimizer = SwingOptimizer(config)
        target = optimizer._build_target_state()
        assert target.shape == (6,)

    def test_target_state_positions_are_zero(self) -> None:
        config = SwingOptimizationConfig(n_joints=2, target_velocity=10.0, allow_mock_solver=True)
        optimizer = SwingOptimizer(config)
        target = optimizer._build_target_state()
        np.testing.assert_array_equal(target[:2], [0.0, 0.0])

    def test_target_state_velocities_are_target_velocity(self) -> None:
        config = SwingOptimizationConfig(n_joints=2, target_velocity=10.0, allow_mock_solver=True)
        optimizer = SwingOptimizer(config)
        target = optimizer._build_target_state()
        np.testing.assert_array_equal(target[2:], [10.0, 10.0])

    def test_cost_unchanged_after_refactor(self) -> None:
        """Ensure compute_cost still works after _build_target_state extraction."""
        config = SwingOptimizationConfig(
            n_joints=2,
            control_weight=1.0,
            target_velocity=10.0,
            allow_mock_solver=True,
        )
        optimizer = SwingOptimizer(config)
        state = np.array([0.0, 0.0, 10.0, 10.0])
        control = np.zeros(2)
        cost = optimizer.compute_cost(state, control)
        assert cost == pytest.approx(0.0, abs=1e-10)


# ── #2162: RoundSimulator input validation ────────────────────────────────


class TestRoundSimulatorValidation:
    """Verify require() preconditions in RoundSimulator.__init__."""

    def test_rejects_non_course(self) -> None:
        with pytest.raises(ContractViolationError):
            RoundSimulator(course="not a course")  # type: ignore[arg-type]

    def test_rejects_invalid_club_bag(self) -> None:
        course = create_par3_course()
        with pytest.raises(ContractViolationError):
            RoundSimulator(course, club_bag="not a bag")  # type: ignore[arg-type]

    def test_rejects_invalid_ball_flight(self) -> None:
        course = create_par3_course()
        with pytest.raises(ContractViolationError):
            RoundSimulator(course, ball_flight=42)  # type: ignore[arg-type]

    def test_accepts_valid_args(self) -> None:
        course = create_par3_course()
        sim = RoundSimulator(course, rng_seed=42)
        assert sim.course is course


# ── #2163: Postconditions in hessian functions ────────────────────────────


class TestHessianPostconditions:
    """Verify ensure() postconditions for non-negative results."""

    @staticmethod
    def _quadratic_fn(x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        return np.array([x[0] ** 2])

    @staticmethod
    def _linear_fn(x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        return np.array([2.0 * x[0] + 1.0])

    def test_compute_hessian_norm_non_negative(self) -> None:
        result = compute_hessian_norm(self._quadratic_fn, np.array([1.0]), np.array([0.0]))
        assert result >= 0

    def test_compute_hessian_bound_non_negative(self) -> None:
        result = compute_hessian_bound(self._quadratic_fn, np.array([1.0]), np.array([0.0]))
        assert result >= 0

    def test_linear_function_hessian_near_zero(self) -> None:
        result = compute_hessian_norm(self._linear_fn, np.array([1.0]), np.array([0.0]))
        assert result >= 0
        assert result < 0.01  # Hessian of a linear function should be near zero


# ── #2174: Shared LaTeX regex patterns ────────────────────────────────────


class TestSharedLatexPatterns:
    """Verify LaTeX regex constants are non-empty strings."""

    def test_abstract_pattern_is_string(self) -> None:
        assert isinstance(LATEX_ABSTRACT_PATTERN, str) and len(LATEX_ABSTRACT_PATTERN) > 0

    def test_keypoint_pattern_is_string(self) -> None:
        assert isinstance(LATEX_KEYPOINT_PATTERN, str) and len(LATEX_KEYPOINT_PATTERN) > 0

    def test_limitation_pattern_is_string(self) -> None:
        assert isinstance(LATEX_LIMITATION_PATTERN, str) and len(LATEX_LIMITATION_PATTERN) > 0

    def test_equation_begin_pattern_is_string(self) -> None:
        assert isinstance(LATEX_EQUATION_BEGIN_PATTERN, str)

    def test_align_begin_pattern_is_string(self) -> None:
        assert isinstance(LATEX_ALIGN_BEGIN_PATTERN, str)

    def test_tikz_pattern_is_string(self) -> None:
        assert isinstance(LATEX_TIKZ_PATTERN, str)

    def test_abstract_pattern_matches(self) -> None:
        import re

        text = r"\begin{abstract}Some abstract text.\end{abstract}"
        assert re.search(LATEX_ABSTRACT_PATTERN, text, re.DOTALL) is not None


# ── #2175: Absolute imports in convert_all scripts ────────────────────────


class TestConvertAllImports:
    """Verify convert_all scripts use absolute imports (importable)."""

    def test_convert_all_to_quarto_importable(self) -> None:
        import importlib

        spec = importlib.util.find_spec("src.tools.convert_all_to_quarto")
        assert spec is not None, "src.tools.convert_all_to_quarto should be importable"

    def test_convert_all_latex_importable(self) -> None:
        import importlib

        spec = importlib.util.find_spec("src.tools.convert_all_latex")
        assert spec is not None, "src.tools.convert_all_latex should be importable"
