#!/usr/bin/env python3
r"""
Robust Quarto Syntax Scanner (State Machine Implementation)
Scans .qmd and .md files for common syntax issues that prevent proper rendering.

Checks:
1. LaTeX delimiters \( and \[ (recommends $ and $$)
2. Spaces inside inline math ($ x $)
3. Escaped underscores inside math ($x\_i$)
4. Unclosed math environments ($$ without closing $$)
5. Empty math blocks
"""

import enum
import sys
from collections.abc import Callable  # noqa: F401  (used in type annotation below)
from pathlib import Path
from typing import Any

from src.tools.utils import find_markdown_files, setup_logging_with_timestamp

logger = setup_logging_with_timestamp(__name__)


class _State(enum.IntEnum):
    """Parser states for the Quarto syntax scanner."""

    TEXT = 0
    CODE_BLOCK = 1
    INLINE_CODE = 2
    DISPLAY_MATH = 3
    INLINE_MATH = 4


class QuartoSyntaxScanner:
    """State-machine scanner for Quarto / Markdown syntax issues.

    Each parser state is handled by a dedicated method, keeping individual
    functions short and testable.
    """

    def __init__(self, content: str) -> None:
        self.content = content
        self.length = len(content)
        self.errors: list[tuple[int, str, str]] = []
        self.state = _State.TEXT
        self.i = 0
        self.line_num = 1
        self.start_line = 0
        self.math_content_start = 0

    # ── public API ─────────────────────────────────────────────

    def scan(self) -> list[tuple[int, str, str]]:
        """Run the scanner and return a list of ``(line, message, suggestion)``."""
        while self.i < self.length:
            char = self.content[self.i]
            if char == "\n":
                self.line_num += 1

            handler = _STATE_HANDLERS[self.state]
            handler(self, char)

        # End-of-file checks
        if self.state == _State.DISPLAY_MATH:
            self.errors.append((self.start_line, "Unclosed display math", "Add closing $$"))

        return self.errors

    # ── state handlers ─────────────────────────────────────────

    def _handle_text(self, char: str) -> None:
        c = self.content
        i = self.i

        # Code block ```
        if char == "`" and i + 2 < self.length and c[i + 1] == "`" and c[i + 2] == "`":
            self.state = _State.CODE_BLOCK
            self.i += 3
            return

        # Inline code `
        if char == "`":
            self.state = _State.INLINE_CODE
            self.i += 1
            return

        # Display math $$
        if char == "$" and i + 1 < self.length and c[i + 1] == "$":
            self.state = _State.DISPLAY_MATH
            self.start_line = self.line_num
            self.math_content_start = i + 2
            self.i += 2
            return

        # Inline math $
        if char == "$":
            if i > 0 and c[i - 1] == "\\":
                self.i += 1
                return
            self.state = _State.INLINE_MATH
            self.start_line = self.line_num
            self.math_content_start = i + 1
            self.i += 1
            return

        # Deprecated delimiters \( and \[
        if char == "\\" and i + 1 < self.length:
            nxt = c[i + 1]
            if nxt == "(":
                self.errors.append((self.line_num, "Found \\(", "Use $ ... $ for inline math"))
            elif nxt == "[":
                self.errors.append((self.line_num, "Found \\[", "Use $$ ... $$ for display math"))
            self.i += 2
            return

        self.i += 1

    def _handle_code_block(self, char: str) -> None:
        c = self.content
        i = self.i
        if char == "`" and i + 2 < self.length and c[i + 1] == "`" and c[i + 2] == "`":
            self.state = _State.TEXT
            self.i += 3
        else:
            self.i += 1

    def _handle_inline_code(self, char: str) -> None:
        if char == "`":
            self.state = _State.TEXT
        self.i += 1

    def _handle_display_math(self, char: str) -> None:
        c = self.content
        i = self.i
        if char == "$" and i + 1 < self.length and c[i + 1] == "$":
            math_text = c[self.math_content_start : i]
            if "\\_" in math_text:
                self.errors.append(
                    (self.start_line, "Escaped underscore in display math", "Use _ instead of \\_")
                )
            self.state = _State.TEXT
            self.i += 2
        else:
            self.i += 1

    def _handle_inline_math(self, char: str) -> None:
        c = self.content
        i = self.i

        # Escaped dollar inside inline math
        if char == "\\" and i + 1 < self.length and c[i + 1] == "$":
            self.i += 2
            return

        if char == "$":
            self._validate_inline_math_content(c[self.math_content_start : i])
            self.state = _State.TEXT
            self.i += 1
        elif char == "\n":
            # Double newline → assume not math (e.g. currency "$10 to $20")
            if i + 1 < self.length and c[i + 1] == "\n":
                self.state = _State.TEXT
            self.i += 1
        else:
            self.i += 1

    # ── validation helpers ─────────────────────────────────────

    def _validate_inline_math_content(self, math_text: str) -> None:
        """Check a captured inline math block for common issues."""
        if not math_text:
            self.errors.append((self.start_line, "Empty inline math", "Remove empty $...$"))
            return

        if math_text[0].isspace():
            self.errors.append(
                (
                    self.start_line,
                    f"Leading space in inline math: '${math_text[:5]}...'",
                    "Remove space after $",
                )
            )

        if math_text[-1].isspace() and len(math_text) > 1 and math_text[-2] != "\\":
            self.errors.append(
                (
                    self.start_line,
                    f"Trailing space in inline math: '...{math_text[-5:]}$'",
                    "Remove space before $",
                )
            )

        if "\\_" in math_text:
            self.errors.append(
                (
                    self.start_line,
                    f"Escaped underscore in inline math: '${math_text[:10]}...'",
                    "Use _ instead of \\_",
                )
            )


# Map each state to its handler method for O(1) dispatch
_STATE_HANDLERS: dict[_State, Any] = {
    _State.TEXT: QuartoSyntaxScanner._handle_text,
    _State.CODE_BLOCK: QuartoSyntaxScanner._handle_code_block,
    _State.INLINE_CODE: QuartoSyntaxScanner._handle_inline_code,
    _State.DISPLAY_MATH: QuartoSyntaxScanner._handle_display_math,
    _State.INLINE_MATH: QuartoSyntaxScanner._handle_inline_math,
}


def check_file(filepath: Path) -> list[tuple[int, str, str]]:
    """Scan a file for Quarto syntax errors.

    Returns list of ``(line_number, error_message, suggestion)``.
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        logger.exception("Failed to read %s", filepath)
        return []

    return QuartoSyntaxScanner(content).scan()


def main() -> None:
    """Scan all Quarto files for syntax issues and report findings."""
    files = find_markdown_files()
    total_issues = 0

    logger.info("Scanning %d files...", len(files))

    for f in files:
        issues = check_file(f)
        if issues:
            logger.warning("File: %s", f)
            for line, msg, fix in issues:
                logger.warning("  Line %d: %s -> %s", line, msg, fix)
            total_issues += len(issues)

    if total_issues > 0:
        logger.error("Found %d issues.", total_issues)
        sys.exit(1)
    else:
        logger.info("No issues found!")
        sys.exit(0)


if __name__ == "__main__":
    main()
