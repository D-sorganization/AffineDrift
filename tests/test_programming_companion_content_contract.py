"""Content contracts for the fail-closed Programming Companion hub (#4098)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "models/models.qmd"
RESOURCE_CSS = ROOT / "css/resources.css"


def _hub() -> str:
    """Read the canonical hub source."""
    return HUB.read_text(encoding="utf-8")


def test_hub_uses_the_stable_route_and_programming_companion_identity() -> None:
    source = _hub()

    assert 'title: "Programming Companion"' in source
    assert "This establishes" in source
    assert "This does not establish" in source


def test_hub_features_the_complete_proximal_distal_reading_map() -> None:
    source = _hub()
    required_routes = (
        "../articles/proximal_distal_energy_transfer/index.html",
        "../articles/proximal-distal-a-journey-through-the-swing.html",
        "../articles/proximal-distal-model-workbench.html",
        "../articles/proximal-distal-falsification-atlas.html",
        "../books/index.html",
        "../resources/learning-path-golf-science.html",
        "../resources/learning-path-biomechanics.html",
    )

    for route in required_routes:
        assert route in source, f"Programming Companion is missing {route}"

    assert "models, claims, and evidence" in source
    assert "human validation" in source.casefold()


def test_hub_uses_a_wide_desktop_canvas_for_the_featured_library() -> None:
    source = _hub()
    css = RESOURCE_CSS.read_text(encoding="utf-8")

    assert '<div class="programming-hub"' in source
    assert '<nav class="programming-hub__jump"' in source
    assert 'class="resource-grid resource-grid--long-form"' in source
    assert ".programming-hub {" in css
    assert ".programming-hub__jump {" in css


def test_provider_dependent_surfaces_fail_closed_with_governing_issues() -> None:
    source = _hub()
    provider_issues = (
        "UpstreamDrift/issues/9174",
        "UpstreamDrift/issues/9190",
        "UpstreamDrift/issues/9191",
        "UpstreamDrift/issues/9192",
        "UpstreamDrift/issues/9193",
    )
    consumer_issues = (
        "AffineDrift/issues/4023",
        "AffineDrift/issues/4024",
        "AffineDrift/issues/4025",
        "AffineDrift/issues/4028",
        "AffineDrift/issues/4029",
        "AffineDrift/issues/4030",
    )

    assert "Unavailable until governed evidence is pinned" in source
    for issue in (*provider_issues, *consumer_issues):
        assert issue in source, f"Missing governing issue link: {issue}"


def test_hub_does_not_copy_mutable_provider_facts_or_commands() -> None:
    source = _hub()
    forbidden = (
        "Python 3.13",
        "git clone https://github.com/D-sorganization/UpstreamDrift.git",
        'pip install -e ".[dev]"',
        "launch_upstream_drift.py",
        "24 routes",
        "GOLF_USE_MOCK_ENGINE",
        "D-sorganization/UpstreamDrift/blob/main/",
        "D-sorganization/UpstreamDrift/tree/main/",
        "Supported Physics Engines",
        "MuJoCo (Recommended)",
    )

    for copied_fact in forbidden:
        assert copied_fact not in source, f"Mutable provider claim remains: {copied_fact}"


def test_legacy_engine_guides_are_retained_as_deferred_editorial_references() -> None:
    source = _hub()
    assert "Deferred Editorial References" in source
    assert "#4060" in source
    for route in (
        "models-mujoco.html",
        "models-drake.html",
        "models-pinocchio.html",
        "models-opensim.html",
        "models-myosim.html",
        "models-simulink.html",
        "models-pendulum.html",
    ):
        assert route in source


def test_research_readiness_route_remains_discoverable() -> None:
    assert "research-protocol-readiness.html" in _hub()
