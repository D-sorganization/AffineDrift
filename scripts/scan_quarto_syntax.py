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

import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def find_files(root_dir: str = ".") -> list[Path]:
    """Find all .qmd and .md files in relevant directories."""
    files = []
    root = Path(root_dir)

    # Root files
    for f in root.iterdir():
        if f.is_file() and f.suffix in {".qmd", ".md"} and not f.name.startswith("README"):
            files.append(f)

    # Directories to scan
    dirs_to_scan = ["articles", "critiques"]

    for d in dirs_to_scan:
        path = root / d
        if path.exists():
            for f in path.rglob("*"):
                if f.is_file() and f.suffix in {".qmd", ".md"} and "archive" not in f.parts:
                    files.append(f)

    return files


def check_file(filepath: Path) -> list[tuple[int, str, str]]:
    """
    Scans a file for errors using a state machine.
    Returns list of (line_number, error_message, suggestion).
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to read {filepath}: {e}")
        return []

    errors = []

    # States
    STATE_TEXT = 0
    STATE_CODE_BLOCK = 1  # ``` ... ```
    STATE_INLINE_CODE = 2  # ` ... `
    STATE_DISPLAY_MATH = 3  # $$ ... $$
    STATE_INLINE_MATH = 4  # $ ... $

    state = STATE_TEXT

    i = 0
    length = len(content)
    line_num = 1

    start_line = 0  # To track where a block started
    math_content_start = 0

    while i < length:
        char = content[i]

        # Track line numbers
        if char == "\n":
            line_num += 1
            # Do not continue; let states handle newline if needed

        # ---------------------------------------------------------
        # State: TEXT
        # ---------------------------------------------------------
        if state == STATE_TEXT:
            # Check for Code Block ```
            if char == "`" and i + 2 < length and content[i + 1] == "`" and content[i + 2] == "`":
                state = STATE_CODE_BLOCK
                i += 3
                continue

            # Check for Inline Code `
            if char == "`":
                state = STATE_INLINE_CODE
                i += 1
                continue

            # Check for Display Math $$
            if char == "$" and i + 1 < length and content[i + 1] == "$":
                state = STATE_DISPLAY_MATH
                start_line = line_num
                math_content_start = i + 2
                i += 2
                continue

            # Check for Inline Math $
            # Must not be followed by space, tab, or newline (unless it's currency? heuristic needed)
            # Quarto/Pandoc requires $x$ not $ x $.
            # Actually, standard Pandoc allows $ 10 $ to be just text, but $x$ is math.
            # However, we want to enforce strictness.
            if char == "$":
                # Check if it is escaped \$
                if i > 0 and content[i - 1] == "\\":
                    i += 1
                    continue

                state = STATE_INLINE_MATH
                start_line = line_num
                math_content_start = i + 1
                i += 1
                continue

            # Check for deprecated delimiters \( and \[
            if char == "\\" and i + 1 < length:
                next_char = content[i + 1]
                if next_char == "(":
                    errors.append((line_num, "Found \\(", "Use $ ... $ for inline math"))
                elif next_char == "[":
                    # Check if it is part of a link/attribute syntax like \[...\] in rare cases?
                    # But generally \[ ... \] is display math in LaTeX.
                    # We accept it might be used for other things, but warn.
                    # Heuristic: check if it looks like `\[ ... \]`
                    errors.append((line_num, "Found \\[", "Use $$ ... $$ for display math"))
                i += 2
                continue

            i += 1

        # ---------------------------------------------------------
        # State: CODE BLOCK
        # ---------------------------------------------------------
        elif state == STATE_CODE_BLOCK:
            if char == "`" and i + 2 < length and content[i + 1] == "`" and content[i + 2] == "`":
                state = STATE_TEXT
                i += 3
            else:
                i += 1

        # ---------------------------------------------------------
        # State: INLINE CODE
        # ---------------------------------------------------------
        elif state == STATE_INLINE_CODE:
            if char == "`":
                state = STATE_TEXT
                i += 1
            else:
                i += 1

        # ---------------------------------------------------------
        # State: DISPLAY MATH
        # ---------------------------------------------------------
        elif state == STATE_DISPLAY_MATH:
            if char == "$" and i + 1 < length and content[i + 1] == "$":
                # End of display math
                math_text = content[math_content_start:i]

                # Check for escaped underscores
                if "\\_" in math_text:
                    errors.append(
                        (start_line, "Escaped underscore in display math", "Use _ instead of \\_")
                    )

                state = STATE_TEXT
                i += 2
            else:
                i += 1

        # ---------------------------------------------------------
        # State: INLINE MATH
        # ---------------------------------------------------------
        elif state == STATE_INLINE_MATH:
            # Check for escaped dollar inside inline math
            if char == "\\" and i + 1 < length and content[i + 1] == "$":
                i += 2
                continue

            if char == "$":
                # End of inline math
                math_text = content[math_content_start:i]

                # Validation logic
                if not math_text:
                    errors.append((start_line, "Empty inline math", "Remove empty $...$"))
                else:
                    # Check for leading/trailing spaces
                    if math_text[0].isspace():
                        errors.append(
                            (
                                start_line,
                                f"Leading space in inline math: '${math_text[:5]}...'",
                                "Remove space after $",
                            )
                        )
                    if math_text[-1].isspace() and len(math_text) > 1 and math_text[-2] != "\\":
                        # ensure the space isn't escaped like "\ " (though rare in math mode endings)
                        errors.append(
                            (
                                start_line,
                                f"Trailing space in inline math: '...{math_text[-5:]}$'",
                                "Remove space before $",
                            )
                        )

                    # Check for escaped underscores
                    if "\\_" in math_text:
                        errors.append(
                            (
                                start_line,
                                f"Escaped underscore in inline math: '${math_text[:10]}...'",
                                "Use _ instead of \\_",
                            )
                        )

                state = STATE_TEXT
                i += 1
            elif char == "\n":
                # Inline math usually shouldn't span multiple paragraphs (double newline)
                # But single newline is okay.
                # If we hit a double newline, we assume the $ was just a dollar sign.
                if i + 1 < length and content[i + 1] == "\n":
                    # Reset state, assume it was currency or mistake
                    # We could warn "Unclosed inline math" but that causes false positives for text like "Prices range from $10 to $20."
                    # So we just silently reset.
                    state = STATE_TEXT
                    i += 1
                else:
                    i += 1
            else:
                i += 1

    # End of file checks
    if state == STATE_DISPLAY_MATH:
        errors.append((start_line, "Unclosed display math", "Add closing $$"))

    return errors


def main() -> None:
    files = find_files()
    total_issues = 0

    print(f"Scanning {len(files)} files...")

    for f in files:
        issues = check_file(f)
        if issues:
            print(f"\nFile: {f}")
            for line, msg, fix in issues:
                print(f"  Line {line}: {msg} -> {fix}")
            total_issues += len(issues)

    if total_issues > 0:
        print(f"\nFound {total_issues} issues.")
        sys.exit(1)
    else:
        print("\nNo issues found!")
        sys.exit(0)


if __name__ == "__main__":
    main()
