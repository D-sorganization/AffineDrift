"""Enhanced Wrist Universal Joint Model - thin Qt launcher.

The heavy GUI, geometry, and kinematics logic now lives in focused modules
under ``src.tools.wrist_universal_joint`` so this legacy script can remain a
stable entry point without carrying the entire application inline.
"""

from __future__ import annotations

import sys

from src.tools.wrist_universal_joint.constants import (
    DEFAULT_CLUB_LENGTH,
    DEFAULT_CLUBHEAD_CG_DISTANCE,
    DEFAULT_CLUBHEAD_WEIGHT,
    DEFAULT_SHAFT_WEIGHT,
)
from src.tools.wrist_universal_joint.qt_canvases import DiagramCanvas, PlotCanvas
from src.tools.wrist_universal_joint.qt_dialogs import DocumentationDialog
from src.tools.wrist_universal_joint.qt_widgets import (
    WheelIgnoringLineEdit,
    WheelIgnoringSlider,
)
from src.tools.wrist_universal_joint.qt_window import MainWindow, run
from src.tools.wrist_universal_joint.torque_calculator import (
    calculate_moments_of_inertia,
    distribute_torque_by_grip_angle,
    universal_joint_transmission_ratio,
)

__all__ = [
    "DEFAULT_CLUBHEAD_WEIGHT",
    "DEFAULT_SHAFT_WEIGHT",
    "DEFAULT_CLUB_LENGTH",
    "DEFAULT_CLUBHEAD_CG_DISTANCE",
    "WheelIgnoringSlider",
    "WheelIgnoringLineEdit",
    "DiagramCanvas",
    "PlotCanvas",
    "DocumentationDialog",
    "MainWindow",
    "calculate_moments_of_inertia",
    "universal_joint_transmission_ratio",
    "distribute_torque_by_grip_angle",
    "run",
]


if __name__ == "__main__":
    sys.exit(run())
