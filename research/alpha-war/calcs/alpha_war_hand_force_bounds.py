"""Planar two-hand force-couple arithmetic for Alpha War Box 3.1 (§5A.1)."""

from __future__ import annotations

GRIP_SEPARATION_M = 0.0762
NEWTONS_PER_LBF = 4.4482216152605


def differential_force_y_from_force_couple(
    force_couple_mid_nm: float,
    grip_separation_m: float = GRIP_SEPARATION_M,
) -> float:
    """Return transverse differential force from the force couple at mid-hands.

    Uses Box 3.1: ``C_F,M = -s * F_d,y`` with ``F_d,y = (F_L,y - F_T,y) / 2``.

    Args:
        force_couple_mid_nm: Force-generated in-plane couple at mid-hands (N·m).
        grip_separation_m: Hand separation along the shaft (m). Must be positive.

    Returns:
        Differential force component ``F_d,y`` (N).
    """
    if grip_separation_m <= 0.0:
        raise ValueError("grip_separation_m must be positive")
    return -force_couple_mid_nm / grip_separation_m


def opposed_pure_couple_contact_forces_y(
    force_couple_mid_nm: float,
    grip_separation_m: float = GRIP_SEPARATION_M,
) -> tuple[float, float]:
    """Return equal-and-opposite transverse contact forces for a pure force couple.

    Assumes zero common-mode transverse shear (``F_c,y = 0``) and zero free wrist
    torques (``tau_free = 0``). Each hand carries the same magnitude; signs oppose.

    Args:
        force_couple_mid_nm: Target force couple ``C_F,M`` at mid-hands (N·m).
        grip_separation_m: Hand separation along the shaft (m).

    Returns:
        ``(F_L,y, F_T,y)`` in newtons.
    """
    f_d_y = differential_force_y_from_force_couple(force_couple_mid_nm, grip_separation_m)
    return (f_d_y, -f_d_y)


def reconstruct_force_couple_mid_nm(
    f_lead_y: float,
    f_trail_y: float,
    grip_separation_m: float = GRIP_SEPARATION_M,
) -> float:
    """Reconstruct ``C_F,M`` from bilateral contact forces (N·m).

    Args:
        f_lead_y: Lead-hand transverse contact force (N).
        f_trail_y: Trail-hand transverse contact force (N).
        grip_separation_m: Hand separation along the shaft (m).

    Returns:
        Force-generated couple at mid-hands (N·m).
    """
    f_d_y = 0.5 * (f_lead_y - f_trail_y)
    return -grip_separation_m * f_d_y


def newtons_to_lbf(force_n: float) -> float:
    """Convert newtons to pound-force."""
    return force_n / NEWTONS_PER_LBF
