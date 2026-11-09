"""Clubface-roll couple projection between FSP and club-fixed frames (#5461)."""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

ILLUSTRATIVE_M_IN_PLANE_NM = -15.0
ILLUSTRATIVE_M_OUT_OF_PLANE_NM = 8.0
ILLUSTRATIVE_M_SHAFT_NM = 4.5


def rotation_fsp_to_club_about_shaft(phi_rad: float) -> NDArray[np.float64]:
    """Return R_club<-FSP(phi) from Box 2.1 / Table 2.2 (rotation about shaft axis)."""
    cos_phi = math.cos(phi_rad)
    sin_phi = math.sin(phi_rad)
    return np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, cos_phi, -sin_phi],
            [0.0, sin_phi, cos_phi],
        ],
        dtype=np.float64,
    )


def couple_vector_fsp_to_club(
    m_shaft_nm: float,
    m_out_of_plane_nm: float,
    m_in_plane_nm: float,
    phi_rad: float,
) -> tuple[float, float, float]:
    """Map (M_shaft, M_out, M_in)_FSP to (M_gamma, M_beta, M_alpha)_club."""
    m_fsp = np.array([m_shaft_nm, m_out_of_plane_nm, m_in_plane_nm], dtype=np.float64)
    m_club = rotation_fsp_to_club_about_shaft(phi_rad) @ m_fsp
    return float(m_club[0]), float(m_club[1]), float(m_club[2])


def alpha_couple_in_club_frame(
    m_in_plane_nm: float,
    m_out_of_plane_nm: float,
    phi_rad: float,
) -> float:
    """Return club-frame alpha projection M_alpha,club(phi) for fixed FSP couple components."""
    return m_in_plane_nm * math.cos(phi_rad) + m_out_of_plane_nm * math.sin(phi_rad)


def illustrative_alpha_zero_crossing_deg(m_in_plane_nm: float, m_out_of_plane_nm: float) -> float:
    """Roll angle (deg) where M_alpha,club vanishes for the illustrative atan2 convention."""
    return math.degrees(math.atan2(-m_in_plane_nm, m_out_of_plane_nm))


def couple_spatial_norm_nm(
    m_shaft_nm: float,
    m_out_of_plane_nm: float,
    m_in_plane_nm: float,
) -> float:
    """Euclidean norm of the spatial couple vector (frame-invariant)."""
    return math.sqrt(m_shaft_nm**2 + m_out_of_plane_nm**2 + m_in_plane_nm**2)
