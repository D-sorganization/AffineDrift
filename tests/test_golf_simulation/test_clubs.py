"""Tests for golf club models and launch conditions."""

import math

import numpy as np
import pytest

from src.core.contracts import ContractViolationError
from src.golf_simulation.ball_flight import BallFlightDynamics
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

    def test_typical_distance_yards_monotone_decreasing(self):
        """Carry distances must be strictly decreasing from driver to lob wedge (#3272)."""
        ordered = [
            ClubType.DRIVER,
            ClubType.THREE_WOOD,
            ClubType.FIVE_WOOD,
            ClubType.THREE_IRON,
            ClubType.FOUR_IRON,
            ClubType.FIVE_IRON,
            ClubType.SIX_IRON,
            ClubType.SEVEN_IRON,
            ClubType.EIGHT_IRON,
            ClubType.NINE_IRON,
            ClubType.PW,
            ClubType.GW,
            ClubType.SW,
            ClubType.LW,
        ]
        club_map = {c.club_type: c for c in STANDARD_CLUBS}
        distances = [club_map[ct].typical_distance_yards for ct in ordered]
        for i in range(len(distances) - 1):
            assert distances[i] > distances[i + 1], (
                f"{ordered[i].value} ({distances[i]:.0f} yd) should carry farther than "
                f"{ordered[i+1].value} ({distances[i+1]:.0f} yd)"
            )

    def test_typical_distance_yards_sanity(self):
        """Driver and 7-iron distances must fall in realistic ranges (#3272)."""
        club_map = {c.club_type: c for c in STANDARD_CLUBS}
        assert 180 <= club_map[ClubType.DRIVER].typical_distance_yards <= 280
        assert 130 <= club_map[ClubType.SEVEN_IRON].typical_distance_yards <= 180


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

    def test_spin_sign_convention_at_zero_direction(self):
        """At launch_direction=0, backspin must map to negative wy (#3266 #3271).

        BallFlightDynamics uses cross(spin, v_rel) for Magnus force.
        For upward lift with forward velocity (+x), spin[1] must be NEGATIVE.
        """
        lc = LaunchConditions(
            ball_speed=70.0,
            launch_angle=math.radians(10.0),
            launch_direction=0.0,
            backspin=280.0,
            sidespin=0.0,
        )
        state = lc.to_ball_flight_state()
        assert (
            pytest.approx(state.spin[1], abs=1e-9) == -280.0
        ), "backspin at launch_direction=0 must be -280 (negative wy) for upward Magnus"
        assert pytest.approx(state.spin[0], abs=1e-9) == 0.0
        assert pytest.approx(state.spin[2], abs=1e-9) == 0.0

    def test_spin_rotation_invariance(self):
        """Carry distance must be the same regardless of launch_direction (#3271)."""
        dyn = BallFlightDynamics()
        carries = []
        for direction in [0.0, math.pi / 4, math.pi / 2, math.pi]:
            lc = LaunchConditions(
                ball_speed=73.0,
                launch_angle=math.radians(10.5),
                launch_direction=direction,
                backspin=2700.0 * 2.0 * math.pi / 60.0,
                sidespin=0.0,
            )
            state = lc.to_ball_flight_state()
            traj = dyn.simulate(state)
            pos = traj[-1].position
            carry = float(np.sqrt(pos[0] ** 2 + pos[1] ** 2))
            carries.append(carry)
        # All carry distances should agree within 1 m
        assert (
            max(carries) - min(carries) < 1.0
        ), f"Carry varies by direction: {carries} — spin rotation is direction-dependent"

    def test_driver_carry_regression(self):
        """Driver via LaunchConditions must carry 150-280 m after spin fix (#3266 #3274).

        Before the fix: carry ~62 m (downward Magnus due to wrong spin sign).
        After the fix: carry ~187 m.
        """
        driver = next(c for c in STANDARD_CLUBS if c.club_type == ClubType.DRIVER)
        lc = LaunchConditions(
            ball_speed=driver.typical_speed_ms,
            launch_angle=driver.typical_launch_rad,
            launch_direction=0.0,
            backspin=driver.typical_spin_rad_s,
            sidespin=0.0,
        )
        state = lc.to_ball_flight_state()
        traj = BallFlightDynamics().simulate(state)
        carry_m = float(traj[-1].position[0])
        apex_m = max(s.position[2] for s in traj)
        assert (
            150 < carry_m < 280
        ), f"Driver carry {carry_m:.1f} m outside expected range [150, 280]"
        assert (
            apex_m > 15
        ), f"Driver apex {apex_m:.1f} m too low — Magnus force likely still inverted"


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


class TestLaunchConditionsValidation:
    """Precondition tests for LaunchConditions.__post_init__ (#3284)."""

    def test_valid_construction_succeeds(self):
        """Valid radians/m/s construction must not raise."""
        lc = LaunchConditions(
            ball_speed=70.0,
            launch_angle=math.radians(12.0),
            launch_direction=0.0,
            backspin=280.0,
            sidespin=0.0,
        )
        assert lc.ball_speed == 70.0

    def test_launch_angle_in_degrees_raises(self):
        """Passing launch_angle in degrees (e.g. 10.5) must raise — catches RPM/deg confusion."""
        with pytest.raises(ContractViolationError):
            LaunchConditions(
                ball_speed=70.0,
                launch_angle=10.5,  # degrees instead of radians
                launch_direction=0.0,
                backspin=280.0,
                sidespin=0.0,
            )

    def test_backspin_in_rpm_raises(self):
        """Passing backspin in RPM (e.g. 2700) must raise — max real spin ~1360 rad/s."""
        with pytest.raises(ContractViolationError):
            LaunchConditions(
                ball_speed=70.0,
                launch_angle=math.radians(12.0),
                launch_direction=0.0,
                backspin=2700.0,  # RPM instead of rad/s
                sidespin=0.0,
            )

    def test_ball_speed_in_mph_raises(self):
        """Passing ball_speed in mph (e.g. 160) must raise — fastest real ball ~95 m/s."""
        with pytest.raises(ContractViolationError):
            LaunchConditions(
                ball_speed=160.0,  # mph instead of m/s
                launch_angle=math.radians(12.0),
                launch_direction=0.0,
                backspin=280.0,
                sidespin=0.0,
            )
