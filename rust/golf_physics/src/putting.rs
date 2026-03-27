use serde::{Deserialize, Serialize};

/// Representation of a putting green surface with elevation control points.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct GreenSurface {
    pub width: f64,
    pub height: f64,
    pub stimp: f64,
    pub control_points: Vec<[f64; 3]>, // x, y, elevation
}

/// State of a ball rolling on the putting green.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PuttState {
    pub position: [f64; 2], // x, y on green
    pub velocity: [f64; 2], // vx, vy
}

const GRAVITY: f64 = 9.81;
const PUTT_STOP_SPEED: f64 = 0.01; // m/s

impl GreenSurface {
    /// Validate that the green surface parameters are physically reasonable.
    pub fn validate(&self) -> Result<(), String> {
        if self.width <= 0.0 {
            return Err("Green width must be positive".into());
        }
        if self.height <= 0.0 {
            return Err("Green height must be positive".into());
        }
        if self.stimp <= 0.0 {
            return Err("Stimp speed must be positive".into());
        }
        if self.control_points.is_empty() {
            return Err("At least one control point is required".into());
        }
        Ok(())
    }
}

/// Evaluate the slope (gradient) of the green surface at position (x, y).
///
/// Returns [dz/dx, dz/dy] using inverse-distance-weighted interpolation
/// of nearby control points. If fewer than 3 control points exist or
/// the point is surrounded by coincident control points, returns [0, 0].
pub fn evaluate_slope(surface: &GreenSurface, x: f64, y: f64) -> [f64; 2] {
    let pts = &surface.control_points;
    if pts.len() < 2 {
        return [0.0, 0.0];
    }

    // Use inverse-distance weighting to estimate local elevation,
    // then compute numerical gradient with small offsets.
    let eps = 0.01; // 1 cm offset for numerical differentiation

    let z_center = idw_elevation(pts, x, y);
    let z_dx = idw_elevation(pts, x + eps, y);
    let z_dy = idw_elevation(pts, x, y + eps);

    let dz_dx = (z_dx - z_center) / eps;
    let dz_dy = (z_dy - z_center) / eps;

    [dz_dx, dz_dy]
}

/// Inverse-distance-weighted interpolation of elevation from control points.
fn idw_elevation(points: &[[f64; 3]], x: f64, y: f64) -> f64 {
    let power = 2.0;
    let mut weight_sum = 0.0;
    let mut value_sum = 0.0;

    for pt in points {
        let dx = x - pt[0];
        let dy = y - pt[1];
        let dist_sq = dx * dx + dy * dy;

        if dist_sq < 1e-12 {
            // Essentially on top of this control point
            return pt[2];
        }

        let w = 1.0 / dist_sq.powf(power / 2.0);
        weight_sum += w;
        value_sum += w * pt[2];
    }

    if weight_sum > 0.0 {
        value_sum / weight_sum
    } else {
        0.0
    }
}

/// Convert stimp meter reading to friction deceleration (m/s^2).
///
/// Simplified empirical model: decel = 1.285 / stimp
pub fn stimp_to_deceleration(stimp: f64) -> f64 {
    assert!(stimp > 0.0, "Stimp must be positive, got {}", stimp);
    1.285 / stimp
}

/// Simulate a putt on the given green surface.
///
/// Returns a vector of `PuttState` snapshots at each timestep, starting with the
/// initial state. Simulation stops when the ball speed drops below threshold,
/// the ball rolls off the green, or max_time is reached.
pub fn simulate_putt(
    surface: &GreenSurface,
    initial: &PuttState,
    dt: f64,
    max_time: f64,
) -> Vec<PuttState> {
    assert!(dt > 0.0, "Time step dt must be positive");
    assert!(max_time > 0.0, "Max time must be positive");
    surface.validate().expect("Invalid green surface parameters");

    let decel = stimp_to_deceleration(surface.stimp);
    let mut trajectory = vec![initial.clone()];
    let mut current = initial.clone();
    let mut t = 0.0;

    while t < max_time {
        let speed = vec2_mag(current.velocity);

        // Check if ball has stopped
        if speed < PUTT_STOP_SPEED {
            break;
        }

        // 1. Get slope at current position
        let slope = evaluate_slope(surface, current.position[0], current.position[1]);

        // 2. Gravity component along slope: a_gravity = -g * slope_gradient
        let a_gravity = [-GRAVITY * slope[0], -GRAVITY * slope[1]];

        // 3. Friction deceleration opposing velocity: a_friction = -decel * v/|v|
        let a_friction = if speed > 1e-10 {
            [
                -decel * current.velocity[0] / speed,
                -decel * current.velocity[1] / speed,
            ]
        } else {
            [0.0, 0.0]
        };

        // 4. Update velocity: v += (a_gravity + a_friction) * dt
        current.velocity[0] += (a_gravity[0] + a_friction[0]) * dt;
        current.velocity[1] += (a_gravity[1] + a_friction[1]) * dt;

        // Check if friction has reversed the velocity direction (ball should stop)
        let new_speed = vec2_mag(current.velocity);
        if new_speed < PUTT_STOP_SPEED {
            current.velocity = [0.0, 0.0];
            trajectory.push(current);
            break;
        }

        // 5. Update position: pos += v * dt
        current.position[0] += current.velocity[0] * dt;
        current.position[1] += current.velocity[1] * dt;

        t += dt;

        // Check if ball has gone off the green
        if current.position[0] < 0.0
            || current.position[0] > surface.width
            || current.position[1] < 0.0
            || current.position[1] > surface.height
        {
            trajectory.push(current);
            break;
        }

        trajectory.push(current.clone());
    }

    trajectory
}

fn vec2_mag(v: [f64; 2]) -> f64 {
    (v[0] * v[0] + v[1] * v[1]).sqrt()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn flat_green(stimp: f64) -> GreenSurface {
        GreenSurface {
            width: 20.0,
            height: 20.0,
            stimp,
            control_points: vec![
                [0.0, 0.0, 0.0],
                [20.0, 0.0, 0.0],
                [0.0, 20.0, 0.0],
                [20.0, 20.0, 0.0],
            ],
        }
    }

    fn sloped_green(stimp: f64) -> GreenSurface {
        // Green that slopes upward in the +x direction
        GreenSurface {
            width: 20.0,
            height: 20.0,
            stimp,
            control_points: vec![
                [0.0, 0.0, 0.0],
                [20.0, 0.0, 1.0],
                [0.0, 20.0, 0.0],
                [20.0, 20.0, 1.0],
            ],
        }
    }

    #[test]
    fn test_flat_green_straight_line() {
        let surface = flat_green(10.0);
        let initial = PuttState {
            position: [10.0, 10.0],
            velocity: [2.0, 0.0],
        };

        let trajectory = simulate_putt(&surface, &initial, 0.001, 30.0);

        // On a flat green, the ball should travel in a straight line (y stays ~10.0)
        for state in &trajectory {
            assert!(
                (state.position[1] - 10.0).abs() < 0.01,
                "Ball deviated laterally on flat green: y = {}",
                state.position[1]
            );
        }
    }

    #[test]
    fn test_sloped_green_curves_ball() {
        let surface = sloped_green(10.0);
        // Putt perpendicular to the slope direction (along +y)
        let initial = PuttState {
            position: [10.0, 5.0],
            velocity: [0.0, 2.0],
        };

        let trajectory = simulate_putt(&surface, &initial, 0.001, 30.0);
        let last = trajectory.last().unwrap();

        // The slope in +x direction should pull the ball toward lower x (negative x)
        assert!(
            last.position[0] < 10.0,
            "Ball should curve downhill on sloped green, final x = {}",
            last.position[0]
        );
    }

    #[test]
    fn test_stimp_10_rolls_further_than_stimp_8() {
        let surface_10 = flat_green(10.0);
        let surface_8 = flat_green(8.0);

        let initial = PuttState {
            position: [5.0, 10.0],
            velocity: [2.0, 0.0],
        };

        let traj_10 = simulate_putt(&surface_10, &initial, 0.001, 30.0);
        let traj_8 = simulate_putt(&surface_8, &initial, 0.001, 30.0);

        let final_x_10 = traj_10.last().unwrap().position[0];
        let final_x_8 = traj_8.last().unwrap().position[0];

        assert!(
            final_x_10 > final_x_8,
            "Stimp 10 ({} m) should roll further than stimp 8 ({} m)",
            final_x_10,
            final_x_8
        );
    }

    #[test]
    fn test_stimp_to_deceleration_values() {
        let decel_10 = stimp_to_deceleration(10.0);
        let decel_8 = stimp_to_deceleration(8.0);

        // Higher stimp = less friction = lower deceleration
        assert!(decel_10 < decel_8);
        assert!(decel_10 > 0.0);
    }

    #[test]
    #[should_panic(expected = "Stimp must be positive")]
    fn test_stimp_zero_panics() {
        stimp_to_deceleration(0.0);
    }

    #[test]
    fn test_ball_stops_on_flat_green() {
        let surface = flat_green(10.0);
        let initial = PuttState {
            position: [10.0, 10.0],
            velocity: [1.0, 0.0],
        };

        let trajectory = simulate_putt(&surface, &initial, 0.001, 60.0);
        let last = trajectory.last().unwrap();

        // Ball should eventually stop
        let final_speed = vec2_mag(last.velocity);
        assert!(
            final_speed < 0.02,
            "Ball should stop, but final speed is {}",
            final_speed
        );
    }
}
