"""Parity contract for the DCR swing-phase widget (js/dcr-visualizer*.js).

The widget's default scenario must reproduce the same equal-instantaneous-DCR,
different-reachable-width counterexample already governed by
``tests/test_dcr_event_sensitivity_protocol.py``. The JS-side numbers for this
identical scenario are locked in ``tests/dcr-visualizer.test.js`` and
``tests/dcr-visualizer-ui.test.js`` (``npx jest``); together the two suites
verify that the Python and browser implementations agree.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from src.affine_control.reachability import (
    LinearScalarSystem,
    instantaneous_scalar_dcr,
    scalar_linear_reachable_interval,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLE = REPO_ROOT / "articles/drift-control-ratio.qmd"
JS_MODULE = REPO_ROOT / "js/dcr-visualizer.js"
JS_UI = REPO_ROOT / "js/dcr-visualizer-ui.js"
FIXTURE = json.loads(
    (REPO_ROOT / "tests/fixtures/dcr_visualizer_parity.json").read_text(encoding="utf-8")
)

DEFAULT_X0 = FIXTURE["initial_state"]
DEFAULT_UBAR = FIXTURE["control_bound"]
DEFAULT_HORIZON = FIXTURE["horizon"]


def _default_input_value(article: str, element_id: str) -> str:
    """Return the ``value`` attribute of the input with the given id."""
    match = re.search(rf'<input[^>]*id="{element_id}"[^>]*>', article)
    assert match is not None, f"no input with id={element_id!r} in the article"
    value_match = re.search(r'value="([^"]*)"', match.group(0))
    assert value_match is not None, f"input id={element_id!r} has no value attribute"
    return value_match.group(1)


def test_default_scenario_matches_the_governed_equal_dcr_fixture() -> None:
    """The widget's default preset must reproduce the tested equal-DCR counterexample."""
    expected = FIXTURE["expected"]
    additive = LinearScalarSystem(
        DEFAULT_X0,
        FIXTURE["additive_system"]["drift_gradient"],
        FIXTURE["additive_system"]["drift_offset"],
        DEFAULT_UBAR,
    )
    state_dependent = LinearScalarSystem(
        DEFAULT_X0,
        FIXTURE["state_dependent_system"]["drift_gradient"],
        FIXTURE["state_dependent_system"]["drift_offset"],
        DEFAULT_UBAR,
    )

    assert instantaneous_scalar_dcr(additive) == pytest.approx(expected["instantaneous_dcr"])
    assert instantaneous_scalar_dcr(state_dependent) == pytest.approx(expected["instantaneous_dcr"])

    additive_interval = scalar_linear_reachable_interval(additive, DEFAULT_HORIZON)
    state_dependent_interval = scalar_linear_reachable_interval(state_dependent, DEFAULT_HORIZON)

    assert additive_interval == pytest.approx(tuple(expected["additive_reachable_interval"]))
    assert state_dependent_interval == pytest.approx(
        tuple(expected["state_dependent_reachable_interval"])
    )
    assert additive_interval[1] - additive_interval[0] == pytest.approx(
        expected["additive_reachable_width"]
    )
    assert state_dependent_interval[1] - state_dependent_interval[0] == pytest.approx(
        expected["state_dependent_reachable_width"]
    )


def test_widget_defaults_in_the_article_match_the_governed_fixture() -> None:
    """The embedded widget's numeric defaults must be the exact fixture parameters."""
    article = ARTICLE.read_text(encoding="utf-8")
    assert _default_input_value(article, "dcrviz-x0") == str(int(DEFAULT_X0))
    assert _default_input_value(article, "dcrviz-ubar") == str(int(DEFAULT_UBAR))
    assert _default_input_value(article, "dcrviz-horizon") == str(int(DEFAULT_HORIZON))


def test_widget_links_the_registered_reachability_claim() -> None:
    """The widget must link the same registered claim as the surrounding prose."""
    article = ARTICLE.read_text(encoding="utf-8")
    assert article.count('data-trust-claim="ad-dcr-001"') >= 2
    assert 'href="#claim-ad-dcr-001"' in article


def test_widget_is_embedded_on_the_dcr_page() -> None:
    article = ARTICLE.read_text(encoding="utf-8")
    assert 'id="dcrviz-app"' in article
    assert '<script src="../js/dcr-visualizer.js"></script>' in article
    assert '<script src="../js/dcr-visualizer-ui.js"></script>' in article


def test_js_module_exposes_the_mirrored_reachability_functions() -> None:
    source = JS_MODULE.read_text(encoding="utf-8")
    for name in (
        "linearScalarSystem",
        "instantaneousScalarDcr",
        "scalarLinearReachableInterval",
        "constantAdditiveDriftInterval",
    ):
        assert name in source
    assert JS_UI.exists()
