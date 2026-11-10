"""Preregistered Option A comparison: correction authority vs tracking-error baseline (#5209)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from typing import Any, Literal, cast

import numpy as np

from src.affine_control.correction_authority_contract import (
    preregistered_humanoid_correction_authority_protocol,
)
from src.affine_control.correction_authority_evaluator import (
    CorrectionAuthorityStepResult,
    Indeterminate,
    LTVLinearizationStep,
    evaluate_correction_authority_along_trajectory,
    horizon_authority_sweep,
)
from src.affine_control.option_a_trace import OptionATrace, load_verified_trace
from src.affine_control.reachability_protocol import HypothesisResult

RESULT_SCHEMA_VERSION = "affinedrift.option_a.comparison_result/v1"
DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "humanoid_robotics" / "option_a"
RESULT_PATH = DATA_DIR / "comparison_result_v1.json"
LINK_LENGTHS = (1.0, 1.0)
METRE_TASK_TOLERANCE_M = 0.05
RAD_TASK_DIRECTION = np.array([1.0, 1.0, 0.0, 0.0], dtype=np.float64) / sqrt(2.0)
ILL_CONDITIONED_MODE: Literal["indeterminate"] = "indeterminate"


@dataclass(frozen=True)
class TrialDetectionRecord:
    """Per-trial detector times and lead time relative to the fixture horizon end."""

    outcome: str
    baseline_flag_time_s: float | None
    correction_authority_flag_time_s: float | None
    failure_time_s: float | None
    lead_time_baseline_s: float | None
    lead_time_correction_authority_s: float | None
    control_effort: float
    indeterminate_steps: int


@dataclass(frozen=True)
class OptionAComparisonResult:
    """Frozen metrics bundle for regression and claim-audit evidence."""

    schema_version: str
    payload_sha256: str
    trials: tuple[TrialDetectionRecord, ...]
    detection_rates: dict[str, float]
    median_lead_time_baseline_s: float | None
    median_lead_time_correction_authority_s: float | None
    median_lead_time_advantage_s: float | None
    mean_successful_trial_effort: float
    horizon_sweep_monotone: bool
    horizon_sweep_violations: tuple[str, ...]
    total_indeterminate_steps: int
    rad_metre_outcome_disagreement_rate: float
    hypothesis_results: tuple[HypothesisResult, ...]

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dict with stable float rounding."""
        return {
            "schema_version": self.schema_version,
            "payload_sha256": self.payload_sha256,
            "trials": [record.__dict__ for record in self.trials],
            "detection_rates": self.detection_rates,
            "median_lead_time_baseline_s": self.median_lead_time_baseline_s,
            "median_lead_time_correction_authority_s": self.median_lead_time_correction_authority_s,
            "median_lead_time_advantage_s": self.median_lead_time_advantage_s,
            "mean_successful_trial_effort": self.mean_successful_trial_effort,
            "horizon_sweep_monotone": self.horizon_sweep_monotone,
            "horizon_sweep_violations": list(self.horizon_sweep_violations),
            "total_indeterminate_steps": self.total_indeterminate_steps,
            "rad_metre_outcome_disagreement_rate": self.rad_metre_outcome_disagreement_rate,
            "hypothesis_results": [
                {
                    "hypothesis_id": item.hypothesis_id,
                    "outcome": item.outcome,
                    "estimate": item.estimate,
                    "uncertainty_interval": item.uncertainty_interval,
                    "interpretation": item.interpretation,
                }
                for item in self.hypothesis_results
            ],
        }


def _planar_tip_xy(joint_angles: np.ndarray) -> np.ndarray:
    """Return the unit-length planar distal-tip position for the declared double pendulum."""
    length_a, length_b = LINK_LENGTHS
    theta_a, theta_b = float(joint_angles[0]), float(joint_angles[1])
    x_pos = length_a * np.sin(theta_a) + length_b * np.sin(theta_a + theta_b)
    y_pos = length_a * np.cos(theta_a) + length_b * np.cos(theta_a + theta_b)
    return np.array([x_pos, y_pos], dtype=np.float64)


def _terminal_rad_pass(trace: OptionATrace, trial: int) -> bool:
    """Return whether joint-configuration error stays within the rad-space recovery threshold."""
    states = trace.x[trial]
    onset = trace.onset_step(trial)
    config_error = float(np.linalg.norm(states[-1, :2] - states[onset, :2]))
    return config_error <= trace.recovery_threshold_rad


def _terminal_metre_pass(trial_state: np.ndarray, onset_state: np.ndarray) -> bool:
    """Return whether declared FK tip error stays within the metre tolerance."""
    tip_error = float(
        np.linalg.norm(_planar_tip_xy(trial_state[:2]) - _planar_tip_xy(onset_state[:2]))
    )
    return tip_error <= METRE_TASK_TOLERANCE_M


def _ltv_steps(trace: OptionATrace, trial: int, onset: int) -> tuple[LTVLinearizationStep, ...]:
    """Build LTV steps with the preregistered one-step residual drift."""
    x_row, u_row = trace.x[trial], trace.u[trial]
    a_row, b_row = trace.a[trial], trace.b[trial]
    steps: list[LTVLinearizationStep] = []
    for step in range(onset, x_row.shape[0] - 1):
        drift = x_row[step + 1] - (a_row[step] @ x_row[step] + b_row[step] @ u_row[step])
        steps.append(LTVLinearizationStep(a_row[step], b_row[step], drift))
    return tuple(steps)


def _first_flag_time(onset: int, dt: float, results: tuple[object, ...]) -> float | None:
    """Return the first step time where correction authority is not recoverable."""
    for index, item in enumerate(results):
        if isinstance(item, CorrectionAuthorityStepResult) and not item.recoverable:
            return float((onset + index) * dt)
    return None


def _failure_time(trace: OptionATrace, outcome: str) -> float | None:
    """Return horizon-end failure time for unrecoverable trials only."""
    if outcome != "unrecoverable":
        return None
    return float((trace.x.shape[1] - 1) * trace.timestep_s)


def _lead_time(flag_time: float | None, failure_time: float | None) -> float | None:
    """Compute t_failure - t_flag; return None when either event is absent."""
    if flag_time is None or failure_time is None:
        return None
    return float(failure_time - flag_time)


def _median_or_none(values: tuple[float, ...]) -> float | None:
    if not values:
        return None
    median_value = np.median(np.asarray(values, dtype=np.float64))
    return cast(float, float(median_value))


def _evaluate_trial(trace: OptionATrace, trial: int) -> TrialDetectionRecord:
    """Evaluate detectors and indeterminate counts for one fixture trial."""
    onset = trace.onset_step(trial)
    steps = _ltv_steps(trace, trial, onset)
    protocol = preregistered_humanoid_correction_authority_protocol().authority
    results = evaluate_correction_authority_along_trajectory(
        steps,
        trace.x[trial, onset],
        trace.torque_limit_nm,
        trace.recovery_threshold_rad,
        RAD_TASK_DIRECTION,
        1e-6,
        protocol.kappa_max,
        ILL_CONDITIONED_MODE,
    )
    baseline_flag = trace.baseline_flag_time_s[trial]
    baseline_time = None if np.isnan(baseline_flag) else float(baseline_flag)
    ca_time = _first_flag_time(onset, trace.timestep_s, results)
    outcome = trace.outcome_label[trial]
    failure_time = _failure_time(trace, outcome)
    indeterminate_steps = sum(1 for item in results if isinstance(item, Indeterminate))
    baseline_flag_f = None if baseline_time is None else float(baseline_time)
    return TrialDetectionRecord(
        outcome=outcome,
        baseline_flag_time_s=baseline_flag_f,
        correction_authority_flag_time_s=ca_time,
        failure_time_s=failure_time,
        lead_time_baseline_s=_lead_time(baseline_time, failure_time),
        lead_time_correction_authority_s=_lead_time(ca_time, failure_time),
        control_effort=float(trace.control_effort[trial]),
        indeterminate_steps=indeterminate_steps,
    )


def _detection_rates(records: tuple[TrialDetectionRecord, ...]) -> dict[str, float]:
    """Compute TPR/FPR-style rates over labelled recovered vs unrecoverable trials."""
    positives = [r for r in records if r.outcome == "unrecoverable"]
    negatives = [r for r in records if r.outcome == "recovered"]
    tp = sum(1 for r in positives if r.correction_authority_flag_time_s is not None)
    fp = sum(1 for r in negatives if r.correction_authority_flag_time_s is not None)
    tn = len(negatives) - fp
    fn = len(positives) - tp
    total_p, total_n = len(positives), len(negatives)
    return {
        "true_positive_rate": tp / total_p if total_p else float("nan"),
        "false_positive_rate": fp / total_n if total_n else float("nan"),
        "true_negative_rate": tn / total_n if total_n else float("nan"),
        "false_negative_rate": fn / total_p if total_p else float("nan"),
    }


def _disagreement_rate(trace: OptionATrace) -> float:
    """Count trials whose rad-space and metre-space terminal pass/fail labels disagree."""
    disagreements = 0
    for trial in range(trace.x.shape[0]):
        onset = trace.onset_step(trial)
        rad_pass = _terminal_rad_pass(trace, trial)
        metre_pass = _terminal_metre_pass(trace.x[trial, -1], trace.x[trial, onset])
        if rad_pass != metre_pass:
            disagreements += 1
    return float(disagreements) / float(trace.x.shape[0])


def _horizon_sweep(trace: OptionATrace) -> tuple[bool, tuple[str, ...]]:
    """Run the preregistered horizon sweep on the representative unrecoverable trial."""
    authority = preregistered_humanoid_correction_authority_protocol().authority
    trial = next(i for i, label in enumerate(trace.outcome_label) if label == "unrecoverable")
    onset = trace.onset_step(trial)
    all_steps = _ltv_steps(trace, trial, onset)
    dt = trace.timestep_s
    horizons = (
        authority.horizon.sweep_min,
        authority.horizon.nominal,
        authority.horizon.sweep_max,
    )

    def step_builder(horizon_s: float) -> tuple[LTVLinearizationStep, ...]:
        step_count = max(1, int(round(horizon_s / dt)))
        return all_steps[: min(step_count, len(all_steps))]

    sweep = horizon_authority_sweep(
        step_builder,
        horizons,
        trace.x[trial, onset],
        trace.torque_limit_nm,
        trace.recovery_threshold_rad,
        RAD_TASK_DIRECTION,
        1e-6,
        authority.kappa_max,
    )
    return sweep.monotone_nondecreasing_margin, sweep.violations


def _hypothesis_outcome(
    records: tuple[TrialDetectionRecord, ...], rates: dict[str, float]
) -> HypothesisResult:
    """Preserve an honest H-CA-LEAD outcome from the fixture metrics."""
    unrecoverable_leads = tuple(
        r.lead_time_correction_authority_s
        for r in records
        if r.lead_time_correction_authority_s is not None
    )
    baseline_leads = tuple(
        r.lead_time_baseline_s for r in records if r.lead_time_baseline_s is not None
    )
    median_ca = _median_or_none(unrecoverable_leads)
    median_base = _median_or_none(baseline_leads)
    advantage = None
    if median_ca is not None and median_base is not None:
        advantage = median_ca - median_base
    fpr = rates["false_positive_rate"]
    supported = advantage is not None and advantage > 0.0 and fpr == 0.0
    outcome: Literal["supported", "null", "negative", "unavailable"] = (
        "supported"
        if supported
        else "null" if advantage is not None and advantage > 0.0 else "negative"
    )
    interpretation = (
        "Simulation-only fixture: median lead-time advantage on unrecoverable trials is "
        f"{advantage:.4f} s with FPR {fpr:.3f}; rad-space correction authority is not a validated "
        "metre-space detector and does not authorize population-level claims."
    )
    return HypothesisResult("H-CA-LEAD", outcome, advantage, None, interpretation)


def compute_option_a_comparison(trace: OptionATrace) -> OptionAComparisonResult:
    """Recompute the full Option A comparison bundle from a verified trace."""
    if trace.x.shape[0] < 1:
        raise ValueError("at least one trial is required")
    records = tuple(_evaluate_trial(trace, trial) for trial in range(trace.x.shape[0]))
    rates = _detection_rates(records)
    unrecoverable = [r for r in records if r.outcome == "unrecoverable"]
    recovered = [r for r in records if r.outcome == "recovered"]
    median_baseline = _median_or_none(
        tuple(r.lead_time_baseline_s for r in unrecoverable if r.lead_time_baseline_s)
    )
    median_ca = _median_or_none(
        tuple(
            r.lead_time_correction_authority_s
            for r in unrecoverable
            if r.lead_time_correction_authority_s
        )
    )
    advantage = None
    if median_baseline is not None and median_ca is not None:
        advantage = median_ca - median_baseline
    monotone, violations = _horizon_sweep(trace)
    effort_values = tuple(r.control_effort for r in recovered)
    hypothesis = _hypothesis_outcome(records, rates)
    return OptionAComparisonResult(
        schema_version=RESULT_SCHEMA_VERSION,
        payload_sha256=trace.payload_sha256,
        trials=records,
        detection_rates=rates,
        median_lead_time_baseline_s=median_baseline,
        median_lead_time_correction_authority_s=median_ca,
        median_lead_time_advantage_s=advantage,
        mean_successful_trial_effort=(
            float(np.mean(effort_values)) if effort_values else float("nan")
        ),
        horizon_sweep_monotone=monotone,
        horizon_sweep_violations=violations,
        total_indeterminate_steps=sum(r.indeterminate_steps for r in records),
        rad_metre_outcome_disagreement_rate=_disagreement_rate(trace),
        hypothesis_results=(hypothesis,),
    )


def run_option_a_comparison() -> OptionAComparisonResult:
    """Load the vendored trace and return the comparison metrics."""
    return compute_option_a_comparison(load_verified_trace())


def write_comparison_result(path: Path = RESULT_PATH) -> OptionAComparisonResult:
    """Compute metrics and write the canonical JSON artifact."""
    result = run_option_a_comparison()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result.to_json_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def load_committed_comparison_result(path: Path = RESULT_PATH) -> dict[str, Any]:
    """Load the committed comparison JSON after verifying schema metadata."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != RESULT_SCHEMA_VERSION:
        raise ValueError("unsupported comparison result schema")
    return cast(dict[str, Any], payload)
