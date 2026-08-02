"""Fail when LaTeX quotation marks survive into rendered prose.

LaTeX quotes as ``opening'' and TeX renders curly quotes from it. Markdown does
not, so the .tex -> .qmd conversions carried the raw marks across and the pages
shipped them:

    the ``best linear approximation'' to the curve at that point

The opening pair survives as two literal backticks; the closing pair becomes two
right single quotes. Neither is a double quote. Quarto's smart quotes turn a
plain "..." into the curly form, which is what the rest of the prose relies on.

Only *pairs* are reported. A lone `''` is usually a double prime -- `\\phi_i''''`
is a fourth derivative -- and a lone `` is usually part of a code fence. The
pair is the unambiguous signal, and the corpus is clean of pairs.

Three exclusions are needed, and each cost a wrong count while this was written:

  * fenced code, including a fence inside a blockquote (`> ```);
  * `$$` blocks, including a one-line `$$ x $$`, which opens and closes on the
    same line and so must not toggle any state;
  * raw LaTeX maths environments, which Pandoc renders as maths.

And one regex trap: an inline-code pattern of `` `[^`]*` `` matches a bare ``
as an *empty* code span, which hides the very opening quote being looked for.
The content must be required.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path("articles")

BLOCK = re.compile(
    r"(?s)^\s*>?\s*```.*?^\s*>?\s*```"
    r"|^\s*>?\s*~~~.*?^\s*>?\s*~~~"
    r"|^\s*\$\$\s*$.*?^\s*\$\$"
    r"|\\begin\{(?:equation|align|gather|multline|displaymath|eqnarray)\*?\}.*?"
    r"\\end\{(?:equation|align|gather|multline|displaymath|eqnarray)\*?\}",
    re.MULTILINE,
)
INLINE = re.compile(r"\$\$.+?\$\$|\$[^$\n]+\$|`{1,3}[^`\n]+`{1,3}")
PAIRED = re.compile(r"``(.+?)''", re.DOTALL)


def masked(text: str) -> str:
    """Same-length copy with code and maths blanked out."""
    out = list(text)

    def blank(start: int, end: int) -> None:
        for index in range(start, end):
            if out[index] != "\n":
                out[index] = "\x00"

    for match in BLOCK.finditer(text):
        blank(match.start(), match.end())
    for match in INLINE.finditer("".join(out)):
        blank(match.start(), match.end())
    return "".join(out)


def find(text: str) -> list[tuple[int, str]]:
    """(line number, quoted text) for each LaTeX quote pair in prose."""
    mask = masked(text)
    found = []
    for match in PAIRED.finditer(mask):
        line = text.count("\n", 0, match.start()) + 1
        quoted = text[match.start() + 2 : match.end() - 2]
        found.append((line, quoted.replace("\n", " ")[:60]))
    return found


def main() -> int:
    problems = 0
    checked = 0
    for path in sorted(ROOT.rglob("*.qmd")):
        checked += 1
        for line, quoted in find(path.read_text(encoding="utf-8", errors="replace")):
            problems += 1
            print(
                f"  {path.as_posix()}:{line}: LaTeX quotes around '{quoted}' -- "
                f'markdown renders these literally; use "..." and let smart quotes curl them'
            )

    if problems:
        print(f"\n  {problems} LaTeX quote pair(s) that render as raw marks")
        return 1

    print(f"  {checked} file(s) checked, no LaTeX quotation marks in prose")
    return 0


if __name__ == "__main__":
    sys.exit(main())
