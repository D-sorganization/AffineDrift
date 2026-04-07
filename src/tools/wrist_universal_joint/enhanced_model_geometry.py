"""Geometry helpers for the enhanced wrist universal joint Qt app.

This module centralizes the anatomical diagram composition logic so the
Qt canvas only coordinates figure lifecycle and redraws.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from .diagram import (
    _draw_club_shaft,
    _draw_clubhead,
    _draw_fingers,
    _draw_forearm,
    _draw_grip_angle_arc,
    _draw_hand,
    _draw_wrist_angle_arc,
    _draw_wrist_joint,
    _setup_diagram_axes,
)


def draw_enhanced_model_diagram(
    ax: Any,
    grip_angle_deg: float,
    wrist_angle_deg: float,
) -> None:
    """Render the enhanced wrist-model diagram onto an existing axes."""
    theta_grip_rad = np.radians(grip_angle_deg)
    phi_wrist_rad = np.radians(wrist_angle_deg)
    wrist_x, wrist_y = 0.4, 0.5
    hand_length = 0.2
    hand_dir_x = np.cos(theta_grip_rad)
    hand_dir_y = np.sin(theta_grip_rad)

    shaft_end_x = _draw_club_shaft(ax, wrist_x, wrist_y, shaft_length=1.05)
    _draw_clubhead(ax, shaft_end_x, wrist_y)
    _draw_hand(ax, wrist_x, wrist_y, hand_length, theta_grip_rad)
    _draw_fingers(ax, wrist_x, wrist_y, hand_dir_x, hand_dir_y)
    _draw_forearm(
        ax,
        wrist_x,
        wrist_y,
        hand_length,
        hand_dir_x,
        hand_dir_y,
        theta_grip_rad,
        phi_wrist_rad,
    )
    _draw_wrist_joint(ax, wrist_x, wrist_y)
    _draw_grip_angle_arc(ax, wrist_x, wrist_y, theta_grip_rad)

    forearm_anchor_x = wrist_x + (hand_length / 2) * hand_dir_x
    forearm_anchor_y = wrist_y + (hand_length / 2) * hand_dir_y
    _draw_wrist_angle_arc(
        ax,
        forearm_anchor_x,
        forearm_anchor_y,
        theta_grip_rad,
        phi_wrist_rad,
    )
    _setup_diagram_axes(ax)
