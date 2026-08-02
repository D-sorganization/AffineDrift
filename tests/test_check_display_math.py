"""Tests for check_display_math.py.

ch08 stated the triple-pendulum equations of motion with no `$$` around them,
so Pandoc read the line as a paragraph, consumed each `\\command` and kept the
punctuation. The page shipped

    The equations of motion for a planar triple pendulum are: () + (, ) + () =

The two traps below are the ones the first scan written for this fell into: it
reported 57 sites where there were 24.
"""

from __future__ import annotations

from pathlib import Path

from scripts.check_display_math import scan, suspicious


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "ch.qmd"
    path.write_text(text, encoding="utf-8")
    return path


class TestSuspicious:
    """Telling maths apart from prose that merely contains an ampersand."""

    def test_flags_a_bare_equation(self) -> None:
        assert suspicious(r"\bm{M}(\bm{q}) \ddot{\bm{q}} + \bm{C}(\bm{q}) = \bm{u}")

    def test_flags_a_bare_matrix_row(self) -> None:
        assert suspicious(r"M_{rr}(q,\eta) & M_{rf}(q,\eta) \\")

    def test_ignores_a_numbered_reference(self) -> None:
        """'10. Jouffroy, J., & Slotine, J. J. E. (2004)' is a citation."""
        assert not suspicious("10. Jouffroy, J., & Slotine, J. J. E. (2004). Methodological")

    def test_ignores_bold_prose_with_an_ampersand(self) -> None:
        assert not suspicious("**Gosselin & Angeles' Singularity Analysis (1990)**")

    def test_ignores_a_sentence_carrying_inline_maths(self) -> None:
        assert not suspicious(
            r"For a partitioned system $\bm{q} = \begin{bmatrix} a \end{bmatrix}$"
        )

    def test_ignores_an_ampersand_with_no_latex(self) -> None:
        assert not suspicious("Cochran & Stobbs studied this in 1968 and again later")

    def test_ignores_a_table_row(self) -> None:
        assert not suspicious("| shoulder | 0.5 | 2.0 |")


class TestScan:
    """Whole-file behaviour, including the two traps."""

    def test_accepts_delimited_maths(self, tmp_path: Path) -> None:
        odd, bare = scan(write(tmp_path, "Text.\n\n$$\nx = y\n$$\n\nMore.\n"))
        assert odd is None
        assert bare == []

    def test_finds_undelimited_maths(self, tmp_path: Path) -> None:
        odd, bare = scan(write(tmp_path, "Text.\n\n\\bm{M} \\ddot{\\bm{q}} = \\bm{u}\n\nMore.\n"))
        assert odd is None
        assert [number for number, _ in bare] == [3]

    def test_a_one_line_equation_does_not_invert_the_state(self, tmp_path: Path) -> None:
        """`$$ x = y $$` opens and closes on one line.

        Toggling on every line beginning `$$` inverts the flag from there on,
        which is what made the first scan report maths inside proper blocks.
        """
        text = "$$ x = y $$\n\n$$\n\\bm{A} = \\bm{B}\n$$\n\nProse.\n"
        odd, bare = scan(write(tmp_path, text))
        assert odd is None
        assert bare == []

    def test_a_labelled_closer_is_a_delimiter(self, tmp_path: Path) -> None:
        text = "$$\n\\bm{A} = \\bm{B}\n$$ {#eq-a}\n\nProse.\n"
        odd, bare = scan(write(tmp_path, text))
        assert odd is None
        assert bare == []

    def test_an_odd_delimiter_count_is_its_own_finding(self, tmp_path: Path) -> None:
        """A fence that never closes makes any such scan unreliable after it."""
        odd, bare = scan(write(tmp_path, "$$\nx = y\n\nProse.\n"))
        assert odd == 1
        assert bare == []

    def test_a_raw_latex_equation_environment_is_maths(self, tmp_path: Path) -> None:
        """Pandoc renders `\\begin{equation}` in a .qmd as display maths.

        Verified against a probe file: one such block becomes one `\\[ … \\]`.
        The Geometry of Motion mirror uses this form throughout, so flagging it
        would report an entire textbook as broken when it renders correctly.
        """
        text = "Text.\n\n\\begin{equation}\n\\bm{M} \\ddot{\\bm{q}} = \\bm{u}\n\\end{equation}\n\nMore.\n"
        odd, bare = scan(write(tmp_path, text))
        assert odd is None
        assert bare == []

    def test_a_raw_align_environment_is_maths(self, tmp_path: Path) -> None:
        text = "\\begin{align}\na &= b \\\\\nc &= d\n\\end{align}\n"
        odd, bare = scan(write(tmp_path, text))
        assert odd is None
        assert bare == []

    def test_maths_inside_a_code_fence_is_ignored(self, tmp_path: Path) -> None:
        text = "```\n\\bm{M} \\ddot{\\bm{q}} = \\bm{u}\n```\n"
        odd, bare = scan(write(tmp_path, text))
        assert odd is None
        assert bare == []
