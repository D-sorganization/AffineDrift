"""Tests for golf course definition."""

import pytest

from src.golf_simulation.course import (
    CHAMPIONSHIP_HANDICAPS,
    CHAMPIONSHIP_HOLE_SPECS,
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

    def test_get_terrain_near_tee_box(self):
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
        assert hole.get_terrain(2.0, 0.0) == TerrainType.TEE_BOX

    def test_get_terrain_fairway_and_rough_corridor(self):
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
        assert hole.get_terrain(180.0, 10.0) == TerrainType.FAIRWAY
        assert hole.get_terrain(180.0, 35.0) == TerrainType.ROUGH
        assert hole.get_terrain(180.0, 60.0) == TerrainType.DEEP_ROUGH

    def test_custom_terrain_function_still_overrides_heuristic(self):
        hole = GolfHole(
            number=1,
            par=4,
            yardage=400.0,
            handicap=1,
            tee_position=(0.0, 0.0, 0.0),
            pin_position=(365.76, 0.0, 0.0),
            green_center=(365.76, 0.0, 0.0),
            green_radius=15.0,
            terrain_fn=lambda _x, _y: TerrainType.BUNKER,
        )
        assert hole.get_terrain(365.76, 0.0) == TerrainType.BUNKER


class TestGolfCourse:
    def test_par3_course_creation(self):
        course = create_par3_course()
        assert len(course.holes) == 9
        assert all(h.par == 3 for h in course.holes)

    def test_championship_course_creation(self):
        course = create_championship_course()
        assert len(course.holes) == 18
        assert course.total_par == 72

    def test_championship_course_uses_declarative_specs(self):
        course = create_championship_course()
        assert [hole.number for hole in course.holes] == list(range(1, 19))
        assert [hole.par for hole in course.holes] == [
            par for par, _yardage in CHAMPIONSHIP_HOLE_SPECS
        ]
        assert [hole.yardage for hole in course.holes] == [
            yardage for _par, yardage in CHAMPIONSHIP_HOLE_SPECS
        ]
        assert [hole.handicap for hole in course.holes] == list(CHAMPIONSHIP_HANDICAPS)
        assert sorted(hole.handicap for hole in course.holes) == list(range(1, 19))

    def test_championship_course_totals_are_stable(self):
        course = create_championship_course()
        assert course.total_par == sum(par for par, _yardage in CHAMPIONSHIP_HOLE_SPECS)
        assert course.total_yardage == pytest.approx(
            sum(yardage for _par, yardage in CHAMPIONSHIP_HOLE_SPECS)
        )

    def test_get_hole_by_number(self):
        course = create_par3_course()
        hole = course.get_hole(1)
        assert hole.number == 1

    def test_invalid_hole_number_raises(self):
        course = create_par3_course()
        with pytest.raises(ValueError):
            course.get_hole(0)

    def test_total_yardage(self):
        course = create_championship_course()
        assert course.total_yardage > 5000
