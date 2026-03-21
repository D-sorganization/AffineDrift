"""Visualization functions for the Wrist Universal Joint model.

This module re-exports all visualization functions from focused sub-modules
to preserve backward-compatible import paths.

Sub-modules:
- diagram: Forearm-hand-club anatomical diagram rendering
- plots: Torque, acceleration, and transmission sweep plots
"""

from __future__ import annotations

import logging

from .diagram import draw_diagram
from .plots import plot_acceleration, plot_torque, plot_transmission_sweep

logger = logging.getLogger(__name__)

__all__ = [
    "draw_diagram",
    "plot_acceleration",
    "plot_torque",
    "plot_transmission_sweep",
]
