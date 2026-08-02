"""Tests for check_bibliography_cross_file.py.

The check exists because four citation keys meant different papers in different
.bib files, so the site cited whichever file the render listed first. The cases
below are the real ones, reduced to the smallest form that reproduces them.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.check_bibliography_cross_file import braced_field, entries, signature


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
