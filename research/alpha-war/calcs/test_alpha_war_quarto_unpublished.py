"""Quarto unpublished guardrails for the Alpha War draft."""

from __future__ import annotations

import re
import shutil
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DRAFT = REPO_ROOT / "research" / "alpha-war" / "draft" / "alpha-war-v0.md"
QUARTO_YML = REPO_ROOT / "_quarto.yml"
RENDER_LOG = REPO_ROOT / "research" / "alpha-war" / "draft" / "render-log.txt"


def _frontmatter_flags(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    assert match, "missing YAML frontmatter"
    block = match.group(1)
    flags: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            flags[key.strip()] = val.strip()
    return flags


class TestAlphaWarQuartoUnpublished(unittest.TestCase):
    def test_frontmatter_blocks_publication(self) -> None:
        flags = _frontmatter_flags(DRAFT.read_text(encoding="utf-8"))
        self.assertEqual(flags.get("draft"), "true")
        self.assertEqual(flags.get("listing"), "false")
        self.assertEqual(flags.get("status"), "do-not-publish")

    def test_not_registered_in_quarto_site_config(self) -> None:
        yml = QUARTO_YML.read_text(encoding="utf-8")
        self.assertNotIn("research/alpha-war", yml)
        self.assertNotIn("alpha-war-v0", yml)

    def test_optional_quarto_render(self) -> None:
        quarto = shutil.which("quarto")
        if quarto is None:
            self.skipTest("quarto not installed in this environment")
        result = subprocess.run(
            [
                quarto,
                "render",
                str(DRAFT),
                "--to",
                "html",
                "--output-dir",
                str(DRAFT.parent / "_render_check"),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        RENDER_LOG.write_text(result.stdout + "\n" + result.stderr, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr[-2000:])


if __name__ == "__main__":
    unittest.main()
