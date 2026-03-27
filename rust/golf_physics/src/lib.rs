pub mod ball_flight;
pub mod putting;
pub mod terrain;

use pyo3::prelude::*;

use ball_flight::{BallFlightParams, BallFlightState};
use putting::{GreenSurface, PuttState};

// ─── PyO3 wrapper types ───────────────────────────────────────────────

/// Python-visible ball flight state.
#[pyclass(name = "BallFlightState")]
#[derive(Clone, Debug)]
pub struct PyBallFlightState {
    #[pyo3(get, set)]
    pub position: [f64; 3],
    #[pyo3(get, set)]
    pub velocity: [f64; 3],
    #[pyo3(get, set)]
    pub spin: [f64; 3],
}

#[pymethods]
impl PyBallFlightState {
    #[new]
    fn new(position: [f64; 3], velocity: [f64; 3], spin: [f64; 3]) -> Self {
        PyBallFlightState {
            position,
            velocity,
            spin,
        }
    }
}

/// Python-visible ball flight parameters.
#[pyclass(name = "BallFlightParams")]
#[derive(Clone, Debug)]
pub struct PyBallFlightParams {
    #[pyo3(get, set)]
    pub mass: f64,
    #[pyo3(get, set)]
    pub radius: f64,
    #[pyo3(get, set)]
    pub area: f64,
    #[pyo3(get, set)]
    pub rho: f64,
    #[pyo3(get, set)]
    pub cd: f64,
    #[pyo3(get, set)]
    pub cl: f64,
    #[pyo3(get, set)]
    pub gravity: f64,
    #[pyo3(get, set)]
    pub wind: [f64; 3],
}

#[pymethods]
impl PyBallFlightParams {
    #[new]
    #[pyo3(signature = (
        mass = 0.04593,
        radius = 0.02135,
        area = None,
        rho = 1.225,
        cd = 0.23,
        cl = 0.54,
        gravity = 9.81,
        wind = [0.0, 0.0, 0.0],
    ))]
    fn new(
        mass: f64,
        radius: f64,
        area: Option<f64>,
        rho: f64,
        cd: f64,
        cl: f64,
        gravity: f64,
        wind: [f64; 3],
    ) -> Self {
        let area = area.unwrap_or_else(|| std::f64::consts::PI * radius * radius);
        PyBallFlightParams {
            mass,
            radius,
            area,
            rho,
            cd,
            cl,
            gravity,
            wind,
        }
    }

    /// Create default parameters for a standard golf ball.
    #[staticmethod]
    fn default_params() -> Self {
        let r = 0.02135;
        PyBallFlightParams {
            mass: 0.04593,
            radius: r,
            area: std::f64::consts::PI * r * r,
            rho: 1.225,
            cd: 0.23,
            cl: 0.54,
            gravity: 9.81,
            wind: [0.0, 0.0, 0.0],
        }
    }
}

impl From<&PyBallFlightParams> for BallFlightParams {
    fn from(p: &PyBallFlightParams) -> Self {
        BallFlightParams {
            mass: p.mass,
            radius: p.radius,
            area: p.area,
            rho: p.rho,
            cd: p.cd,
            cl: p.cl,
            gravity: p.gravity,
            wind: p.wind,
        }
    }
}

// ─── Python-exposed functions ─────────────────────────────────────────

/// Simulate a ball flight trajectory and return a list of [x, y, z] positions.
///
/// # Arguments
/// * `pos` - Initial position [x, y, z] in meters
/// * `vel` - Initial velocity [vx, vy, vz] in m/s
/// * `spin` - Initial spin [wx, wy, wz] in rad/s
/// * `params` - Ball flight parameters
/// * `dt` - Time step in seconds (default 0.001)
/// * `max_time` - Maximum simulation time in seconds (default 30.0)
#[pyfunction]
#[pyo3(signature = (pos, vel, spin, params, dt = 0.001, max_time = 30.0))]
fn simulate_ball_flight(
    pos: [f64; 3],
    vel: [f64; 3],
    spin: [f64; 3],
    params: &PyBallFlightParams,
    dt: f64,
    max_time: f64,
) -> Vec<[f64; 3]> {
    let initial = BallFlightState {
        position: pos,
        velocity: vel,
        spin,
    };
    let flight_params: BallFlightParams = params.into();

    let trajectory = ball_flight::simulate_trajectory(&initial, &flight_params, dt, max_time);
    trajectory.into_iter().map(|s| s.position).collect()
}

/// Simulate a putt on a green and return a list of [x, y] positions.
///
/// # Arguments
/// * `green_width` - Width of the green in meters
/// * `green_height` - Height (depth) of the green in meters
/// * `stimp` - Stimp meter reading
/// * `control_points` - List of [x, y, elevation] control points defining the surface
/// * `start_pos` - Starting position [x, y] on the green
/// * `start_vel` - Starting velocity [vx, vy] in m/s
/// * `dt` - Time step in seconds (default 0.001)
/// * `max_time` - Maximum simulation time in seconds (default 30.0)
#[pyfunction]
#[pyo3(signature = (green_width, green_height, stimp, control_points, start_pos, start_vel, dt = 0.001, max_time = 30.0))]
fn simulate_putt_py(
    green_width: f64,
    green_height: f64,
    stimp: f64,
    control_points: Vec<[f64; 3]>,
    start_pos: [f64; 2],
    start_vel: [f64; 2],
    dt: f64,
    max_time: f64,
) -> Vec<[f64; 2]> {
    let surface = GreenSurface {
        width: green_width,
        height: green_height,
        stimp,
        control_points,
    };
    let initial = PuttState {
        position: start_pos,
        velocity: start_vel,
    };

    let trajectory = putting::simulate_putt(&surface, &initial, dt, max_time);
    trajectory.into_iter().map(|s| s.position).collect()
}

// ─── PyO3 module ──────────────────────────────────────────────────────

/// Golf physics engine implemented in Rust.
#[pymodule]
fn golf_physics(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyBallFlightState>()?;
    m.add_class::<PyBallFlightParams>()?;
    m.add_function(wrap_pyfunction!(simulate_ball_flight, m)?)?;
    m.add_function(wrap_pyfunction!(simulate_putt_py, m)?)?;
    Ok(())
}
