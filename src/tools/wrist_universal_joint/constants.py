"""Physical constants and configuration for the Wrist Universal Joint model.

This module centralizes all physical constants, default values, and
configuration parameters used throughout the wrist universal joint
torque transmission model.

Default club properties are derived from the PoG canonical equipment
parameter set (``src.core.constants`` POG_DRIVER_* constants, Issue #2792).
"""

from __future__ import annotations

import logging

import numpy as np

from src.core.constants import (  # noqa: F401 -- EPSILON re-exported for backward compat
    EPSILON,
    POG_DRIVER_CLUBHEAD_MASS_KG,
    POG_DRIVER_SHAFT_LENGTH_M,
    POG_DRIVER_SHAFT_MASS_KG,
    POG_L2_CM,
)

logger = logging.getLogger(__name__)

# Random seed for reproducibility
# Set to None for non-reproducible random behavior, or an integer for reproducibility
# Reference: Essential for scientific reproducibility per AGENTS.md guidelines
RANDOM_SEED: int | None = 42

# Create random number generator with controlled seed
rng = np.random.default_rng(RANDOM_SEED)

# Default golf club properties -- sourced from PoG canonical equipment parameters
# (POG_DRIVER_* in src.core.constants, Issue #2792).
# Shaft weight uses canonical 55 g (graphite driver), not the old 100 g placeholder.
DEFAULT_CLUBHEAD_WEIGHT: float = POG_DRIVER_CLUBHEAD_MASS_KG * 1000.0  # grams (= 200.0)
DEFAULT_SHAFT_WEIGHT: float = POG_DRIVER_SHAFT_MASS_KG * 1000.0  # grams (= 55.0)
DEFAULT_CLUB_LENGTH: float = POG_DRIVER_SHAFT_LENGTH_M  # meters (= 1.13)
DEFAULT_CLUBHEAD_CG_DISTANCE: float = POG_L2_CM  # meters (= 0.85)

# Maximum wrist angle before singularity protection (degrees)
MAX_DELTA_DEGREES: float = 89.0

# Default time array length for signal generation
DEFAULT_SIGNAL_LENGTH: int = 500

# Legacy demo-model ratio between gamma- and alpha-axis inertia.
# This remains the default for backward compatibility, but callers should
# override it with measured club-specific data whenever available.
DEFAULT_GAMMA_TO_ALPHA_RATIO: float = 0.5
