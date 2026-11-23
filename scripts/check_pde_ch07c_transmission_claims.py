#!/usr/bin/env python3
"""Fail closed when Chapter 7c transmission prose diverges from pinned study snapshots."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from scripts.pde_monograph_numerical_claims import (
    _format_scientific_latex,
    _round_display,
    load_ch07c_transmission_claims,
    load_integrator_closure,
)


def _chapter_text() -> str:
    root = Path(__file__).resolve().parents[1]
    path = (
        root
        / "articles/proximal_distal_energy_transfer/chapters/_ch07c_transmission_robustness.qmd"
    )
    return path.read_text(encoding="utf-8")


def verify_ch07c_transmission_claims() -> list[str]:
    """Return human-readable mismatch messages (empty when prose matches snapshots)."""
    text = re.sub(r"\s+", " ", _chapter_text())
    claims = load_ch07c_transmission_claims()
    closure = load_integrator_closure()
    errors: list[str] = []

    def require(fragment: str, label: str) -> None:
        collapsed = re.sub(r"\s+", " ", fragment)
        if collapsed not in text:
            errors.append(f"missing {label}: {fragment!r}")

    require(f"$n={claims.held_out_perturbations}$", "held-out perturbation count")
    require(
        f"from {_round_display(claims.clock_q10_delivery_speed_m_s):.2f} to "
        f"{_round_display(claims.state_q10_delivery_speed_m_s):.2f} m/s",
        "held-out q10 speed contrast",
    )
    require(
        f"from {_round_display(claims.clock_mean_face_path_deg):.2f} to "
        f"{_round_display(claims.state_mean_face_path_deg):.2f} degrees",
        "face/path mean contrast",
    )
    require(
        f"from {_round_display(claims.clock_q90_peak_hand_force_n, 1):.1f} to "
        f"{_round_display(claims.state_q90_peak_hand_force_n, 1):.1f} N",
        "peak hand force q90 contrast",
    )
    require(
        f"{_round_display(claims.higher_impedance_nominal_speed_m_s):.2f} m/s",
        "higher-impedance nominal speed",
    )
    require(
        f"{_round_display(claims.higher_impedance_mean_face_path_deg):.2f} degrees",
        "higher-impedance face/path mean",
    )
    require(
        f"{_round_display(claims.null_variance, 4):.4f}",
        "task-null variance total",
    )
    require(
        f"{_round_display(claims.task_relevant_variance, 5):.5f}",
        "task-relevant variance total",
    )
    require(
        f"{_round_display(claims.null_variance_per_dof, 4):.4f} per degree of freedom",
        "task-null per-DoF variance",
    )
    require(
        f"{_round_display(claims.task_relevant_variance_per_dof, 5):.5f} per degree of freedom",
        "task-relevant per-DoF variance",
    )
    require(
        f"=0.{int(round(claims.synergy_index * 1000)):03d}",
        "declared synergy index",
    )
    require("worst normalized work--energy residual of 3.77%", "work-energy residual wording")
    require(
        f"({closure.maximum_pathway_residual_j:.3f} J on the registered scale)",
        "pathway residual joules",
    )
    contact_latex = _format_scientific_latex(closure.maximum_contact_power_residual_w)
    contact_plain = contact_latex.strip("$")
    if contact_plain not in text:
        errors.append(
            "contact-power residual mismatch: "
            f"expected LaTeX fragment {contact_plain!r} from closure snapshot"
        )
    if re.search(r"6\.40\s*\\times10", text):
        errors.append("stale 6.40×10⁻¹⁴ W contact-power figure must not remain in Chapter 7c")
    return errors


def main() -> int:
    """Exit non-zero when Chapter 7c diverges from pinned transmission data."""
    errors = verify_ch07c_transmission_claims()
    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        return 1
    print("Chapter 7c transmission claims match pinned snapshots.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
