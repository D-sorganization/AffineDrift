"""Phrase pins for the Tools #5431 distributed-convention disclosure (AffineDrift #5007)."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "articles/proximal-distal-model-workbench.qmd"
IMPACT = ROOT / "articles/impact-optimality-and-model-limits.qmd"
TITLE = 'title="Disclosure: Tools #5431 Changed the Club Convention"'
ISSUE_URL = "https://github.com/D-sorganization/Tools/issues/5431"
PR_URL = "https://github.com/D-sorganization/Tools/pull/5554"
FOLLOW_UP_URL = "https://github.com/D-sorganization/Tools/issues/5523"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def _disclosure(path: Path) -> str:
    source = _text(path)
    assert source.count(TITLE) == 1
    start = source.index(TITLE)
    return source[start : source.index("\n:::", start)]


@pytest.mark.parametrize("page", [WORKBENCH, IMPACT], ids=lambda path: path.stem)
def test_page_discloses_the_tools_5431_convention_change(page: Path) -> None:
    note = " ".join(_disclosure(page).split())
    assert ".callout-warning" in _text(page)
    for required in (ISSUE_URL, PR_URL, FOLLOW_UP_URL):
        assert required in note
    assert "AffineDrift/issues/5007" not in note  # closed by this change
    assert "historical" in note
    assert "uniform shaft" in note or "uniform" in note


def test_workbench_labels_pinned_numbers_as_pre_fix_and_not_recomputed() -> None:
    note = " ".join(_disclosure(WORKBENCH).split())
    assert "`cefcc1878`" in note
    assert "predates that fix" in note
    assert "have **not been recomputed**" in note
    assert "8 J versus 4 J" in note


def test_workbench_historical_diagnostic_example_is_kept() -> None:
    source = _text(WORKBENCH)
    assert "the same state yields 8 J versus 4 J" in source
    assert "A Known Diagnostic Consistency Limit" in source


def test_impact_page_keeps_historical_numbers_and_states_the_sign_change() -> None:
    note = " ".join(_disclosure(IMPACT).split())
    source = _text(IMPACT)
    assert "historical, pre-fix values" in note
    assert "kept unchanged" in note
    assert "exact $m_2 \\rightarrow 0$ limit" in note
    assert "negative (hands move backward) rather than zero" in note
    assert "| 0.500 kg | 36.4 | 0.36 | 59.4 | 33% |" in source
    assert "36.4 m/s and hand speed of about 0.36 m/s" in " ".join(source.split())
