"""Generate the deterministic non-authorizing population-validation report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.affine_control.population_generalization import evaluate_population_prediction
from src.affine_control.population_generalization_fixtures import (
    manufactured_observations,
    manufactured_split,
)

ROOT = Path(__file__).resolve().parents[1]
JSON_TARGET = ROOT / "data" / "population_generalization" / "validation_report.json"
MARKDOWN_TARGET = ROOT / "reports" / "population-generalization-validation.md"


def build_payload() -> dict[str, Any]:
    """Return the stable public projection of the manufactured result."""
    report = evaluate_population_prediction(
        manufactured_observations(), manufactured_split(), minimum_subgroup_size=2
    )
    return {
        "schema_version": "affinedrift.population-generalization-report/v1",
        "evidence_origin": "manufactured-synthetic",
        "split_id": manufactured_split().split_id,
        "locked_test_set": manufactured_split().locked_test_set,
        "mean_error": report.mean_error,
        "mean_absolute_error": report.mean_absolute_error,
        "participant_weighted_interval": {
            "lower": report.participant_weighted_interval.lower,
            "upper": report.participant_weighted_interval.upper,
        },
        "calibration": {
            "intercept": report.calibration.intercept,
            "slope": report.calibration.slope,
        },
        "subgroup_performance": [
            {
                "subgroup": row.subgroup,
                "sample_size": row.sample_size,
                "status": row.status,
                "mean_absolute_error": row.mean_absolute_error,
                "limitation": row.limitation,
            }
            for row in report.subgroup_performance
        ],
        "outcomes": [
            {"outcome_id": row.outcome_id, "status": row.status, "finding": row.finding}
            for row in report.outcomes
        ],
        "sensitivity_result": report.sensitivity_result,
        "external_validation_status": report.external_validation_status,
        "authorizes_population_claim": report.authorizes_population_claim,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    """Render a concise human-readable projection from the JSON payload."""
    calibration = payload["calibration"]
    interval = payload["participant_weighted_interval"]
    outcomes = payload["outcomes"]
    headers = ("Outcome", "Status", "Finding")
    widths = tuple(
        max(len(headers[index]), *(len(str(row[key])) for row in outcomes))
        for index, key in enumerate(("outcome_id", "status", "finding"))
    )
    rows = [
        "# Population-Generalization Manufactured Validation Report",
        "",
        "> **DO NOT use as population authority.** This report contains only "
        "manufactured-synthetic records and validates software/report mechanics.",
        "",
        "## Locked Test Summary",
        "",
        f"- Mean error: {payload['mean_error']:.3f} manufactured units",
        f"- Mean absolute error: {payload['mean_absolute_error']:.3f} manufactured units",
        f"- Participant-weighted interval: {interval['lower']:.3f} to {interval['upper']:.3f}",
        f"- Calibration intercept/slope: {calibration['intercept']:.3f} / {calibration['slope']:.3f}",
        f"- External validation: {payload['external_validation_status']}",
        f"- Authorizes population claim: {str(payload['authorizes_population_claim']).lower()}",
        "",
        "## Retained Outcomes",
        "",
        f"| {headers[0]:<{widths[0]}} | {headers[1]:<{widths[1]}} | {headers[2]:<{widths[2]}} |",
        f"| {'-' * widths[0]} | {'-' * widths[1]} | {'-' * widths[2]} |",
    ]
    rows.extend(
        f"| {row['outcome_id']:<{widths[0]}} | {row['status']:<{widths[1]}} | "
        f"{row['finding']:<{widths[2]}} |"
        for row in outcomes
    )
    rows.extend(
        (
            "",
            "The next gate is a separately approved, preregistered, privacy- and "
            "consent-governed participant study with locked participant/site test data.",
            "",
        )
    )
    return "\n".join(rows)


def generate(*, check: bool) -> None:
    """Write outputs or fail when committed projections are stale."""
    payload = build_payload()
    json_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    markdown_text = render_markdown(payload)
    expected = ((JSON_TARGET, json_text), (MARKDOWN_TARGET, markdown_text))
    if check:
        stale = [path for path, text in expected if not path.exists() or path.read_text() != text]
        if stale:
            raise SystemExit("stale population report: " + ", ".join(str(path) for path in stale))
        return
    for path, text in expected:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generate(check=args.check)


if __name__ == "__main__":
    main()
