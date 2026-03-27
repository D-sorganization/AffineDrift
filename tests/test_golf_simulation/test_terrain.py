"""Tests for terrain types and bounce physics."""

import numpy as np

from src.golf_simulation.terrain import (
    TERRAIN_PROPERTIES,
    TerrainType,
    compute_bounce,
)


class TestTerrainType:
    def test_all_terrain_types_have_properties(self):
        for tt in TerrainType:
            assert tt in TERRAIN_PROPERTIES

    def test_fairway_better_lie_than_rough(self):
        assert TERRAIN_PROPERTIES[TerrainType.FAIRWAY].lie_quality > (
            TERRAIN_PROPERTIES[TerrainType.ROUGH].lie_quality
        )

    def test_water_is_unplayable(self):
        props = TERRAIN_PROPERTIES[TerrainType.WATER]
        assert props.lie_quality == 0.0
        assert props.coefficient_of_restitution == 0.0

    def test_cor_less_than_one(self):
        for tt in TerrainType:
            assert TERRAIN_PROPERTIES[tt].coefficient_of_restitution <= 1.0

    def test_friction_positive(self):
        for tt in TerrainType:
            assert TERRAIN_PROPERTIES[tt].friction_coefficient >= 0.0


class TestBounce:
    def test_bounce_reduces_speed(self):
        vel = np.array([30.0, 0.0, -10.0])
        spin = np.array([0.0, -200.0, 0.0])
        props = TERRAIN_PROPERTIES[TerrainType.FAIRWAY]
        normal = np.array([0.0, 0.0, 1.0])
        result_vel, result_spin = compute_bounce(vel, spin, props, normal)
        result_speed = np.linalg.norm(result_vel)
        original_speed = np.linalg.norm(vel)
        assert result_speed < original_speed

    def test_bounce_reverses_vertical(self):
        vel = np.array([30.0, 0.0, -10.0])
        spin = np.zeros(3)
        props = TERRAIN_PROPERTIES[TerrainType.FAIRWAY]
        normal = np.array([0.0, 0.0, 1.0])
        result_vel, _ = compute_bounce(vel, spin, props, normal)
        assert result_vel[2] > 0  # Vertical should be positive after bounce

    def test_bunker_absorbs_more_energy(self):
        vel = np.array([20.0, 0.0, -15.0])
        spin = np.zeros(3)
        normal = np.array([0.0, 0.0, 1.0])
        fairway_vel, _ = compute_bounce(vel, spin, TERRAIN_PROPERTIES[TerrainType.FAIRWAY], normal)
        bunker_vel, _ = compute_bounce(vel, spin, TERRAIN_PROPERTIES[TerrainType.BUNKER], normal)
        assert np.linalg.norm(bunker_vel) < np.linalg.norm(fairway_vel)
