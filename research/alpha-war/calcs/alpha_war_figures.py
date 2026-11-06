"""Generate SVG figures for the Alpha War draft from alpha_war_calculations.json."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

CALCS_DIR = Path(__file__).resolve().parent
JSON_PATH = CALCS_DIR / "alpha_war_calculations.json"
FIG_DIR = CALCS_DIR.parent / "draft" / "figures"


def _svg_header(w: int, h: int) -> str:
    """Return the opening SVG root element for a figure of the given size."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img">'
    )


def fig_transport_stations(payload: dict[str, Any]) -> str:
    """Plot M(s) = C_alpha - s*R_y along the shaft with simulated and illustrative s*."""
    study1 = payload["study_1_grip_point_transport"]
    sim = study1["wscg_at_minimum_couple"]
    ill = study1["analytical_driver_transport_cases"][0]

    stations = sim["stations"]
    xs = [s["shaft_offset_from_mid_hands_m"] for s in stations]
    ys_sim = [s["reported_alpha_moment_nm"] for s in stations]
    c_sim = sim["total_couple_about_mid_hands_nm"]
    ry_sim = sim["resultant_axial_normal_n"][1]
    s_star_sim = sim["sign_flip_station_offset_m"]

    c_ill = ill["couple_about_mid_hands_nm"]
    ry_ill = ill["resultant_force_n"][1]
    s_star_ill = ill["sign_flip_offset_from_mid_hands_m"]
    xs_ill = [s["shaft_offset_m"] for s in ill["stations"]]
    ys_ill = [s["moment_nm"] for s in ill["stations"]]

    ys_low = [c_sim - s * (0.8 * ry_sim) for s in xs]
    ys_high = [c_sim - s * (1.2 * ry_sim) for s in xs]

    w, h, pad_l, pad_r, pad_t, pad_b = 720, 400, 68, 36, 62, 58
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = -28.0, 42.0
    span_x = xmax - xmin or 1.0
    span_y = ymax - ymin or 1.0

    def tx(x: float) -> float:
        """Map shaft offset (m) to horizontal SVG coordinate."""
        return float(pad_l + (x - xmin) / span_x * (w - pad_l - pad_r))

    def ty(y: float) -> float:
        """Map alpha moment (N·m) to vertical SVG coordinate."""
        return h - pad_b - (y - ymin) / span_y * (h - pad_t - pad_b)

    band_pts = " ".join(
        [f"{tx(x):.1f},{ty(y):.1f}" for x, y in zip(xs, ys_high, strict=True)]
        + [f"{tx(x):.1f},{ty(y):.1f}" for x, y in zip(reversed(xs), reversed(ys_low), strict=True)]
    )
    sim_pts = " ".join(f"{tx(x):.1f},{ty(y):.1f}" for x, y in zip(xs, ys_sim, strict=True))
    ill_pts = " ".join(f"{tx(x):.1f},{ty(y):.1f}" for x, y in zip(xs_ill, ys_ill, strict=True))
    y0 = ty(0.0)
    circles = "".join(
        f'<circle cx="{tx(x):.1f}" cy="{ty(y):.1f}" r="3.5" fill="#1f77b4"/>'
        for x, y in zip(xs, ys_sim, strict=True)
    )

    lines = [
        _svg_header(w, h),
        '<text x="68" y="22" font-size="13" font-weight="bold">'
        "Fig 1: Reference-point transport M(s) = C_alpha - s*R_y along the shaft (N·m vs m)"
        "</text>",
        '<text x="68" y="39" font-size="11" fill="#333">'
        "Plain-language takeaway: Moving the reference point toward the clubhead shifts "
        "reported moment from negative to positive."
        "</text>",
        '<text x="68" y="54" font-size="10.5" fill="#555">'
        "Frame: F_FSP (functional swing plane) | Sign convention: +CCW uncocking (alpha) | "
        "Units: s in m, M in N·m"
        "</text>",
        f'<line x1="{pad_l}" y1="{h - pad_b}" x2="{w - pad_r}" y2="{h - pad_b}" stroke="#333"/>',
        f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{h - pad_b}" stroke="#333"/>',
        f'<line x1="{pad_l}" y1="{y0:.1f}" x2="{w - pad_r}" y2="{y0:.1f}" '
        'stroke="#666" stroke-dasharray="4 3"/>',
        f'<polygon points="{band_pts}" fill="#1f77b4" fill-opacity="0.18" stroke="none"/>',
        f'<polyline fill="none" stroke="#1f77b4" stroke-width="2.2" points="{sim_pts}"/>',
        f'<polyline fill="none" stroke="#ff7f0e" stroke-width="2" '
        f'stroke-dasharray="6 4" points="{ill_pts}"/>',
        circles,
        f'<circle cx="{tx(s_star_sim):.1f}" cy="{y0:.1f}" r="5" fill="#d62728"/>',
        f'<text x="{tx(s_star_sim) - 155:.1f}" y="{y0 + 18:.1f}" font-size="10.5" fill="#1f77b4">'
        f"Simulated WSCG (t=0.2151 s): s* = +{s_star_sim:.3f} m "
        f"(C={c_sim:.2f} N·m, R_y={ry_sim:.2f} N)"
        "</text>",
        f'<circle cx="{tx(s_star_ill):.1f}" cy="{y0:.1f}" r="5" fill="#ff7f0e"/>',
        f'<text x="{tx(s_star_ill) + 8:.1f}" y="{y0 - 10:.1f}" font-size="10.5" fill="#b85600">'
        f"Illustrative Case 1: s* = +{s_star_ill:.3f} m (C={c_ill:.2f} N·m, R_y={ry_ill:.2f} N)"
        "</text>",
        f'<text x="{pad_l + 12}" y="{pad_t + 18}" font-size="10.5" fill="#1f77b4">'
        "Shaded band: ±20% R_y sensitivity envelope on simulated WSCG transport line"
        "</text>",
        f'<text x="{w // 2 - 95}" y="{h - 16}" font-size="11">'
        "Shaft offset s from mid-hands M (m)"
        "</text>",
        f'<text x="14" y="{h // 2}" font-size="11" '
        f'transform="rotate(-90 14,{h // 2})">Reported alpha moment M(s) (N·m)</text>',
        "</svg>",
    ]
    return "\n".join(lines)


def fig_club_roll_projection(payload: dict[str, Any]) -> str:
    """Plot club-frame alpha couple M_alpha,club(phi) across roll angle with phi*."""
    study3 = payload["study_3_frame_conventions"]
    fsp = study3["input_physical_couple_fsp_nm"]
    m_in = fsp["M_in_plane_n"]
    m_out = fsp["M_out_of_plane_p"]
    m_shaft = fsp["M_shaft_t"]
    phi_star_deg = math.degrees(math.atan2(-m_in, m_out))

    angles = list(range(0, 181, 5))
    ys = [m_in * math.cos(math.radians(a)) + m_out * math.sin(math.radians(a)) for a in angles]
    ys_low = [
        m_in * math.cos(math.radians(a)) + (0.8 * m_out) * math.sin(math.radians(a)) for a in angles
    ]
    ys_high = [
        m_in * math.cos(math.radians(a)) + (1.2 * m_out) * math.sin(math.radians(a)) for a in angles
    ]

    w, h, pad_l, pad_r, pad_t, pad_b = 720, 400, 68, 36, 62, 58
    xmin, xmax = 0.0, 180.0
    ymin, ymax = -18.0, 20.0
    span_x = xmax - xmin
    span_y = ymax - ymin

    def tx(x: float) -> float:
        """Map roll angle (deg) to horizontal SVG coordinate."""
        return pad_l + (x - xmin) / span_x * (w - pad_l - pad_r)

    def ty(y: float) -> float:
        """Map projected couple (N·m) to vertical SVG coordinate."""
        return h - pad_b - (y - ymin) / span_y * (h - pad_t - pad_b)

    band_pts = " ".join(
        [f"{tx(x):.1f},{ty(y):.1f}" for x, y in zip(angles, ys_high, strict=True)]
        + [
            f"{tx(x):.1f},{ty(y):.1f}"
            for x, y in zip(reversed(angles), reversed(ys_low), strict=True)
        ]
    )
    curve_pts = " ".join(f"{tx(x):.1f},{ty(y):.1f}" for x, y in zip(angles, ys, strict=True))
    sweep_rows = study3["jacobs_club_frame_roll_sweep"]
    sweep_circles = "".join(
        f'<circle cx="{tx(r["clubface_roll_rel_fsp_deg"]):.1f}" '
        f'cy="{ty(r["club_frame_alpha_couple_nm"]):.1f}" r="3.5" fill="#2ca02c"/>'
        for r in sweep_rows
    )
    y0 = ty(0.0)

    lines = [
        _svg_header(w, h),
        '<text x="68" y="22" font-size="13" font-weight="bold">'
        "Fig 3: Club-frame projected alpha couple M_alpha,club(phi) vs clubface roll (N·m vs deg)"
        "</text>",
        '<text x="68" y="39" font-size="11" fill="#333">'
        "Plain-language takeaway: Rotating the frame with face roll flips apparent alpha sign "
        "above phi* = 61.93 deg (illustrative)."
        "</text>",
        '<text x="68" y="54" font-size="10.5" fill="#555">'
        f"Frame: F_club rotated by phi from F_FSP | Sign convention: +CCW uncocking | "
        f"Illustrative input: M_FSP=({m_in:.1f}, +{m_out:.1f}, +{m_shaft:.1f}) N·m"
        "</text>",
        f'<line x1="{pad_l}" y1="{h - pad_b}" x2="{w - pad_r}" y2="{h - pad_b}" stroke="#333"/>',
        f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{h - pad_b}" stroke="#333"/>',
        f'<line x1="{pad_l}" y1="{y0:.1f}" x2="{w - pad_r}" y2="{y0:.1f}" '
        'stroke="#666" stroke-dasharray="4 3"/>',
        f'<polygon points="{band_pts}" fill="#2ca02c" fill-opacity="0.18" stroke="none"/>',
        f'<polyline fill="none" stroke="#2ca02c" stroke-width="2.2" points="{curve_pts}"/>',
        sweep_circles,
        f'<circle cx="{tx(phi_star_deg):.1f}" cy="{y0:.1f}" r="5.5" fill="#d62728"/>',
        f'<text x="{tx(phi_star_deg) + 10:.1f}" y="{y0 + 16:.1f}" font-size="10.5" fill="#d62728">'
        f"phi* = {phi_star_deg:.2f} deg (illustrative zero crossing: arctan(15/8))"
        "</text>",
        f'<text x="{pad_l + 12}" y="{pad_t + 18}" font-size="10.5" fill="#2ca02c">'
        "Shaded band: ±20% out-of-plane M_beta sensitivity envelope on illustrative roll projection"
        "</text>",
        f'<text x="{w // 2 - 115}" y="{h - 16}" font-size="11">'
        "Clubface roll angle phi_roll relative to FSP (deg)"
        "</text>",
        f'<text x="14" y="{h // 2}" font-size="11" '
        f'transform="rotate(-90 14,{h // 2})">Club-frame M_alpha,club(phi) (N·m)</text>',
        "</svg>",
    ]
    return "\n".join(lines)


def fig_filter_sweep(payload: dict[str, Any]) -> str:
    """Plot two small-multiple panels: (a) pre-impact truncation vs (b) across-impact bleed."""
    study4 = payload["study_4_filtering_and_drag_sensitivity"]
    rows = study4["butterworth_cutoff_sweep"]
    true_tau = study4["true_couple_at_impact_nm"]
    xs = [r["cutoff_hz"] for r in rows]
    clean_t0 = [r["clean_filtered_at_impact_nm"] for r in rows]
    clean_5ms = [r["clean_filtered_5ms_pre_nm"] for r in rows]
    bleed_t0 = [r["across_impact_filtered_at_impact_nm"] for r in rows]
    bleed_5ms = [r["across_impact_filtered_5ms_pre_nm"] for r in rows]
    by_fc = {r["cutoff_hz"]: r for r in rows}

    w, h = 760, 410
    p1_x0, p1_x1, p2_x0, p2_x1 = 58, 358, 428, 728
    y_top, y_bot = 82, 348
    ymin, ymax = -85.0, 10.0

    def tx(x: float, x0: int, x1: int) -> float:
        """Map cutoff frequency (4..100 Hz) to panel horizontal coordinate."""
        return x0 + (x - 4.0) / 96.0 * (x1 - x0)

    def ty(y: float) -> float:
        """Map couple (N·m) to vertical coordinate."""
        return y_bot - (y - ymin) / (ymax - ymin) * (y_bot - y_top)

    def band(series: list[float], delta: float, x0: int, x1: int) -> str:
        """Build a polygon error/sensitivity band around a cutoff series."""
        hi = [f"{tx(x, x0, x1):.1f},{ty(y + delta):.1f}" for x, y in zip(xs, series, strict=True)]
        lo = [
            f"{tx(x, x0, x1):.1f},{ty(y - delta):.1f}"
            for x, y in zip(reversed(xs), reversed(series), strict=True)
        ]
        return " ".join(hi + lo)

    def pts(series: list[float], x0: int, x1: int) -> str:
        """Build polyline coordinate string for a cutoff series."""
        return " ".join(f"{tx(x, x0, x1):.1f},{ty(y):.1f}" for x, y in zip(xs, series, strict=True))

    y0 = ty(0.0)
    yt = ty(true_tau)
    c8 = by_fc[8.0]["clean_filtered_at_impact_nm"]
    b30 = by_fc[30.0]["across_impact_filtered_at_impact_nm"]
    b100 = by_fc[100.0]["across_impact_filtered_at_impact_nm"]

    lines = [
        _svg_header(w, h),
        '<text x="58" y="20" font-size="13" font-weight="bold">'
        "Fig 4: Butterworth cutoff sweep (4-100 Hz): pre-impact truncation vs across-impact bleed"
        "</text>",
        '<text x="58" y="37" font-size="10.8" fill="#333">'
        "Plain-language takeaway: Low cutoffs (&lt;10 Hz) erase the negative peak and flip sign; "
        "filtering across impact bleeds collision force backward."
        "</text>",
        '<text x="58" y="52" font-size="10.2" fill="#555">'
        "Filter: 2nd-order Butterworth per pass, bidirectional zero-lag filtfilt "
        "(effective 4th-order) | Truncation: &gt;=20 ms before contact | "
        "Frame: F_FSP (+CCW uncocking)"
        "</text>",
        f'<text x="{p1_x0}" y="72" font-size="11.5" font-weight="bold" fill="#1f77b4">'
        "Panel (a): Pre-impact truncation (&gt;=20 ms pre-contact)</text>",
        f'<text x="{p2_x0}" y="72" font-size="11.5" font-weight="bold" fill="#d62728">'
        "Panel (b): Filtering across impact (collision bleed)</text>",
        f'<rect x="{p1_x0}" y="{y_top}" width="{p1_x1 - p1_x0}" height="{y_bot - y_top}" '
        'fill="#fafafa" stroke="#333"/>',
        f'<rect x="{p2_x0}" y="{y_top}" width="{p2_x1 - p2_x0}" height="{y_bot - y_top}" '
        'fill="#fafafa" stroke="#333"/>',
        f'<line x1="{p1_x0}" y1="{y0:.1f}" x2="{p1_x1}" y2="{y0:.1f}" '
        'stroke="#666" stroke-dasharray="4 3"/>',
        f'<line x1="{p2_x0}" y1="{y0:.1f}" x2="{p2_x1}" y2="{y0:.1f}" '
        'stroke="#666" stroke-dasharray="4 3"/>',
        f'<line x1="{p1_x0}" y1="{yt:.1f}" x2="{p1_x1}" y2="{yt:.1f}" '
        'stroke="#2ca02c" stroke-dasharray="3 3"/>',
        f'<line x1="{p2_x0}" y1="{yt:.1f}" x2="{p2_x1}" y2="{yt:.1f}" '
        'stroke="#2ca02c" stroke-dasharray="3 3"/>',
        f'<polygon points="{band(clean_t0, 2.0, p1_x0, p1_x1)}" '
        'fill="#1f77b4" fill-opacity="0.18"/>',
        f'<polyline fill="none" stroke="#1f77b4" stroke-width="2.2" '
        f'points="{pts(clean_t0, p1_x0, p1_x1)}"/>',
        f'<polyline fill="none" stroke="#1f77b4" stroke-width="1.5" '
        f'stroke-dasharray="5 3" points="{pts(clean_5ms, p1_x0, p1_x1)}"/>',
        f'<circle cx="{tx(8.0, p1_x0, p1_x1):.1f}" cy="{ty(c8):.1f}" r="4.5" fill="#d62728"/>',
        f'<text x="{tx(8.0, p1_x0, p1_x1) + 6:.1f}" y="{ty(c8) - 6:.1f}" '
        f'font-size="10" fill="#d62728">8 Hz sign flip: +{c8:.2f} N·m</text>',
        f'<text x="{p1_x0 + 8}" y="{yt + 14:.1f}" font-size="10" fill="#2ca02c">'
        f"True pre-impact couple: {true_tau:.2f} N·m</text>",
        f'<polygon points="{band(bleed_t0, 3.5, p2_x0, p2_x1)}" '
        'fill="#d62728" fill-opacity="0.16"/>',
        f'<polyline fill="none" stroke="#d62728" stroke-width="2.2" '
        f'points="{pts(bleed_t0, p2_x0, p2_x1)}"/>',
        f'<polyline fill="none" stroke="#ff7f0e" stroke-width="1.5" '
        f'stroke-dasharray="5 3" points="{pts(bleed_5ms, p2_x0, p2_x1)}"/>',
        f'<circle cx="{tx(30.0, p2_x0, p2_x1):.1f}" cy="{ty(b30):.1f}" r="4.5" fill="#d62728"/>',
        f'<text x="{tx(30.0, p2_x0, p2_x1) + 6:.1f}" y="{ty(b30) + 4:.1f}" '
        f'font-size="10" fill="#d62728">'
        f"30 Hz bleed: {b30:.2f} N·m (100 Hz: {b100:.2f} N·m)</text>",
        f'<text x="{p1_x0 + 70}" y="{h - 18}" font-size="11">Butterworth cutoff f_c (Hz)</text>',
        f'<text x="{p2_x0 + 70}" y="{h - 18}" font-size="11">Butterworth cutoff f_c (Hz)</text>',
        f'<text x="16" y="{(y_top + y_bot) // 2}" font-size="11" '
        f'transform="rotate(-90 16,{(y_top + y_bot) // 2})">Filtered alpha couple (N·m)</text>',
        "</svg>",
    ]
    return "\n".join(lines)


def fig_couple_timeseries(payload: dict[str, Any]) -> str:
    """Plot hand couple, ZTCF passive couple, and COM moment over time with error bands."""
    snaps = payload["study_2_couple_vs_sum_of_moments"]["snapshots"]
    ts = [s["time_s"] for s in snaps]
    couple = [s["total_hand_couple_mid_nm"] for s in snaps]
    ztcf = [s["ztcf_passive_couple_mid_nm"] for s in snaps]
    com = [s["sum_of_moments_about_com_nm"] for s in snaps]

    min_snap = next(s for s in snaps if abs(s["time_s"] - 0.2151) < 1e-4)
    c_min = min_snap["total_hand_couple_mid_nm"]
    z_min = min_snap["ztcf_passive_couple_mid_nm"]
    share_pct = 100.0 * abs(z_min) / abs(c_min)

    w, h, pad_l, pad_r, pad_t, pad_b = 720, 400, 68, 36, 62, 58
    tmin, tmax = min(ts), max(ts)
    vmin, vmax = -28.0, 62.0
    span_t = tmax - tmin or 1.0
    span_v = vmax - vmin or 1.0

    def tx(t: float) -> float:
        """Map time (s) to horizontal SVG coordinate."""
        return float(pad_l + (t - tmin) / span_t * (w - pad_l - pad_r))

    def ty(v: float) -> float:
        """Map moment/couple (N·m) to vertical SVG coordinate."""
        return h - pad_b - (v - vmin) / span_v * (h - pad_t - pad_b)

    def poly(series: list[float], color: str, dash: str = "") -> str:
        """Build a polyline element for one time series."""
        pts = " ".join(f"{tx(t):.1f},{ty(v):.1f}" for t, v in zip(ts, series, strict=True))
        d_attr = f' stroke-dasharray="{dash}"' if dash else ""
        return f'<polyline fill="none" stroke="{color}" stroke-width="2.2"{d_attr} points="{pts}"/>'

    def band(series: list[float], sigma: float, color: str) -> str:
        """Build an error-propagation polygon band around a time series."""
        hi = [f"{tx(t):.1f},{ty(v + sigma):.1f}" for t, v in zip(ts, series, strict=True)]
        lo = [
            f"{tx(t):.1f},{ty(v - sigma):.1f}"
            for t, v in zip(reversed(ts), reversed(series), strict=True)
        ]
        pts_str = " ".join(hi + lo)
        return f'<polygon points="{pts_str}" fill="{color}" fill-opacity="0.16" stroke="none"/>'

    y0 = ty(0.0)
    lines = [
        _svg_header(w, h),
        '<text x="68" y="22" font-size="13" font-weight="bold">'
        "Fig 2: WSCG time series — hand couple C_alpha,M(t) vs ZTCF passive vs COM moment "
        "(N·m vs s)</text>",
        '<text x="68" y="39" font-size="10.8" fill="#333">'
        "Plain-language takeaway: The hand couple turns negative before impact and tracks the "
        f"passive ZTCF curve ({share_pct:.2f}% share at t=0.2151 s)."
        "</text>",
        '<text x="68" y="54" font-size="10.2" fill="#555">'
        "Frame: F_FSP (functional swing plane) | Sign convention: +CCW uncocking | "
        "Source: simulated WSCG with ±3.0 N·m inverse-dynamics error-propagation bands"
        "</text>",
        f'<line x1="{pad_l}" y1="{h - pad_b}" x2="{w - pad_r}" y2="{h - pad_b}" stroke="#333"/>',
        f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{h - pad_b}" stroke="#333"/>',
        f'<line x1="{pad_l}" y1="{y0:.1f}" x2="{w - pad_r}" y2="{y0:.1f}" '
        'stroke="#666" stroke-dasharray="4 3"/>',
        band(couple, 3.0, "#1f77b4"),
        band(ztcf, 2.5, "#2ca02c"),
        band(com, 3.0, "#ff7f0e"),
        poly(couple, "#1f77b4"),
        poly(ztcf, "#2ca02c", "6 4"),
        poly(com, "#ff7f0e"),
        f'<circle cx="{tx(0.2151):.1f}" cy="{ty(c_min):.1f}" r="4.5" fill="#1f77b4"/>',
        f'<circle cx="{tx(0.2151):.1f}" cy="{ty(z_min):.1f}" r="4.5" fill="#2ca02c"/>',
        f'<text x="{tx(0.2151) - 285:.1f}" y="{ty(c_min) + 14:.1f}" '
        f'font-size="10.5" fill="#1f77b4">'
        f"t=0.2151 s (simulated): ZTCF {z_min:.2f} N·m / Total {c_min:.2f} N·m = "
        f"{share_pct:.2f}% passive share</text>",
        f'<text x="{pad_l + 12}" y="{pad_t + 18}" font-size="10.5" fill="#333">'
        "Legend: Blue = Total hand couple C_alpha,M | Green dashed = ZTCF passive | "
        "Orange = COM moment M_alpha,G</text>",
        f'<text x="{w // 2 - 65}" y="{h - 16}" font-size="11">Downswing time t (s)</text>',
        f'<text x="16" y="{h // 2}" font-size="11" '
        f'transform="rotate(-90 16,{h // 2})">Couple / moment (N·m)</text>',
        "</svg>",
    ]
    return "\n".join(lines)


def fig_swing_plane_schematic() -> str:
    """Return a publication-grade vector schematic SVG of the functional swing plane (FSP)."""
    w, h = 760, 360
    font = 'font-family="system-ui, -apple-system, sans-serif"'
    return "\n".join(
        [
            _svg_header(w, h),
            "<defs>",
            '  <marker id="fsp-arrow-blue" markerWidth="8" markerHeight="8" '
            'refX="6" refY="3" orient="auto">',
            '    <path d="M0,0 L6,3 L0,6 Z" fill="#1f77b4"/>',
            "  </marker>",
            '  <marker id="fsp-arrow-red" markerWidth="8" markerHeight="8" '
            'refX="6" refY="3" orient="auto">',
            '    <path d="M0,0 L6,3 L0,6 Z" fill="#d62728"/>',
            "  </marker>",
            '  <marker id="fsp-arrow-green" markerWidth="8" markerHeight="8" '
            'refX="6" refY="3" orient="auto">',
            '    <path d="M0,0 L6,3 L0,6 Z" fill="#15803d"/>',
            "  </marker>",
            "</defs>",
            '<rect x="10" y="10" width="740" height="340" rx="8" '
            'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>',
            f'<text x="30" y="34" {font} font-size="14" font-weight="bold" fill="#0f172a">'
            "Functional swing plane (schematic) — Kwon FSP &amp; Instantaneous Plane Geometry"
            "</text>",
            f'<text x="30" y="52" {font} font-size="11" fill="#475569">'
            "Orthogonal triad (e_t, e_n, e_b): clubhead trajectory, inward grip hub arc, "
            "and out-of-plane normal axis e_alpha</text>",
            '<polygon points="90,285 260,95 680,95 510,285" fill="#e0f2fe" '
            'fill-opacity="0.55" stroke="#0284c7" stroke-width="1.5" stroke-dasharray="6 4"/>',
            f'<text x="515" y="116" {font} font-size="11" font-weight="bold" fill="#0369a1">'
            "Functional Swing Plane (F_FSP)</text>",
            '<ellipse cx="385" cy="195" rx="220" ry="68" fill="none" '
            'stroke="#64748b" stroke-width="2" stroke-dasharray="6 4"/>',
            f'<text x="230" y="275" {font} font-size="11.5" font-weight="bold" fill="#334155">'
            "Instantaneous swing plane &amp; clubhead delivery arc</text>",
            '<path d="M 250 185 Q 310 225 395 205" fill="none" '
            'stroke="#1f77b4" stroke-width="2.5"/>',
            '<circle cx="315" cy="205" r="6.5" fill="#1f77b4"/>',
            f'<text x="225" y="210" {font} font-size="12" font-weight="bold" fill="#1f77b4">'
            "Grip hub (M)</text>",
            '<line x1="315" y1="205" x2="545" y2="145" stroke="#0f172a" stroke-width="3.5"/>',
            '<circle cx="545" cy="145" r="7" fill="#0f172a"/>',
            f'<text x="558" y="148" {font} font-size="12" font-weight="bold" fill="#0f172a">'
            "Club path &amp; head</text>",
            '<line x1="315" y1="205" x2="315" y2="105" stroke="#d62728" '
            'stroke-width="2.5" marker-end="url(#fsp-arrow-red)"/>',
            f'<text x="325" y="115" {font} font-size="11.5" font-weight="bold" fill="#d62728">'
            "Out-of-plane normal e_b = e_alpha (+CCW uncocking)</text>",
            '<line x1="315" y1="205" x2="365" y2="155" stroke="#15803d" '
            'stroke-width="2.2" marker-end="url(#fsp-arrow-green)"/>',
            f'<text x="372" y="162" {font} font-size="11" font-weight="bold" fill="#15803d">'
            "Centripetal normal e_n</text>",
            '<line x1="315" y1="205" x2="405" y2="225" stroke="#1f77b4" '
            'stroke-width="2.2" marker-end="url(#fsp-arrow-blue)"/>',
            f'<text x="412" y="232" {font} font-size="11" font-weight="bold" fill="#1f77b4">'
            "Tangent e_t</text>",
            '<rect x="25" y="302" width="710" height="34" rx="4" fill="#f1f5f9" stroke="#cbd5e1"/>',
            f'<text x="38" y="323" {font} font-size="11" fill="#334155">'
            "Key insight: Alpha torque C_alpha is the moment component projected onto "
            "the plane normal e_alpha perpendicular to the FSP.</text>",
            "</svg>",
        ]
    )


def fig_nesbit_fig11_schematic() -> str:
    """Return a four-panel layout for Nesbit and Serrano (2005) Fig. 11, with no curve data.

    The paper tabulates no per-subject values at impact, so this figure draws no curve,
    value or trend. It labels the four subjects (handicap and sex from Table 1) and marks
    the impact reading as eye-read only (unverified, VRF-11).
    """
    w, h = 760, 300
    font = 'font-family="system-ui, -apple-system, sans-serif"'
    panels = [
        ("Subject 1", "handicap 0, male"),
        ("Subject 2", "handicap 5, male"),
        ("Subject 3", "handicap 13, male"),
        ("Subject 4", "handicap 18, female"),
    ]
    lines = [
        _svg_header(w, h),
        '<rect x="10" y="10" width="740" height="280" rx="8" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>',
        f'<text x="30" y="34" {font} font-size="14" font-weight="bold" fill="#0f172a">'
        "Nesbit &amp; Serrano (2005), Fig. 11, p. 529: subject layout (no curve data)</text>",
        f'<text x="30" y="52" {font} font-size="11" fill="#475569">'
        "Subject handicap and sex from Table 1 of the paper; the curves are not reproduced "
        "here.</text>",
    ]
    for i, (label, note) in enumerate(panels):
        x0 = 28 + i * 178
        lines.append(
            f'<rect x="{x0}" y="68" width="164" height="150" rx="6" '
            'fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>'
        )
        lines.append(f'<rect x="{x0}" y="68" width="164" height="44" rx="6" fill="#f1f5f9"/>')
        lines.append(
            f'<text x="{x0 + 10}" y="86" {font} font-size="12" '
            f'font-weight="bold" fill="#0f172a">{label}</text>'
        )
        lines.append(
            f'<text x="{x0 + 10}" y="103" {font} font-size="10.5" fill="#334155">{note}</text>'
        )
        lines.append(
            f'<text x="{x0 + 10}" y="150" {font} font-size="10" fill="#64748b">'
            "Impact sign: not tabulated</text>"
        )
        lines.append(
            f'<text x="{x0 + 10}" y="166" {font} font-size="10" fill="#64748b">'
            "(eye-read only)</text>"
        )
    lines.append(
        '<rect x="28" y="234" width="698" height="40" rx="4" fill="#eff6ff" stroke="#bfdbfe"/>'
    )
    lines.append(
        f'<text x="40" y="252" {font} font-size="10.8" fill="#1e3a8a">'
        "Any per-subject sign reading of Fig. 11 is unverified, VRF-11: the paper gives "
        "no values at impact.</text>"
    )
    lines.append(
        f'<text x="40" y="267" {font} font-size="10.8" fill="#1e3a8a">'
        "A faithful re-plot needs digitised data from the primary figure.</text>"
    )
    lines.append("</svg>")
    return "\n".join(lines)


def main() -> None:
    """Load calculation JSON and write all draft figure SVGs to disk."""
    payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    outputs = {
        "fig-transport-stations.svg": fig_transport_stations(payload),
        "fig-club-roll-projection.svg": fig_club_roll_projection(payload),
        "fig-filter-cutoff-sweep.svg": fig_filter_sweep(payload),
        "fig-couple-vs-com.svg": fig_couple_timeseries(payload),
        "fig-swing-plane-schematic.svg": fig_swing_plane_schematic(),
        "fig-nesbit-fig11-schematic.svg": fig_nesbit_fig11_schematic(),
    }
    for name, svg in outputs.items():
        (FIG_DIR / name).write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
