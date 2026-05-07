# API Reference

Public API documentation for AffineDrift's Python source modules in `src/`.

> **Note**: This is a living document. Auto-generated docstring extraction is
> tracked in Issue #3052. Until automation is in place, this reference is
> maintained manually alongside module changes.

## Module Overview

| Module | Purpose | Primary Classes/Functions |
|--------|---------|--------------------------|
| `src.affine_control` | Golf swing optimization pipeline | `SwingOptimizer`, `SwingOptimizationConfig` |
| `src.affine_control.ddp` | Differential Dynamic Programming solver | `DDPSolver`, `adaptive_timestep_ddp_mock` |
| `src.affine_control.residuals` | Residual computation for iLQR | `compute_residual`, `ResidualMonitor` |
| `src.affine_control.swing_types` | Type definitions and defaults | `SwingState`, `TrajectoryResult` |
| `src.core.constants` | Numeric constants (physics, algorithm) | Module-level constants |
| `src.core.protocols` | Abstract interfaces (DBC protocols) | `DynamicsProtocol`, `CostProtocol` |
| `src.core.contracts` | Design-by-contract utilities | `require`, `check_positive`, `check_non_negative` |
| `src.core.optimizers.ilqr_solver` | iLQR optimal control solver | `ILQRSolver` |
| `src.golf_simulation.ball_flight` | Aerodynamic ball flight model | `BallFlightModel`, `BallFlightState` |
| `src.golf_simulation.round_simulator` | Full round golf simulator | `RoundSimulator` |
| `src.tangent_models.examples` | Tangent space dynamical system examples | `DynamicalSystem`, `DoublePendulum` |
| `src.tools.check_links` | Quarto link and URL validator | `check_links()` |
| `src.tools.check_site_health` | Site health monitoring | `check_site_health()` |

---

## `src.affine_control.swing_optimizer`

### `SwingOptimizationConfig`

```python
@dataclass
class SwingOptimizationConfig:
    """Configuration for the swing optimization pipeline.

    Attributes:
        n_joints: Number of degrees of freedom in the swing model. Default: 3.
        horizon_steps: Time steps in the optimization horizon. Default: 50.
        dt: Time step duration in seconds. Default: 0.01.
        max_iterations: Maximum iLQR/DDP iterations. Default: 100.
        convergence_tol: Convergence threshold (relative cost improvement). Default: 1e-6.
        control_weight: Weight matrix R for control effort penalty. Default: eye(n_joints).
        target_velocity: Target clubhead velocity in m/s. Default: 40.0.
    """
    n_joints: int = 3
    horizon_steps: int = 50
    dt: float = 0.01
    max_iterations: int = 100
    convergence_tol: float = 1e-6
    target_velocity: float = 40.0
```

**Preconditions** (enforced at construction):
- `n_joints >= 1`
- `horizon_steps >= 2`
- `dt > 0.0`
- `convergence_tol > 0.0`
- `target_velocity > 0.0`

---

### `SwingOptimizer`

```python
class SwingOptimizer:
    """Reusable golf swing trajectory optimizer.

    Wraps a DDP or iLQR solver and exposes a configuration-driven API
    for finding optimal joint torque trajectories.
    """

    def __init__(
        self,
        config: SwingOptimizationConfig,
        ddp_solver: DDPSolverProtocol | None = None,
    ) -> None:
        """Initialize the optimizer.

        Args:
            config: Optimization configuration (see SwingOptimizationConfig).
            ddp_solver: DDP solver instance. If None, uses the adaptive
                timestep mock solver (for testing/CI).
        """

    def optimize(
        self,
        initial_state: np.ndarray,
        dynamics_fn: Callable[[np.ndarray, np.ndarray], np.ndarray],
    ) -> TrajectoryResult:
        """Run the optimization from an initial state.

        Args:
            initial_state: Initial joint positions and velocities,
                shape (2 * n_joints,).
            dynamics_fn: Discrete-time dynamics function f(x, u) -> x_next.

        Returns:
            TrajectoryResult with optimal state/control sequences and
            convergence metadata.

        Raises:
            ValueError: If initial_state has wrong shape.
            RuntimeError: If solver diverges beyond recovery.
        """
```

**Usage**:

```python
from src.affine_control.swing_optimizer import SwingOptimizationConfig, SwingOptimizer

config = SwingOptimizationConfig(n_joints=3, horizon_steps=50)
optimizer = SwingOptimizer(config)
result = optimizer.optimize(initial_state, dynamics_fn)

print(f"Converged: {result.converged}")
print(f"Final velocity: {result.final_velocity:.2f} m/s")
print(f"Iterations: {result.n_iterations}")
```

---

## `src.affine_control.ddp`

### `adaptive_timestep_ddp_mock`

```python
def adaptive_timestep_ddp_mock(
    initial_state: np.ndarray,
    target_velocity: float,
    n_joints: int,
    horizon_steps: int,
    dt: float,
    max_iterations: int,
    convergence_tol: float,
) -> DDPResult:
    """Mock DDP solver for CI and testing environments.

    Returns a plausible trajectory without running the full DDP algorithm.
    Enabled when AFFINE_DRIFT_MOCK_SOLVER=1 or no real solver is configured.

    Args:
        initial_state: Initial joint state vector.
        target_velocity: Target clubhead velocity in m/s.
        n_joints: Number of joints.
        horizon_steps: Optimization horizon length.
        dt: Time step in seconds.
        max_iterations: (Ignored in mock; included for API compatibility.)
        convergence_tol: (Ignored in mock; included for API compatibility.)

    Returns:
        DDPResult with synthesized trajectory and mock convergence data.
    """
```

### `MOCK_SOLVER_ENV_VAR`

```python
MOCK_SOLVER_ENV_VAR: str = "AFFINE_DRIFT_MOCK_SOLVER"
```

Set this environment variable to `"1"` to force mock solver usage:

```bash
export AFFINE_DRIFT_MOCK_SOLVER=1
python -m pytest tests/
```

---

## `src.core.constants`

Constants are grouped by category. Import individually:

```python
from src.core.constants import GRAVITY_M_S2, EPSILON, DEFAULT_DT_INIT
```

### Physics Constants

| Constant | Value | Units | Description |
|----------|-------|-------|-------------|
| `GRAVITY_M_S2` | `9.80665` | m/s² | Standard gravity |
| `AIR_DENSITY_SEA_LEVEL` | `1.225` | kg/m³ | Air density at sea level, 15°C |

### Tolerances

| Constant | Value | Description |
|----------|-------|-------------|
| `EPSILON` | `1e-12` | General numerical zero-threshold |
| `FINITE_DIFF_STEP_HESSIAN_BOUND` | `1e-5` | Step size for Hessian finite differences |

### Algorithm Defaults

| Constant | Value | Description |
|----------|-------|-------------|
| `DEFAULT_DT_INIT` | `0.01` | Default timestep (seconds) |
| `DEFAULT_MAX_ITER` | `100` | Default max iLQR iterations |
| `DEFAULT_CONVERGENCE_TOL` | `1e-6` | Default convergence threshold |

### Environment Variable Overrides

Algorithm constants can be overridden via environment variables with the `AD_`
prefix:

```bash
export AD_DEFAULT_MAX_ITER=200
export AD_DEFAULT_DT_INIT=0.005
```

Physics constants are **not** overridable.

---

## `src.core.contracts`

Design-by-Contract (DBC) utilities for precondition enforcement.

### `require`

```python
def require(condition: bool, message: str) -> None:
    """Assert a precondition; raise ValueError if not met.

    Args:
        condition: The precondition to check.
        message: Error message if condition is False.

    Raises:
        ValueError: If condition is False.

    Example:
        require(dt > 0.0, f"dt must be positive, got {dt}")
    """
```

### `check_positive`

```python
def check_positive(value: float, name: str) -> None:
    """Raise ValueError if value is not strictly positive.

    Args:
        value: Numeric value to check.
        name: Variable name for the error message.

    Raises:
        ValueError: If value <= 0.
    """
```

### `check_non_negative`

```python
def check_non_negative(value: float, name: str) -> None:
    """Raise ValueError if value is negative.

    Args:
        value: Numeric value to check.
        name: Variable name for the error message.

    Raises:
        ValueError: If value < 0.
    """
```

---

## `src.core.optimizers.ilqr_solver`

### `ILQRSolver`

```python
class ILQRSolver:
    """Iterative Linear Quadratic Regulator (iLQR) solver.

    Solves finite-horizon optimal control problems for nonlinear discrete-time
    systems using the iLQR algorithm with Levenberg-Marquardt regularization.
    """

    def __init__(
        self,
        cost_fn: CostProtocol,
        dynamics: DynamicsProtocol,
        max_iterations: int = 100,
        convergence_tol: float = 1e-6,
        regularization_init: float = 1e-4,
    ) -> None:
        """Initialize the iLQR solver.

        Args:
            cost_fn: Quadratic cost function (implements CostProtocol).
            dynamics: Discrete-time dynamics model (implements DynamicsProtocol).
            max_iterations: Maximum backward-forward pass iterations.
            convergence_tol: Relative cost improvement threshold for convergence.
            regularization_init: Initial Levenberg-Marquardt regularization value.
        """

    def solve(
        self,
        initial_state: np.ndarray,
        initial_controls: np.ndarray,
    ) -> ILQRResult:
        """Run iLQR from the given initial trajectory.

        Args:
            initial_state: Initial system state, shape (n_states,).
            initial_controls: Initial control sequence, shape (horizon, n_controls).

        Returns:
            ILQRResult with optimal controls, state trajectory, and metadata.

        Raises:
            ValueError: If array dimensions are incompatible.
            np.linalg.LinAlgError: If Hessian becomes singular and
                regularization cannot recover.
        """
```

---

## `src.golf_simulation.ball_flight`

### `BallFlightState`

```python
@dataclass(frozen=True)
class BallFlightState:
    """Immutable snapshot of golf ball state during flight.

    Attributes:
        position: 3D position [x, y, z] in meters. x=downrange, z=height.
        velocity: 3D velocity [vx, vy, vz] in m/s.
        spin: 3D angular velocity [wx, wy, wz] in rad/s.
    """
    position: np.ndarray  # shape (3,)
    velocity: np.ndarray  # shape (3,)
    spin: np.ndarray      # shape (3,)
```

### `BallFlightModel`

```python
class BallFlightModel(DynamicalSystem):
    """Aerodynamic golf ball flight model.

    Models drag (including Reynolds-number transition), Magnus lift,
    gravity, and wind. Compatible with the DynamicalSystem ABC for
    integration with scipy.integrate.solve_ivp.

    State vector (9D):
        [x, y, z, vx, vy, vz, wx, wy, wz]

    Control vector (3D):
        [0, 0, 0]  — no active control during flight (ballistic)
    """

    def __init__(
        self,
        ball_mass_kg: float = 0.04593,
        ball_radius_m: float = 0.02135,
        wind_ms: np.ndarray | None = None,
    ) -> None:
        """Initialize the ball flight model.

        Args:
            ball_mass_kg: Ball mass. Defaults to regulation golf ball (45.93g).
            ball_radius_m: Ball radius. Defaults to regulation radius (42.67mm diameter).
            wind_ms: 3D wind vector [wx, wy, wz] in m/s. Defaults to no wind.
        """

    def simulate(
        self,
        launch_state: BallFlightState,
        t_max: float = 10.0,
        rtol: float = 1e-6,
        atol: float = 1e-8,
    ) -> BallFlightTrajectory:
        """Simulate ball flight until landing (z <= 0) or t_max.

        Args:
            launch_state: Initial ball state at impact.
            t_max: Maximum simulation time in seconds.
            rtol: Relative tolerance for ODE integrator.
            atol: Absolute tolerance for ODE integrator.

        Returns:
            BallFlightTrajectory with position/velocity history and landing point.
        """
```

**Usage**:

```python
import numpy as np
from src.golf_simulation.ball_flight import BallFlightModel, BallFlightState

model = BallFlightModel()
launch = BallFlightState(
    position=np.array([0.0, 0.0, 0.0]),
    velocity=np.array([55.0, 0.0, 25.0]),  # ~125 mph launch, 24° angle
    spin=np.array([0.0, -300.0, 0.0]),      # 2865 rpm backspin
)
trajectory = model.simulate(launch)
print(f"Carry distance: {trajectory.carry_distance:.1f} m")
```

---

## `src.tools.check_links`

### `check_links`

```python
def check_links(
    root_dir: str = ".",
    external_only: bool = False,
    internal_only: bool = False,
    verbose: bool = False,
) -> tuple[list[str], list[str]]:
    """Validate Quarto internal references and external URLs.

    Args:
        root_dir: Repository root directory to scan.
        external_only: If True, only check external HTTP/HTTPS URLs.
        internal_only: If True, only check Quarto @sec-/@fig- references.
        verbose: Print progress to stderr.

    Returns:
        Tuple of (errors, warnings) where errors are critical (undefined
        internal references) and warnings are non-critical (external URL
        failures with retry).

    Exit behavior (when called as main):
        0: All checks passed
        1: Critical errors (undefined internal references)
        2: Warnings only (external URL failures after retries)
    """
```

---

## `src.tools.check_site_health`

### `check_site_health`

```python
def check_site_health(
    root_dir: str = ".",
    strict: bool = False,
) -> dict[str, Any]:
    """Run a comprehensive site health check.

    Checks:
    - Quarto front matter completeness
    - Navigation link consistency
    - Manifest icon references
    - SEO meta descriptions
    - Broken image references

    Args:
        root_dir: Repository root directory.
        strict: If True, treat warnings as errors.

    Returns:
        Dict with keys: 'errors', 'warnings', 'ok_count', 'check_count'.
    """
```

---

## Type Stubs

Type stubs for external dependencies (NumPy, SciPy) are provided by
`types-scipy` and `numpy` (which ships its own `py.typed` marker).
MyPy strict mode is enforced in CI — see `pyproject.toml` for the configuration.

## Adding to this Reference

When adding a new public function or class to `src/`:

1. Add a complete docstring (Args, Returns, Raises, Example).
2. Add an entry to this document in the appropriate module section.
3. Add type annotations to all parameters and the return value.
4. Add a test in `tests/test_<module>.py`.
5. Verify mypy passes: `python -m mypy src/<module>.py`.

## Cross-Repository APIs

For APIs spanning multiple repositories in the D-sorganization fleet:

- **UpstreamDrift**: Provides the canonical DDP solver and runner infrastructure.
  See [UpstreamDrift README](https://github.com/D-sorganization/UpstreamDrift).
- **Gasification_Model**: Gibbs minimization solver with provenance tracking.
- **Tools_Private**: Glass FEA exporter and GUI modules.

Cross-repository API contracts are documented in issue epics and the
[repository inventory](development/repository_inventory.md).
