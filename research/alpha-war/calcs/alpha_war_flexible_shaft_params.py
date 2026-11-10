"""Lumped flexible-shaft reference parameters and oracle-3 frequency bookkeeping (#5463)."""

from __future__ import annotations

import math
from typing import Any

G_STANDARD_M_S2 = 9.81
SWING_PLANE_TILT_FROM_HORIZONTAL_DEG = 35.0
REFERENCE_SHAFT_STIFFNESS_NM_RAD = 80.0
REFERENCE_GRAVITY_PLANAR_M_S2 = 8.033
REFERENCE_DISTAL_HEAD_MASS_KG = 0.20
REFERENCE_DISTAL_SHAFT_LENGTH_M = 0.55


def planar_gravity_m_s2(
    tilt_from_horizontal_deg: float = SWING_PLANE_TILT_FROM_HORIZONTAL_DEG,
) -> float:
    """Return gravity projected into a swing plane tilted from horizontal by ``tilt``."""
    return G_STANDARD_M_S2 * math.cos(math.radians(tilt_from_horizontal_deg))


def lumped_shaft_natural_frequency_hz(
    shaft_stiffness_nm_rad: float,
    distal_head_mass_kg: float,
    distal_shaft_length_m: float,
) -> float:
    """Oracle 3: √(k/(m_head·b²))/(2π) for the clamped-proximal small-deflection mode."""
    inertia_kg_m2 = distal_head_mass_kg * distal_shaft_length_m**2
    return math.sqrt(shaft_stiffness_nm_rad / inertia_kg_m2) / (2.0 * math.pi)


def lumped_shaft_cpm(
    shaft_stiffness_nm_rad: float,
    distal_head_mass_kg: float,
    distal_shaft_length_m: float,
) -> float:
    """Return lumped-shaft small-oscillation frequency in cycles per minute."""
    return (
        lumped_shaft_natural_frequency_hz(
            shaft_stiffness_nm_rad, distal_head_mass_kg, distal_shaft_length_m
        )
        * 60.0
    )


def reference_stiffness_metadata(
    shaft_stiffness_nm_rad: float = REFERENCE_SHAFT_STIFFNESS_NM_RAD,
    distal_head_mass_kg: float = REFERENCE_DISTAL_HEAD_MASS_KG,
    distal_shaft_length_m: float = REFERENCE_DISTAL_SHAFT_LENGTH_M,
    gravity_planar_m_s2: float = REFERENCE_GRAVITY_PLANAR_M_S2,
    swing_plane_tilt_deg: float = SWING_PLANE_TILT_FROM_HORIZONTAL_DEG,
) -> dict[str, Any]:
    """Serialize reference ``k``, cpm equivalent, and gravity projection for Study 6."""
    projected = planar_gravity_m_s2(swing_plane_tilt_deg)
    hz = lumped_shaft_natural_frequency_hz(
        shaft_stiffness_nm_rad, distal_head_mass_kg, distal_shaft_length_m
    )
    return {
        "shaft_stiffness_nm_rad": float(shaft_stiffness_nm_rad),
        "distal_head_mass_kg": float(distal_head_mass_kg),
        "distal_shaft_length_m": float(distal_shaft_length_m),
        "gravity_planar_m_s2": float(gravity_planar_m_s2),
        "swing_plane_tilt_from_horizontal_deg": float(swing_plane_tilt_deg),
        "standard_gravity_m_s2": G_STANDARD_M_S2,
        "planar_gravity_from_tilt_m_s2": float(projected),
        "lumped_shaft_natural_frequency_hz": float(hz),
        "lumped_shaft_equivalent_cpm": float(
            lumped_shaft_cpm(shaft_stiffness_nm_rad, distal_head_mass_kg, distal_shaft_length_m)
        ),
        "cpm_formula": "sqrt(k/(m_head*b^2))/(2*pi)*60; oracle 3 clamped-proximal small deflection",
        "gravity_projection_note": (
            f"g_planar = {gravity_planar_m_s2} m/s^2 in UpstreamDrift reference; "
            f"interpreted as g·cos({swing_plane_tilt_deg}°) ≈ {projected:.3f} m/s^2"
        ),
    }
