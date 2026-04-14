pub mod ball_flight;
pub mod putting;
pub mod terrain;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use ball_flight::{BallFlightParams, BallFlightState};
use putting::{GreenSurface, PuttState};

// ─── Input validation helpers ─────────────────────────────────────────

fn require_finite(value: f64, name: &str) -> PyResult<()> {
    if value.is_nan() {
        return Err(PyValueError::new_err(format!(
            "{name} must be a finite number, got NaN"
        )));
    }
    if value.is_infinite() {
        return Err(PyValueError::new_err(format!(
            "{name} must be a finite number, got infinite"
        )));
    }
    Ok(())
}

fn require_finite_arr3(arr: [f64; 3], name: &str) -> PyResult<()> {
    for (i, &v) in arr.iter().enumerate() {
        require_finite(v, &format!("{name}[{i}]"))?;
    }
    Ok(())
}

fn require_finite_arr2(arr: [f64; 2], name: &str) -> PyResult<()> {
    for (i, &v) in arr.iter().enumerate() {
        require_finite(v, &format!("{name}[{i}]"))?;
    }
    Ok(())
}

fn require_positive(value: f64, name: &str) -> PyResult<()> {
    require_finite(value, name)?;
    if value <= 0.0 {
        return Err(PyValueError::new_err(format!(
            "{name} must be positive, got {value}"
        )));
    }
    Ok(())
}

fn require_nonnegative(value: f64, name: &str) -> PyResult<()> {
    require_finite(value, name)?;
    if value < 0.0 {
        return Err(PyValueError::new_err(format!(
            "{name} must be non-negative, got {value}"
        )));
    }
    Ok(())
}

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
    ) -> PyResult<Self> {
        require_positive(mass, "mass")?;
        require_positive(radius, "radius")?;
        if let Some(a) = area {
            require_positive(a, "area")?;
        }
        require_nonnegative(rho, "rho")?;
        require_nonnegative(cd, "cd")?;
        require_nonnegative(cl, "cl")?;
        require_positive(gravity, "gravity")?;
        require_finite_arr3(wind, "wind")?;

        let area = area.unwrap_or_else(|| std::f64::consts::PI * radius * radius);
        Ok(PyBallFlightParams {
            mass,
            radius,
            area,
            rho,
            cd,
            cl,
            gravity,
            wind,
        })
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
) -> PyResult<Vec<[f64; 3]>> {
    // DbC: validate all inputs at the Python/Rust FFI boundary before any Rust
    // internals are called.  This prevents assert!/expect() panics from reaching
    // the Python interpreter.
    require_finite_arr3(pos, "pos")?;
    require_finite_arr3(vel, "vel")?;
    require_finite_arr3(spin, "spin")?;
    require_positive(dt, "dt")?;
    require_positive(max_time, "max_time")?;

    // Validate physical parameters (params were validated at construction, but
    // re-validate here in case attributes were mutated via Python setters).
    let flight_params: BallFlightParams = params.into();
    flight_params
        .validate()
        .map_err(|msg| PyValueError::new_err(format!("invalid ball flight params: {msg}")))?;

    let initial = BallFlightState {
        position: pos,
        velocity: vel,
        spin,
    };

    let trajectory = ball_flight::simulate_trajectory(&initial, &flight_params, dt, max_time);
    Ok(trajectory.into_iter().map(|s| s.position).collect())
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
) -> PyResult<Vec<[f64; 2]>> {
    // DbC: validate all inputs at the Python/Rust FFI boundary.
    require_positive(green_width, "green_width")?;
    require_positive(green_height, "green_height")?;
    require_positive(stimp, "stimp")?;
    if control_points.is_empty() {
        return Err(PyValueError::new_err(
            "control_points must contain at least one point",
        ));
    }
    for (i, &cp) in control_points.iter().enumerate() {
        require_finite_arr3(cp, &format!("control_points[{i}]"))?;
    }
    require_finite_arr2(start_pos, "start_pos")?;
    require_finite_arr2(start_vel, "start_vel")?;
    require_positive(dt, "dt")?;
    require_positive(max_time, "max_time")?;

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
    Ok(trajectory.into_iter().map(|s| s.position).collect())
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

#[cfg(test)]
mod tests {
    use super::*;

    // ── require_finite ────────────────────────────────────────────────

    #[test]
    fn test_require_finite_ok() {
        assert!(require_finite(0.0, "x").is_ok());
        assert!(require_finite(1.5, "x").is_ok());
        assert!(require_finite(-99.9, "x").is_ok());
    }

    #[test]
    fn test_require_finite_nan_errors() {
        let err = require_finite(f64::NAN, "dt").unwrap_err();
        let msg = err.to_string();
        assert!(msg.contains("NaN"), "expected NaN in message, got: {msg}");
        assert!(msg.contains("dt"), "expected param name in message, got: {msg}");
    }

    #[test]
    fn test_require_finite_inf_errors() {
        let err = require_finite(f64::INFINITY, "max_time").unwrap_err();
        let msg = err.to_string();
        assert!(
            msg.contains("infinite"),
            "expected 'infinite' in message, got: {msg}"
        );
        assert!(
            msg.contains("max_time"),
            "expected param name in message, got: {msg}"
        );
    }

    #[test]
    fn test_require_finite_neg_inf_errors() {
        assert!(require_finite(f64::NEG_INFINITY, "x").is_err());
    }

    // ── require_positive ──────────────────────────────────────────────

    #[test]
    fn test_require_positive_ok() {
        assert!(require_positive(0.001, "dt").is_ok());
        assert!(require_positive(30.0, "max_time").is_ok());
    }

    #[test]
    fn test_require_positive_zero_errors() {
        let err = require_positive(0.0, "dt").unwrap_err();
        assert!(err.to_string().contains("dt"));
    }

    #[test]
    fn test_require_positive_negative_errors() {
        assert!(require_positive(-1.0, "dt").is_err());
    }

    #[test]
    fn test_require_positive_nan_errors() {
        assert!(require_positive(f64::NAN, "dt").is_err());
    }

    // ── require_nonnegative ───────────────────────────────────────────

    #[test]
    fn test_require_nonnegative_ok() {
        assert!(require_nonnegative(0.0, "cd").is_ok());
        assert!(require_nonnegative(0.5, "cd").is_ok());
    }

    #[test]
    fn test_require_nonnegative_negative_errors() {
        assert!(require_nonnegative(-0.1, "cd").is_err());
    }

    // ── require_finite_arr3 ───────────────────────────────────────────

    #[test]
    fn test_require_finite_arr3_ok() {
        assert!(require_finite_arr3([1.0, 2.0, 3.0], "pos").is_ok());
        assert!(require_finite_arr3([0.0, 0.0, 0.0], "spin").is_ok());
    }

    #[test]
    fn test_require_finite_arr3_nan_in_middle() {
        let err = require_finite_arr3([0.0, f64::NAN, 0.0], "vel").unwrap_err();
        let msg = err.to_string();
        assert!(msg.contains("vel[1]"), "expected index in message, got: {msg}");
    }

    #[test]
    fn test_require_finite_arr3_inf() {
        assert!(require_finite_arr3([f64::INFINITY, 0.0, 0.0], "pos").is_err());
    }

    // ── require_finite_arr2 ───────────────────────────────────────────

    #[test]
    fn test_require_finite_arr2_ok() {
        assert!(require_finite_arr2([5.0, 10.0], "start_pos").is_ok());
    }

    #[test]
    fn test_require_finite_arr2_nan_errors() {
        assert!(require_finite_arr2([f64::NAN, 0.0], "start_vel").is_err());
    }
}
