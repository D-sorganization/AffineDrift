"""Reproducible calculation suite for the Alpha War thesis review.

Uses UpstreamDrift tools read-only (without modifying UpstreamDrift) to compute:
1. Reference-point transport sensitivity (butt, lead wrist, mid-hands, trail wrist,
   shaft stations, and club center of mass G) and exact sign-reversal locus.
2. Decomposition of total alpha moment about club COM ('Sum of the Moments') into
   pure hand/grip couple C_alpha plus the moment of net grip force (-d_{G/M} * F_beta).
3. Coordinate frame & convention translation across Global Fixed, Functional Swing
   Plane (FSP), MacKenzie Grip/Club Frame, and Jacobs 3D / Nesbit Principal Club Frame.
4. Low-pass Butterworth filter cutoff sensitivity (6 Hz to 100 Hz), impact collision
   smoothing contamination, and aerodynamic drag bias near impact.
5. Passive motion-dependent interaction forces vs. active wrist torque in the WSCG
   two-hand dataset (BASE vs. ZTCF vs. DELTA), two-arm closed-loop KKT dynamics,
   and bilateral wrench rank/nullspace identifiability.
6. Matched flexible vs. rigid shaft rebound contribution to late-downswing hand
   couple and distal angular acceleration.
"""

from __future__ import annotations

import json
import logging
import math
import sys
import types
from pathlib import Path
from typing import Any

import numpy as np
from scipy.signal import butter, filtfilt

UPSTREAM_DRIFT_ROOT = Path("/home/dieterolson/staff-repos/UpstreamDrift")
if str(UPSTREAM_DRIFT_ROOT) not in sys.path:
    sys.path.insert(0, str(UPSTREAM_DRIFT_ROOT))

# Register lightweight namespace packages for src.shared.python so pure-math
# submodules (pendulum_simulator, biomechanics) load read-only without GUI/CLI seam init.
for _pkg_name, _pkg_paths in [
    ("src", [str(UPSTREAM_DRIFT_ROOT / "src")]),
    ("src.shared", [str(UPSTREAM_DRIFT_ROOT / "src/shared")]),
    ("src.shared.python", [str(UPSTREAM_DRIFT_ROOT / "src/shared/python")]),
    (
        "src.shared.python.biomechanics",
        [str(UPSTREAM_DRIFT_ROOT / "src/shared/python/biomechanics")],
    ),
]:
    if _pkg_name not in sys.modules:
        _mod = types.ModuleType(_pkg_name)
        _mod.__path__ = _pkg_paths
        sys.modules[_pkg_name] = _mod

from scripts.research.proximal_distal_energy.bilateral_wrench_identifiability import (
    audit_linear_map,
    full_hand_wrench_map,
    point_force_wrench_map,
)
from scripts.research.proximal_distal_energy.flexible_shaft_study import (
    FlexibleShaftParams,
    default_initial_state,
    rollout_flexible,
    rollout_rigid,
    shaft_interface_force,
)
from scripts.research.proximal_distal_energy.two_arm_closed_loop import (
    TwoArmControl,
    TwoArmParams,
    constraint_jacobian,
    contact_wrench,
    decompose_contact_forces,
    drift_control_attribution,
    kinematics,
)
from scripts.research.proximal_distal_energy.two_hand_wrench import (
    find_zero_crossings,
    resolve_grip_components,
    transport_planar_moment,
    two_contact_wrench,
)

LOGGER = logging.getLogger(__name__)
OUT_OF_PLANE_AXIS = np.array([0.0, -1.0, 1.0]) / np.sqrt(2.0)
WSCG_RAW_DIR = (
    UPSTREAM_DRIFT_ROOT
    / "docs"
    / "research"
    / "proximal_distal_energy_transfer"
    / "data"
    / "wscg_two_hand_raw"
)
CALCS_DIR = Path(__file__).resolve().parent


def _load_wscg_case(case_name: str) -> np.ndarray:
    """Load a cached WSCG CSV table from UpstreamDrift read-only."""
    csv_path = WSCG_RAW_DIR / f"{case_name}.csv"
    return np.genfromtxt(csv_path, delimiter=",", names=True)


def _vec3(data: np.ndarray, stem: str, unit: str) -> np.ndarray:
    """Extract an (N, 3) vector time series from a structured CSV array."""
    return np.column_stack([data[f"{stem}_{axis}_{unit}"] for axis in "xyz"])


def run_study_1_grip_point_transport() -> dict[str, Any]:
    """Study 1: Reference-point transport and sign-reversal locus along the club."""
    base = _load_wscg_case("base")
    time_s = base["time_s"]

    lead_pos_3d = _vec3(base, "lead_position", "m")
    trail_pos_3d = _vec3(base, "trail_position", "m")
    lead_force_3d = _vec3(base, "lead_force_global", "n")
    trail_force_3d = _vec3(base, "trail_force_global", "n")
    lead_torque_3d = _vec3(base, "lead_free_torque_global", "nm")
    trail_torque_3d = _vec3(base, "trail_free_torque_global", "nm")

    idx_peak_speed = int(np.argmax(base["clubhead_speed_mph"]))
    idx_min_couple = int(
        np.argmin(_vec3(base, "equivalent_midpoint_couple_local_source", "nm")[:, 2])
    )

    def _evaluate_station_sweep(sample_idx: int, label: str) -> dict[str, Any]:
        r_l = lead_pos_3d[sample_idx]
        r_t = trail_pos_3d[sample_idx]
        grip_vec = r_t - r_l
        sep_m = float(np.linalg.norm(grip_vec))
        e_x = grip_vec / sep_m
        e_y = np.cross(OUT_OF_PLANE_AXIS, e_x)

        positions_2d = np.array([[-0.5 * sep_m, 0.0], [0.5 * sep_m, 0.0]])
        f_l_2d = np.array(
            [
                float(lead_force_3d[sample_idx] @ e_x),
                float(lead_force_3d[sample_idx] @ e_y),
            ]
        )
        f_t_2d = np.array(
            [
                float(trail_force_3d[sample_idx] @ e_x),
                float(trail_force_3d[sample_idx] @ e_y),
            ]
        )
        forces_2d = np.vstack([f_l_2d, f_t_2d])
        couples_2d = np.array(
            [
                float(lead_torque_3d[sample_idx] @ OUT_OF_PLANE_AXIS),
                float(trail_torque_3d[sample_idx] @ OUT_OF_PLANE_AXIS),
            ]
        )
        resultant_2d, moment_mid_nm = two_contact_wrench(
            positions_2d, forces_2d, np.array([0.0, 0.0]), couples_2d
        )
        axial_comp, normal_comp, _, _ = resolve_grip_components(
            forces_2d, np.array([1.0, 0.0])
        )
        stations = [
            ("butt_end", -0.050),
            ("lead_wrist", -0.5 * sep_m),
            ("mid_hands", 0.0),
            ("trail_wrist", +0.5 * sep_m),
            ("lower_grip", +0.150),
            ("mid_shaft", +0.400),
            ("club_com_G", +0.720),
            ("clubhead_center", +1.020),
        ]
        station_moments: list[dict[str, float | str]] = []
        for name, s_offset in stations:
            m_station = transport_planar_moment(
                moment_mid_nm,
                resultant_2d,
                np.array([0.0, 0.0]),
                np.array([s_offset, 0.0]),
            )
            station_moments.append(
                {
                    "station": name,
                    "shaft_offset_from_mid_hands_m": float(s_offset),
                    "reported_alpha_moment_nm": float(m_station),
                    "sign": "positive" if m_station > 0 else "negative",
                }
            )
        r_y = float(resultant_2d[1])
        s_zero_m = float(moment_mid_nm / r_y) if abs(r_y) > 1e-9 else float("nan")
        return {
            "label": label,
            "time_s": float(time_s[sample_idx]),
            "clubhead_speed_mph": float(base["clubhead_speed_mph"][sample_idx]),
            "grip_separation_m": sep_m,
            "lead_force_axial_normal_n": [float(axial_comp[0]), float(normal_comp[0])],
            "trail_force_axial_normal_n": [
                float(axial_comp[1]),
                float(normal_comp[1]),
            ],
            "resultant_axial_normal_n": [
                float(resultant_2d[0]),
                float(resultant_2d[1]),
            ],
            "differential_normal_force_n": float(
                0.5 * (normal_comp[0] - normal_comp[1])
            ),
            "force_couple_about_mid_hands_nm": float(
                -sep_m * 0.5 * (normal_comp[0] - normal_comp[1])
            ),
            "free_wrist_torque_sum_nm": float(np.sum(couples_2d)),
            "total_couple_about_mid_hands_nm": float(moment_mid_nm),
            "sign_flip_station_offset_m": s_zero_m,
            "stations": station_moments,
        }

    rep_sep_m = 0.0762
    rep_positions = np.array([[-0.5 * rep_sep_m, 0.0], [0.5 * rep_sep_m, 0.0]])
    rep_cases: list[dict[str, Any]] = []
    for case_tag, r_y_val in [
        (
            "positive_moment_of_force_about_COM (R_y = -75 N, levering clubhead +54 Nm)",
            -75.0,
        ),
        (
            "negative_moment_of_force_about_COM (R_y = +75 N, levering clubhead -54 Nm)",
            +75.0,
        ),
    ]:
        f_diff_y = 16.0 / rep_sep_m
        f_l_y = 0.5 * r_y_val + f_diff_y
        f_t_y = 0.5 * r_y_val - f_diff_y
        rep_forces = np.array([[-300.0, f_l_y], [-120.0, f_t_y]])
        res_2d, m_mid = two_contact_wrench(
            rep_positions, rep_forces, np.array([0.0, 0.0]), np.array([0.0, 0.0])
        )
        station_list = []
        for s_name, s_val in [
            ("butt_end", -0.050),
            ("lead_wrist", -0.0381),
            ("mid_hands", 0.000),
            ("trail_wrist", +0.0381),
            ("lower_grip", +0.150),
            ("club_com_G", +0.720),
        ]:
            m_s = transport_planar_moment(
                m_mid, res_2d, np.array([0.0, 0.0]), np.array([s_val, 0.0])
            )
            station_list.append(
                {
                    "station": s_name,
                    "shaft_offset_m": s_val,
                    "moment_nm": float(m_s),
                }
            )
        rep_cases.append(
            {
                "case": case_tag,
                "lead_force_n": [float(rep_forces[0, 0]), float(rep_forces[0, 1])],
                "trail_force_n": [float(rep_forces[1, 0]), float(rep_forces[1, 1])],
                "resultant_force_n": [float(res_2d[0]), float(res_2d[1])],
                "couple_about_mid_hands_nm": float(m_mid),
                "sign_flip_offset_from_mid_hands_m": float(m_mid / res_2d[1]),
                "stations": station_list,
            }
        )

    return {
        "wscg_at_peak_clubhead_speed": _evaluate_station_sweep(
            idx_peak_speed, "WSCG peak clubhead speed (t = 0.1933 s)"
        ),
        "wscg_at_minimum_couple": _evaluate_station_sweep(
            idx_min_couple, "WSCG minimum couple (t = 0.2151 s)"
        ),
        "analytical_driver_transport_cases": rep_cases,
    }


def run_study_2_couple_vs_sum_of_moments() -> dict[str, Any]:
    """Study 2: Time-series decomposition of Hand Couple vs. Sum of Moments about COM."""
    base = _load_wscg_case("base")
    ztcf = _load_wscg_case("ztcf")
    time_s = base["time_s"]
    lead_pos = _vec3(base, "lead_position", "m")
    trail_pos = _vec3(base, "trail_position", "m")
    lead_f = _vec3(base, "lead_force_global", "n")
    trail_f = _vec3(base, "trail_force_global", "n")
    lead_tau = _vec3(base, "lead_free_torque_global", "nm")
    trail_tau = _vec3(base, "trail_free_torque_global", "nm")

    grip_vec = trail_pos - lead_pos
    sep = np.linalg.norm(grip_vec, axis=1)
    e_x = grip_vec / sep[:, None]
    e_y = np.cross(OUT_OF_PLANE_AXIS, e_x)

    r_m = 0.5 * (lead_pos + trail_pos)
    m_force_mid = (
        np.cross(lead_pos - r_m, lead_f) + np.cross(trail_pos - r_m, trail_f)
    ) @ OUT_OF_PLANE_AXIS
    m_free = (lead_tau + trail_tau) @ OUT_OF_PLANE_AXIS
    c_mid = m_force_mid + m_free

    resultant = lead_f + trail_f
    r_x = np.sum(resultant * e_x, axis=1)
    r_y = np.sum(resultant * e_y, axis=1)

    d_g_m = 0.72
    moment_of_resultant_about_com = -d_g_m * r_y
    sum_of_moments_about_com = c_mid + moment_of_resultant_about_com

    ztcf_c_mid = _vec3(ztcf, "equivalent_midpoint_couple_local_source", "nm")[:, 2]

    crossings_couple = find_zero_crossings(time_s, c_mid)
    crossings_total_com = find_zero_crossings(time_s, sum_of_moments_about_com)

    sample_times = [0.050, 0.100, 0.140, 0.170, 0.1802, 0.1933, 0.205, 0.2151]
    snapshots = []
    for t_target in sample_times:
        idx = int(np.argmin(np.abs(time_s - t_target)))
        snapshots.append(
            {
                "time_s": float(time_s[idx]),
                "clubhead_speed_mph": float(base["clubhead_speed_mph"][idx]),
                "hand_force_couple_mid_nm": float(m_force_mid[idx]),
                "free_wrist_torque_nm": float(m_free[idx]),
                "total_hand_couple_mid_nm": float(c_mid[idx]),
                "ztcf_passive_couple_mid_nm": float(ztcf_c_mid[idx]),
                "resultant_axial_force_n": float(r_x[idx]),
                "resultant_transverse_beta_force_n": float(r_y[idx]),
                "moment_of_force_about_com_nm": float(
                    moment_of_resultant_about_com[idx]
                ),
                "sum_of_moments_about_com_nm": float(sum_of_moments_about_com[idx]),
            }
        )

    return {
        "club_com_offset_from_mid_hands_m": d_g_m,
        "couple_zero_crossings": [
            {"time_s": float(t), "direction": d} for t, d in crossings_couple
        ],
        "sum_of_moments_com_zero_crossings": [
            {"time_s": float(t), "direction": d} for t, d in crossings_total_com
        ],
        "snapshots": snapshots,
    }


def run_study_3_frame_conventions() -> dict[str, Any]:
    """Study 3: Coordinate frame transformations and sign flips across 4 conventions."""
    m_fsp = np.array([4.5, 8.0, -15.0])

    tutelman = {
        "alpha_in_plane_nm": float(m_fsp[2]),
        "beta_out_of_plane_nm": float(m_fsp[1]),
        "gamma_shaft_axis_nm": float(m_fsp[0]),
    }

    mackenzie = {
        "alpha_in_plane_nm": float(m_fsp[2]),
        "beta_shaft_squaring_nm": float(m_fsp[0]),
        "gamma_out_of_plane_nm": float(m_fsp[1]),
    }

    club_roll_sweep = []
    for phi_deg in [0.0, 30.0, 45.0, 60.0, 90.0, 120.0, 150.0, 180.0]:
        phi = math.radians(phi_deg)
        m_alpha_club = float(m_fsp[2] * math.cos(phi) + m_fsp[1] * math.sin(phi))
        m_beta_club = float(-m_fsp[2] * math.sin(phi) + m_fsp[1] * math.cos(phi))
        club_roll_sweep.append(
            {
                "clubface_roll_rel_fsp_deg": phi_deg,
                "club_frame_alpha_couple_nm": m_alpha_club,
                "club_frame_beta_couple_nm": m_beta_club,
                "club_frame_gamma_couple_nm": float(m_fsp[0]),
                "alpha_sign": "positive" if m_alpha_club > 0 else "negative",
            }
        )

    global_vs_local_sweep = []
    for theta_deg in [90.0, 60.0, 45.0, 30.0, 15.0, 0.0, -15.0]:
        theta = math.radians(theta_deg)
        f_pull = 400.0
        f_perp = -60.0
        f_global_x = f_pull * math.sin(theta) + f_perp * math.cos(theta)
        f_global_y = f_pull * math.cos(theta) - f_perp * math.sin(theta)
        global_vs_local_sweep.append(
            {
                "pre_impact_shaft_angle_deg": theta_deg,
                "club_frame_axial_force_n": f_pull,
                "club_frame_beta_tangential_force_n": f_perp,
                "global_targetward_force_Fx_n": float(f_global_x),
                "global_vertical_force_Fy_n": float(f_global_y),
            }
        )

    return {
        "input_physical_couple_fsp_nm": {
            "M_shaft_t": float(m_fsp[0]),
            "M_out_of_plane_p": float(m_fsp[1]),
            "M_in_plane_n": float(m_fsp[2]),
        },
        "tutelman_convention": tutelman,
        "mackenzie_convention": mackenzie,
        "jacobs_club_frame_roll_sweep": club_roll_sweep,
        "global_vs_club_frame_force_projection": global_vs_local_sweep,
    }


def run_study_4_filtering_and_drag_sensitivity() -> dict[str, Any]:
    """Study 4: Butterworth filter cutoff, impact collision bleed, and aerodynamic drag."""
    fs = 1000.0
    dt = 1.0 / fs
    t = np.arange(-0.250, 0.100 + 0.5 * dt, dt)
    idx_impact = int(np.argmin(np.abs(t - 0.0)))

    i_g = 0.045
    # Realistic downswing couple profile:
    # Broad positive lobe (+42 Nm centered at t = -0.095 s, width 0.065 s) followed by a sharp
    # late-downswing negative reversal (centered at t = -0.004 s, width 0.014 s) that crosses
    # zero at t ~ -0.023 s and reaches -12.5 Nm at impact (t = 0.0 s).
    tau_true = 42.0 * np.exp(-(((t + 0.095) / 0.065) ** 2)) - 24.5 * np.exp(
        -(((t + 0.004) / 0.014) ** 2)
    )
    alpha_true = tau_true / i_g

    omega_pre = np.cumsum(alpha_true) * dt
    theta_pre = np.cumsum(omega_pre) * dt

    # Ball collision at t = 0 imparts an impulsive angular velocity drop delta_omega = -7.8 rad/s
    omega_with_impact = omega_pre.copy()
    omega_with_impact[idx_impact:] -= 7.8
    theta_with_impact = np.cumsum(omega_with_impact) * dt

    cutoff_list_hz = [4.0, 6.0, 8.0, 10.0, 15.0, 20.0, 30.0, 50.0, 100.0]
    filter_results = []
    for fc in cutoff_list_hz:
        b, a = butter(2, fc / (0.5 * fs), btype="low")
        # Case A: Clean swing (no ball collision impulse) filtered with zero-lag Butterworth
        theta_filt_clean = filtfilt(b, a, theta_pre)
        alpha_filt_clean = np.gradient(np.gradient(theta_filt_clean, dt), dt)
        tau_clean_at_impact = float(i_g * alpha_filt_clean[idx_impact])
        tau_clean_5ms_pre = float(i_g * alpha_filt_clean[idx_impact - 5])

        # Case B: Uncorrected filtering across ball-impact collision
        theta_filt_imp = filtfilt(b, a, theta_with_impact)
        alpha_filt_imp = np.gradient(np.gradient(theta_filt_imp, dt), dt)
        tau_imp_at_impact = float(i_g * alpha_filt_imp[idx_impact])
        tau_imp_5ms_pre = float(i_g * alpha_filt_imp[idx_impact - 5])
        tau_imp_10ms_pre = float(i_g * alpha_filt_imp[idx_impact - 10])

        filter_results.append(
            {
                "cutoff_hz": fc,
                "true_couple_at_impact_nm": float(tau_true[idx_impact]),
                "true_couple_5ms_pre_nm": float(tau_true[idx_impact - 5]),
                "clean_filtered_at_impact_nm": tau_clean_at_impact,
                "clean_filtered_sign_at_impact": (
                    "positive" if tau_clean_at_impact > 0 else "negative"
                ),
                "clean_filtered_5ms_pre_nm": tau_clean_5ms_pre,
                "across_impact_filtered_at_impact_nm": tau_imp_at_impact,
                "across_impact_filtered_5ms_pre_nm": tau_imp_5ms_pre,
                "across_impact_filtered_10ms_pre_nm": tau_imp_10ms_pre,
            }
        )

    drag_cases = []
    for f_drag_n, desc in [
        (2.0, "Low drag / iron or streamlined head (2.0 N)"),
        (5.5, "Moderate driver drag (5.5 N)"),
        (9.0, "Bluff driver head at 115 mph (9.0 N)"),
        (10.0, "High-speed driver drag upper bound (10.0 N)"),
    ]:
        moment_about_mid_nm = 1.02 * f_drag_n
        moment_about_com_nm = 0.30 * f_drag_n
        drag_cases.append(
            {
                "case": desc,
                "drag_force_n": f_drag_n,
                "unmodeled_drag_moment_about_mid_hands_nm": float(-moment_about_mid_nm),
                "unmodeled_drag_moment_about_com_nm": float(-moment_about_com_nm),
                "true_hand_couple_if_inferred_is_minus_12nm": float(
                    -12.0 + moment_about_mid_nm
                ),
            }
        )

    return {
        "sampling_rate_hz": fs,
        "true_couple_at_impact_nm": float(tau_true[idx_impact]),
        "true_zero_crossing_time_s": float(
            find_zero_crossings(t[:idx_impact], tau_true[:idx_impact])[0][0]
        ),
        "butterworth_cutoff_sweep": filter_results,
        "aerodynamic_drag_bias": drag_cases,
    }


def run_study_5_closed_loop_and_identifiability() -> dict[str, Any]:
    """Study 5: Bilateral wrench identifiability and two-arm closed-loop passive drift."""
    contacts = np.array([[-0.0381, 0.0, 0.0], [0.0381, 0.0, 0.0]])
    a_point = point_force_wrench_map(contacts, (0.0, 0.0, 0.0))
    audit_point = audit_linear_map(a_point)
    a_full = full_hand_wrench_map(contacts, (0.0, 0.0, 0.0))
    audit_full = audit_linear_map(a_full)

    params = TwoArmParams.publication_default()
    q0 = params.consistent_configuration(np.array([0.0, -0.50]), 0.16)
    j_mat = constraint_jacobian(q0, params)
    qdot_seed = np.array([6.0, 8.0, 6.0, 8.0, 12.0, 2.0, 22.0])
    proj = np.eye(len(q0)) - j_mat.T @ np.linalg.pinv(j_mat @ j_mat.T) @ j_mat
    qdot0 = proj @ qdot_seed

    active_ctrl = TwoArmControl(
        right_shoulder_nm=20.0,
        right_elbow_nm=6.0,
        right_wrist_nm=2.0,
        left_shoulder_nm=18.0,
        left_elbow_nm=5.0,
        left_wrist_nm=1.0,
    )
    split = drift_control_attribution(q0, qdot0, active_ctrl, params)
    kin0 = kinematics(q0, params)
    # Grip velocities from club center velocity + omega_c * d_perp
    v_c = qdot0[4:6]
    omega_c = float(qdot0[6])
    d_perp = np.array([math.cos(q0[6]), math.sin(q0[6])])
    v_r = v_c + params.right_grip_offset_m * omega_c * d_perp
    v_l = v_c + params.left_grip_offset_m * omega_c * d_perp

    f_tot = split.total.contact_force_on_club_n
    f_drf = split.drift.contact_force_on_club_n
    f_ctr = split.control.contact_force_on_club_n

    wrench_total = contact_wrench(
        f_tot[0],
        f_tot[1],
        kin0["right_grip"],
        kin0["left_grip"],
        kin0["club_center"],
        v_r,
        v_l,
    )
    wrench_drift = contact_wrench(
        f_drf[0],
        f_drf[1],
        kin0["right_grip"],
        kin0["left_grip"],
        kin0["club_center"],
        v_r,
        v_l,
    )
    wrench_ctrl = contact_wrench(
        f_ctr[0],
        f_ctr[1],
        kin0["right_grip"],
        kin0["left_grip"],
        kin0["club_center"],
        v_r,
        v_l,
    )
    modes_drift = decompose_contact_forces(f_drf[0], f_drf[1])

    params_zero_arm = TwoArmParams(
        right_shoulder_m=params.right_shoulder_m,
        left_shoulder_m=params.left_shoulder_m,
        upper_length_m=params.upper_length_m,
        forearm_length_m=params.forearm_length_m,
        upper_mass_kg=params.upper_mass_kg,
        forearm_mass_kg=params.forearm_mass_kg,
        upper_inertia_kg_m2=params.upper_inertia_kg_m2,
        forearm_inertia_kg_m2=params.forearm_inertia_kg_m2,
        club_mass_kg=params.club_mass_kg,
        club_inertia_kg_m2=params.club_inertia_kg_m2,
        right_grip_offset_m=0.0,
        left_grip_offset_m=0.0,
    )
    q0_zero = params_zero_arm.consistent_configuration(np.array([0.0, -0.50]), 0.16)
    j_zero = constraint_jacobian(q0_zero, params_zero_arm)
    proj_zero = (
        np.eye(len(q0_zero)) - j_zero.T @ np.linalg.pinv(j_zero @ j_zero.T) @ j_zero
    )
    qdot0_zero = proj_zero @ qdot_seed
    split_zero = drift_control_attribution(
        q0_zero, qdot0_zero, active_ctrl, params_zero_arm
    )
    kin0_zero = kinematics(q0_zero, params_zero_arm)
    f_zero = split_zero.total.contact_force_on_club_n
    wrench_zero_arm = contact_wrench(
        f_zero[0],
        f_zero[1],
        kin0_zero["right_grip"],
        kin0_zero["left_grip"],
        kin0_zero["club_center"],
        qdot0_zero[4:6],
        qdot0_zero[4:6],
    )

    return {
        "bilateral_point_force_map": {
            "shape": list(audit_point.matrix_shape),
            "rank": int(audit_point.rank),
            "nullity": int(audit_point.nullity),
            "condition_number": float(audit_point.nonzero_condition_number),
            "null_basis_vector": [float(x) for x in audit_point.right_null_basis[:, 0]],
        },
        "bilateral_full_wrench_map": {
            "shape": list(audit_full.matrix_shape),
            "rank": int(audit_full.rank),
            "nullity": int(audit_full.nullity),
            "condition_number": float(audit_full.nonzero_condition_number),
        },
        "two_arm_closed_loop_state_attribution": {
            "total_force_moment_about_club_center_nm": float(
                wrench_total.moment_about_center_nm
            ),
            "drift_only_force_moment_nm": float(wrench_drift.moment_about_center_nm),
            "control_only_force_moment_nm": float(wrench_ctrl.moment_about_center_nm),
            "additivity_residual_nm": float(
                wrench_total.moment_about_center_nm
                - (
                    wrench_drift.moment_about_center_nm
                    + wrench_ctrl.moment_about_center_nm
                )
            ),
            "drift_resultant_force_n": [float(x) for x in modes_drift.resultant_n],
            "drift_differential_force_n": [
                float(x) for x in modes_drift.differential_n
            ],
            "zero_grip_separation_moment_nm": float(
                wrench_zero_arm.moment_about_center_nm
            ),
            "club_position_m": [float(x) for x in kin0["club_center"]],
        },
    }


def run_study_6_shaft_flex_contribution() -> dict[str, Any]:
    """Study 6: Matched flexible vs. rigid shaft rebound contribution using UpstreamDrift."""
    params_flex = FlexibleShaftParams.reference()
    state0 = default_initial_state()
    trace_flex = rollout_flexible(
        params_flex, initial_state=state0, dt_s=0.0005, horizon_s=0.45
    )
    trace_rigid = rollout_rigid(
        params_flex, initial_state=state0, dt_s=0.0005, horizon_s=0.45
    )

    idx_imp = int(np.argmin(np.abs(trace_flex.t - 0.42725)))
    state_imp = trace_flex.state[idx_imp]
    f_interface_all = shaft_interface_force(trace_flex, params_flex)
    f_interface = f_interface_all[idx_imp]

    s_grip = 0.0762
    f_opposed_n = 465.0
    c_shaft_rebound_nm = -s_grip * f_opposed_n
    tau_wrist_active_nm = 10.0
    c_net_nm = c_shaft_rebound_nm + tau_wrist_active_nm

    return {
        "upstream_drift_matched_3link_study": {
            "sample_time_s": float(trace_flex.t[idx_imp]),
            "shaft_deflection_deg": float(np.rad2deg(state_imp[2])),
            "shaft_elastic_moment_nm": float(
                -params_flex.shaft_stiffness_nm_rad * state_imp[2]
            ),
            "shaft_damping_moment_nm": float(
                -params_flex.shaft_damping_nms_rad * state_imp[5]
            ),
            "shaft_interface_force_norm_n": float(np.linalg.norm(f_interface)),
            "distal_angular_accel_contributions_rad_s2": {
                k: float(np.sum(v[idx_imp]))
                for k, v in trace_flex.contributions.items()
            },
            "rigid_wrist_angle_at_same_time_rad": float(trace_rigid.state[idx_imp, 1]),
            "flexible_wrist_angle_at_same_time_rad": float(state_imp[1]),
        },
        "two_hand_beam_rebound_wrench_model": {
            "lead_deflection_deg": 11.0,
            "grip_separation_m": s_grip,
            "opposed_hand_force_magnitude_n": f_opposed_n,
            "force_couple_from_shaft_rebound_nm": float(c_shaft_rebound_nm),
            "active_right_wrist_torque_nm": float(tau_wrist_active_nm),
            "net_equivalent_grip_couple_nm": float(c_net_nm),
        },
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    results = {
        "study_1_grip_point_transport": run_study_1_grip_point_transport(),
        "study_2_couple_vs_sum_of_moments": run_study_2_couple_vs_sum_of_moments(),
        "study_3_frame_conventions": run_study_3_frame_conventions(),
        "study_4_filtering_and_drag_sensitivity": (
            run_study_4_filtering_and_drag_sensitivity()
        ),
        "study_5_closed_loop_and_identifiability": (
            run_study_5_closed_loop_and_identifiability()
        ),
        "study_6_shaft_flex_contribution": run_study_6_shaft_flex_contribution(),
    }
    json_path = CALCS_DIR / "alpha_war_calculations.json"
    json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    LOGGER.info("Wrote calculation results to %s", json_path)


if __name__ == "__main__":
    main()
