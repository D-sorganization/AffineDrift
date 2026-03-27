"""Tests for golf club models and launch conditions."""

import math

from src.golf_simulation.clubs import (
    STANDARD_CLUBS,
    ClubBag,
    ClubType,
    LaunchConditions,
)
from src.golf_simulation.terrain import TerrainType


class TestGolfClub:
    def test_standard_clubs_defined(self):
        assert len(STANDARD_CLUBS) > 0

    def test_driver_has_lowest_loft(self):
        driver = next(c for c in STANDARD_CLUBS if c.club_type == ClubType.DRIVER)
        pw = next(c for c in STANDARD_CLUBS if c.club_type == ClubType.PW)
        assert driver.loft_degrees < pw.loft_degrees

    def test_club_properties_positive(self):
        for club in STANDARD_CLUBS:
            assert club.loft_degrees > 0
            assert club.length_meters > 0
            assert club.mass_kg > 0
            assert club.typical_speed_ms > 0


class TestLaunchConditions:
    def test_to_ball_flight_state(self):
        lc = LaunchConditions(
            ball_speed=70.0,
            launch_angle=math.radians(12.0),
            launch_direction=0.0,
            backspin=280.0,
            sidespin=0.0,
        )
        state = lc.to_ball_flight_state()
        assert state.position.shape == (3,)
        assert state.speed > 0
        # Horizontal speed should be majority of ball speed
        assert state.velocity[0] > state.velocity[2]


class TestClubBag:
    def test_default_bag_has_clubs(self):
        bag = ClubBag()
        assert len(bag.clubs) > 0

    def test_select_club_for_long_distance(self):
        bag = ClubBag()
        club = bag.select_club(250.0, TerrainType.TEE_BOX)
        assert club.club_type == ClubType.DRIVER

    def test_select_club_for_short_distance(self):
        bag = ClubBag()
        club = bag.select_club(30.0, TerrainType.FAIRWAY)
        # Should be a short iron or wedge
        assert club.loft_degrees > 40

    def test_get_club_by_type(self):
        bag = ClubBag()
        driver = bag.get_club(ClubType.DRIVER)
        assert driver.club_type == ClubType.DRIVER

    def test_select_club_on_green_returns_putter(self):
        bag = ClubBag()
        club = bag.select_club(20.0, TerrainType.GREEN)
        assert club.club_type == ClubType.PUTTER
