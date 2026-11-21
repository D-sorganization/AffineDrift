"""Reproduce published proximal-distal monograph numerical claims from pinned artifacts."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np

LOGGER = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
UNCERTAINTY_JSON = REPO_ROOT / "data/illustrations/uncertainty_control_study.json"
UNCERTAINTY_NPZ = REPO_ROOT / "data/illustrations/uncertainty_control_study.npz"
TRANSMISSION_CLOSURE_JSON = (
    REPO_ROOT / "data/proximal_distal_energy_transfer/transmission_robustness_closure_snapshot.json"
)

PROGRAM_ORDER = (
    "passive_wrist",
    "early_drive",
    "late_drive",
    "restrain_then_drive",
    "higher_impedance",
    "later_release",
    "lower_drive",
    "early_restrain",
)

DELIVERY_SPEED_INDEX = 0
FACE_PATH_INDEX = 1


@dataclass(frozen=True)
class H4HeldOutContrast:
    """Held-out lower-tail speed contrast for early restrain versus late drive."""

    held_out_samples: int
    early_restrain_q10_m_s: float
    late_drive_q10_m_s: float
    speed_delta_q10_m_s: float
    speed_delta_fraction: float
    paired_speed_delta_min_m_s: float
    paired_speed_delta_median_m_s: float
    paired_speed_delta_max_m_s: float
    early_restrain_face_path_mean_deg: float
    late_drive_face_path_mean_deg: float


@dataclass(frozen=True)
class IntegratorClosure:
    """Constraint and work-energy closure for the shared 4 ms integrator."""

    step_s: float
    maximum_normalized_work_energy_residual: float
    maximum_pathway_residual_j: float
    maximum_position_constraint_m: float
    maximum_velocity_constraint_m_s: float
    maximum_kkt_residual: float | None
    maximum_contact_power_residual_w: float


@dataclass(frozen=True)
class TorqueProgramCounts:
    """Row and distinct-program counts for the E1 onset sweep."""

    program_rows: int
    distinct_programs: int
    duplicates_at_zero_onset_per_shoulder: int


def _interpolated_percentile(values: np.ndarray, percentile: float) -> float:
    """Linearly interpolate an order statistic (Hyndman type 7 style for small n)."""
    if values.ndim != 1:
        raise ValueError("values must be one-dimensional")
    if values.size == 0:
        raise ValueError("values must not be empty")
    if not 0.0 <= percentile <= 100.0:
        raise ValueError("percentile must be in [0, 100]")
    ordered = np.sort(values)
    if ordered.size == 1:
        return float(ordered[0])
    position = 1.0 + (percentile / 100.0) * (ordered.size - 1)
    lower_index = int(np.floor(position)) - 1
    upper_index = min(lower_index + 1, ordered.size - 1)
    weight = position - np.floor(position)
    return float((1.0 - weight) * ordered[lower_index] + weight * ordered[upper_index])


def count_e1_torque_programs() -> TorqueProgramCounts:
    """Count program rows and distinct torque schedules in the registered E1 sweep."""
    onsets = np.arange(0.0, 0.351, 0.025)
    restrain_levels = (5.0, 10.0)
    rows_per_shoulder = 1 + len(onsets) + len(onsets) * len(restrain_levels)
    distinct_per_shoulder: set[str] = {"passive"}
    for onset in onsets:
        if onset == 0.0:
            distinct_per_shoulder.add("timed_drive:0")
        else:
            distinct_per_shoulder.add(f"drive:{onset:.6f}")
            for restrain in restrain_levels:
                distinct_per_shoulder.add(f"restrain:{onset:.6f}:{restrain}")
    return TorqueProgramCounts(
        program_rows=2 * rows_per_shoulder,
        distinct_programs=2 * len(distinct_per_shoulder),
        duplicates_at_zero_onset_per_shoulder=len(restrain_levels),
    )


def load_integrator_closure(path: Path = TRANSMISSION_CLOSURE_JSON) -> IntegratorClosure:
    """Load pinned work-energy closure for the 4 ms projected integrator."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    closure = payload["closure"]
    return IntegratorClosure(
        step_s=float(payload["integrator_step_s"]),
        maximum_normalized_work_energy_residual=float(
            closure["maximum_normalized_pathway_residual"]
        ),
        maximum_pathway_residual_j=float(closure["maximum_pathway_residual_j"]),
        maximum_position_constraint_m=float(closure["maximum_position_constraint_m"]),
        maximum_velocity_constraint_m_s=float(closure["maximum_velocity_constraint_m_s"]),
        maximum_kkt_residual=None,
        maximum_contact_power_residual_w=float(closure["maximum_contact_power_residual_w"]),
    )


def load_uncertainty_integrator_closure(
    path: Path = UNCERTAINTY_JSON,
) -> dict[str, float]:
    """Load constraint-only closure recorded for the uncertainty-control rollouts."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    closure = payload["closure"]
    return {key: float(value) for key, value in closure.items()}


def compute_h4_held_out_contrast(
    json_path: Path = UNCERTAINTY_JSON,
    npz_path: Path = UNCERTAINTY_NPZ,
) -> H4HeldOutContrast:
    """Compute the H4 held-out speed contrast and paired per-case differences."""
    study = json.loads(json_path.read_text(encoding="utf-8"))
    held_out_samples = int(study["design"]["held_out_samples"])
    archive = np.load(npz_path)
    held_out_outputs = archive["held_out_outputs"]
    early_index = PROGRAM_ORDER.index("early_restrain")
    late_index = PROGRAM_ORDER.index("late_drive")
    early_speeds = held_out_outputs[early_index, :, DELIVERY_SPEED_INDEX]
    late_speeds = held_out_outputs[late_index, :, DELIVERY_SPEED_INDEX]
    paired_delta = early_speeds - late_speeds
    early_q10 = _interpolated_percentile(early_speeds, 10.0)
    late_q10 = _interpolated_percentile(late_speeds, 10.0)
    candidates = study["control_comparison"]["candidates"]
    early_summary = next(row for row in candidates if row["name"] == "early_restrain")
    late_summary = next(row for row in candidates if row["name"] == "late_drive")
    return H4HeldOutContrast(
        held_out_samples=held_out_samples,
        early_restrain_q10_m_s=early_q10,
        late_drive_q10_m_s=late_q10,
        speed_delta_q10_m_s=early_q10 - late_q10,
        speed_delta_fraction=(early_q10 - late_q10) / late_q10,
        paired_speed_delta_min_m_s=float(np.min(paired_delta)),
        paired_speed_delta_median_m_s=float(np.median(paired_delta)),
        paired_speed_delta_max_m_s=float(np.max(paired_delta)),
        early_restrain_face_path_mean_deg=float(
            early_summary["held_out"]["face_path_error_mean_deg"]
        ),
        late_drive_face_path_mean_deg=float(late_summary["held_out"]["face_path_error_mean_deg"]),
    )


def render_verification_report() -> str:
    """Build a human-readable report of the reproduced monograph numbers."""
    h4 = compute_h4_held_out_contrast()
    closure = load_integrator_closure()
    constraint_closure = load_uncertainty_integrator_closure()
    programs = count_e1_torque_programs()
    work_energy_pct = 100.0 * closure.maximum_normalized_work_energy_residual
    h4_speed_pct = 100.0 * h4.speed_delta_fraction
    lines = [
        "Proximal-distal monograph numerical claim reproduction",
        f"H4 held-out n={h4.held_out_samples}: q10 early_restrain={h4.early_restrain_q10_m_s:.3f} m/s,",
        f"  late_drive={h4.late_drive_q10_m_s:.3f} m/s (delta {h4.speed_delta_q10_m_s:.3f} m/s,",
        f"  {h4_speed_pct:.2f}% of late-drive q10).",
        "  Paired per-case speed deltas (m/s):",
        f"  min={h4.paired_speed_delta_min_m_s:.3f},",
        f"  median={h4.paired_speed_delta_median_m_s:.3f},",
        f"  max={h4.paired_speed_delta_max_m_s:.3f}.",
        f"4 ms integrator worst normalized work-energy residual: {work_energy_pct:.2f}%",
        f"  ({closure.maximum_pathway_residual_j:.3f} J on the registered pathway audit).",
        "Uncertainty-control constraint residuals (same integrator, no work-energy field in JSON):",
        f"  position {constraint_closure['maximum_position_constraint_m']:.3e} m,",
        f"  contact-power {constraint_closure['maximum_contact_power_residual_w']:.3e} W.",
        f"E1 torque programs: {programs.program_rows} rows, {programs.distinct_programs} distinct",
        f"  ({programs.duplicates_at_zero_onset_per_shoulder} duplicate restrain rows per shoulder at",
        "  t_on=0).",
    ]
    return "\n".join(lines)


def main() -> None:
    """Print the verification report."""
    logging.basicConfig(level=logging.INFO)
    print(render_verification_report())


if __name__ == "__main__":
    main()
