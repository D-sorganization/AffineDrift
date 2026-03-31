"""Tests for helper functions extracted during issue #2072 function-size refactor.

Each test verifies the contract and behaviour of a newly-extracted private helper
so that the refactoring is covered by TDD as required by the project guidelines.
"""

from __future__ import annotations

import math
from typing import Any
from unittest.mock import MagicMock

import numpy as np
import pytest

from src.affine_control.residuals import ResidualMonitor, _build_hessian_tensor
from src.golf_simulation.ball_flight import BallFlightDynamics
from src.golf_simulation.course import (
    _CHAMPIONSHIP_HANDICAPS,
    _CHAMPIONSHIP_HOLE_SPECS,
    GolfHole,
    create_championship_course,
)
from src.golf_simulation.putting import GreenSurface, PuttingSimulator
from src.golf_simulation.round_simulator import RoundSimulator
from src.golf_simulation.terrain import (
    TerrainType,
    _apply_friction_to_tangential,
    _resolve_surface_normal,
)
from src.tools.utils.conversion_utils import (
    _execute_single_conversion,
    _validate_conversion_entry,
)
from src.tools.wrist_universal_joint.torque_calculator import (
    _compute_i_alpha,
    calculate_moments_of_inertia,
)

# ─────────────────────────────────────────────────────────────────────────────
# residuals._build_hessian_tensor
# ─────────────────────────────────────────────────────────────────────────────


class TestBuildHessianTensor:
    def test_shape(self):
        """Hessian tensor has shape (output_dim, n, n)."""

        def f(x: Any, u: Any) -> Any:
            return np.array([x[0] ** 2, x[1] ** 2])

        x = np.array([1.0, 2.0])
        u = np.array([0.0])
        H = _build_hessian_tensor(f, x, u, epsilon=1e-4)
        assert H.shape == (2, 2, 2)

    def test_quadratic_diagonal(self):
        """For f(x)=x^2, H[0,0,0] ~ 2 (second derivative of x^2 at any x)."""

        def f(x: Any, u: Any) -> Any:
            return np.array([x[0] ** 2])

        x = np.array([1.0])
        u = np.array([0.0])
        H = _build_hessian_tensor(f, x, u, epsilon=1e-4)
        assert abs(H[0, 0, 0] - 2.0) < 0.01

    def test_linear_function_near_zero_hessian(self):
        """For f(x)=x, Hessian should be near zero."""

        def f(x: Any, u: Any) -> Any:
            return x.copy()

        x = np.array([1.0, 0.5])
        u = np.array([0.0])
        H = _build_hessian_tensor(f, x, u, epsilon=1e-4)
        assert np.max(np.abs(H)) < 1e-6


# ─────────────────────────────────────────────────────────────────────────────
# ResidualMonitor helpers (_update_hysteresis_counters, _compute_next_mode,
# _apply_mode_transition)
# ─────────────────────────────────────────────────────────────────────────────


class TestResidualMonitorHelpers:
    def _monitor(self, n: int = 2) -> ResidualMonitor:
        return ResidualMonitor(eps_warning=0.1, eps_critical=0.5, n_hysteresis=n)

    def test_update_counters_critical(self):
        m = self._monitor()
        m._update_hysteresis_counters(0.6)
        assert m.high_count == 1
        assert m.warn_count == 1
        assert m.low_count == 0

    def test_update_counters_warning(self):
        m = self._monitor()
        m._update_hysteresis_counters(0.2)
        assert m.warn_count == 1
        assert m.high_count == 0
        assert m.low_count == 0

    def test_update_counters_low(self):
        m = self._monitor()
        m._update_hysteresis_counters(0.01)
        assert m.low_count == 1
        assert m.high_count == 0

    def test_compute_next_mode_lqr_escalates(self):
        m = self._monitor(n=1)
        m.high_count = 1
        assert m._compute_next_mode() == "MPC_WARN"

    def test_compute_next_mode_mpc_warn_escalates(self):
        m = self._monitor(n=1)
        m.mode = "MPC_WARN"
        m.high_count = 1
        assert m._compute_next_mode() == "MPC_FULL"

    def test_compute_next_mode_mpc_full_recovers(self):
        m = self._monitor(n=1)
        m.mode = "MPC_FULL"
        m.low_count = 1
        assert m._compute_next_mode() == "MPC_WARN"

    def test_apply_mode_transition_resets_counters(self):
        m = self._monitor()
        m.high_count = 5
        m.warn_count = 3
        m.low_count = 2
        m._apply_mode_transition("MPC_WARN", 0.6)
        assert m.mode == "MPC_WARN"
        assert m.high_count == 0
        assert m.warn_count == 0
        assert m.low_count == 0


# ─────────────────────────────────────────────────────────────────────────────
# terrain._resolve_surface_normal
# ─────────────────────────────────────────────────────────────────────────────


class TestResolveSurfaceNormal:
    def test_none_returns_vertical(self):
        n = _resolve_surface_normal(None)
        np.testing.assert_array_almost_equal(n, [0.0, 0.0, 1.0])

    def test_normalises_vector(self):
        raw = np.array([0.0, 0.0, 5.0])
        n = _resolve_surface_normal(raw)
        np.testing.assert_array_almost_equal(n, [0.0, 0.0, 1.0])

    def test_tilted_normal(self):
        raw = np.array([1.0, 0.0, 1.0])
        n = _resolve_surface_normal(raw)
        assert abs(np.linalg.norm(n) - 1.0) < 1e-10

    def test_zero_vector_raises(self):
        with pytest.raises(ValueError):
            _resolve_surface_normal(np.zeros(3))


# ─────────────────────────────────────────────────────────────────────────────
# terrain._apply_friction_to_tangential
# ─────────────────────────────────────────────────────────────────────────────


class TestApplyFrictionToTangential:
    def test_reduces_speed(self):
        v_t = np.array([10.0, 0.0, 0.0])
        result = _apply_friction_to_tangential(v_t, v_normal_mag=-5.0, friction=0.3)
        assert np.linalg.norm(result) < np.linalg.norm(v_t)

    def test_zero_tangential_unchanged(self):
        v_t = np.zeros(3)
        result = _apply_friction_to_tangential(v_t, v_normal_mag=-5.0, friction=0.3)
        np.testing.assert_array_equal(result, v_t)

    def test_high_friction_clamps_to_zero(self):
        v_t = np.array([1.0, 0.0, 0.0])
        result = _apply_friction_to_tangential(v_t, v_normal_mag=-20.0, friction=10.0)
        assert np.linalg.norm(result) == pytest.approx(0.0)


# ─────────────────────────────────────────────────────────────────────────────
# course._CHAMPIONSHIP_HOLE_SPECS constant and create_championship_course
# ─────────────────────────────────────────────────────────────────────────────


class TestChampionshipCourseData:
    def test_specs_length(self):
        assert len(_CHAMPIONSHIP_HOLE_SPECS) == 18

    def test_handicaps_length(self):
        assert len(_CHAMPIONSHIP_HANDICAPS) == 18

    def test_handicaps_unique(self):
        assert len(set(_CHAMPIONSHIP_HANDICAPS)) == 18

    def test_par_72(self):
        total = sum(p for p, _ in _CHAMPIONSHIP_HOLE_SPECS)
        assert total == 72

    def test_course_creation(self):
        course = create_championship_course()
        assert len(course.holes) == 18
        assert course.total_par == 72


# ─────────────────────────────────────────────────────────────────────────────
# course.GolfHole._fairway_projection
# ─────────────────────────────────────────────────────────────────────────────


def _make_test_hole() -> GolfHole:
    return GolfHole(
        number=1,
        par=4,
        yardage=400.0,
        handicap=1,
        tee_position=(0.0, 0.0, 0.0),
        pin_position=(366.0, 0.0, 0.0),
        green_center=(366.0, 0.0, 0.0),
        green_radius=15.0,
    )


class TestFairwayProjection:
    def test_on_centre_line(self):
        hole = _make_test_hole()
        t, perp = hole._fairway_projection(183.0, 0.0)
        assert abs(t - 0.5) < 0.01
        assert perp == pytest.approx(0.0, abs=1e-9)

    def test_off_centre_line(self):
        hole = _make_test_hole()
        _, perp = hole._fairway_projection(183.0, 10.0)
        assert abs(perp - 10.0) < 0.01

    def test_before_tee_t_negative(self):
        hole = _make_test_hole()
        t, _ = hole._fairway_projection(-50.0, 0.0)
        assert t < 0.0


# ─────────────────────────────────────────────────────────────────────────────
# ball_flight.BallFlightDynamics._clamp_to_ground
# ─────────────────────────────────────────────────────────────────────────────


class TestClampToGround:
    def test_clamps_z(self):
        dynamics = BallFlightDynamics()
        state_vec = np.array([100.0, 50.0, -2.0, 30.0, 0.0, -5.0, 0.0, 0.0, 0.0])
        result = dynamics._clamp_to_ground(state_vec, t=3.0)
        assert result.position[2] == pytest.approx(0.0)

    def test_preserves_xy(self):
        dynamics = BallFlightDynamics()
        state_vec = np.array([55.0, 20.0, -1.0, 25.0, 0.0, -3.0, 0.0, 0.0, 0.0])
        result = dynamics._clamp_to_ground(state_vec, t=1.0)
        assert result.position[0] == pytest.approx(55.0)
        assert result.position[1] == pytest.approx(20.0)


# ─────────────────────────────────────────────────────────────────────────────
# putting.PuttingSimulator._euler_step
# ─────────────────────────────────────────────────────────────────────────────


class TestEulerStep:
    def test_step_changes_position(self):
        surface = GreenSurface.create_flat_green()
        sim = PuttingSimulator(surface=surface, dt=0.01)
        x, y, vx, vy = sim._euler_step(0.0, 0.0, 1.0, 0.0, deceleration=0.1)
        assert x != pytest.approx(0.0)

    def test_friction_reduces_speed(self):
        surface = GreenSurface.create_flat_green()
        sim = PuttingSimulator(surface=surface, dt=0.1)
        x, y, vx1, vy1 = sim._euler_step(0.0, 0.0, 2.0, 0.0, deceleration=0.5)
        speed_after = math.sqrt(vx1**2 + vy1**2)
        assert speed_after < 2.0


# ─────────────────────────────────────────────────────────────────────────────
# round_simulator helpers (_build_launch_conditions, _apply_hazard_penalty,
# _compute_putt_initial_velocity, _find_holed_position)
# ─────────────────────────────────────────────────────────────────────────────


def _make_simulator_with_hole() -> tuple[RoundSimulator, GolfHole]:
    from src.golf_simulation.course import create_par3_course

    course = create_par3_course()
    sim = RoundSimulator(course=course, rng_seed=42)
    hole = course.holes[0]
    return sim, hole


class TestBuildLaunchConditions:
    def test_returns_launch_conditions(self):
        from src.golf_simulation.clubs import LaunchConditions

        sim, hole = _make_simulator_with_hole()
        from src.golf_simulation.clubs import ClubType

        club = sim.club_bag.get_club(ClubType.DRIVER)
        lc = sim._build_launch_conditions(hole.tee_position, hole, club)
        assert isinstance(lc, LaunchConditions)
        assert lc.ball_speed > 0

    def test_speed_within_range(self):
        sim, hole = _make_simulator_with_hole()
        from src.golf_simulation.clubs import ClubType

        club = sim.club_bag.get_club(ClubType.DRIVER)
        speeds = [
            sim._build_launch_conditions(hole.tee_position, hole, club).ball_speed
            for _ in range(30)
        ]
        assert all(s > 0 for s in speeds)


class TestApplyHazardPenalty:
    def _sim_and_hole(self) -> tuple[RoundSimulator, GolfHole]:
        return _make_simulator_with_hole()

    def test_no_penalty_on_fairway(self):
        sim, hole = self._sim_and_hole()
        end = (100.0, 5.0, 0.0)
        result_pos, result_terrain, is_penalty = sim._apply_hazard_penalty(
            hole.tee_position, end, TerrainType.FAIRWAY, hole
        )
        assert not is_penalty
        assert result_pos == end

    def test_penalty_on_water(self):
        sim, hole = self._sim_and_hole()
        start = hole.tee_position
        end = (200.0, 200.0, 0.0)
        _, _, is_penalty = sim._apply_hazard_penalty(start, end, TerrainType.WATER, hole)
        assert is_penalty

    def test_penalty_drops_80_percent(self):
        sim, hole = self._sim_and_hole()
        start = (0.0, 0.0, 0.0)
        end = (100.0, 0.0, 0.0)
        result_pos, _, _ = sim._apply_hazard_penalty(start, end, TerrainType.WATER, hole)
        assert result_pos[0] == pytest.approx(80.0)


class TestComputePuttInitialVelocity:
    def test_velocity_points_toward_pin(self):
        sim, hole = _make_simulator_with_hole()
        vx, vy = sim._compute_putt_initial_velocity(dx=1.0, dy=0.0, dist=1.0, stimp=11.0)
        # With no direction error (statistically), vx > 0 and vy ~ 0
        assert abs(vx) > abs(vy) * 0.5  # rough directional check

    def test_speed_positive(self):
        sim, _ = _make_simulator_with_hole()
        vx, vy = sim._compute_putt_initial_velocity(dx=5.0, dy=0.0, dist=5.0, stimp=11.0)
        assert math.sqrt(vx**2 + vy**2) > 0


class TestFindHoledPosition:
    def test_not_holed_returns_last_point(self):
        sim, hole = _make_simulator_with_hole()
        surface = GreenSurface.create_flat_green()
        putt_sim = PuttingSimulator(surface=surface)
        # Trajectory far from pin
        traj = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)]
        fx, fy = sim._find_holed_position(traj, putt_sim, hole)
        assert (fx, fy) == (2.0, 0.0)

    def test_holed_returns_pin(self):
        sim, hole = _make_simulator_with_hole()
        surface = GreenSurface.create_flat_green()
        putt_sim = PuttingSimulator(surface=surface)
        pin_x, pin_y = hole.pin_position[0], hole.pin_position[1]
        # Place ball right at pin with near-zero velocity
        traj = [(pin_x, pin_y), (pin_x + 0.001, pin_y)]
        fx, fy = sim._find_holed_position(traj, putt_sim, hole)
        assert (fx, fy) == (pin_x, pin_y)


# ─────────────────────────────────────────────────────────────────────────────
# conversion helpers
# ─────────────────────────────────────────────────────────────────────────────


class TestValidateConversionEntry:
    def test_valid_existing_entry(self, tmp_path):
        import logging

        src = tmp_path / "in.txt"
        src.write_text("hi")
        log = logging.getLogger("test")
        s, t = _validate_conversion_entry({"source": str(src), "target": "/out.txt"}, log)
        assert s == str(src)
        assert t == "/out.txt"

    def test_missing_source_returns_none(self, tmp_path):
        import logging

        log = logging.getLogger("test")
        s, t = _validate_conversion_entry(
            {"source": str(tmp_path / "ghost.txt"), "target": "out.txt"}, log
        )
        assert s is None

    def test_non_string_source_returns_none(self):
        import logging

        log = logging.getLogger("test")
        s, t = _validate_conversion_entry({"source": 123, "target": "out.txt"}, log)
        assert s is None


class TestExecuteSingleConversion:
    def test_dry_run_returns_true(self):
        import logging

        log = logging.getLogger("test")
        assert _execute_single_conversion(None, "a.txt", "b.txt", dry_run=True, logger=log)

    def test_success_calls_converter(self):
        import logging

        log = logging.getLogger("test")
        conv = MagicMock()
        result = _execute_single_conversion(conv, "a.txt", "b.txt", dry_run=False, logger=log)
        assert result
        conv.convert_file.assert_called_once_with("a.txt", "b.txt")

    def test_exception_returns_false(self):
        import logging

        log = logging.getLogger("test")
        conv = MagicMock()
        conv.convert_file.side_effect = OSError("disk full")
        result = _execute_single_conversion(conv, "a.txt", "b.txt", dry_run=False, logger=log)
        assert not result


# ─────────────────────────────────────────────────────────────────────────────
# torque_calculator._compute_i_alpha
# ─────────────────────────────────────────────────────────────────────────────


class TestComputeIAlpha:
    def test_positive_result(self):
        i_alpha = _compute_i_alpha(
            m_head_kg=0.2, m_shaft_kg=0.08, club_length_m=1.1, cg_distance_m=1.0
        )
        assert i_alpha > 0

    def test_heavier_head_increases_inertia(self):
        i_light = _compute_i_alpha(0.1, 0.08, 1.1, 1.0)
        i_heavy = _compute_i_alpha(0.4, 0.08, 1.1, 1.0)
        assert i_heavy > i_light

    def test_matches_calculate_moments(self):
        i_alpha_helper = _compute_i_alpha(
            m_head_kg=200.0 / 1000.0,
            m_shaft_kg=80.0 / 1000.0,
            club_length_m=1.1,
            cg_distance_m=1.0,
        )
        i_alpha_full, _ = calculate_moments_of_inertia(200.0, 80.0, 1.1, 1.0)
        assert i_alpha_helper == pytest.approx(i_alpha_full)
