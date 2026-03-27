use serde::{Deserialize, Serialize};

/// State of a golf ball in flight.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BallFlightState {
    pub position: [f64; 3], // x, y, z (meters)
    pub velocity: [f64; 3], // vx, vy, vz (m/s)
    pub spin: [f64; 3],     // wx, wy, wz (rad/s)
}

/// Physical parameters governing ball flight.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BallFlightParams {
    pub mass: f64,     // kg (0.04593)
    pub radius: f64,   // m (0.02135)
    pub area: f64,     // cross-section area (pi*r^2)
    pub rho: f64,      // air density kg/m^3 (1.225)
    pub cd: f64,       // drag coefficient (~0.25)
    pub cl: f64,       // lift coefficient (~0.15)
    pub gravity: f64,  // 9.81
    pub wind: [f64; 3], // wind vector m/s
}

/// Derivatives of the ball flight state for RK4 integration.
#[derive(Clone, Debug)]
pub struct BallFlightDerivatives {
    pub d_position: [f64; 3],
    pub d_velocity: [f64; 3],
    pub d_spin: [f64; 3],
}

const SPIN_DECAY_RATE: f64 = 0.05;

impl BallFlightParams {
    /// Create default parameters for a standard golf ball in standard atmosphere.
    pub fn default_params() -> Self {
        let radius = 0.02135;
        BallFlightParams {
            mass: 0.04593,
            radius,
            area: std::f64::consts::PI * radius * radius,
            rho: 1.225,
            cd: 0.23,
            cl: 0.54,
            gravity: 9.81,
            wind: [0.0, 0.0, 0.0],
        }
    }

    /// Validate that all parameters are physically reasonable.
    pub fn validate(&self) -> Result<(), String> {
        if self.mass <= 0.0 {
            return Err("Mass must be positive".into());
        }
        if self.radius <= 0.0 {
            return Err("Radius must be positive".into());
        }
        if self.area <= 0.0 {
            return Err("Area must be positive".into());
        }
        if self.rho < 0.0 {
            return Err("Air density must be non-negative".into());
        }
        if self.cd < 0.0 {
            return Err("Drag coefficient must be non-negative".into());
        }
        if self.cl < 0.0 {
            return Err("Lift coefficient must be non-negative".into());
        }
        if self.gravity <= 0.0 {
            return Err("Gravity must be positive".into());
        }
        Ok(())
    }
}

fn vec3_add(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
}

fn vec3_sub(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}

fn vec3_scale(a: [f64; 3], s: f64) -> [f64; 3] {
    [a[0] * s, a[1] * s, a[2] * s]
}

fn vec3_mag(a: [f64; 3]) -> f64 {
    (a[0] * a[0] + a[1] * a[1] + a[2] * a[2]).sqrt()
}

fn vec3_cross(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}

/// Compute the derivatives of position, velocity, and spin for the given state.
pub fn compute_derivatives(
    state: &BallFlightState,
    params: &BallFlightParams,
) -> BallFlightDerivatives {
    let v_rel = vec3_sub(state.velocity, params.wind);
    let v_rel_mag = vec3_mag(v_rel);

    // Gravity: F_g = [0, 0, -mass * g]
    let f_gravity = [0.0, 0.0, -params.mass * params.gravity];

    // Drag: F_d = -0.5 * rho * cd * A * |v_rel| * v_rel
    let f_drag = if v_rel_mag > 1e-10 {
        vec3_scale(v_rel, -0.5 * params.rho * params.cd * params.area * v_rel_mag)
    } else {
        [0.0, 0.0, 0.0]
    };

    // Magnus (lift) via Kutta-Joukowski for a spinning sphere with dimple
    // enhancement.  Base formula: F = (4/3)*pi*r^3*rho*(spin x v).
    // The cl parameter scales this for dimple-enhanced lift (golf balls
    // see ~2-3x the lift of a smooth sphere due to turbulent boundary
    // layer effects).  Direction comes from spin x v_rel.
    let f_magnus = if v_rel_mag > 1e-10 {
        let spin_cross_v = vec3_cross(state.spin, v_rel);
        let spin_cross_v_mag = vec3_mag(spin_cross_v);
        if spin_cross_v_mag > 1e-10 {
            let kj_coeff = params.cl
                * (4.0 / 3.0)
                * std::f64::consts::PI
                * params.radius.powi(3)
                * params.rho;
            vec3_scale(spin_cross_v, kj_coeff)
        } else {
            [0.0, 0.0, 0.0]
        }
    } else {
        [0.0, 0.0, 0.0]
    };

    // Total force -> acceleration
    let f_total = vec3_add(vec3_add(f_gravity, f_drag), f_magnus);
    let acceleration = vec3_scale(f_total, 1.0 / params.mass);

    // Spin decay: dspin/dt = -spin_decay_rate * spin
    let d_spin = vec3_scale(state.spin, -SPIN_DECAY_RATE);

    BallFlightDerivatives {
        d_position: state.velocity,
        d_velocity: acceleration,
        d_spin,
    }
}

/// Apply state derivatives scaled by dt to produce a new state.
fn apply_derivatives(
    state: &BallFlightState,
    deriv: &BallFlightDerivatives,
    dt: f64,
) -> BallFlightState {
    BallFlightState {
        position: vec3_add(state.position, vec3_scale(deriv.d_position, dt)),
        velocity: vec3_add(state.velocity, vec3_scale(deriv.d_velocity, dt)),
        spin: vec3_add(state.spin, vec3_scale(deriv.d_spin, dt)),
    }
}

/// Perform a single RK4 integration step.
pub fn rk4_step(
    state: &BallFlightState,
    params: &BallFlightParams,
    dt: f64,
) -> BallFlightState {
    assert!(dt > 0.0, "Time step dt must be positive");

    let k1 = compute_derivatives(state, params);

    let state2 = apply_derivatives(state, &k1, dt * 0.5);
    let k2 = compute_derivatives(&state2, params);

    let state3 = apply_derivatives(state, &k2, dt * 0.5);
    let k3 = compute_derivatives(&state3, params);

    let state4 = apply_derivatives(state, &k3, dt);
    let k4 = compute_derivatives(&state4, params);

    // Combine: y_{n+1} = y_n + (dt/6)(k1 + 2*k2 + 2*k3 + k4)
    let sixth_dt = dt / 6.0;
    BallFlightState {
        position: vec3_add(
            state.position,
            vec3_scale(
                vec3_add(
                    vec3_add(k1.d_position, vec3_scale(k2.d_position, 2.0)),
                    vec3_add(vec3_scale(k3.d_position, 2.0), k4.d_position),
                ),
                sixth_dt,
            ),
        ),
        velocity: vec3_add(
            state.velocity,
            vec3_scale(
                vec3_add(
                    vec3_add(k1.d_velocity, vec3_scale(k2.d_velocity, 2.0)),
                    vec3_add(vec3_scale(k3.d_velocity, 2.0), k4.d_velocity),
                ),
                sixth_dt,
            ),
        ),
        spin: vec3_add(
            state.spin,
            vec3_scale(
                vec3_add(
                    vec3_add(k1.d_spin, vec3_scale(k2.d_spin, 2.0)),
                    vec3_add(vec3_scale(k3.d_spin, 2.0), k4.d_spin),
                ),
                sixth_dt,
            ),
        ),
    }
}

/// Simulate a full trajectory until the ball hits the ground (z <= 0) or max_time is reached.
///
/// Returns a vector of states at each timestep including the initial state.
pub fn simulate_trajectory(
    initial: &BallFlightState,
    params: &BallFlightParams,
    dt: f64,
    max_time: f64,
) -> Vec<BallFlightState> {
    assert!(dt > 0.0, "Time step dt must be positive");
    assert!(max_time > 0.0, "Max time must be positive");
    params.validate().expect("Invalid ball flight parameters");

    let mut trajectory = vec![initial.clone()];
    let mut current = initial.clone();
    let mut t = 0.0;

    while t < max_time {
        current = rk4_step(&current, params, dt);
        t += dt;

        // Check if ball has hit the ground
        if current.position[2] <= 0.0 && t > dt {
            // Clamp z to 0
            current.position[2] = 0.0;
            trajectory.push(current);
            break;
        }

        trajectory.push(current.clone());
    }

    trajectory
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_driver_shot_carry_distance() {
        // Typical driver: ~70 m/s ball speed, ~12 deg launch, ~2700 rpm backspin
        let launch_angle_rad = 12.0_f64.to_radians();
        let ball_speed = 70.0;
        let backspin_rpm = 2700.0;
        let backspin_rad_s = backspin_rpm * 2.0 * std::f64::consts::PI / 60.0;

        let initial = BallFlightState {
            position: [0.0, 0.0, 0.0],
            velocity: [
                ball_speed * launch_angle_rad.cos(),
                0.0,
                ball_speed * launch_angle_rad.sin(),
            ],
            // Backspin: negative y-rotation so cross(spin, v) yields positive z (lift)
            spin: [0.0, -backspin_rad_s, 0.0],
        };
        let params = BallFlightParams::default_params();

        let trajectory = simulate_trajectory(&initial, &params, 0.001, 30.0);
        let last = trajectory.last().unwrap();
        let carry = last.position[0];

        // A driver shot should carry roughly 150-300 meters
        assert!(
            carry > 150.0 && carry < 300.0,
            "Driver carry was {} m, expected 150-300 m",
            carry
        );
    }

    #[test]
    fn test_driver_shot_apex() {
        let launch_angle_rad = 12.0_f64.to_radians();
        let ball_speed = 70.0;
        let backspin_rpm = 2700.0;
        let backspin_rad_s = backspin_rpm * 2.0 * std::f64::consts::PI / 60.0;

        let initial = BallFlightState {
            position: [0.0, 0.0, 0.0],
            velocity: [
                ball_speed * launch_angle_rad.cos(),
                0.0,
                ball_speed * launch_angle_rad.sin(),
            ],
            spin: [0.0, -backspin_rad_s, 0.0],
        };
        let params = BallFlightParams::default_params();
        let trajectory = simulate_trajectory(&initial, &params, 0.001, 30.0);

        let apex = trajectory
            .iter()
            .map(|s| s.position[2])
            .fold(f64::NEG_INFINITY, f64::max);

        // Apex should be roughly 15-60 meters for a driver
        assert!(
            apex > 15.0 && apex < 60.0,
            "Apex was {} m, expected ~15-60 m",
            apex
        );
    }

    #[test]
    fn test_zero_spin_no_magnus() {
        let initial = BallFlightState {
            position: [0.0, 0.0, 10.0],
            velocity: [50.0, 0.0, 10.0],
            spin: [0.0, 0.0, 0.0],
        };
        let params = BallFlightParams::default_params();

        let deriv = compute_derivatives(&initial, &params);

        // With zero spin, there should be no lateral (y) acceleration from Magnus
        // The only y-force would be if wind had y-component (it doesn't by default)
        assert!(
            deriv.d_velocity[1].abs() < 1e-10,
            "Zero spin should produce no lateral acceleration, got {}",
            deriv.d_velocity[1]
        );
    }

    #[test]
    fn test_rk4_step_positive_dt() {
        let state = BallFlightState {
            position: [0.0, 0.0, 10.0],
            velocity: [30.0, 0.0, 5.0],
            spin: [0.0, 100.0, 0.0],
        };
        let params = BallFlightParams::default_params();
        let next = rk4_step(&state, &params, 0.01);

        // Ball should move forward
        assert!(next.position[0] > state.position[0]);
    }

    #[test]
    #[should_panic(expected = "Time step dt must be positive")]
    fn test_rk4_negative_dt_panics() {
        let state = BallFlightState {
            position: [0.0, 0.0, 0.0],
            velocity: [0.0, 0.0, 0.0],
            spin: [0.0, 0.0, 0.0],
        };
        let params = BallFlightParams::default_params();
        rk4_step(&state, &params, -0.01);
    }
}
