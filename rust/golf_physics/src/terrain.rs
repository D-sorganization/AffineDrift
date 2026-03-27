use serde::{Deserialize, Serialize};

use crate::ball_flight::BallFlightState;

/// Types of terrain on a golf course.
#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
pub enum TerrainType {
    TeeBox,
    Fairway,
    Rough,
    DeepRough,
    Bunker,
    Green,
    Water,
    OutOfBounds,
}

/// Physical properties of a terrain surface affecting ball interaction.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TerrainProperties {
    pub friction_coefficient: f64,
    pub coefficient_of_restitution: f64,
    pub spin_retention: f64,
    pub lie_quality: f64, // 0.0 = terrible, 1.0 = perfect
}

impl TerrainType {
    /// Return the physical properties for this terrain type.
    pub fn properties(&self) -> TerrainProperties {
        match self {
            TerrainType::TeeBox => TerrainProperties {
                friction_coefficient: 0.08,
                coefficient_of_restitution: 0.65,
                spin_retention: 0.75,
                lie_quality: 1.0,
            },
            TerrainType::Fairway => TerrainProperties {
                friction_coefficient: 0.10,
                coefficient_of_restitution: 0.60,
                spin_retention: 0.70,
                lie_quality: 1.0,
            },
            TerrainType::Rough => TerrainProperties {
                friction_coefficient: 0.20,
                coefficient_of_restitution: 0.40,
                spin_retention: 0.40,
                lie_quality: 0.7,
            },
            TerrainType::DeepRough => TerrainProperties {
                friction_coefficient: 0.30,
                coefficient_of_restitution: 0.30,
                spin_retention: 0.30,
                lie_quality: 0.4,
            },
            TerrainType::Bunker => TerrainProperties {
                friction_coefficient: 0.40,
                coefficient_of_restitution: 0.20,
                spin_retention: 0.20,
                lie_quality: 0.5,
            },
            TerrainType::Green => TerrainProperties {
                friction_coefficient: 0.065,
                coefficient_of_restitution: 0.50,
                spin_retention: 0.80,
                lie_quality: 1.0,
            },
            TerrainType::Water => TerrainProperties {
                friction_coefficient: 1.0,
                coefficient_of_restitution: 0.0,
                spin_retention: 0.0,
                lie_quality: 0.0,
            },
            TerrainType::OutOfBounds => TerrainProperties {
                friction_coefficient: 0.0,
                coefficient_of_restitution: 0.0,
                spin_retention: 0.0,
                lie_quality: 0.0,
            },
        }
    }
}

fn vec3_dot(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

fn vec3_scale(a: [f64; 3], s: f64) -> [f64; 3] {
    [a[0] * s, a[1] * s, a[2] * s]
}

fn vec3_add(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
}

fn vec3_sub(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}

fn vec3_mag(a: [f64; 3]) -> f64 {
    (a[0] * a[0] + a[1] * a[1] + a[2] * a[2]).sqrt()
}

/// Normalize a vector. Returns zero vector if magnitude is near zero.
fn vec3_normalize(a: [f64; 3]) -> [f64; 3] {
    let m = vec3_mag(a);
    if m < 1e-10 {
        [0.0, 0.0, 0.0]
    } else {
        vec3_scale(a, 1.0 / m)
    }
}

/// Compute the bounce of a ball off a terrain surface.
///
/// Uses the coefficient of restitution and friction to compute the post-bounce
/// velocity, and applies spin retention to reduce spin.
///
/// # Arguments
/// * `state` - The ball state at the moment of impact
/// * `terrain` - The physical properties of the terrain
/// * `surface_normal` - The outward-facing normal of the surface (should be unit length)
///
/// # Returns
/// A new `BallFlightState` representing the ball after the bounce.
pub fn compute_bounce(
    state: &BallFlightState,
    terrain: &TerrainProperties,
    surface_normal: [f64; 3],
) -> BallFlightState {
    let normal = vec3_normalize(surface_normal);
    assert!(
        vec3_mag(normal) > 0.5,
        "Surface normal must be a non-zero vector"
    );

    let v = state.velocity;

    // Decompose velocity into normal and tangential components
    let v_n_mag = vec3_dot(v, normal);
    let v_normal = vec3_scale(normal, v_n_mag);
    let v_tangential = vec3_sub(v, v_normal);

    // Apply coefficient of restitution to normal component (reflect and scale)
    let v_normal_out = vec3_scale(normal, -v_n_mag * terrain.coefficient_of_restitution);

    // Apply friction to tangential component
    let tang_speed = vec3_mag(v_tangential);
    let v_tangential_out = if tang_speed > 1e-10 {
        let friction_reduction = (1.0 - terrain.friction_coefficient).max(0.0);
        vec3_scale(v_tangential, friction_reduction)
    } else {
        [0.0, 0.0, 0.0]
    };

    let velocity_out = vec3_add(v_normal_out, v_tangential_out);

    // Apply spin retention
    let spin_out = vec3_scale(state.spin, terrain.spin_retention);

    BallFlightState {
        position: state.position,
        velocity: velocity_out,
        spin: spin_out,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_fairway_cor_less_than_one() {
        let terrain = TerrainType::Fairway.properties();
        assert!(
            terrain.coefficient_of_restitution < 1.0,
            "Fairway COR should be less than 1.0 (energy loss)"
        );
        assert!(
            terrain.coefficient_of_restitution > 0.0,
            "Fairway COR should be positive"
        );
    }

    #[test]
    fn test_bounce_reduces_speed() {
        let state = BallFlightState {
            position: [100.0, 0.0, 0.0],
            velocity: [20.0, 0.0, -10.0],
            spin: [0.0, 200.0, 0.0],
        };
        let terrain = TerrainType::Fairway.properties();
        let normal = [0.0, 0.0, 1.0];

        let bounced = compute_bounce(&state, &terrain, normal);

        // After bounce, vertical velocity should be upward and reduced
        assert!(bounced.velocity[2] > 0.0, "Ball should bounce upward");
        assert!(
            bounced.velocity[2] < 10.0,
            "Bounce should lose energy (COR < 1)"
        );
    }

    #[test]
    fn test_bounce_spin_retention() {
        let state = BallFlightState {
            position: [0.0, 0.0, 0.0],
            velocity: [10.0, 0.0, -5.0],
            spin: [0.0, 300.0, 0.0],
        };
        let terrain = TerrainType::Rough.properties();
        let normal = [0.0, 0.0, 1.0];

        let bounced = compute_bounce(&state, &terrain, normal);
        let spin_mag_before = vec3_mag(state.spin);
        let spin_mag_after = vec3_mag(bounced.spin);

        assert!(
            spin_mag_after < spin_mag_before,
            "Spin should be reduced after bounce on rough"
        );
        let expected = spin_mag_before * terrain.spin_retention;
        assert!(
            (spin_mag_after - expected).abs() < 1e-6,
            "Spin retention not applied correctly"
        );
    }

    #[test]
    fn test_terrain_properties_exist_for_all_types() {
        let types = [
            TerrainType::TeeBox,
            TerrainType::Fairway,
            TerrainType::Rough,
            TerrainType::DeepRough,
            TerrainType::Bunker,
            TerrainType::Green,
            TerrainType::Water,
            TerrainType::OutOfBounds,
        ];

        for t in &types {
            let props = t.properties();
            assert!(
                props.friction_coefficient >= 0.0,
                "{:?} friction must be >= 0",
                t
            );
            assert!(
                props.coefficient_of_restitution >= 0.0
                    && props.coefficient_of_restitution <= 1.0,
                "{:?} COR must be in [0, 1]",
                t
            );
            assert!(
                props.lie_quality >= 0.0 && props.lie_quality <= 1.0,
                "{:?} lie quality must be in [0, 1]",
                t
            );
        }
    }
}
