"""Tests for putting green simulation."""

import pytest

from src.golf_simulation.putting import (
    GreenSurface,
    PuttingSimulator,
    stimpmeter_deceleration,
)


class TestGreenSurface:
    def test_flat_green_creation(self):
        green = GreenSurface.create_flat_green(30.0, 30.0, 10.0)
        assert green.width == 30.0
        assert green.stimp == 10.0

    def test_flat_green_zero_slope(self):
        green = GreenSurface.create_flat_green(30.0, 30.0, 10.0)
        dx, dy = green.evaluate_slope(15.0, 15.0)
        assert abs(dx) < 0.01
        assert abs(dy) < 0.01

    def test_sloped_green_has_slope(self):
        green = GreenSurface.create_sloped_green(30.0, 30.0, 10.0, 0.02, 0.0)
        dx, dy = green.evaluate_slope(15.0, 15.0)
        assert abs(dx) > 0.001

    def test_is_on_green(self):
        green = GreenSurface.create_flat_green(30.0, 30.0, 10.0)
        assert green.is_on_green(15.0, 15.0)
        assert not green.is_on_green(-1.0, -1.0)

    def test_invalid_stimp_raises(self):
        with pytest.raises(ValueError):
            GreenSurface(width=30.0, height=30.0, stimp=2.0)


class TestPuttingSimulator:
    def test_stimpmeter_deceleration_uses_usga_launch_speed(self):
        deceleration = stimpmeter_deceleration(10.0)
        assert deceleration == pytest.approx(0.549, rel=0.01)

    def test_flat_stimp_10_rolls_stimpmeter_distance(self):
        green = GreenSurface.create_flat_green(20.0, 20.0, 10.0)
        sim = PuttingSimulator(green)
        positions = sim.simulate(10.0, 5.0, 0.0, 1.83, max_time=10.0)
        rollout_m = abs(positions[-1][1] - 5.0)
        assert rollout_m == pytest.approx(3.048, rel=0.03)

    def test_straight_putt_on_flat_green(self):
        green = GreenSurface.create_flat_green(30.0, 30.0, 10.0)
        sim = PuttingSimulator(green)
        positions = sim.simulate(15.0, 5.0, 0.0, 2.0)
        assert len(positions) > 1
        # Ball should travel in y direction on flat green
        final_x, final_y = positions[-1]
        assert abs(final_x - 15.0) < 0.5  # Should stay roughly straight

    def test_faster_stimp_rolls_farther(self):
        green_slow = GreenSurface.create_flat_green(40.0, 40.0, 8.0)
        green_fast = GreenSurface.create_flat_green(40.0, 40.0, 12.0)
        sim_slow = PuttingSimulator(green_slow)
        sim_fast = PuttingSimulator(green_fast)
        pos_slow = sim_slow.simulate(20.0, 5.0, 0.0, 2.0)
        pos_fast = sim_fast.simulate(20.0, 5.0, 0.0, 2.0)
        dist_slow = abs(pos_slow[-1][1] - 5.0)
        dist_fast = abs(pos_fast[-1][1] - 5.0)
        assert dist_fast > dist_slow

    def test_sloped_green_curves_putt(self):
        green = GreenSurface.create_sloped_green(30.0, 30.0, 10.0, 0.03, 0.0)
        sim = PuttingSimulator(green)
        positions = sim.simulate(15.0, 5.0, 0.0, 2.0)
        final_x = positions[-1][0]
        # Slope in x should cause ball to drift in x
        assert abs(final_x - 15.0) > 0.1

    def test_putt_stops_eventually(self):
        green = GreenSurface.create_flat_green(60.0, 60.0, 10.0)
        sim = PuttingSimulator(green)
        positions = sim.simulate(30.0, 30.0, 0.0, 3.0)
        # Check last two positions are very close (ball stopped)
        if len(positions) >= 2:
            dx = positions[-1][0] - positions[-2][0]
            dy = positions[-1][1] - positions[-2][1]
            assert abs(dx) < 0.01 and abs(dy) < 0.01


class TestHoleDetection:
    def test_ball_in_hole(self):
        green = GreenSurface.create_flat_green(30.0, 30.0, 10.0)
        sim = PuttingSimulator(green, hole_radius=0.054)
        assert sim.is_holed(15.0, 15.0, 0.0, 0.1, 15.0, 15.0)

    def test_ball_too_fast_to_hole(self):
        green = GreenSurface.create_flat_green(30.0, 30.0, 10.0)
        sim = PuttingSimulator(green, hole_radius=0.054)
        # Ball going too fast over hole
        assert not sim.is_holed(15.0, 15.0, 0.0, 5.0, 15.0, 15.0)
