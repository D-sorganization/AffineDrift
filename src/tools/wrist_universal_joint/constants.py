"""Physical constants and configuration for the Wrist Universal Joint model.

This module centralizes all physical constants, default values, and
configuration parameters used throughout the wrist universal joint
torque transmission model.
"""

from __future__ import annotations

import logging

import numpy as np

from src.core.constants import EPSILON  # noqa: F401 -- re-exported for backward compat

logger = logging.getLogger(__name__)

# Random seed for reproducibility
# Set to None for non-reproducible random behavior, or an integer for reproducibility
# Reference: Essential for scientific reproducibility per AGENTS.md guidelines
RANDOM_SEED: int | None = 42

# Create random number generator with controlled seed
rng = np.random.default_rng(RANDOM_SEED)

# Default golf club properties
DEFAULT_CLUBHEAD_WEIGHT: float = 200.0  # grams
DEFAULT_SHAFT_WEIGHT: float = 100.0  # grams
DEFAULT_CLUB_LENGTH: float = 1.0  # meters
DEFAULT_CLUBHEAD_CG_DISTANCE: float = 0.85  # meters

# Maximum wrist angle before singularity protection (degrees)
MAX_DELTA_DEGREES: float = 89.0

# Default time array length for signal generation
DEFAULT_SIGNAL_LENGTH: int = 500

# Legacy demo-model ratio between gamma- and alpha-axis inertia.
# This remains the default for backward compatibility, but callers should
# override it with measured club-specific data whenever available.
DEFAULT_GAMMA_TO_ALPHA_RATIO: float = 0.5
