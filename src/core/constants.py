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

Usage::

    from src.core.constants import (
        EPSILON,
        FINITE_DIFF_STEP_HESSIAN_BOUND,
        DEFAULT_DT_INIT,
    )
"""

from __future__ import annotations

# ── TOLERANCES ──────────────────────────────────────────────────────────────

EPSILON: float = 1e-6
"""General-purpose numerical stability guard (division-by-zero, etc.)."""

FINITE_DIFF_STEP_HESSIAN_BOUND: float = 1e-5
"""Finite-difference step for ``compute_hessian_bound``."""

FINITE_DIFF_STEP_HESSIAN_NORM: float = 1e-4
"""Finite-difference step for ``compute_hessian_norm``."""

FINITE_DIFF_STEP_LINEARIZE: float = 1e-6
"""Finite-difference step for numerical linearization (e.g. RobotArm)."""

# ── ALGORITHM ───────────────────────────────────────────────────────────────

DEFAULT_BASE_NOISE: float = 0.01
"""Minimum noise floor for perturbation estimation."""

DEFAULT_STATE_SCALE: float = 0.1
"""Fraction of state magnitude added as perturbation."""

DEFAULT_EPS_RESIDUAL: float = 0.01
"""Maximum acceptable residual for DDP convergence."""

DEFAULT_MAX_ITERS: int = 100
"""Maximum iterations for DDP optimisation loop."""

DEFAULT_DT_INIT: float = 0.01
"""Initial uniform timestep guess for adaptive DDP."""

DT_CLIP_MIN: float = 0.001
"""Lower bound when clipping adaptive timesteps."""

DT_CLIP_MAX: float = 0.1
"""Upper bound when clipping adaptive timesteps."""

DEFAULT_EPS_WARNING: float = 0.01
"""Residual warning threshold for ``ResidualMonitor``."""

DEFAULT_EPS_CRITICAL: float = 0.05
"""Residual critical threshold for ``ResidualMonitor``."""

DEFAULT_N_HYSTERESIS: int = 3
"""Number of consecutive samples before ``ResidualMonitor`` switches mode."""

# ── PHYSICS ─────────────────────────────────────────────────────────────────

GRAVITY_M_S2 = 9.81
"""Standard gravitational acceleration on Earth's surface (m/s^2)."""

EARTH_MU: float = 3.986e14
"""Earth's gravitational parameter mu (m^3/s^2)."""

ISS_ORBIT_RADIUS_M: float = 6_771_000.0
"""Approximate ISS circular-orbit radius (m), ~400 km altitude."""

DEFAULT_SPACECRAFT_MASS_KG: float = 100.0
"""Default chaser spacecraft mass (kg) for rendezvous examples."""

# ── DISPLAY ─────────────────────────────────────────────────────────────────

LINK_TEXT_TRUNCATE_LENGTH: int = 50
"""Maximum characters kept when truncating anchor text in health reports."""
