"""Pin figure integrity: alt text, calcs-built SVGs, honest Fig. 11 (#5368)."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from alpha_war_figures import fig_nesbit_fig11_schematic

ALPHA_WAR = Path(__file__).resolve().parents[1]
DRAFT = ALPHA_WAR / "draft" / "alpha-war-v1.md"
FIG_DIR = ALPHA_WAR / "draft" / "figures"
IMAGE = re.compile(r"^!\[(?P<caption>.*?)\]\((?P<path>[^)]+)\)(?P<attrs>\{[^}]*\})?", re.M)
#: Handicap and sex per subject, confirmed against Nesbit and Serrano (2005) Table 1.
SUBJECTS = ("Subject 1", "Subject 2", "Subject 3", "Subject 4")
INVENTED = ("-18", "+12", "0.73", "Takeaway", "Impact trend", "plateaus", "casts early")


class TestFigureIntegrity(unittest.TestCase):
    """Every figure has alt text and a file; Fig. 11 shows no untabulated values."""

    def test_every_figure_has_alt_text_and_an_existing_file(self) -> None:
        """Each image in the draft names a real file and a non-empty fig-alt."""
        problems = []
        for match in IMAGE.finditer(DRAFT.read_text(encoding="utf-8")):
            attrs = match.group("attrs") or ""
            alt = re.search(r'fig-alt="([^"]+)"', attrs)
            if alt is None:
                problems.append(f"no alt: {match.group('path')}")
            if not (DRAFT.parent / match.group("path")).is_file():
                problems.append(f"missing: {match.group('path')}")
        self.assertEqual(problems, [])

    def test_no_ascii_box_tables(self) -> None:
        """The draft has no +---+ or box-drawing tables."""
        text = DRAFT.read_text(encoding="utf-8")
        self.assertTrue(re.search(r"^\s*\+[-=+]{5,}\+", text, re.M) is None)
        self.assertTrue(not any(ch in text for ch in "┌└├┐┘┤"))

    def test_fig11_caption_cites_the_paper(self) -> None:
        """The Fig. 11 caption carries the Nesbit and Serrano citation key."""
        text = DRAFT.read_text(encoding="utf-8")
        line = next(ln for ln in text.splitlines() if "fig-nesbit-fig11-schematic" in ln)
        self.assertTrue("[@nesbit2005work" in line)

    def test_fig11_shows_no_untabulated_values_or_trends(self) -> None:
        """The Fig. 11 panel set labels four subjects and invents no value."""
        svg = fig_nesbit_fig11_schematic()
        for label in SUBJECTS:
            self.assertTrue(label in svg, msg=label)
        for token in INVENTED:
            self.assertTrue(token not in svg, msg=token)
        self.assertTrue("unverified, VRF-11" in svg)
        self.assertTrue("polyline" not in svg)

    def test_committed_fig11_svg_matches_the_generator(self) -> None:
        """The committed SVG equals the generator output (no hand edits)."""
        committed = (FIG_DIR / "fig-nesbit-fig11-schematic.svg").read_text(encoding="utf-8")
        self.assertTrue(committed == fig_nesbit_fig11_schematic())


if __name__ == "__main__":
    unittest.main()
