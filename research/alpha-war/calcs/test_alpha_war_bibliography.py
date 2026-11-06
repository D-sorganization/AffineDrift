"""Pin the Alpha War bibliography: keys resolve, DOIs or notes, VRF labels (#5367)."""

from __future__ import annotations

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ALPHA_WAR = Path(__file__).resolve().parents[1]
DRAFT = ALPHA_WAR / "draft" / "alpha-war-v1.md"
BIB = ALPHA_WAR / "references.bib"
LIMITED = {
    "croker2019pushing": "VRF-05",
    "jacobs2020lookinside": "VRF-06",
    "manzella2020webinar": "VRF-07",
    "sinclair2020workshop": "VRF-08",
}
ENTRY = re.compile(r"@(\w+)\{([^,\s]+),(.*?)(?=\n@|\Z)", re.S)


def _entries() -> dict[str, tuple[str, str]]:
    """Return {key: (entry type, body)} parsed from references.bib."""
    text = BIB.read_text(encoding="utf-8")
    return {key: (kind.lower(), body) for kind, key, body in ENTRY.findall(text)}


def _cited_keys() -> set[str]:
    """Return every citation key used in a ``[@key ...]`` group of the draft."""
    keys: set[str] = set()
    for group in re.findall(r"\[(@[^\]]+)\]", DRAFT.read_text(encoding="utf-8")):
        for part in group.split(";"):
            found = re.match(r"\s*@([A-Za-z][\w:-]*\d[\w:-]*)", part)
            if found:
                keys.add(found.group(1))
    return keys


class TestBibliography(unittest.TestCase):
    """The draft cites only keys that exist, and each entry is traceable."""

    def test_frontmatter_points_at_the_bib_file(self) -> None:
        """Quarto reads references.bib, not the working registry."""
        head = DRAFT.read_text(encoding="utf-8").split("---", 2)[1]
        self.assertTrue("bibliography: ../references.bib" in head)

    def test_every_cited_key_exists(self) -> None:
        """No in-text key is missing from references.bib."""
        missing = sorted(_cited_keys() - set(_entries()))
        self.assertEqual(missing, [])

    def test_journal_entries_have_a_doi_or_a_recorded_search(self) -> None:
        """A peer-reviewed entry carries a DOI, or a note saying none was found."""
        bad = []
        for key, (kind, body) in _entries().items():
            if kind not in {"article", "inproceedings"}:
                continue
            has_doi = re.search(r"^\s*doi\s*=", body, re.M) is not None
            noted = re.search(r"note\s*=\s*\{[^}]*DOI", body) is not None
            if not (has_doi or noted):
                bad.append(key)
        self.assertEqual(bad, [])

    def test_putnam_doi_is_the_crossref_record(self) -> None:
        """Putnam (1991) carries the DOI Crossref lists for vol. 23, pp. 130-144."""
        body = _entries()["putnam1991segment"][1]
        self.assertTrue("10.1249/00005768-199101000-00019" in body)

    def test_limited_circulation_sources_are_labelled(self) -> None:
        """VRF-05 to VRF-08 sources carry their VRF id in the entry note."""
        for key, vrf in LIMITED.items():
            self.assertTrue(vrf in _entries()[key][1], msg=key)

    def test_pandoc_resolves_every_citation(self) -> None:
        """Pandoc citeproc reports no unresolved citation for the draft."""
        pandoc = shutil.which("pandoc")
        if pandoc is None:
            self.skipTest("pandoc is unavailable")
        result = subprocess.run(  # noqa: S603 -- fixed argv, no shell, no user input
            [pandoc, str(DRAFT), "--citeproc", f"--bibliography={BIB}", "-t", "plain"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertTrue("Citation" not in result.stderr)


if __name__ == "__main__":
    unittest.main()
