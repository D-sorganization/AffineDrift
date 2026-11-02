"""Generate SVG figures for the Alpha War draft from alpha_war_calculations.json."""

from __future__ import annotations

import json
from pathlib import Path

CALCS_DIR = Path(__file__).resolve().parent
JSON_PATH = CALCS_DIR / "alpha_war_calculations.json"
FIG_DIR = CALCS_DIR.parent / "draft" / "figures"


def _svg_header(w: int, h: int) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img">'
    )


def fig_transport_stations(payload: dict) -> str:
    study = payload["study_1_grip_point_transport"]["wscg_at_minimum_couple"]
    stations = study["stations"]
    xs = [s["shaft_offset_from_mid_hands_m"] for s in stations]
    ys = [s["reported_alpha_moment_nm"] for s in stations]
    w, h, pad = 640, 360, 50
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    span_x = xmax - xmin or 1.0
    span_y = ymax - ymin or 1.0

    def tx(x: float) -> float:
        return pad + (x - xmin) / span_x * (w - 2 * pad)

    def ty(y: float) -> float:
        return h - pad - (y - ymin) / span_y * (h - 2 * pad)

    lines = [
        _svg_header(w, h),
        f'<text x="{pad}" y="24" font-size="14">Alpha moment vs shaft station (WSCG min couple)</text>',
        f'<line x1="{pad}" y1="{h-pad}" x2="{w-pad}" y2="{h-pad}" stroke="#333"/>',
        f'<line x1="{pad}" y1="{pad}" x2="{pad}" y2="{h-pad}" stroke="#333"/>',
    ]
    for x, y in zip(xs, ys):
        lines.append(
            f'<circle cx="{tx(x):.1f}" cy="{ty(y):.1f}" r="4" fill="#1f77b4"/>'
        )
    lines.append(f'<line x1="{tx(xs[0]):.1f}" y1="{ty(ys[0]):.1f}" '
                 f'x2="{tx(xs[-1]):.1f}" y2="{ty(ys[-1]):.1f}" stroke="#1f77b4"/>')
    lines.append("</svg>")
    return "\n".join(lines)


def fig_filter_sweep(payload: dict) -> str:
    rows = payload["study_4_filtering_and_drag_sensitivity"]["butterworth_cutoff_sweep"]
    xs = [r["cutoff_hz"] for r in rows]
    ys = [r["clean_filtered_at_impact_nm"] for r in rows]
    w, h, pad = 640, 360, 50
    xmax = max(xs)
    ymin, ymax = min(ys), max(ys)
    span_y = ymax - ymin or 1.0

    def tx(x: float) -> float:
        return pad + x / xmax * (w - 2 * pad)

    def ty(y: float) -> float:
        return h - pad - (y - ymin) / span_y * (h - 2 * pad)

    lines = [
        _svg_header(w, h),
        '<text x="50" y="24" font-size="14">Filtered impact couple vs Butterworth cutoff (Hz)</text>',
        f'<line x1="{pad}" y1="{h-pad}" x2="{w-pad}" y2="{h-pad}" stroke="#333"/>',
        f'<line x1="{pad}" y1="{pad}" x2="{pad}" y2="{h-pad}" stroke="#333"/>',
    ]
    pts = " ".join(f"{tx(x):.1f},{ty(y):.1f}" for x, y in zip(xs, ys))
    lines.append(f'<polyline fill="none" stroke="#d62728" stroke-width="2" points="{pts}"/>')
    lines.append("</svg>")
    return "\n".join(lines)


def fig_couple_timeseries(payload: dict) -> str:
    snaps = payload["study_2_couple_vs_sum_of_moments"]["snapshots"]
    ts = [s["time_s"] for s in snaps]
    couple = [s["total_hand_couple_mid_nm"] for s in snaps]
    com = [s["sum_of_moments_about_com_nm"] for s in snaps]
    w, h, pad = 640, 360, 50
    tmin, tmax = min(ts), max(ts)
    vals = couple + com
    vmin, vmax = min(vals), max(vals)
    span_t = tmax - tmin or 1.0
    span_v = vmax - vmin or 1.0

    def tx(t: float) -> float:
        return pad + (t - tmin) / span_t * (w - 2 * pad)

    def ty(v: float) -> float:
        return h - pad - (v - vmin) / span_v * (h - 2 * pad)

    def poly(series: list[float], color: str) -> str:
        pts = " ".join(f"{tx(t):.1f},{ty(v):.1f}" for t, v in zip(ts, series))
        return f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{pts}"/>'

    lines = [
        _svg_header(w, h),
        '<text x="50" y="24" font-size="14">Hand couple vs sum of moments about COM</text>',
        poly(couple, "#1f77b4"),
        poly(com, "#ff7f0e"),
        "</svg>",
    ]
    return "\n".join(lines)


def fig_swing_plane_schematic() -> str:
    w, h = 640, 280
    return "\n".join(
        [
            _svg_header(w, h),
            '<text x="40" y="30" font-size="14">Functional swing plane (schematic)</text>',
            '<ellipse cx="320" cy="160" rx="220" ry="70" fill="none" stroke="#888" stroke-dasharray="6 4"/>',
            '<text x="260" y="250" font-size="12">Instantaneous swing plane</text>',
            '<line x1="120" y1="200" x2="520" y2="120" stroke="#333" stroke-width="3"/>',
            '<text x="500" y="110" font-size="12">Club path</text>',
            '<circle cx="140" cy="195" r="6" fill="#1f77b4"/>',
            '<text x="90" y="200" font-size="12">Grip hub</text>',
            "</svg>",
        ]
    )


def fig_nesbit_fig11_schematic() -> str:
    w, h = 640, 320
    panels = [
        ("S1 scratch", "negative"),
        ("S2 5-hcp", "positive"),
        ("S3 13-hcp", "near zero"),
        ("S4 18-hcp", "positive"),
    ]
    lines = [_svg_header(w, h), '<text x="40" y="28" font-size="14">Nesbit &amp; Serrano Fig. 11 — qualitative subject trends (re-plot)</text>']
    for i, (label, trend) in enumerate(panels):
        x0 = 40 + i * 150
        color = "#d62728" if trend == "negative" else "#2ca02c" if trend == "positive" else "#888"
        lines.append(f'<rect x="{x0}" y="50" width="130" height="220" fill="#f7f7f7" stroke="#ccc"/>')
        lines.append(f'<text x="{x0+10}" y="75" font-size="12">{label}</text>')
        lines.append(f'<text x="{x0+10}" y="95" font-size="11">Impact trend: {trend}</text>')
        lines.append(f'<polyline fill="none" stroke="{color}" stroke-width="3" points="{x0+20},240 {x0+60},120 {x0+110},200"/>')
    lines.append("</svg>")
    return "\n".join(lines)


def main() -> None:
    payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    outputs = {
        "fig-transport-stations.svg": fig_transport_stations(payload),
        "fig-filter-cutoff-sweep.svg": fig_filter_sweep(payload),
        "fig-couple-vs-com.svg": fig_couple_timeseries(payload),
        "fig-swing-plane-schematic.svg": fig_swing_plane_schematic(),
        "fig-nesbit-fig11-schematic.svg": fig_nesbit_fig11_schematic(),
    }
    for name, svg in outputs.items():
        (FIG_DIR / name).write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
