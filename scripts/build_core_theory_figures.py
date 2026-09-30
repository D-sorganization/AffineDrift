"""Deterministic figure generator for Core Theory pages.

Generates 9 high-resolution, lightweight SVG figures across:
- articles/controllability-drift-ratio.qmd (3 figures)
- articles/zero-torque-counterfactual.qmd (3 figures)
- articles/superposition.qmd (3 figures)
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from scripts.core_theory_figures.common import (
    ACCENT_ORANGE,
    GRID_COLOR,
    LIGHT_BG,
    PRIMARY_BLUE,
    SAGE_GREEN,
    SLATE_GRAY,
    TEXT_COLOR,
    _clean_svg,
)
from scripts.core_theory_figures.dcr import (
    build_dcr_reachability_tubes,
    build_dcr_swing_phases,
    build_dcr_vector_decomposition,
)
from scripts.core_theory_figures.superposition import (
    build_superposition_breakdown_boundary,
    build_superposition_decomposition,
    build_superposition_modal_response,
)
from scripts.core_theory_figures.ztcf import (
    build_ztcf_clubhead_speed_loss,
    build_ztcf_passive_dynamics_attribution,
    build_ztcf_trajectory_divergence,
)

LOGGER = logging.getLogger("build_core_theory_figures")

FIGURE_NAMES = (
    "fig_dcr_vector_decomposition.svg",
    "fig_dcr_swing_phases.svg",
    "fig_dcr_reachability_tubes.svg",
    "fig_ztcf_trajectory_divergence.svg",
    "fig_ztcf_clubhead_speed_loss.svg",
    "fig_ztcf_passive_dynamics_attribution.svg",
    "fig_superposition_decomposition.svg",
    "fig_superposition_modal_response.svg",
    "fig_superposition_breakdown_boundary.svg",
)

__all__ = [
    "ACCENT_ORANGE",
    "FIGURE_NAMES",
    "GRID_COLOR",
    "LIGHT_BG",
    "PRIMARY_BLUE",
    "SAGE_GREEN",
    "SLATE_GRAY",
    "TEXT_COLOR",
    "_clean_svg",
    "build_all_figures",
    "build_dcr_reachability_tubes",
    "build_dcr_swing_phases",
    "build_dcr_vector_decomposition",
    "build_superposition_breakdown_boundary",
    "build_superposition_decomposition",
    "build_superposition_modal_response",
    "build_ztcf_clubhead_speed_loss",
    "build_ztcf_passive_dynamics_attribution",
    "build_ztcf_trajectory_divergence",
    "check_figures",
    "main",
]


def build_all_figures(output_dir: Path) -> list[Path]:
    """Generate all 9 core theory SVG figures in the designated directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    generators = [
        ("fig_dcr_vector_decomposition.svg", build_dcr_vector_decomposition),
        ("fig_dcr_swing_phases.svg", build_dcr_swing_phases),
        ("fig_dcr_reachability_tubes.svg", build_dcr_reachability_tubes),
        ("fig_ztcf_trajectory_divergence.svg", build_ztcf_trajectory_divergence),
        ("fig_ztcf_clubhead_speed_loss.svg", build_ztcf_clubhead_speed_loss),
        ("fig_ztcf_passive_dynamics_attribution.svg", build_ztcf_passive_dynamics_attribution),
        ("fig_superposition_decomposition.svg", build_superposition_decomposition),
        ("fig_superposition_modal_response.svg", build_superposition_modal_response),
        ("fig_superposition_breakdown_boundary.svg", build_superposition_breakdown_boundary),
    ]

    for filename, func in generators:
        target = output_dir / filename
        LOGGER.info("Generating figure: %s", target)
        func(target)
        generated.append(target)

    return generated


def check_figures(output_dir: Path) -> bool:
    """Validate that all expected figures exist, are non-empty, and are valid SVGs."""
    all_ok = True
    for filename in FIGURE_NAMES:
        target = output_dir / filename
        if not target.is_file():
            LOGGER.error("Missing figure: %s", target)
            all_ok = False
            continue
        size = target.stat().st_size
        if size == 0:
            LOGGER.error("Empty figure: %s", target)
            all_ok = False
            continue
        # Verify valid SVG content
        content = target.read_text(encoding="utf-8")
        if "<svg" not in content or "</svg>" not in content:
            LOGGER.error("Invalid SVG file (missing <svg> root): %s", target)
            all_ok = False
            continue
        LOGGER.info("Verified figure %s (%d bytes)", filename, size)

    return all_ok


def main() -> int:
    """CLI entrypoint."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description="Generate SVG figures for core theory pages.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "articles/figures/core_theory",
        help="Destination directory for generated SVGs.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check that all figures exist and are valid SVGs without modifying them.",
    )

    args = parser.parse_args()

    if args.check:
        LOGGER.info("Running figure check against %s", args.output_dir)
        ok = check_figures(args.output_dir)
        return 0 if ok else 1

    LOGGER.info("Generating core theory figures into %s", args.output_dir)
    build_all_figures(args.output_dir)
    LOGGER.info("All 9 figures generated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
