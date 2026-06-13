"""Tests for the full round simulator."""

import math

import numpy as np
import pytest

from src.golf_simulation.ball_flight import BallFlightDynamics, BallFlightState
from src.golf_simulation.clubs import ClubBag
from src.golf_simulation.course import GolfHole, create_championship_course, create_par3_course
from src.golf_simulation.putting import GreenSurface, PuttingSimulator
from src.golf_simulation.round_simulator import MAX_STROKES_PER_HOLE, RoundSimulator
from src.golf_simulation.terrain import TerrainType


class FastBallFlightDynamics(BallFlightDynamics):
    """Deterministic low-cost flight model for round-level simulator tests."""

    def simulate(
        self,
        initial_state: BallFlightState,
        dt: float = 0.001,
        max_time: float = 15.0,
    ) -> list[BallFlightState]:
        del dt, max_time
        velocity_xy = np.asarray(initial_state.velocity[:2], dtype=float)
        horizontal_speed = float(np.linalg.norm(velocity_xy))
        if horizontal_speed <= 1e-9:
            direction = np.array([1.0, 0.0])
        else:
            direction = velocity_xy / horizontal_speed

        carry_m = max(8.0, horizontal_speed * 1.8)
        landing = np.array(initial_state.position, dtype=float)
        landing[:2] += direction * carry_m
        landing[2] = 0.0
        return [
            initial_state,
            BallFlightState(
                position=landing,
                velocity=np.array([0.0, 0.0, -0.1]),
                spin=np.zeros(3),
            ),
        ]


def _make_round_simulator(course, rng_seed: int = 42) -> RoundSimulator:
    """Build a round simulator with fast flight dynamics for round-level tests."""
    return RoundSimulator(course, ball_flight=FastBallFlightDynamics(), rng_seed=rng_seed)


class TestRoundSimulator:
    def test_simulate_par3_round(self):
        course = create_par3_course()
        sim = _make_round_simulator(course)
        result = sim.simulate_round()
        assert len(result.hole_results) == 9
        assert result.total_score > 0
        assert all(hr.score > 0 for hr in result.hole_results)

    def test_simulate_championship_round(self):
        course = create_championship_course()
        sim = _make_round_simulator(course)
        result = sim.simulate_round()
        assert len(result.hole_results) == 18
        assert result.total_par == 72
        hole_count = len(result.hole_results)
        assert result.total_score <= MAX_STROKES_PER_HOLE * hole_count

    def test_hole_results_have_shots(self):
        course = create_par3_course()
        sim = _make_round_simulator(course)
        result = sim.simulate_round()
        for hr in result.hole_results:
            assert len(hr.shots) >= 1
            assert hr.score == len(hr.shots)

    def test_custom_clubs_and_flight(self):
        course = create_par3_course()
        bag = ClubBag()
        flight = FastBallFlightDynamics()
        sim = RoundSimulator(course, club_bag=bag, ball_flight=flight, rng_seed=42)
        result = sim.simulate_round()
        assert result.total_score > 0

    def test_shot_trajectories_populated(self):
        course = create_par3_course()
        sim = _make_round_simulator(course)
        result = sim.simulate_round()
        for hr in result.hole_results:
            for shot in hr.shots:
                assert len(shot.trajectory) > 0

    def test_penalty_handling(self):
        """Simulator should handle water/OB without crashing."""
        course = create_championship_course()
        sim = _make_round_simulator(course)
        result = sim.simulate_round()
        assert result.total_score > 0

    def test_par3_score_bounds(self):
        """Par-3 course score stays within simulator stroke caps."""
        course = create_par3_course()
        sim = _make_round_simulator(course)
        result = sim.simulate_round()
        hole_count = len(result.hole_results)
        assert hole_count <= result.total_score <= MAX_STROKES_PER_HOLE * hole_count

    def test_per_hole_scores_within_cap(self):
        """Every hole score must not exceed MAX_STROKES_PER_HOLE."""
        course = create_championship_course()
        sim = _make_round_simulator(course)
        result = sim.simulate_round()
        for hr in result.hole_results:
            assert hr.score <= MAX_STROKES_PER_HOLE


class TestRoundSimulatorDeterminism:
    def test_same_seed_produces_identical_hole_scores(self):
        """Two simulators with the same seed must produce identical hole_scores."""
        course = create_par3_course()
        sim_a = _make_round_simulator(course)
        sim_b = _make_round_simulator(course)
        result_a = sim_a.simulate_round()
        result_b = sim_b.simulate_round()
        scores_a = [hr.score for hr in result_a.hole_results]
        scores_b = [hr.score for hr in result_b.hole_results]
        assert scores_a == scores_b

    def test_different_seeds_change_first_shot_endpoint(self):
        """Two simulators with different seeds should vary the first shot endpoint."""
        course = create_championship_course()
        hole = course.holes[0]
        result_42 = _make_round_simulator(course, rng_seed=42).simulate_hole(hole)
        result_99 = _make_round_simulator(course, rng_seed=99).simulate_hole(hole)
        assert result_42.shots[0].end_position != result_99.shots[0].end_position


class TestHandleShotPenalty:
    """Tests for _handle_shot_penalty (also reachable via _apply_hazard_penalty alias)."""

    def _make_sim_and_hole(self):
        course = create_par3_course()
        sim = _make_round_simulator(course)
        hole = course.holes[0]
        return sim, hole

    def test_no_penalty_on_fairway(self):
        sim, hole = self._make_sim_and_hole()
        start = hole.tee_position
        end = (50.0, 2.0, 0.0)
        result_pos, result_terrain, is_penalty = sim._handle_shot_penalty(
            start, end, TerrainType.FAIRWAY, hole
        )
        assert not is_penalty
        assert result_pos == end

    def test_water_hazard_triggers_penalty(self):
        sim, hole = self._make_sim_and_hole()
        start = (0.0, 0.0, 0.0)
        end = (200.0, 200.0, 0.0)
        _pos, _terrain, is_penalty = sim._handle_shot_penalty(start, end, TerrainType.WATER, hole)
        assert is_penalty

    def test_penalty_drop_at_80_percent_of_shot_vector(self):
        """Drop point must be at exactly 80 % of the shot vector."""
        sim, hole = self._make_sim_and_hole()
        start = (0.0, 0.0, 0.0)
        end = (100.0, 0.0, 0.0)
        drop_pos, _terrain, is_penalty = sim._handle_shot_penalty(
            start, end, TerrainType.WATER, hole
        )
        assert is_penalty
        assert drop_pos[0] == pytest.approx(80.0)
        assert drop_pos[1] == pytest.approx(0.0)

    def test_out_of_bounds_also_triggers_penalty(self):
        sim, hole = self._make_sim_and_hole()
        start = (0.0, 0.0, 0.0)
        end = (300.0, 300.0, 0.0)
        _pos, _terrain, is_penalty = sim._handle_shot_penalty(
            start, end, TerrainType.OUT_OF_BOUNDS, hole
        )
        assert is_penalty

    def test_alias_apply_hazard_penalty_agrees(self):
        """_apply_hazard_penalty is an alias; it must return the same result."""
        sim, hole = self._make_sim_and_hole()
        start = (0.0, 0.0, 0.0)
        end = (100.0, 0.0, 0.0)
        direct = sim._handle_shot_penalty(start, end, TerrainType.WATER, hole)
        via_alias = sim._apply_hazard_penalty(start, end, TerrainType.WATER, hole)
        assert direct == via_alias


class TestFindPuttStoppingPoint:
    """Tests for _find_putt_stopping_point and its _find_holed_position alias."""

    def _make_sim_and_hole(self):
        course = create_par3_course()
        sim = _make_round_simulator(course)
        hole = course.holes[0]
        return sim, hole

    def _make_putt_sim(self) -> PuttingSimulator:
        surface = GreenSurface.create_flat_green(stimp=11.0)
        return PuttingSimulator(surface=surface, dt=0.01)

    def test_trajectory_far_from_pin_returns_last_point(self):
        """A trajectory nowhere near the pin should return the final (x, y)."""
        _sim, hole = self._make_sim_and_hole()
        putt_sim = self._make_putt_sim()
        traj = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)]
        fx, fy = RoundSimulator._find_putt_stopping_point(traj, putt_sim, hole)
        assert (fx, fy) == (2.0, 0.0)

    def test_ball_at_pin_with_low_speed_is_holed(self):
        """A ball positioned right at the pin with near-zero velocity is holed."""
        _sim, hole = self._make_sim_and_hole()
        putt_sim = self._make_putt_sim()
        pin_x, pin_y = hole.pin_position[0], hole.pin_position[1]
        traj = [(pin_x, pin_y), (pin_x + 0.0001, pin_y)]
        fx, fy = RoundSimulator._find_putt_stopping_point(traj, putt_sim, hole)
        assert fx == pytest.approx(pin_x)
        assert fy == pytest.approx(pin_y)

    def test_alias_find_holed_position_agrees(self):
        """_find_holed_position is a backward-compat alias; must match."""
        _sim, hole = self._make_sim_and_hole()
        putt_sim = self._make_putt_sim()
        traj = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)]
        result_direct = RoundSimulator._find_putt_stopping_point(traj, putt_sim, hole)
        result_alias = RoundSimulator._find_holed_position(traj, putt_sim, hole)
        assert result_direct == result_alias

    def test_putt_through_pin_returns_pin(self):
        """A realistic putt that passes through the pin position is captured."""
        _sim, hole = self._make_sim_and_hole()
        putt_sim = self._make_putt_sim()
        pin_x, pin_y = hole.pin_position[0], hole.pin_position[1]
        traj = [
            (pin_x - 0.01, pin_y),
            (pin_x, pin_y),
            (pin_x + 0.0001, pin_y),
        ]
        fx, fy = RoundSimulator._find_putt_stopping_point(traj, putt_sim, hole)
        dist_to_pin = math.sqrt((fx - pin_x) ** 2 + (fy - pin_y) ** 2)
        assert dist_to_pin < 1e-6


def _uniform_terrain_hole(terrain: TerrainType) -> GolfHole:
    """Build a hole whose terrain_fn returns a single terrain everywhere."""
    return GolfHole(
        number=1,
        par=4,
        yardage=400.0,
        handicap=1,
        tee_position=(0.0, 0.0, 0.0),
        pin_position=(300.0, 0.0, 0.0),
        green_center=(300.0, 0.0, 0.0),
        green_radius=9.0,
        terrain_fn=lambda x, y: terrain,
    )


class TestBounceAndRoll:
    """Tests for _apply_bounce_and_roll terrain physics integration."""

    def _make_sim(self) -> RoundSimulator:
        return _make_round_simulator(create_par3_course(), rng_seed=7)

    def _landing_state(self) -> BallFlightState:
        # Ball arriving at the ground moving forward and downward, with backspin.
        return BallFlightState(
            position=np.array([100.0, 0.0, 0.0]),
            velocity=np.array([20.0, 0.0, -10.0]),
            spin=np.array([0.0, -200.0, 0.0]),
        )

    def test_bounce_and_roll_shifts_landing_vs_no_bounce(self):
        """Bounce/roll must move the resting point past the first touchdown."""
        sim = self._make_sim()
        hole = _uniform_terrain_hole(TerrainType.FAIRWAY)
        landing = self._landing_state()
        resting, extra, _terrain = sim._apply_bounce_and_roll(landing, hole)
        # No-bounce resting position would be the touchdown x (100.0).
        assert resting[0] > float(landing.position[0]) + 1.0
        assert len(extra) > 0
        assert resting[2] == pytest.approx(0.0)

    def test_fairway_rolls_farther_than_bunker(self):
        """Identical landing rolls out farther on fairway than in a bunker."""
        sim = self._make_sim()
        fairway_rest, _f_extra, _ft = sim._apply_bounce_and_roll(
            self._landing_state(), _uniform_terrain_hole(TerrainType.FAIRWAY)
        )
        bunker_rest, _b_extra, _bt = sim._apply_bounce_and_roll(
            self._landing_state(), _uniform_terrain_hole(TerrainType.BUNKER)
        )
        touchdown_x = float(self._landing_state().position[0])
        fairway_rollout = fairway_rest[0] - touchdown_x
        bunker_rollout = bunker_rest[0] - touchdown_x
        assert fairway_rollout > bunker_rollout

    def test_deep_rough_carries_shorter_than_fairway(self):
        """A shot from deep rough must carry shorter than from fairway."""
        course = create_par3_course()
        club = ClubBag().select_club(150.0, TerrainType.FAIRWAY)

        fairway_hole = _uniform_terrain_hole(TerrainType.FAIRWAY)
        rough_hole = _uniform_terrain_hole(TerrainType.DEEP_ROUGH)
        start = (0.0, 0.0, 0.0)

        sim_fw = _make_round_simulator(course, rng_seed=123)
        sim_dr = _make_round_simulator(course, rng_seed=123)
        fairway_shot = sim_fw._simulate_shot(start, fairway_hole, club)
        rough_shot = sim_dr._simulate_shot(start, rough_hole, club)
        assert rough_shot.distance_yards < fairway_shot.distance_yards

    def test_terrain_at_rest_is_resolved_from_resting_point(self):
        """Resting terrain reflects the post-rollout position."""
        sim = self._make_sim()
        hole = _uniform_terrain_hole(TerrainType.GREEN)
        resting, _extra, terrain = sim._apply_bounce_and_roll(self._landing_state(), hole)
        assert terrain == TerrainType.GREEN
        assert resting[2] == pytest.approx(0.0)
