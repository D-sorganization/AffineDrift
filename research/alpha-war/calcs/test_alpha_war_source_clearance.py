"""Pin source clearance for Facebook and private-group material (#5366).

Tracked Alpha War text must carry no private-group URL or numeric group ID, the
clearance register must tag every social-media source, and ``corpus/`` must not
be tracked by git.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ALPHA_WAR = Path(__file__).resolve().parents[1]
REPO_ROOT = ALPHA_WAR.parents[1]
PENDING = ALPHA_WAR / "CLEARANCE_PENDING.md"
DIGEST = ALPHA_WAR / "work" / "01_corpus_digest.md"
TEXT_SUFFIXES = {".md", ".bib", ".json", ".py", ".yml", ".yaml", ".txt"}
#: The only Facebook group whose permalinks are stated to be public (CLR-07).
PUBLIC_GROUP = "golfbiomechanists"
GROUP_URL = re.compile(r"facebook\.com/groups/([A-Za-z0-9_.-]+)", re.I)
NUMERIC_GROUP_ID = re.compile(r"group[ _-]?id\D{0,12}\d{6,}", re.I)


def _tracked_text_files() -> list[Path]:
    """Return the text files under research/alpha-war (excluding corpus/)."""
    return [
        path
        for path in ALPHA_WAR.rglob("*")
        if path.is_file()
        and path.suffix in TEXT_SUFFIXES
        and "corpus" not in path.relative_to(ALPHA_WAR).parts[:1]
        and "__pycache__" not in path.parts
        and path != Path(__file__).resolve()
    ]


class TestSourceClearance(unittest.TestCase):
    """The repository holds no private-group identifiers and a status register."""

    def test_only_the_public_group_is_linked(self) -> None:
        """Any Facebook group URL in tracked text names the public group."""
        offenders = []
        for path in _tracked_text_files():
            text = path.read_text(encoding="utf-8")
            for group in GROUP_URL.findall(text):
                if group.lower() != PUBLIC_GROUP:
                    offenders.append(f"{path.name}:{group}")
        self.assertEqual(offenders, [])

    def test_no_numeric_private_group_id(self) -> None:
        """No tracked text spells out a numeric group ID."""
        offenders = [
            path.name
            for path in _tracked_text_files()
            if NUMERIC_GROUP_ID.search(path.read_text(encoding="utf-8"))
        ]
        self.assertEqual(offenders, [])

    def test_private_group_permalinks_are_withheld_in_the_digest(self) -> None:
        """The digest carries the withheld-marker instead of private URLs."""
        text = DIGEST.read_text(encoding="utf-8")
        self.assertTrue("groups/postmoderngolf" not in text.lower())
        self.assertTrue("withheld; not cleared, CLR-09" in text)

    def test_register_tags_every_social_media_source(self) -> None:
        """CLR-01, 06, 07, 08 and 09 each have a status in the register."""
        register = PENDING.read_text(encoding="utf-8").split("## Clearance status register")[1]
        for clr_id in ("CLR-01", "CLR-06", "CLR-07", "CLR-08", "CLR-09"):
            row = next(ln for ln in register.splitlines() if ln.startswith(f"| {clr_id} "))
            self.assertTrue(("not cleared" in row) or ("unverified" in row), msg=clr_id)

    def test_corpus_directory_has_no_tracked_files(self) -> None:
        """Git tracks nothing under research/alpha-war/corpus/."""
        git = shutil.which("git")
        if git is None:
            self.skipTest("git is unavailable")
        out = subprocess.run(  # noqa: S603 -- fixed argv, no shell, no user input
            [git, "ls-files", "research/alpha-war/corpus"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        self.assertEqual(out.strip(), "")


if __name__ == "__main__":
    unittest.main()
