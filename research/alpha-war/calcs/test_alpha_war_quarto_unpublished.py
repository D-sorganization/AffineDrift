"""Quarto unpublished guardrails, citation resolution, and zero-warning render check for v1."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ALPHA_WAR_DIR = REPO_ROOT / "research" / "alpha-war"
DRAFT = ALPHA_WAR_DIR / "draft" / "alpha-war-v1.md"
BIB_PATH = ALPHA_WAR_DIR / "references.bib"
QUARTO_YML = REPO_ROOT / "_quarto.yml"


def _frontmatter_flags(text: str) -> dict[str, str]:
    """Parse simple key/value pairs from YAML frontmatter in ``text``."""
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if match is None:
        raise ValueError("missing YAML frontmatter")
    block = match.group(1)
    flags: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            flags[key.strip()] = val.strip()
    return flags


class TestAlphaWarQuartoUnpublished(unittest.TestCase):
    """Ensure the Alpha War v1 draft stays unpublished and renders with zero warnings."""

    def test_frontmatter_blocks_publication(self) -> None:
        """Draft frontmatter must mark the document as unpublished."""
        flags = _frontmatter_flags(DRAFT.read_text(encoding="utf-8"))
        self.assertEqual(flags.get("draft"), "true")
        self.assertEqual(flags.get("listing"), "false")
        self.assertEqual(flags.get("status"), "do-not-publish")

    def test_not_registered_in_quarto_site_config(self) -> None:
        """The site ``_quarto.yml`` must not positively register alpha-war paths."""
        yml = QUARTO_YML.read_text(encoding="utf-8")
        for line in yml.splitlines():
            if "research/alpha-war" not in line:
                continue
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            self.assertTrue(
                stripped.startswith('- "!'),
                f"research/alpha-war may only appear as a render exclusion: {stripped}",
            )
        self.assertIn('!research/alpha-war/**/*.md', yml)
        self.assertNotIn("alpha-war-v0", yml)
        self.assertNotIn("alpha-war-v1", yml)

    def test_all_citations_resolve_in_references_bib(self) -> None:
        """Every [@key] citation in alpha-war-v1.md must exist in references.bib."""
        draft_text = DRAFT.read_text(encoding="utf-8").replace("`[@key]`", "")
        bib_text = BIB_PATH.read_text(encoding="utf-8")
        bib_keys = set(re.findall(r"^@\w+\{([^,\s]+),", bib_text, flags=re.MULTILINE))
        cite_blocks = re.findall(r"\[([^\[\]]*@[a-zA-Z0-9_]+[^\[\]]*)\]", draft_text)
        cited_keys: set[str] = set()
        for block in cite_blocks:
            for key in re.findall(r"@([a-zA-Z0-9_]+)", block):
                cited_keys.add(key)
        self.assertGreater(len(cited_keys), 20)
        missing = sorted(cited_keys - bib_keys)
        self.assertEqual(missing, [], f"Unresolved citation keys: {missing}")

    def test_no_ascii_art_or_box_drawing_tables(self) -> None:
        """Draft v1 must not contain ASCII stick-art diagrams or box-drawing tables."""
        draft_text = DRAFT.read_text(encoding="utf-8")
        for forbidden_ascii in (
            "+===",
            "+---",
            "O===>",
            "|||",
            "```mermaid",
            "```\n  ",
            "```\n+",
            "```\n|",
        ):
            self.assertNotIn(
                forbidden_ascii,
                draft_text,
                f"Forbidden ASCII diagram/table token found: {forbidden_ascii!r}",
            )

    def test_optional_quarto_render(self) -> None:
        """When Quarto is installed, HTML render must succeed with zero warnings."""
        quarto = shutil.which("quarto")
        if quarto is None:
            self.skipTest("quarto not installed in this environment")
        env = os.environ.copy()
        env.setdefault("CODECOV_TOKEN", "unused")
        html_out = DRAFT.with_suffix(".html")
        files_dir = DRAFT.parent / f"{DRAFT.stem}_files"
        try:
            result = subprocess.run(  # noqa: S603 -- fixed argv from shutil.which, no shell
                [
                    quarto,
                    "render",
                    str(DRAFT),
                    "--to",
                    "html",
                ],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            combined_log = result.stdout + "\n" + result.stderr
            self.assertEqual(result.returncode, 0, combined_log[-2000:])
            self.assertNotIn("[WARNING]", combined_log)
            self.assertNotIn("not found", combined_log.lower())
            self.assertTrue(html_out.is_file(), "Rendered HTML file must exist")
            html_text = html_out.read_text(encoding="utf-8")
            self.assertIn("callout-warning", html_text)
            self.assertIn("callout-important", html_text)
            self.assertIn("fig-transport-stations.svg", html_text)
            self.assertIn("fig-couple-vs-com.svg", html_text)
            self.assertIn("fig-club-roll-projection.svg", html_text)
            self.assertIn("fig-filter-cutoff-sweep.svg", html_text)
            self.assertNotIn("rain-soaked professional tournament", html_text)
            self.assertNotIn("private coaching forum whose name", html_text)
        finally:
            if html_out.is_file():
                html_out.unlink()
            if files_dir.is_dir():
                shutil.rmtree(files_dir)


if __name__ == "__main__":
    unittest.main()
