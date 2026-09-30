"""Core Theory figure generation modules."""

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

__all__ = [
    "ACCENT_ORANGE",
    "GRID_COLOR",
    "LIGHT_BG",
    "PRIMARY_BLUE",
    "SAGE_GREEN",
    "SLATE_GRAY",
    "TEXT_COLOR",
    "_clean_svg",
    "build_dcr_reachability_tubes",
    "build_dcr_swing_phases",
    "build_dcr_vector_decomposition",
    "build_superposition_breakdown_boundary",
    "build_superposition_decomposition",
    "build_superposition_modal_response",
    "build_ztcf_clubhead_speed_loss",
    "build_ztcf_passive_dynamics_attribution",
    "build_ztcf_trajectory_divergence",
]
