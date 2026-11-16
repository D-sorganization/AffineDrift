"""Tests for check_latex_quotes.py.

The Geometry of Motion mirror shipped `` ``best linear approximation'' `` as
literal backticks and right-quotes. 93 pairs were converted; these cases are the
exclusions that had to be right first, each of which produced a wrong count
while the sweep was being written.
"""

from __future__ import annotations

from scripts.check_latex_quotes import find, masked

OPEN = "`" * 2
CLOSE = "'" * 2


def quoted(inner: str) -> str:
    return f"{OPEN}{inner}{CLOSE}"


class TestFind:
    """What counts as a LaTeX quote pair in prose."""

    def test_finds_a_pair(self) -> None:
        assert find(f"The {quoted('best linear approximation')} to the curve.\n")

    def test_finds_a_pair_spanning_two_lines(self) -> None:
        """Most of the real ones opened on one line and closed on the next."""
        text = (
            f"we apologize: {OPEN}Yes, the model is wrong for\nsmall perturbations.{CLOSE} In the\n"
        )
        assert len(find(text)) == 1

    def test_accepts_plain_quotes(self) -> None:
        assert find('The "best linear approximation" to the curve.\n') == []


class TestExclusions:
    """Everything that must not be touched."""

    def test_a_double_prime_is_not_a_quote(self) -> None:
        r"""`\phi_i''''` is a fourth derivative, not two quotation marks."""
        assert find("$$\nEI \\,\\phi_i'''' = \\omega_i^2 \\rho A \\,\\phi_i\n$$\n") == []

    def test_a_prime_in_inline_maths_is_not_a_quote(self) -> None:
        assert find("The curvature $\\norm{\\traj'}^2\\norm{\\traj''}^2$ is positive.\n") == []

    def test_a_fenced_block_is_ignored(self) -> None:
        assert find(f"```\n{quoted('not prose')}\n```\n") == []

    def test_a_fence_inside_a_blockquote_is_ignored(self) -> None:
        """`> ```' is still a fence; missing that produced two false positives."""
        assert find(f"> ```\n> {quoted('not prose')}\n> ```\n") == []

    def test_a_raw_latex_maths_environment_is_ignored(self) -> None:
        text = "\\begin{equation}\nf''(x) = 0\n\\end{equation}\n"
        assert find(text) == []

    def test_inline_code_is_ignored(self) -> None:
        assert find(f"Write `{quoted('x')}` to quote.\n") == []

    def test_a_one_line_display_equation_does_not_break_the_state(self) -> None:
        """`$$ x = y $$` opens and closes on one line.

        Treating it as a toggle inverts the state for the rest of the file,
        which is the trap that has cost three separate scans in this review.
        """
        text = f"$$ x = y $$\n\nThe {quoted('tangent plane')} is flat.\n"
        assert len(find(text)) == 1


class TestMasked:
    """The mask must line up with the original, or the offsets are wrong."""

    def test_mask_preserves_length(self) -> None:
        text = f"Prose {quoted('a')} and `code` and $x$ here.\n"
        assert len(masked(text)) == len(text)

    def test_mask_keeps_newlines(self) -> None:
        text = "```\nhidden\n```\nvisible\n"
        assert masked(text).count("\n") == text.count("\n")

    def test_a_bare_open_quote_is_not_an_empty_code_span(self) -> None:
        """`[^`]*` lets `` match as empty inline code, hiding the opener."""
        text = f"we said {OPEN}something long here\nand closed it.{CLOSE}\n"
        assert OPEN in masked(text)


class TestMultiplePairsAndLongFences:
    """Two pairs on one line, and fences longer than three backticks."""

    def test_two_pairs_on_one_line_are_both_found(self) -> None:
        """The first closing mark and the second opener must not read as code."""
        text = f"He said {quoted('first')} and then {quoted('second')} to us.\n"
        assert [q for _, q in find(text)] == ["first", "second"]

    def test_pair_then_inline_code_still_finds_the_pair(self) -> None:
        text = f"The {quoted('tangent')} of `f` is flat.\n"
        assert [q for _, q in find(text)] == ["tangent"]

    def test_a_four_backtick_fence_may_contain_a_three_backtick_line(self) -> None:
        """The inner ``` is content, so the pair after it is still fenced."""
        text = f"````\n```\n{quoted('not prose')}\n````\n"
        assert find(text) == []

    def test_a_tilde_fence_may_contain_a_shorter_tilde_line(self) -> None:
        text = f"~~~~\n~~~\n{quoted('not prose')}\n~~~~\n"
        assert find(text) == []
