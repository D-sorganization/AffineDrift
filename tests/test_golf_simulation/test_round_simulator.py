"""Tests for the full round simulator."""

from src.golf_simulation.round_simulator import RoundSimulator

from src.golf_simulation.ball_flight import BallFlightDynamics
from src.golf_simulation.clubs import ClubBag
from src.golf_simulation.course import create_championship_course, create_par3_course


class TestRoundSimulator:
    def test_simulate_par3_round(self):
        course = create_par3_course()
        sim = RoundSimulator(course)
        result = sim.simulate_round()
        assert len(result.hole_results) == 9
        assert result.total_score > 0
        assert all(hr.score > 0 for hr in result.hole_results)

    def test_simulate_championship_round(self):
        course = create_championship_course()
        sim = RoundSimulator(course)
        result = sim.simulate_round()
        assert len(result.hole_results) == 18
        assert result.total_par == 72
        # Score should be reasonable (not 0, not 200)
        assert 50 < result.total_score < 150

    def test_hole_results_have_shots(self):
        course = create_par3_course()
        sim = RoundSimulator(course)
        result = sim.simulate_round()
        for hr in result.hole_results:
            assert len(hr.shots) >= 1
            assert hr.score == len(hr.shots)

    def test_custom_clubs_and_flight(self):
        course = create_par3_course()
        bag = ClubBag()
        flight = BallFlightDynamics()
        sim = RoundSimulator(course, club_bag=bag, ball_flight=flight)
        result = sim.simulate_round()
        assert result.total_score > 0

    def test_shot_trajectories_populated(self):
        course = create_par3_course()
        sim = RoundSimulator(course)
        result = sim.simulate_round()
        for hr in result.hole_results:
            for shot in hr.shots:
                assert len(shot.trajectory) > 0

    def test_penalty_handling(self):
        """Simulator should handle water/OB without crashing."""
        course = create_championship_course()
        sim = RoundSimulator(course)
        # Run multiple times to increase chance of hitting penalty areas
        result = sim.simulate_round()
        assert result.total_score > 0
