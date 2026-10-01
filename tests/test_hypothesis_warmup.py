"""Regression test: Hypothesis's local-constants scan is pre-warmed per session.

Hypothesis (>= 6.131) scans every imported local module for literals the
first time any test draws a float, and charges that one-off scan to the
first draw's timing. On Windows its ``"/site-packages/"`` fast path never
matches backslash paths, so the scan resolves ~1000 module paths (~2.4 s
alone, ~7 s under ``pytest -n 8``) and trips ``HealthCheck.too_slow`` on
whichever ``@given`` test runs first in each xdist worker. The failure moved
between TestMomentOfInertiaProperties tests depending on scheduling.
``tests/conftest.py`` warms the scan after collection so no test pays it.
"""

from __future__ import annotations

import sys

import pytest

providers = pytest.importorskip("hypothesis.internal.conjecture.providers")


def test_local_constants_scan_already_done_before_first_draw() -> None:
    """The warm-up ran before any test drew from Hypothesis."""
    if not hasattr(providers, "_get_local_constants"):
        pytest.skip("this Hypothesis version has no local-constants scan")
    assert providers._sys_modules_len is not None
    # Every module imported by collection has already been visited.
    assert providers._sys_modules_len <= len(sys.modules)
