"""The rendered site has no executable Quarto cells (issue #4539).

`ci-standard.yml` documents that "the site has no executable cells" to
justify skipping the Quarto freeze cache. This test enforces that claim
against every `.qmd` file Quarto actually renders (per `_quarto.yml`'s
`project.render` include/exclude globs), so a stray `{python}`/`{r}`/
`{javascript}`/`{ojs}`/`{julia}` cell fails CI instead of silently
contradicting the documentation.
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts.check_quarto_render_coverage import load_render_rules

REPO_ROOT = Path(__file__).resolve().parent.parent
EXECUTABLE_CELL_PATTERN = re.compile(r"^```\{(python|r|javascript|ojs|julia)\b", re.MULTILINE)


def _rendered_qmd_files() -> list[Path]:
    rules = load_render_rules(REPO_ROOT / "_quarto.yml")
    included: set[Path] = set()
    excluded: set[Path] = set()
    for rule in rules:
        if not rule.endswith(".qmd"):
            continue
        negate = rule.startswith("!")
        pattern = rule[1:] if negate else rule
        matches = set(REPO_ROOT.glob(pattern))
        if negate:
            excluded |= matches
        else:
            included |= matches
    return sorted(included - excluded)


def test_rendered_qmd_files_have_no_executable_cells() -> None:
    offenders = []
    for qmd in _rendered_qmd_files():
        text = qmd.read_text(encoding="utf-8")
        if EXECUTABLE_CELL_PATTERN.search(text):
            offenders.append(str(qmd.relative_to(REPO_ROOT)))
    assert not offenders, f"Executable Quarto cells found in rendered pages: {offenders}"
