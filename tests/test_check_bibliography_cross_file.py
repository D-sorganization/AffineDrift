"""Tests for check_bibliography_cross_file.py.

The check exists because four citation keys meant different papers in different
.bib files, so the site cited whichever file the render listed first. The cases
below are the real ones, reduced to the smallest form that reproduces them.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.check_bibliography_cross_file import (
    STANDALONE_LINKED,
    braced_field,
    duplicate_dois,
    entries,
    signature,
)


class TestBracedField:
    """Fields must be read by brace matching, not line by line."""

    def test_reads_a_single_line_field(self) -> None:
        body = "@article{k,\n  title = {A Short Title},\n  year = {1999}\n}"
        assert braced_field(body, "title") == "A Short Title"

    def test_reads_a_title_wrapped_across_lines(self) -> None:
        """golf_physics.bib wraps titles; geometry_of_motion.bib does not.

        An earlier single-line regex reported 16 false differences for exactly
        this, because every wrapped entry looked as though it had no title.
        """
        body = (
            "@article{k,\n"
            "  title = {Muscle Forces and Their Contributions to Vertical\n"
            "           and Horizontal Acceleration of the Center of Mass},\n"
            "  year = {2016}\n}"
        )
        assert braced_field(body, "title") == (
            "Muscle Forces and Their Contributions to Vertical "
            "and Horizontal Acceleration of the Center of Mass"
        )

    def test_reads_a_quoted_field(self) -> None:
        body = '@article{k,\n  title = "Quoted Title",\n  year = {2000}\n}'
        assert braced_field(body, "title") == "Quoted Title"

    def test_missing_field_is_empty(self) -> None:
        assert braced_field("@article{k,\n  year = {2000}\n}", "title") == ""


class TestSignature:
    """Two entries describe the same work if title and year agree."""

    def test_ignores_wrapping_and_punctuation(self) -> None:
        one = {"title": "Impedance Control: An Approach", "year": "1985"}
        two = {"title": "impedance control  an approach", "year": "1985"}
        assert signature(one) == signature(two)

    def test_year_difference_is_a_difference(self) -> None:
        """Silverman2014 was dated 2014 in one file and 2018 in the other."""
        one = {"title": "Induced Acceleration and Power Analyses", "year": "2014"}
        two = {"title": "Induced Acceleration and Power Analyses", "year": "2018"}
        assert signature(one) != signature(two)

    def test_different_papers_differ(self) -> None:
        """todorov2004optimality named two genuinely different papers."""
        one = {"title": "Optimality principles in sensorimotor control", "year": "2004"}
        two = {
            "title": "Optimal Feedback Control as a Theory of Motor Coordination",
            "year": "2002",
        }
        assert signature(one) != signature(two)


class TestEntries:
    def test_parses_keys_and_fields(self, tmp_path: Any) -> None:
        path = Path(tmp_path) / "refs.bib"
        path.write_text(
            "@article{alpha,\n  title = {First},\n  year = {2001}\n}\n\n"
            "@book{beta,\n  title = {Second},\n  year = {2002}\n}\n",
            encoding="utf-8",
        )
        found = entries(path)
        assert set(found) == {"alpha", "beta"}
        assert found["alpha"]["title"] == "First"
        assert found["beta"]["year"] == "2002"

    def test_parses_and_normalises_doi(self, tmp_path: Any) -> None:
        path = Path(tmp_path) / "refs.bib"
        path.write_text(
            "@article{k,\n  title = {T},\n  doi = {10.1000/Example.DOI.},\n}\n",
            encoding="utf-8",
        )
        assert entries(path)["k"]["doi"] == "10.1000/example.doi"

    def test_missing_doi_is_empty_string(self, tmp_path: Any) -> None:
        path = Path(tmp_path) / "refs.bib"
        path.write_text("@article{k,\n  title = {T},\n  year = {2000}\n}\n", encoding="utf-8")
        assert entries(path)["k"]["doi"] == ""

    def test_shared_key_agreeing_has_one_signature(self, tmp_path: Any) -> None:
        first = Path(tmp_path) / "a.bib"
        second = Path(tmp_path) / "b.bib"
        first.write_text(
            "@article{k,\n  title = {Same Paper},\n  year = {2012}\n}\n", encoding="utf-8"
        )
        second.write_text(
            "@article{k,\n  title = {Same\n           Paper},\n  year = {2012}\n}\n",
            encoding="utf-8",
        )
        signatures = {signature(entries(p)["k"]) for p in (first, second)}
        assert len(signatures) == 1

    def test_shared_key_disagreeing_has_two_signatures(self, tmp_path: Any) -> None:
        """The worobets2012effects case: same key, different papers."""
        first = Path(tmp_path) / "a.bib"
        second = Path(tmp_path) / "b.bib"
        first.write_text(
            "@article{k,\n  title = {The effects of shaft properties},\n  year = {2012}\n}\n",
            encoding="utf-8",
        )
        second.write_text(
            "@article{k,\n  title = {The influence of shaft stiffness},\n  year = {2012}\n}\n",
            encoding="utf-8",
        )
        signatures = {signature(entries(p)["k"]) for p in (first, second)}
        assert len(signatures) == 2


class TestDuplicateDois:
    """A DOI on more than one key is a literal duplicate bibliography entry.

    Issue #4547: 183 keys duplicated across the site's bibliographies, several
    under mismatched keys for the same DOI (Penner2001/penner2003,
    Sprigings2005/sprigings2000). ``golf_physics.bib`` and
    ``geometry_of_motion.bib`` are exempt because each is also loaded by its
    own independent Quarto book project, so a shared reference legitimately
    needs its own local copy in each.
    """

    @staticmethod
    def _fields(title: str = "T", year: str = "2000") -> dict[str, str]:
        return {"title": title, "year": year, "doi": "10.1/x"}

    def test_two_non_standalone_files_is_a_violation(self) -> None:
        # Neither label is in STANDALONE_LINKED, so both copies are avoidable.
        # The second is a synthetic label rather than a real BIBS path: every
        # file actually in BIBS except impact-acoustics.bib is someone's sole
        # page/book bibliography, so no second real non-exempt file exists to
        # name here.
        owners = {
            "10.1/x": [
                ("references/impact-acoustics.bib", "keyA", self._fields()),
                ("some/other/non-exempt.bib", "keyB", self._fields()),
            ]
        }
        assert "10.1/x" in duplicate_dois(owners)

    def test_single_entry_is_not_a_duplicate(self) -> None:
        owners = {"10.1/x": [("references/impact-acoustics.bib", "keyA", self._fields())]}
        assert duplicate_dois(owners) == {}

    def test_both_copies_in_standalone_files_is_exempt(self) -> None:
        """Both books cite the same paper -- each needs its own local copy."""
        owners = {
            "10.1/x": [
                ("articles/The_Physics_of_Golf/golf_physics.bib", "A", self._fields()),
                ("articles/The_Geometry_of_Motion/geometry_of_motion.bib", "B", self._fields()),
            ]
        }
        assert duplicate_dois(owners) == {}

    def test_one_standalone_copy_plus_one_avoidable_copy_is_exempt(self) -> None:
        """Only one copy is outside a standalone file -- nothing to consolidate against."""
        owners = {
            "10.1/x": [
                ("articles/The_Physics_of_Golf/golf_physics.bib", "A", self._fields()),
                ("references/impact-acoustics.bib", "B", self._fields()),
            ]
        }
        assert duplicate_dois(owners) == {}

    def test_one_standalone_copy_plus_two_avoidable_copies_is_a_violation(self) -> None:
        """The standalone copy is pinned, but the other two still duplicate each other."""
        owners = {
            "10.1/x": [
                ("articles/The_Physics_of_Golf/golf_physics.bib", "A", self._fields()),
                ("references/impact-acoustics.bib", "B", self._fields()),
                ("some/other/non-exempt.bib", "C", self._fields()),
            ]
        }
        assert "10.1/x" in duplicate_dois(owners)

    def test_standalone_linked_paths_exist_in_the_repo(self) -> None:
        """Guards against the set silently going stale if a path is ever renamed."""
        repo = Path(__file__).resolve().parent.parent
        for rel in STANDALONE_LINKED:
            assert (repo / rel).is_file(), rel
