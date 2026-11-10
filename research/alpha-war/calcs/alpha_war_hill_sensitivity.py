"""Hill-type force–velocity sensitivity for §5A.1 wrist-speed discussion (#5464)."""

from __future__ import annotations

A_REL_DEFAULT = 0.25


def hill_active_force_fraction(
    shortening_velocity_m_s: float,
    max_shortening_velocity_m_s: float,
    *,
    a_rel: float = A_REL_DEFAULT,
) -> float:
    """Return ``F/F0`` from the symmetric Hill hyperbola at fixed ``a_rel``.

    Uses ``(F/F0) = (1 - v/v_max) / (1 + (v/v_max)/a_rel)`` with concentric ``v >= 0``.
    """
    if max_shortening_velocity_m_s <= 0.0:
        raise ValueError("max_shortening_velocity_m_s must be positive")
    v_ratio = shortening_velocity_m_s / max_shortening_velocity_m_s
    if v_ratio < 0.0:
        return 1.0
    if v_ratio >= 1.0:
        return 0.0
    return (1.0 - v_ratio) / (1.0 + v_ratio / a_rel)


def fascicle_velocity_m_s(moment_arm_m: float, omega_rel_rad_s: float) -> float:
    """Map wrist-relative angular rate to fascicle shortening speed."""
    return abs(moment_arm_m * omega_rel_rad_s)


def hill_sensitivity_rows(
    *,
    moment_arm_m: float = 0.02,
    omega_club_rad_s: float = 35.0,
    omega_rel_rad_s: float = 20.0,
    fascicle_length_m: float = 0.05,
    vmax_lengths_per_s: float = 8.0,
    a_rel: float = A_REL_DEFAULT,
) -> list[dict[str, float]]:
    """Build illustrative ``v/v_max`` and ``F/F0`` rows for club vs wrist-relative rates."""
    vmax_m_s = vmax_lengths_per_s * fascicle_length_m
    rows: list[dict[str, float]] = []
    for label, omega in (("omega_club", omega_club_rad_s), ("omega_rel", omega_rel_rad_s)):
        v_m = fascicle_velocity_m_s(moment_arm_m, omega)
        v_ratio = v_m / vmax_m_s
        rows.append(
            {
                "kinematic_label": label,
                "omega_rad_s": omega,
                "v_m_m_s": v_m,
                "v_over_vmax": v_ratio,
                "f_over_f0": hill_active_force_fraction(v_m, vmax_m_s, a_rel=a_rel),
            }
        )
    return rows
