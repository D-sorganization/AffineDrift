"""Lumped flexible-shaft reference parameters and oracle-3 frequency bookkeeping (#5463)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

GRAVITY_M_S2 = 9.81
SWING_PLANE_TILT_FROM_HORIZONTAL_DEG = 35.0
REFERENCE_SHAFT_STIFFNESS_NM_RAD = 80.0
REFERENCE_GRAVITY_PLANAR_M_S2 = 8.033
REFERENCE_DISTAL_HEAD_MASS_KG = 0.20
REFERENCE_DISTAL_SHAFT_LENGTH_M = 0.55


def _validate_finite_real(name: str, value: float) -> float:
    """Validate that ``value`` is a non-boolean finite real number."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number, got {type(value).__name__}")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{name} must be finite, got {value!r}")
    return numeric


def _validate_positive_finite(name: str, value: float) -> float:
    """Validate that ``value`` is a non-boolean finite strictly positive real."""
    numeric = _validate_finite_real(name, value)
    if numeric <= 0.0:
        raise ValueError(f"{name} must be > 0, got {numeric!r}")
    return numeric


@dataclass(frozen=True)
class ShaftReferenceConfig:
    """Study 6 reference shaft and swing-plane gravity configuration (#5463)."""

    shaft_stiffness_nm_rad: float = REFERENCE_SHAFT_STIFFNESS_NM_RAD
    distal_head_mass_kg: float = REFERENCE_DISTAL_HEAD_MASS_KG
    distal_shaft_length_m: float = REFERENCE_DISTAL_SHAFT_LENGTH_M
    gravity_planar_m_s2: float = REFERENCE_GRAVITY_PLANAR_M_S2
    swing_plane_tilt_deg: float = SWING_PLANE_TILT_FROM_HORIZONTAL_DEG

    def __post_init__(self) -> None:
        """Validate all parameters are positive finite scalars (and tilt is finite)."""
        _validate_positive_finite("shaft_stiffness_nm_rad", self.shaft_stiffness_nm_rad)
        _validate_positive_finite("distal_head_mass_kg", self.distal_head_mass_kg)
        _validate_positive_finite("distal_shaft_length_m", self.distal_shaft_length_m)
        _validate_positive_finite("gravity_planar_m_s2", self.gravity_planar_m_s2)
        _validate_finite_real("swing_plane_tilt_deg", self.swing_plane_tilt_deg)


def planar_gravity_m_s2(
    tilt_from_horizontal_deg: float = SWING_PLANE_TILT_FROM_HORIZONTAL_DEG,
) -> float:
    """Return gravity projected into a swing plane tilted from horizontal by ``tilt``."""
    tilt = _validate_finite_real("tilt_from_horizontal_deg", tilt_from_horizontal_deg)
    return GRAVITY_M_S2 * math.cos(math.radians(tilt))


def lumped_shaft_natural_frequency_hz(
    shaft_stiffness_nm_rad: float,
    distal_head_mass_kg: float,
    distal_shaft_length_m: float,
) -> float:
    """Oracle 3: √(k/(m_head·b²))/(2π) for the clamped-proximal small-deflection mode."""
    k = _validate_positive_finite("shaft_stiffness_nm_rad", shaft_stiffness_nm_rad)
    mass = _validate_positive_finite("distal_head_mass_kg", distal_head_mass_kg)
    length = _validate_positive_finite("distal_shaft_length_m", distal_shaft_length_m)
    inertia_kg_m2 = mass * length**2
    return math.sqrt(k / inertia_kg_m2) / (2.0 * math.pi)


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
    config: ShaftReferenceConfig | None = None,
) -> dict[str, Any]:
    """Serialize reference ``k``, cpm equivalent, and gravity projection for Study 6."""
    cfg = config if config is not None else ShaftReferenceConfig()
    projected = planar_gravity_m_s2(cfg.swing_plane_tilt_deg)
    hz = lumped_shaft_natural_frequency_hz(
        cfg.shaft_stiffness_nm_rad, cfg.distal_head_mass_kg, cfg.distal_shaft_length_m
    )
    return {
        "shaft_stiffness_nm_rad": float(cfg.shaft_stiffness_nm_rad),
        "distal_head_mass_kg": float(cfg.distal_head_mass_kg),
        "distal_shaft_length_m": float(cfg.distal_shaft_length_m),
        "gravity_planar_m_s2": float(cfg.gravity_planar_m_s2),
        "swing_plane_tilt_from_horizontal_deg": float(cfg.swing_plane_tilt_deg),
        "standard_gravity_m_s2": GRAVITY_M_S2,
        "planar_gravity_from_tilt_m_s2": float(projected),
        "lumped_shaft_natural_frequency_hz": float(hz),
        "lumped_shaft_equivalent_cpm": float(
            lumped_shaft_cpm(
                cfg.shaft_stiffness_nm_rad, cfg.distal_head_mass_kg, cfg.distal_shaft_length_m
            )
        ),
        "cpm_formula": "sqrt(k/(m_head*b^2))/(2*pi)*60; oracle 3 clamped-proximal small deflection",
        "gravity_projection_note": (
            f"g_planar = {cfg.gravity_planar_m_s2} m/s^2 in UpstreamDrift reference; "
            f"interpreted as g·cos({cfg.swing_plane_tilt_deg}°) ≈ {projected:.3f} m/s^2"
        ),
    }
