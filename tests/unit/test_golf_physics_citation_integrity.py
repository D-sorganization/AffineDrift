"""Unit tests for Physics of Golf citation-integrity checks (issue #5600)."""

from __future__ import annotations

from src.tools.golf_physics_citation_integrity import (
    check_bib_key_year_alignment,
    check_ch28_impact_sourcing,
    check_jorgensen_entry,
    check_obsolete_bib_keys,
    find_violations,
)


def test_check_obsolete_bib_keys_flags_legacy_names() -> None:
    bib = "@article{Sprigings2005, year = {2000}}\n"
    assert check_obsolete_bib_keys(bib) == ["obsolete bib key: Sprigings2005"]


def test_check_bib_key_year_alignment_allows_jorgensen_exception() -> None:
    bib = """
@book{Jorgensen1994,
  year = {1999},
  edition = {2nd}
}
"""
    assert check_bib_key_year_alignment(bib) == []


def test_check_bib_key_year_alignment_catches_mismatch() -> None:
    bib = """
@article{SprigingsNeal2000,
  year = {2005},
  title = {An Example}
}
"""
    assert check_bib_key_year_alignment(bib) == [
        "SprigingsNeal2000: key embeds 2000 but year field is 2005"
    ]


def test_check_jorgensen_entry_requires_second_edition_metadata() -> None:
    bad = "@book{Jorgensen1994, year = {1994}, edition = {2nd}}\n"
    violations = check_jorgensen_entry(bad)
    assert any("1999" in item for item in violations)

    good = """
@book{Jorgensen1994,
  edition = {2nd},
  publisher = {Springer-Verlag},
  year = {1999}
}
"""
    assert check_jorgensen_entry(good) == []


def test_check_ch28_impact_sourcing_requires_equipment_and_duration_cites() -> None:
    bad = "For illustrative $e=0.83$, the speed ratio is about $1.488$.\n"
    violations = check_ch28_impact_sourcing(bad)
    assert violations

    good = """
For $e=0.83$ in conformance rules [@glossaryUSGAEquipment].
Driver-ball contact durations of about $0.45$--$0.5$ ms [@Cochran1968; @Penner2003].
"""
    assert check_ch28_impact_sourcing(good) == []


def test_find_violations_empty_on_current_repo() -> None:
    """Integration smoke: main-tree PoG sources satisfy issue #5600 gates."""
    assert find_violations() == []
