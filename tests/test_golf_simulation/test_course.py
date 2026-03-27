"""Tests for golf course definition."""

import pytest

from src.golf_simulation.course import (
    GolfHole,
    create_championship_course,
    create_par3_course,
)
from src.golf_simulation.terrain import TerrainType


class TestGolfHole:
    def test_distance_to_pin(self):
        hole = GolfHole(
            number=1,
            par=4,
            yardage=400.0,
            handicap=1,
            tee_position=(0.0, 0.0, 0.0),
            pin_position=(365.76, 0.0, 0.0),  # 400 yards in meters
            green_center=(365.76, 0.0, 0.0),
            green_radius=15.0,
        )
        dist = hole.distance_to_pin(0.0, 0.0)
        assert abs(dist - 365.76) < 0.01

    def test_get_terrain_near_green(self):
        hole = GolfHole(
            number=1,
            par=4,
            yardage=400.0,
            handicap=1,
            tee_position=(0.0, 0.0, 0.0),
            pin_position=(365.76, 0.0, 0.0),
            green_center=(365.76, 0.0, 0.0),
            green_radius=15.0,
        )
        terrain = hole.get_terrain(365.76, 0.0)
        assert terrain == TerrainType.GREEN


class TestGolfCourse:
    def test_par3_course_creation(self):
        course = create_par3_course()
        assert len(course.holes) == 9
        assert all(h.par == 3 for h in course.holes)

    def test_championship_course_creation(self):
        course = create_championship_course()
        assert len(course.holes) == 18
        assert course.total_par == 72

    def test_get_hole_by_number(self):
        course = create_par3_course()
        hole = course.get_hole(1)
        assert hole.number == 1

    def test_invalid_hole_number_raises(self):
        course = create_par3_course()
        with pytest.raises(Exception):
            course.get_hole(0)

    def test_total_yardage(self):
        course = create_championship_course()
        assert course.total_yardage > 5000
