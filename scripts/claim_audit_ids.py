"""Stable identifiers and source-route mappings for claim-audit tooling."""

from __future__ import annotations

import hashlib
from pathlib import Path

ISSUE_ROOT = "https://github.com/D-sorganization/AffineDrift/issues"

DEFERRED_AUDIT_SCOPE_COUNTS = {
    f"{ISSUE_ROOT}/4054": 36,
    f"{ISSUE_ROOT}/4055": 26,
    f"{ISSUE_ROOT}/4056": 16,
    f"{ISSUE_ROOT}/4057": 40,
    f"{ISSUE_ROOT}/4058": 29,
    f"{ISSUE_ROOT}/4059": 18,
    f"{ISSUE_ROOT}/4060": 14,
    f"{ISSUE_ROOT}/4061": 21,
    f"{ISSUE_ROOT}/4062": 6,
    f"{ISSUE_ROOT}/4063": 13,
}

CORE_ARTICLE_ROUTES = frozenset(
    {
        "/articles/affine-nature-golf-swing.html",
        "/articles/appendix-applications.html",
        "/articles/calculation-framework-comparison/multibody-drift-control-v3.html",
        "/articles/degrees-of-freedom-and-dimensionality.html",
        "/articles/drift-components-wrench-double-pendulum.html",
        "/articles/force-mobility-matrices.html",
        "/articles/green-simulation.html",
        "/articles/intentional-constraint-collapse.html",
        "/articles/inverse-dynamics-inference.html",
        "/articles/inverse-dynamics.html",
        "/articles/lagrangian-reference.html",
        "/articles/nonlinear-control-insights.html",
        "/articles/null-space-constraint-jacobian.html",
        "/articles/passive-distributed-control.html",
        "/articles/reference-point-problem.html",
        "/articles/rotation-converter.html",
        "/articles/rotation-induced-spin.html",
        "/articles/rotation-representations-reference.html",
        "/articles/screw-theory-reference.html",
        "/articles/secondary-axis-stability.html",
        "/articles/sources-of-nonlinearity.html",
        "/articles/superposition.html",
        "/articles/theory-part1.html",
        "/articles/theory-part2.html",
        "/articles/theory-part3.html",
        "/articles/theory-part4.html",
        "/articles/theory-part5.html",
        "/articles/wrist-universal-joint.html",
        "/articles/zero-torque-counterfactual.html",
    }
)

APPLIED_ARTICLE_ROUTES = frozenset(
    {
        "/articles/drifter-manifesto.html",
        "/articles/ideomotor-theory-and-predictive-brain.html",
        "/articles/impact-mechanics-and-ball-flight.html",
        "/articles/impact-optimality-and-model-limits.html",
        "/articles/launch-monitor-vendor-reference.html",
        "/articles/markerless-mocap-camera-selection.html",
        "/articles/proximal-distal-a-journey-through-the-swing.html",
        "/articles/proximal-distal-energy-transfer.html",
        "/articles/proximal-distal-model-workbench.html",
        "/articles/proximal_distal_energy_transfer/index.html",
        "/articles/putting-roll-models.html",
        "/articles/strokes-gained-limitations.html",
        "/articles/technology-club-fitting.html",
        "/articles/technology-force-measurement.html",
        "/articles/technology-heavy-hit-impact-coupling.html",
        "/articles/technology-launch-monitors.html",
        "/articles/technology-motion-capture.html",
        "/articles/upstreamdrift-educational-integration.html",
    }
)


def deferred_issue_urls(route: str) -> tuple[str, ...]:
    """Return every child audit issue whose declared scope contains ``route``."""
    matches: list[str] = []
    if route.startswith("/articles/The_Physics_of_Golf/quarto/"):
        matches.append(f"{ISSUE_ROOT}/4054")
    if route.startswith("/articles/The_Geometry_of_Motion/quarto/"):
        matches.append(f"{ISSUE_ROOT}/4055")
    if route.startswith(
        ("/articles/tangent-hyperplane-articles/", "/articles/tangent-hyperplanes-series/")
    ):
        matches.append(f"{ISSUE_ROOT}/4056")
    if route.startswith("/critiques/"):
        matches.append(f"{ISSUE_ROOT}/4057")
    if route in CORE_ARTICLE_ROUTES:
        matches.append(f"{ISSUE_ROOT}/4058")
    if route in APPLIED_ARTICLE_ROUTES:
        matches.append(f"{ISSUE_ROOT}/4059")
    if route.startswith(("/models/", "/repositories/")):
        matches.append(f"{ISSUE_ROOT}/4060")
    if route.startswith("/resources/"):
        matches.append(f"{ISSUE_ROOT}/4061")
    if route.startswith("/books/"):
        matches.append(f"{ISSUE_ROOT}/4062")
    if route == "/" or route.startswith("/pages/"):
        matches.append(f"{ISSUE_ROOT}/4063")
    return tuple(matches)


def deferred_issue_url(route: str) -> str:
    """Return the one child issue responsible for a deferred public route."""
    matches = deferred_issue_urls(route)
    if len(matches) != 1:
        raise ValueError(f"Deferred route {route} maps to {len(matches)} child issues: {matches}")
    return matches[0]


def stable_audit_id(route: str) -> str:
    """Return the stable content-derived audit ID for a canonical route."""
    digest = hashlib.sha256(route.encode("utf-8")).hexdigest()[:12]
    return f"ad-route-{digest}"


def source_route(source_path: object) -> str:
    """Map one canonical source path to its public HTML route."""
    return f"/{Path(str(source_path)).with_suffix('.html').as_posix()}"
