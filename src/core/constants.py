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

Reversibility
-------------
Algorithm and display constants can be overridden at runtime via
environment variables (prefixed with ``AD_``).  Physics constants are
**not** overridable -- the speed of light is not a config option.

Usage::

    from src.core.constants import (
        EPSILON,
        FINITE_DIFF_STEP_HESSIAN_BOUND,
        DEFAULT_DT_INIT,
    )
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
