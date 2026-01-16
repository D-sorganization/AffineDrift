"""Script to check for equation syntax errors."""

import logging
import re
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def find_qmd_md_files(root_dir: Path) -> list[Path]:
    """Find all .qmd and .md files in the repository."""
    files_list: list[Path] = []
    # Explicitly check root .qmd files
    for f in root_dir.iterdir():
        if f.suffix in {".qmd", ".md"} and f.is_file():
            files_list.append(f)

    # Check articles and critiques
    for subdir in ["articles", "critiques"]:
        path = root_dir / subdir
        if path.exists():
            # Use rglob and filter instead of os.walk
            for f in path.rglob("*"):
                if f.suffix in {".qmd", ".md"} and "archive" not in f.parts:
                    files_list.append(f)

    return files_list


def check_file(filepath: Path) -> None:
    """Check a file for equation errors."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return

    errors: list[str] = []

    i = 0
    length = len(content)
    line_num = 1

    # States
    STATE_TEXT = 0
    STATE_CODE_BLOCK = 1  # ``` ... ```
    STATE_INLINE_CODE = 2  # ` ... `

    state = STATE_TEXT

    while i < length:
        char = content[i]

        if char == "\n":
            line_num += 1
            i += 1
            continue

        # Check for code block start/end
        # We need to look ahead for ```
        if char == "`":
            if i + 2 < length and content[i + 1] == "`" and content[i + 2] == "`":
                # Triple backtick
                if state == STATE_TEXT:
                    state = STATE_CODE_BLOCK
                elif state == STATE_CODE_BLOCK:
                    state = STATE_TEXT
                i += 3
                continue
            if state != STATE_CODE_BLOCK:
                # Single backtick (inline code)
                if state == STATE_TEXT:
                    state = STATE_INLINE_CODE
                elif state == STATE_INLINE_CODE:
                    state = STATE_TEXT
                i += 1
                continue

        if state != STATE_TEXT:
            # Inside code, ignore all $
            i += 1
            continue

        # Handle escaped dollar
        if char == "\\" and i + 1 < length and content[i + 1] == "$":
            i += 2
            continue

        if char == "$":
            # Check for double dollar $$
            if i + 1 < length and content[i + 1] == "$":
                # Display math start
                start_line = line_num
                i += 2  # Skip opening $$

                # Look for closing $$
                while i < length:
                    if content[i] == "\n":
                        line_num += 1

                    if content[i] == "$" and i + 1 < length and content[i + 1] == "$":
                        i += 2
                        break
                    i += 1
                else:
                    errors.append(f"Line {start_line}: Unclosed display math '$$'")
            else:
                # Inline math start
                # start_i = i # Unused
                start_line = line_num
                i += 1

                has_leading_space = False
                if i < length and content[i].isspace() and content[i] != "\n":
                    has_leading_space = True

                math_content: list[str] = []
                # Look for closing $
                while i < length:
                    curr = content[i]
                    if curr == "\n":
                        line_num += 1

                    if curr == "\\" and i + 1 < length and content[i + 1] == "$":
                        math_content.append(curr)
                        math_content.append(content[i + 1])
                        i += 2
                        continue

                    if curr == "$":
                        if i + 1 < length and content[i + 1] == "$":
                            # Found $$ inside inline?
                            # Check if we just hit a code block or something?
                            # But we are in "inline math search mode".
                            # It's possible the first $ was actually start of $$ but we treated it as start of inline.
                            # But we check for $$ first in the outer loop.

                            # Maybe it's $ .. $$ (end of math is $$?)
                            # If we see $$, it's definitely weird if we started with $.
                            errors.append(
                                f"Line {start_line}: Encountered '$$' inside inline math starting at line {start_line}",
                            )
                            i += 2
                            break

                        # Found closing $
                        if len(math_content) > 0:
                            if math_content[-1].isspace():
                                errors.append(f"Line {start_line}: Inline math has trailing space")

                        if has_leading_space:
                            # Heuristic: Check if content looks like valid math or just text/numbers
                            # If it's just digits and spaces, likely money. e.g. "$ 100 "
                            content_str = "".join(math_content)
                            if not re.match(r"^\s*[\d\.,]+\s*$", content_str):
                                errors.append(
                                    f"Line {start_line}: Inline math has leading space: '${content_str}$'",
                                )

                        if not math_content:
                            errors.append(f"Line {start_line}: Empty inline math '$'")

                        i += 1
                        break

                    math_content.append(curr)
                    i += 1
                else:
                    # Unclosed inline math. Ignore for now as it's likely non-math text.
                    pass  # Explicitly allowing unclosed inline math for now

        else:
            i += 1

    if errors:
        for error in errors:
            logger.error("%s: %s", filepath, error)


if __name__ == "__main__":
    files = find_qmd_md_files(Path("."))
    for f in files:
        check_file(f)
