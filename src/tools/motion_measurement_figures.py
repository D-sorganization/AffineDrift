"""Generate static figures F1-F8 from MM-2 JSON outputs (MM-3, #5411).

Every figure is synthetic or analytic and labelled accordingly. Compact SVG rendering.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

FIGURE_NAMES: tuple[str, ...] = (
    "f1_cardan_sequences.svg",
    "f2_gimbal_lock.svg",
    "f3_angle_unwrap.svg",
    "f4_orthogonality_drift.svg",
    "f5_quaternion_continuity.svg",
    "f6_helical_axis_error.svg",
    "f7_angular_velocity_differences.svg",
    "f8_xfactor_variants.svg",
)

FIGURE_METADATA: dict[str, dict[str, str]] = {
    "f1_cardan_sequences.svg": {
        "title": "F1: Cardan Sequence Dependence",
        "label": "synthetic",
        "alt_text": "Comparison of intrinsic Cardan sequences XYZ vs ZYX on an identical rotation matrix, demonstrating sequence-dependent angular divergence. Labelled synthetic.",
    },
    "f2_gimbal_lock.svg": {
        "title": "F2: Gimbal Lock Singularity vs Rotation Vector",
        "label": "model_scenario",
        "alt_text": "Demonstration of Euler gimbal lock near 90 degrees pitch causing indeterminate yaw/roll difference, contrasted with the rotation vector remaining smooth. Labelled model_scenario.",
    },
    "f3_angle_unwrap.svg": {
        "title": "F3: Turn Angle Phase Wrapping and Unwrapping",
        "label": "synthetic",
        "alt_text": "Trajectory of turn angle wrapping showing a 2-pi jump across +/-180 degrees boundary, contrasted with continuous unwrapped trajectory. Labelled synthetic.",
    },
    "f4_orthogonality_drift.svg": {
        "title": "F4: Matrix Orthogonality Drift and SVD Projection",
        "label": "model_scenario",
        "alt_text": "Numerical matrix orthogonality drift under perturbation and SVD re-orthogonalization restoring det(R) = 1. Labelled model_scenario.",
    },
    "f5_quaternion_continuity.svg": {
        "title": "F5: Quaternion Component-Wise Smoothing and Hemisphere Continuity",
        "label": "synthetic",
        "alt_text": "Moving-average quaternion smoothing showing collapse of norm without hemisphere tracking vs preserved unit norm with sign continuity. Labelled synthetic.",
    },
    "f6_helical_axis_error.svg": {
        "title": "F6: Helical Axis Direction Error vs Step Size",
        "label": "synthetic",
        "alt_text": "Finite versus instantaneous helical axis error across step sizes, showing noise amplification at small angles and kinematic drift at large angles. Labelled synthetic.",
    },
    "f7_angular_velocity_differences.svg": {
        "title": "F7: Angular Velocity Poisson Kinematics vs Euler Differences",
        "label": "synthetic",
        "alt_text": "Comparison of true angular velocity from Poisson rotation differences against naive Euler angle time differentiation under noise and near gimbal lock. Labelled synthetic.",
    },
    "f8_xfactor_variants.svg": {
        "title": "F8: Golf Swing X-Factor Variant Discrepancy",
        "label": "model_scenario",
        "alt_text": "Comparison of golf swing X-factor computation variants (plane projection vs Cardan joint coordinate system) on a synthetic swing path. Labelled model_scenario.",
    },
}


def _card(title: str, label: str, alt_text: str, inner: str) -> str:
    """Wrap figure content in a labelled, accessible SVG card."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 320" width="600" height="320">'
        f'<rect width="600" height="320" fill="#f8fafc" rx="8"/>'
        f'<text x="24" y="34" font-family="sans-serif" font-size="15" font-weight="bold" fill="#17324d">{title}</text>'
        f'<rect x="476" y="16" width="100" height="22" rx="4" fill="#e2e8f0"/>'
        f'<text x="526" y="31" font-family="sans-serif" font-size="11" fill="#475569" text-anchor="middle">{label}</text>'
        f"<title>{title}</title><desc>{label}: {alt_text}</desc>{inner}</svg>"
    )


def render_figure(name: str, data: dict[str, Any]) -> str:
    """Render a named MM-3 SVG figure from MM-2 fixture data."""
    meta = FIGURE_METADATA[name]
    title, label, alt = meta["title"], meta["label"], meta["alt_text"]
    if name == "f1_cardan_sequences.svg":
        c = data["cardan"]
        inner = (
            f'<rect x="40" y="60" width="520" height="220" fill="#fff" stroke="#cbd5e1" rx="6"/>'
            f'<text x="60" y="95" font-family="sans-serif" font-size="13" fill="#1e293b">Decomposed into intrinsic sequences (rad):</text>'
            f'<text x="60" y="135" font-family="monospace" font-size="13" fill="#0369a1">XYZ: {[f"{x:.2f}" for x in c["xyz_rad"]]}</text>'
            f'<text x="60" y="165" font-family="monospace" font-size="13" fill="#0f766e">ZYX: {[f"{x:.2f}" for x in c["zyx_rad"]]}</text>'
            f'<text x="60" y="210" font-family="sans-serif" font-size="13" font-weight="bold" fill="#b91c1c">Max difference: {c["max_diff_rad"]:.2f} rad (sequence dependent)</text>'
            f'<text x="60" y="250" font-family="sans-serif" font-size="11" fill="#64748b">Convention card required: no sequence is universally correct.</text>'
        )
    elif name == "f2_gimbal_lock.svg":
        inner = (
            '<rect x="40" y="60" width="520" height="220" fill="#fff" stroke="#cbd5e1" rx="6"/>'
            '<text x="60" y="95" font-family="sans-serif" font-size="13" fill="#1e293b">Middle Cardan pitch = 90.0° (pi/2 rad):</text>'
            '<text x="60" y="135" font-family="sans-serif" font-size="12" fill="#b91c1c">Euler Cardan (ZYX): Gimbal lock detected (roll/yaw indeterminate)</text>'
            '<text x="60" y="170" font-family="sans-serif" font-size="12" fill="#15803d">Rotation Vector (rotvec): Continuous, well-conditioned (norm = 1.571 rad)</text>'
            '<text x="60" y="235" font-family="sans-serif" font-size="11" fill="#64748b">Trade-off: coordinate singularities vs parameter redundancy. Neither is universally correct.</text>'
        )
    elif name == "f3_angle_unwrap.svg":
        inner = (
            f'<rect x="40" y="60" width="520" height="220" fill="#fff" stroke="#cbd5e1" rx="6"/>'
            f'<text x="60" y="95" font-family="sans-serif" font-size="13" fill="#1e293b">Angle continuity across +/-180° boundary:</text>'
            f'<text x="60" y="140" font-family="sans-serif" font-size="12" fill="#dc2626">Wrapped series jump: {data["unwrap"]["wrapped_max_jump_rad"]:.2f} rad</text>'
            f'<text x="60" y="180" font-family="sans-serif" font-size="12" fill="#0284c7">Unwrapped continuous series: jump &lt; {data["unwrap"]["unwrapped_max_jump_rad"]:.2f} rad</text>'
            f'<text x="60" y="245" font-family="sans-serif" font-size="11" fill="#64748b">Differentiating wrapped angles injects false impulse spikes into velocities.</text>'
        )
    elif name == "f4_orthogonality_drift.svg":
        inner = (
            f'<rect x="40" y="60" width="520" height="220" fill="#fff" stroke="#cbd5e1" rx="6"/>'
            f'<text x="60" y="95" font-family="sans-serif" font-size="13" fill="#1e293b">Matrix integration drift vs SVD projection:</text>'
            f'<text x="60" y="140" font-family="sans-serif" font-size="12" fill="#991b1b">Drifted matrix det error: {data["orthogonality"]["drifted_det_error"]:.3f}</text>'
            f'<text x="60" y="180" font-family="sans-serif" font-size="12" fill="#166534">SVD re-orthogonalised det error: &lt; 1e-12 (proper SO(3))</text>'
            f'<text x="60" y="245" font-family="sans-serif" font-size="11" fill="#64748b">SVD projection restores R^T R = I and det(R) = +1 without shearing.</text>'
        )
    elif name == "f5_quaternion_continuity.svg":
        q = data["quaternion"]
        inner = (
            f'<rect x="40" y="60" width="520" height="220" fill="#fff" stroke="#cbd5e1" rx="6"/>'
            f'<text x="60" y="95" font-family="sans-serif" font-size="13" fill="#1e293b">Moving-average filtering (window={q["window"]}):</text>'
            f'<text x="60" y="140" font-family="sans-serif" font-size="12" fill="#b91c1c">Without hemisphere tracking: min norm = {q["min_norm_without_continuity"]:.2f} (collapses)</text>'
            f'<text x="60" y="180" font-family="sans-serif" font-size="12" fill="#15803d">With hemisphere continuity: min norm = {q["min_norm_with_continuity"]:.2f} (preserved)</text>'
            f'<text x="60" y="245" font-family="sans-serif" font-size="11" fill="#64748b">Antipodal double-cover requires sign tracking before component smoothing.</text>'
        )
    elif name == "f6_helical_axis_error.svg":
        h = data["helical_axis"]
        inner = (
            f'<rect x="40" y="60" width="520" height="220" fill="#fff" stroke="#cbd5e1" rx="6"/>'
            f'<text x="60" y="95" font-family="sans-serif" font-size="13" fill="#1e293b">Helical axis estimation vs step size (sigma={h["sigma"]}):</text>'
            f'<text x="60" y="140" font-family="sans-serif" font-size="12" fill="#0369a1">Small step {h["steps_rad"][0]} rad: error = {h["mean_axis_error_rad"][0]:.3f} rad (noise-limited)</text>'
            f'<text x="60" y="180" font-family="sans-serif" font-size="12" fill="#334155">Moving axis error is U-shaped: noise at small steps, kinematic bias at large steps.</text>'
            f'<text x="60" y="245" font-family="sans-serif" font-size="11" fill="#64748b">Woltring (1985): finite screw axis is ill-conditioned near zero rotation.</text>'
        )
    elif name == "f7_angular_velocity_differences.svg":
        av = data["angular_velocity"]["pitch_30_deg"]
        inner = (
            f'<rect x="40" y="60" width="520" height="220" fill="#fff" stroke="#cbd5e1" rx="6"/>'
            f'<text x="60" y="95" font-family="sans-serif" font-size="13" fill="#1e293b">Angular velocity ω computation comparison:</text>'
            f'<text x="60" y="140" font-family="sans-serif" font-size="12" fill="#15803d">Poisson difference error: {av["poisson_max_error"]:.1e} rad/s</text>'
            f'<text x="60" y="180" font-family="sans-serif" font-size="12" fill="#b91c1c">Naive Euler difference error: {av["euler_difference_max_error"]:.2f} rad/s</text>'
            f'<text x="60" y="245" font-family="sans-serif" font-size="11" fill="#64748b">Euler angle rates are not angular velocity: R_dot = [omega]_x R.</text>'
        )
    else:  # f8_xfactor_variants.svg
        x = data["xfactor"]
        inner = (
            f'<rect x="40" y="60" width="520" height="220" fill="#fff" stroke="#cbd5e1" rx="6"/>'
            f'<text x="60" y="95" font-family="sans-serif" font-size="13" fill="#1e293b">X-factor variants on synthetic swing:</text>'
            f'<text x="60" y="135" font-family="sans-serif" font-size="12" fill="#0369a1">Plane-projection peak: {x["plane_peak_deg"]:.1f}°</text>'
            f'<text x="60" y="165" font-family="sans-serif" font-size="12" fill="#0f766e">Cardan / JCS axial peak: {x["cardan_peak_deg"]:.1f}°</text>'
            f'<text x="60" y="200" font-family="sans-serif" font-size="13" font-weight="bold" fill="#b91c1c">Spread between methods: {x["spread_deg"]:.1f}°</text>'
            f'<text x="60" y="245" font-family="sans-serif" font-size="11" fill="#64748b">Kwon (2013) &amp; Brown (2013): conventions cannot be compared interchangeably.</text>'
        )
    return _card(title, label, alt, inner)


def generate_figures(json_path: Path, output_dir: Path) -> list[Path]:
    """Generate all 8 MM-3 SVG figures from an MM-2 JSON fixture file."""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    for name in FIGURE_NAMES:
        path = output_dir / name
        path.write_text(render_figure(name, data) + "\n", encoding="utf-8")
        generated.append(path)
    return generated


def main() -> None:
    """CLI entry point for generating MM-3 figures from MM-2 JSON."""
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_path", type=Path, help="Path to MM-2 fixture JSON")
    parser.add_argument("output_dir", type=Path, help="Directory to save generated SVGs")
    args = parser.parse_args()
    paths = generate_figures(args.json_path, args.output_dir)
    logging.getLogger(__name__).info("Generated %d figures in %s", len(paths), args.output_dir)


if __name__ == "__main__":
    main()
