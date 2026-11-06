"""Pin that the Alpha War draft is outside the site render set and the sitemap (#5370)."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DRAFT = REPO_ROOT / "research" / "alpha-war" / "draft" / "alpha-war-v1.md"
QUARTO_YML = REPO_ROOT / "_quarto.yml"
SITEMAP_SCRIPT = REPO_ROOT / "scripts" / "generate_sitemap.py"


def _render_patterns() -> list[str]:
    """Return the include patterns of the ``project.render`` list in _quarto.yml."""
    block = QUARTO_YML.read_text(encoding="utf-8").split("\n  render:\n", 1)[1]
    block = block.split("\n  resources:", 1)[0]
    return re.findall(r'^\s+- "([^"!][^"]*)"', block, re.M)


def _sitemap_dirs() -> list[str]:
    """Return SITEMAP_CONTENT_DIRS parsed from the sitemap script."""
    text = SITEMAP_SCRIPT.read_text(encoding="utf-8")
    body = text.split("SITEMAP_CONTENT_DIRS = [", 1)[1].split("]", 1)[0]
    return re.findall(r'"([^"]*)"', body)


class TestNotInSiteListing(unittest.TestCase):
    """The draft is not rendered by the site project and not collected for the sitemap."""

    def test_draft_is_matched_by_no_site_render_pattern(self) -> None:
        """No project.render include pattern selects the draft file."""
        relative = DRAFT.relative_to(REPO_ROOT)
        patterns = _render_patterns()
        self.assertTrue(len(patterns) >= 5)
        matched = [pat for pat in patterns if relative.match(pat)]
        self.assertEqual(matched, [])

    def test_alpha_war_is_not_a_sitemap_content_directory(self) -> None:
        """The sitemap collects no directory that contains research/alpha-war."""
        dirs = _sitemap_dirs()
        self.assertTrue("articles" in dirs)
        self.assertTrue("research" not in dirs)
        self.assertTrue(not any("alpha-war" in d for d in dirs))

    def test_sitemap_collects_qmd_only_and_the_draft_is_markdown(self) -> None:
        """The sitemap walks .qmd sources; the draft is a .md file under research/."""
        self.assertTrue("collect_qmd_files" in SITEMAP_SCRIPT.read_text(encoding="utf-8"))
        self.assertEqual(DRAFT.suffix, ".md")
        self.assertEqual(DRAFT.relative_to(REPO_ROOT).parts[0], "research")


if __name__ == "__main__":
    unittest.main()
