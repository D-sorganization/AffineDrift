"""Line-preserving removal of fenced Quarto code examples."""

from __future__ import annotations

import re

FENCE_OPEN = re.compile(r"^\s*(`{3,}|~{3,})")


def strip_fenced_code(text: str) -> str:
    """Blank fenced lines, preserving line numbers and newline boundaries.

    Close only with the opener's character and at least its run length,
    followed by whitespace. An unclosed fence consumes the remaining text.
    Preconditions: ``text`` is a string. No inline code is removed.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    closing: re.Pattern[str] | None = None
    lines: list[str] = []
    for line in text.splitlines(keepends=True):
        if closing is not None:
            if closing.fullmatch(line.rstrip("\r\n")):
                closing = None
            lines.append("\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else "")
            continue
        opening = FENCE_OPEN.match(line)
        if opening is None:
            lines.append(line)
            continue
        marker = opening.group(1)
        closing = re.compile(r"\s*" + re.escape(marker[0]) + "{" + str(len(marker)) + r",}\s*")
        lines.append("\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else "")
    return "".join(lines)
