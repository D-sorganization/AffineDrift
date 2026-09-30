"""Parity contract for the DCR swing-phase widget (js/dcr-visualizer*.js).

The widget's default scenario must reproduce the same equal-instantaneous-DCR,
different-reachable-width counterexample already governed by
``tests/test_dcr_event_sensitivity_protocol.py``. The JS-side numbers for this
identical scenario are locked in ``tests/dcr-visualizer.test.js`` and
``tests/dcr-visualizer-ui.test.js`` (``npx jest``); together the two suites
verify that the Python and browser implementations agree.
"""

from __future__ import annotations

import re
from math import e
from pathlib import Path

import pytest

from src.affine_control.reachability import (
    LinearScalarSystem,
    instantaneous_scalar_dcr,
    scalar_linear_reachable_interval,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLE = REPO_ROOT / "articles/controllability-drift-ratio.qmd"
JS_MODULE = REPO_ROOT / "js/dcr-visualizer.js"
JS_UI = REPO_ROOT / "js/dcr-visualizer-ui.js"

DEFAULT_X0 = 1.0
DEFAULT_UBAR = 1.0
DEFAULT_HORIZON = 1.0


def _default_input_value(article: str, element_id: str) -> str:
    """Return the ``value`` attribute of the input with the given id."""
    match = re.search(rf'<input[^>]*id="{element_id}"[^>]*>', article)
    assert match is not None, f"no input with id={element_id!r} in the article"
    value_match = re.search(r'value="([^"]*)"', match.group(0))
    assert value_match is not None, f"input id={element_id!r} has no value attribute"
    return value_match.group(1)


def test_default_scenario_matches_the_governed_equal_dcr_fixture() -> None:
    """The widget's default preset must reproduce the tested equal-DCR counterexample."""
    gradient_b = DEFAULT_UBAR / DEFAULT_X0
    additive = LinearScalarSystem(DEFAULT_X0, 0.0, DEFAULT_UBAR, DEFAULT_UBAR)
    state_dependent = LinearScalarSystem(DEFAULT_X0, gradient_b, 0.0, DEFAULT_UBAR)

    assert instantaneous_scalar_dcr(additive) == pytest.approx(1.0)
    assert instantaneous_scalar_dcr(state_dependent) == pytest.approx(1.0)

    additive_interval = scalar_linear_reachable_interval(additive, DEFAULT_HORIZON)
    state_dependent_interval = scalar_linear_reachable_interval(state_dependent, DEFAULT_HORIZON)

    assert additive_interval == pytest.approx((1.0, 3.0))
    assert state_dependent_interval == pytest.approx((1.0, 2.0 * e - 1.0))
    assert additive_interval[1] - additive_interval[0] == pytest.approx(2.0)
    assert state_dependent_interval[1] - state_dependent_interval[0] == pytest.approx(
        2.0 * (e - 1.0)
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
