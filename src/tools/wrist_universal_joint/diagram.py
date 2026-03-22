"""Anatomical diagram drawing functions for the Wrist Universal Joint model.

This module contains the forearm-hand-club diagram rendering:
- Club shaft and clubhead
- Hand and fingers
- Forearm
- Wrist joint marker
- Grip angle and wrist angle arcs
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, cast

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.patches import Ellipse, Polygon

from src.core.contracts import check_range

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


def _draw_club_shaft(ax: Any, wrist_x: float, wrist_y: float, shaft_length: float) -> float:
    """Draw the horizontal club shaft and return the shaft end X-coordinate."""
    shaft_end_x = wrist_x - shaft_length
    ax.plot(
        [shaft_end_x, wrist_x],
        [wrist_y, wrist_y],
        "k-",
        linewidth=8,
        solid_capstyle="round",
        label="Club Shaft",
        zorder=3,
    )
    return shaft_end_x


def _draw_clubhead(ax: Any, base_x: float, base_y: float) -> None:
    """Draw the tilted trapezoid clubhead at the shaft end."""
    width_bottom = 0.08 / 3
    width_top = 0.08 * 4 / 3
    height = 0.24
    angle_rad = np.radians(30)

    corners = np.array(
        [
            [-width_bottom / 2, 0],
            [width_bottom / 2, 0],
            [width_top / 2, height],
            [-width_top / 2, height],
        ]
    )

    cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)
    rotation = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
    rotated = corners @ rotation.T
    rotated[:, 0] += base_x
    rotated[:, 1] += base_y

    ax.add_patch(
        Polygon(
            rotated,
            facecolor="silver",
            alpha=0.9,
            edgecolor="gray",
            linewidth=2,
            zorder=4,
        )
    )


def _draw_hand(
    ax: Any,
    wrist_x: float,
    wrist_y: float,
    hand_length: float,
    theta_grip_rad: float,
) -> None:
    """Draw the hand ellipse at the wrist position."""
    ax.add_patch(
        Ellipse(
            (wrist_x, wrist_y),
            hand_length,
            0.12,
            angle=np.degrees(theta_grip_rad),
            facecolor="tan",
            alpha=0.8,
            edgecolor="saddlebrown",
            linewidth=2,
            zorder=6,
        )
    )


def _draw_wrist_joint(ax: Any, wrist_x: float, wrist_y: float) -> None:
    """Draw the wrist joint marker and label."""
    ax.plot(wrist_x, wrist_y, "ko", markersize=12, zorder=10)
    ax.text(
        wrist_x,
        wrist_y - 0.1,
        "Wrist Joint",
        ha="center",
        fontsize=10,
        fontweight="bold",
        zorder=11,
    )


def _draw_fingers(
    ax: Any,
    hand_center_x: float,
    hand_center_y: float,
    hand_dir_x: float,
    hand_dir_y: float,
) -> None:
    """Draw 4 fingers on the hand."""
    finger_length = 0.12
    finger_width = 0.015
    finger_dir_x = -hand_dir_x
    finger_dir_y = -hand_dir_y

    perp_to_hand_x = -hand_dir_y
    perp_to_hand_y = hand_dir_x
    finger_spacing = 0.03
    finger_positions = [-1.2, -0.4, 0.4, 1.2]

    for pos in finger_positions:
        base_x = hand_center_x + pos * finger_spacing * perp_to_hand_x
        base_y = hand_center_y + pos * finger_spacing * perp_to_hand_y
        tip_x = base_x + finger_length * finger_dir_x
        tip_y = base_y + finger_length * finger_dir_y
        finger_mid_x = (base_x + tip_x) / 2
        finger_mid_y = (base_y + tip_y) / 2
        finger_angle = np.rad2deg(np.arctan2(finger_dir_y, finger_dir_x))
        finger = Ellipse(
            (finger_mid_x, finger_mid_y),
            finger_length,
            finger_width,
            angle=finger_angle,
            facecolor="tan",
            alpha=0.9,
            edgecolor="saddlebrown",
            linewidth=1,
            zorder=7,
        )
        ax.add_patch(finger)


def _draw_forearm(
    ax: Any,
    wrist_x: float,
    wrist_y: float,
    hand_length: float,
    hand_dir_x: float,
    hand_dir_y: float,
    theta_grip_rad: float,
    phi_wrist_rad: float,
) -> None:
    """Draw the forearm attached to the hand."""
    forearm_angle_rad = theta_grip_rad + phi_wrist_rad + np.pi
    forearm_length = 0.35
    forearm_width = 0.1

    hand_endpoint_forearm_x = wrist_x + (hand_length / 2) * hand_dir_x
    hand_endpoint_forearm_y = wrist_y + (hand_length / 2) * hand_dir_y

    forearm_dir_x = np.cos(forearm_angle_rad)
    forearm_dir_y = np.sin(forearm_angle_rad)
    forearm_center_x = hand_endpoint_forearm_x - (forearm_length / 2) * forearm_dir_x
    forearm_center_y = hand_endpoint_forearm_y - (forearm_length / 2) * forearm_dir_y

    forearm = Ellipse(
        (forearm_center_x, forearm_center_y),
        forearm_length,
        forearm_width,
        angle=np.degrees(forearm_angle_rad),
        facecolor="tan",
        alpha=0.8,
        edgecolor="saddlebrown",
        linewidth=2,
        zorder=5,
    )
    ax.add_patch(forearm)


def _draw_arc_arrows(
    ax: Any,
    center_x: float,
    center_y: float,
    radius: float,
    theta_grip_rad: float,
) -> None:
    """Draw two annotation arrows for a grip-angle arc: baseline and rotated."""
    ax.arrow(
        center_x, center_y, radius, 0,
        head_width=0.012, head_length=0.018, fc="k", ec="k", linewidth=2, zorder=8,
    )
    ax.arrow(
        center_x, center_y,
        radius * np.cos(theta_grip_rad), radius * np.sin(theta_grip_rad),
        head_width=0.012, head_length=0.018, fc="r", ec="r", linewidth=2, zorder=8,
    )


def _draw_grip_angle_arc(
    ax: Any,
    wrist_x: float,
    wrist_y: float,
    theta_grip_rad: float,
) -> None:
    """Draw the grip angle arc annotation."""
    arc_center_x = wrist_x - 0.05
    arc_center_y = wrist_y
    arc_radius = 0.12
    arc_theta = np.linspace(0, theta_grip_rad, 30)
    arc_x = cast("np.ndarray[Any, Any]", arc_center_x + arc_radius * np.cos(arc_theta))
    arc_y = cast("np.ndarray[Any, Any]", arc_center_y + arc_radius * np.sin(arc_theta))
    ax.plot(arc_x, arc_y, "g-", linewidth=2.5, zorder=8)
    _draw_arc_arrows(ax, arc_center_x, arc_center_y, arc_radius, theta_grip_rad)
    label_x = arc_center_x + arc_radius * np.cos(theta_grip_rad / 2) * 0.7
    label_y = arc_center_y + arc_radius * np.sin(theta_grip_rad / 2) * 0.7
    ax.text(
        label_x, label_y + 0.02, r"$\theta_{grip}$",
        color="g", fontsize=13, ha="center", fontweight="bold", zorder=9,
    )


def _draw_wrist_arrows(
    ax: Any,
    center_x: float,
    center_y: float,
    radius: float,
    hand_axis_angle: float,
    forearm_axis_angle: float,
) -> None:
    """Draw two annotation arrows for the wrist deviation arc."""
    ax.arrow(
        center_x, center_y,
        radius * np.cos(hand_axis_angle), radius * np.sin(hand_axis_angle),
        head_width=0.012, head_length=0.018, fc="r", ec="r", linewidth=2, zorder=8,
    )
    ax.arrow(
        center_x, center_y,
        radius * np.cos(forearm_axis_angle), radius * np.sin(forearm_axis_angle),
        head_width=0.012, head_length=0.018, fc="b", ec="b", linewidth=2, zorder=8,
    )


def _draw_wrist_angle_arc(
    ax: Any,
    wrist_arc_center_x: float,
    wrist_arc_center_y: float,
    theta_grip_rad: float,
    phi_wrist_rad: float,
) -> None:
    """Draw the wrist deviation angle arc annotation."""
    center_x = wrist_arc_center_x - 0.05
    center_y = wrist_arc_center_y
    radius = 0.12
    hand_axis_angle = theta_grip_rad
    forearm_axis_angle = theta_grip_rad + phi_wrist_rad
    wrist_arc_theta = np.linspace(hand_axis_angle, forearm_axis_angle, 30)
    w_arc_x = cast("np.ndarray[Any, Any]", center_x + radius * np.cos(wrist_arc_theta))
    w_arc_y = cast("np.ndarray[Any, Any]", center_y + radius * np.sin(wrist_arc_theta))
    ax.plot(w_arc_x, w_arc_y, "b-", linewidth=2.5, alpha=0.8, zorder=8)
    _draw_wrist_arrows(ax, center_x, center_y, radius, hand_axis_angle, forearm_axis_angle)
    phi_mid = (hand_axis_angle + forearm_axis_angle) / 2
    phi_label_x = center_x + radius * np.cos(phi_mid) * 0.7
    phi_label_y = center_y + radius * np.sin(phi_mid) * 0.7
    ax.text(
        phi_label_x, phi_label_y + 0.02, r"$\phi$",
        color="b", fontsize=13, ha="center", fontweight="bold", zorder=9,
    )


def _setup_diagram_axes(ax: Any) -> None:
    """Configure final axis limits, aspect, and title for the diagram."""
    ax.set_xlim(-1.5, 0.8)
    ax.set_ylim(-0.2, 1.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Forearm-Hand-Club Diagram", fontsize=12, fontweight="bold", pad=20)


# Cache figure generation to prevent expensive redraws
# Limit entries to prevent OOM when sliding through many angles
@st.cache_resource(max_entries=20)  # type: ignore[untyped-decorator]
def draw_diagram(
    grip_angle_deg: float,
    wrist_angle_deg: float,
) -> Figure:
    """Draw the forearm-hand-club diagram.

    This coordinator delegates rendering to focused helper functions.

    Args:
        grip_angle_deg: Grip angle in degrees [0, 90].
        wrist_angle_deg: Wrist deviation angle in degrees [-60, 60].

    Returns:
        Matplotlib Figure with the rendered diagram.
    """
    check_range(grip_angle_deg, 0, 90, "grip_angle_deg")
    check_range(wrist_angle_deg, -60, 60, "wrist_angle_deg")
    fig, ax = plt.subplots(figsize=(12, 4))

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
        ax, wrist_x, wrist_y, hand_length, hand_dir_x, hand_dir_y, theta_grip_rad, phi_wrist_rad
    )
    _draw_wrist_joint(ax, wrist_x, wrist_y)
    _draw_grip_angle_arc(ax, wrist_x, wrist_y, theta_grip_rad)
    forearm_x = wrist_x + (hand_length / 2) * hand_dir_x
    forearm_y = wrist_y + (hand_length / 2) * hand_dir_y
    _draw_wrist_angle_arc(ax, forearm_x, forearm_y, theta_grip_rad, phi_wrist_rad)
    _setup_diagram_axes(ax)
    plt.tight_layout()
    return fig
