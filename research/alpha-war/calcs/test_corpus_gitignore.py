"""Ensure Facebook corpus exports stay out of version control."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CORPUS_DIR = REPO_ROOT / "research" / "alpha-war" / "corpus"
GITIGNORE = REPO_ROOT / "research" / "alpha-war" / ".gitignore"


class TestAlphaWarCorpusGitignore(unittest.TestCase):
    """Corpus export directory must stay git-ignored per #5206."""

    def test_gitignore_lists_corpus(self) -> None:
        """The alpha-war gitignore file must list ``corpus/``."""
        self.assertIn("corpus/", GITIGNORE.read_text(encoding="utf-8"))

    def test_corpus_directory_is_ignored_by_git(self) -> None:
        """Git must treat files under ``corpus/`` as ignored."""
        CORPUS_DIR.mkdir(parents=True, exist_ok=True)
        probe = CORPUS_DIR / ".keep"
        probe.write_text("", encoding="utf-8")
        try:
            result = subprocess.run(
                ["git", "check-ignore", "-q", str(probe.relative_to(REPO_ROOT))],
                cwd=REPO_ROOT,
                check=False,
            )
            self.assertEqual(result.returncode, 0, "corpus/ must be ignored by git")
        finally:
            probe.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
