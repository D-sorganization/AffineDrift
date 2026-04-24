"""Centralized numeric constants for the AffineDrift core modules.

This module collects magic numbers that were previously scattered across
``src/affine_control/`` and ``src/tangent_models/`` into named, documented
constants.  Grouping them here makes the code easier to audit, tune, and
keep consistent.

Categories
----------
TOLERANCES   -- numerical stability thresholds and finite-difference steps
ALGORITHM    -- default hyper-parameters for DDP and residual monitoring
PHYSICS      -- physical constants (gravity, orbital mechanics)
DISPLAY      -- shared UI/formatting constants
POG_DOUBLE_PENDULUM  -- canonical double-pendulum parameters (PoG Table 3.1)
POG_TRIPLE_PENDULUM  -- canonical triple-pendulum parameters (PoG Ch08)
POG_EQUIPMENT        -- canonical equipment parameters (driver, ball)
POG_SWING_TIMING     -- canonical swing timing parameters

Reversibility
-------------
Algorithm and display constants can be overridden at runtime via
environment variables (prefixed with ``AD_``).  Physics constants are
**not** overridable -- the speed of light is not a config option.
PoG canonical parameters are similarly immutable: override by passing
explicit arguments to functions, not by patching module constants.

Usage::

    from src.core.constants import (
        EPSILON,
        FINITE_DIFF_STEP_HESSIAN_BOUND,
        DEFAULT_DT_INIT,
        POG_L1, POG_M1,
        POG_DRIVER_CLUBHEAD_MASS_KG,
        POG_DOWNSWING_DURATION_S,
    )

PoG canonical parameter set (Table 3.1)
----------------------------------------
Every numerical example in Physics of Golf Ch02-Ch16 must reference these
values (or explicitly label a "Counterfactual Example Parameters" variant
with justification).  Machine-readable source of truth: data/canonical_parameters.yml.

References
----------
- De Leva (1996) PMID 8872316 — segment inertia adjustments
- Zatsiorsky (1998) Kinematics of Human Motion — rotational inertia
- USGA Equipment Rules (2024) — club/ball specifications
- MacKenzie & Sprigings (2009) Sports Engineering — shaft + club inertia
- Nesbit (2005) J Sports Sci Med 4:1-20 — downswing duration kinematics
- McTeigue et al. (1994) Golf Digest study — downswing timing
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def _env_float(key: str, default: float) -> float:
    """Read a float from the environment, falling back to *default*."""
    raw = os.environ.get(key, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(key: str, default: int) -> int:
    """Read an int from the environment, falling back to *default*."""
    raw = os.environ.get(key, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


# ── TOLERANCES ──────────────────────────────────────────────────────────────

EPSILON: float = 1e-6
"""General-purpose numerical stability guard (division-by-zero, etc.)."""

FINITE_DIFF_STEP_HESSIAN_BOUND: float = 1e-5
"""Finite-difference step for ``compute_hessian_bound``."""

FINITE_DIFF_STEP_HESSIAN_NORM: float = 1e-4
"""Finite-difference step for ``compute_hessian_norm``."""

FINITE_DIFF_STEP_LINEARIZE: float = 1e-6
"""Finite-difference step for numerical linearization (e.g. RobotArm)."""

# ── ALGORITHM (overridable via AD_* env vars) ──────────────────────────────

DEFAULT_BASE_NOISE: float = _env_float("AD_BASE_NOISE", 0.01)
"""Minimum noise floor for perturbation estimation."""

DEFAULT_STATE_SCALE: float = _env_float("AD_STATE_SCALE", 0.1)
"""Fraction of state magnitude added as perturbation."""

DEFAULT_EPS_RESIDUAL: float = _env_float("AD_EPS_RESIDUAL", 0.01)
"""Maximum acceptable residual for DDP convergence."""

DEFAULT_MAX_ITERS: int = _env_int("AD_MAX_ITERS", 100)
"""Maximum iterations for DDP optimisation loop."""

DEFAULT_DT_INIT: float = _env_float("AD_DT_INIT", 0.01)
"""Initial uniform timestep guess for adaptive DDP."""

DT_CLIP_MIN: float = _env_float("AD_DT_CLIP_MIN", 0.001)
"""Lower bound when clipping adaptive timesteps."""

DT_CLIP_MAX: float = _env_float("AD_DT_CLIP_MAX", 0.1)
"""Upper bound when clipping adaptive timesteps."""

DEFAULT_EPS_WARNING: float = _env_float("AD_EPS_WARNING", 0.01)
"""Residual warning threshold for ``ResidualMonitor``."""

DEFAULT_EPS_CRITICAL: float = _env_float("AD_EPS_CRITICAL", 0.05)
"""Residual critical threshold for ``ResidualMonitor``."""

DEFAULT_N_HYSTERESIS: int = _env_int("AD_N_HYSTERESIS", 3)
"""Number of consecutive samples before ``ResidualMonitor`` switches mode."""

# ── PHYSICS (immutable -- not configurable) ────────────────────────────────

GRAVITY_M_S2 = 9.81
"""Standard gravitational acceleration on Earth's surface (m/s^2)."""

EARTH_MU: float = 3.986e14
"""Earth's gravitational parameter mu (m^3/s^2)."""

ISS_ORBIT_RADIUS_M: float = 6_771_000.0
"""Approximate ISS circular-orbit radius (m), ~400 km altitude."""

DEFAULT_SPACECRAFT_MASS_KG: float = 100.0
"""Default chaser spacecraft mass (kg) for rendezvous examples."""

# ── DISPLAY (overridable via AD_* env vars) ────────────────────────────────

LINK_TEXT_TRUNCATE_LENGTH: int = _env_int("AD_LINK_TEXT_TRUNCATE", 50)
"""Maximum characters kept when truncating anchor text in health reports."""

# ── POG CANONICAL DOUBLE-PENDULUM PARAMETERS (PoG Table 3.1, immutable) ─────
#
# Source-of-truth for all Physics of Golf Ch02-Ch16 numerical examples.
# Link 1 = upper arm + forearm assembly; Link 2 = golf club (driver).
# Anthropometric data: 50th-percentile adult male.
# Machine-readable duplicate: data/canonical_parameters.yml
#
# References:
#   De Leva (1996) PMID 8872316 — segment lengths and CoM distances
#   Zatsiorsky (1998) Kinematics of Human Motion — rotational inertia
#   MacKenzie & Sprigings (2009) Sports Engineering — club inertia
#   USGA Equipment Rules (2024) — shaft length and total club mass

# Link 1 (upper arm + forearm assembly)
POG_L1: float = 0.60
"""Link 1 total length, shoulder to wrist (m). [De Leva 1996]"""

POG_L1_CM: float = 0.28
"""Link 1 CoM distance from shoulder joint (m). [De Leva 1996]"""

POG_M1: float = 3.5
"""Link 1 combined arm segment mass (kg). [De Leva 1996]"""

POG_I1: float = 0.075
"""Link 1 rotational inertia about CoM (kg m^2). [Zatsiorsky 1998]"""

# Link 2 (golf club -- driver)
POG_L2: float = 1.13
"""Link 2 driver shaft length, grip to clubhead (m). [USGA Equipment Rules 2024]"""

POG_L2_CM: float = 0.85
"""Link 2 CoM distance from grip end, clubhead-weighted (m). [MacKenzie & Sprigings 2009]"""

POG_M2: float = 0.310
"""Link 2 total club mass, head + shaft + grip (kg). [USGA Equipment Rules 2024]"""

POG_I2: float = 0.058
"""Link 2 rotational inertia about CoM (kg m^2). [MacKenzie & Sprigings 2009]"""

# ── POG CANONICAL TRIPLE-PENDULUM PARAMETERS (PoG Ch08, immutable) ───────────
#
# Adds a torso segment (pelvis + trunk) proximal to the arm.
# Link 0 = torso; Link 1 = arm; Link 2 = club (same as double-pendulum above).
#
# References:
#   De Leva (1996) PMID 8872316
#   Zatsiorsky (1998) Kinematics of Human Motion

POG_L0: float = 0.55
"""Torso segment length, hip to shoulder (m). [De Leva 1996]"""

POG_L0_CM: float = 0.28
"""Torso CoM distance from hip joint (m). [De Leva 1996]"""

POG_M0: float = 35.0
"""Torso segment mass, pelvis + trunk (kg). [De Leva 1996]"""

POG_I0: float = 1.80
"""Torso rotational inertia about CoM, axial (kg m^2). [Zatsiorsky 1998]"""

# ── POG CANONICAL EQUIPMENT PARAMETERS (PoG Equipment Table, immutable) ──────
#
# Driver and ball specifications for Physics of Golf impact, aerodynamic,
# and shaft chapters (Ch14, Ch17-Ch31).
#
# References:
#   USGA Equipment Rules (2024) -- ball mass/diameter, COR limit
#   MacKenzie & Sprigings (2009) Sports Engineering -- shaft parameters

POG_DRIVER_CLUBHEAD_MASS_KG: float = 0.200
"""Driver clubhead mass (kg). [USGA Equipment Rules 2024 / manufacturer typical]"""

POG_DRIVER_SHAFT_MASS_KG: float = 0.055
"""Driver shaft mass (kg), typical lightweight graphite shaft. [MacKenzie & Sprigings 2009]"""

POG_DRIVER_SHAFT_LENGTH_M: float = 1.13
"""Driver shaft length (m), USGA/tour specification. [USGA Equipment Rules 2024]"""

POG_DRIVER_SHAFT_STIFFNESS_N_M: float = 4200.0
"""Driver equivalent bending stiffness at tip (N/m). [MacKenzie & Sprigings 2009]"""

POG_DRIVER_SHAFT_DAMPING_NS_M: float = 2.5
"""Driver equivalent tip damping coefficient (N*s/m). [MacKenzie & Sprigings 2009]"""

POG_DRIVER_GRIP_MASS_KG: float = 0.055
"""Grip mass, typical rubber grip (kg). [MacKenzie & Sprigings 2009]"""

POG_BALL_MASS_KG: float = 0.04593
"""Golf ball mass (kg). USGA rule: maximum 1.620 oz = 45.93 g. [USGA Equipment Rules 2024]"""

POG_BALL_DIAMETER_M: float = 0.04267
"""Golf ball diameter (m). USGA rule: minimum 1.680 in = 42.67 mm. [USGA Equipment Rules 2024]"""

POG_BALL_COR_DRIVER: float = 0.822
"""Ball COR at driver test conditions (dimensionless).

Derived from the USGA Characteristic Time (CT) limit of 239 microseconds.
The USGA/R&A imposed a maximum COR of 0.830 in 1998; nominal value
0.822 is the modal value from tour-player driver tests.
[USGA Equipment Rules 2024; Penner 2003 Rep. Prog. Phys.]
"""

# ── POG CANONICAL SWING TIMING (immutable) ───────────────────────────────────
#
# Downswing duration declared once here.  All Physics of Golf worked examples
# use this value.  Local variants must be explicitly labeled "Counterfactual".
#
# Literature range: 200-300 ms across skilled golfers (Nesbit 2005 reports
# mean ~250 ms for scratch players; McTeigue 1994 reports 200-300 ms).
# Conservative central estimate 250 ms is adopted.  Do NOT silently substitute
# 150 ms or 200 ms in worked examples -- if a different duration is needed,
# label it explicitly.
#
# References:
#   Nesbit (2005) J Sports Sci Med 4:1-20 -- kinematic study of 4 skill levels
#   McTeigue et al. (1994) Golf Digest -- biomechanical study of tour players

POG_DOWNSWING_DURATION_S: float = 0.250
"""Canonical downswing duration (s).

Central value: 250 ms.  Literature range: 200-300 ms across skill levels
(Nesbit 2005; McTeigue 1994).  Use this value in all worked examples unless
the example is explicitly labeled as a counterfactual or sensitivity study.
"""

POG_DOWNSWING_DURATION_MIN_S: float = 0.200
"""Lower bound of literature range for downswing duration (s). [Nesbit 2005]"""

POG_DOWNSWING_DURATION_MAX_S: float = 0.300
"""Upper bound of literature range for downswing duration (s). [McTeigue 1994]"""

# ── GOLF SIMULATION PHYSICS (immutable) ──────────────────────────────────

STIMPMETER_CALIBRATION_FACTOR: float = 1.285
"""Stimpmeter deceleration calibration factor (m/s^2 per stimp-unit inverse).

The deceleration due to friction on a putting green is modelled as
``STIMPMETER_CALIBRATION_FACTOR / stimpmeter_reading``.
"""

REGULATION_HOLE_RADIUS_M: float = 0.054
"""Regulation golf hole radius in meters (4.25 inches / 2)."""

HOLE_CAPTURE_SPEED_MS: float = 1.5
"""Maximum ball speed (m/s) at which the hole can capture the ball."""
