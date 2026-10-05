"""Freshness contract of ``scripts/generate_widget_parity.py`` (ADR 0002 section 6).

A committed fixture is current when every non-numeric field matches exactly and
every number matches a fresh regeneration within its case tolerance. Byte
equality is too strict: LAPACK builds differ in the last bits across platforms,
and RK4 carries those bits along a trajectory.
"""

from __future__ import annotations

import copy
from typing import Any

from scripts.generate_widget_parity import CLOSED_FORM, INTEGRATED, fixture_matches

FRESH: dict[str, Any] = {
    "schema": "affinedrift/widget-parity/v1",
    "source_sha256": "abc",
    "tolerance": CLOSED_FORM,
    "cases": [
        {"id": "split-0", "expected": {"drift_qdd": [1.0, -2.0]}},
        {"id": "preset-a", "tolerance": INTEGRATED, "expected": {"q": [[0.5, 3.0]]}},
    ],
}


def _committed(edit: Any) -> dict[str, Any]:
    document = copy.deepcopy(FRESH)
    edit(document)
    return document


def test_identical_documents_match() -> None:
    assert fixture_matches(copy.deepcopy(FRESH), FRESH)


def test_last_bit_differences_within_the_case_tolerance_match() -> None:
    def nudge(d: dict[str, Any]) -> None:
        d["cases"][0]["expected"]["drift_qdd"][0] = 1.0 + 1e-15
        d["cases"][1]["expected"]["q"][0][1] = 3.0 + 1e-10

    assert fixture_matches(_committed(nudge), FRESH)


def test_differences_beyond_the_case_tolerance_do_not_match() -> None:
    def closed_form(d: dict[str, Any]) -> None:
        d["cases"][0]["expected"]["drift_qdd"][0] = 1.0 + 1e-9

    def integrated(d: dict[str, Any]) -> None:
        d["cases"][1]["expected"]["q"][0][1] = 3.0 + 1e-6

    assert not fixture_matches(_committed(closed_form), FRESH)
    assert not fixture_matches(_committed(integrated), FRESH)


def test_non_numeric_fields_and_shapes_must_match_exactly() -> None:
    def digest(d: dict[str, Any]) -> None:
        d["source_sha256"] = "def"

    def shape(d: dict[str, Any]) -> None:
        d["cases"][1]["expected"]["q"].append([0.0, 0.0])

    def key(d: dict[str, Any]) -> None:
        d["cases"][0]["expected"]["extra"] = 1.0

    for edit in (digest, shape, key):
        assert not fixture_matches(_committed(edit), FRESH)
