"""Scientific-scope contract for planar golf-model explanations."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.content_lint

ROOT_DIR = Path(__file__).resolve().parent.parent
GOVERNED_SOURCES = (
    "articles/drift-components-wrench-double-pendulum.qmd",
    "articles/force-mobility-matrices.qmd",
)

UNSUPPORTED_FIDELITY_CLAIMS = (
    "approx. 90% of kinetic energy",
    "over 90% of the energy transfer occurs",
)


@pytest.mark.parametrize("relative_path", GOVERNED_SOURCES)
def test_planar_articles_do_not_publish_unsupported_fidelity_percentages(
    relative_path: str,
) -> None:
    source = (ROOT_DIR / relative_path).read_text(encoding="utf-8")

    for claim in UNSUPPORTED_FIDELITY_CLAIMS:
        assert claim not in source, f"{relative_path} retains unsupported claim: {claim}"

    assert "pedagogical planar model" in source
    assert "does not establish a quantitative fidelity percentage" in source
    assert "governed three-dimensional comparison" in source
