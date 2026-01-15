import os
import re


def find_qmd_md_files(root_dir: str) -> list[str]:
    files_list: list[str] = []
    # Explicitly check root .qmd files
    for f in os.listdir(root_dir):
        if (f.endswith(".qmd") or f.endswith(".md")) and os.path.isfile(os.path.join(root_dir, f)):
            files_list.append(os.path.join(root_dir, f))

    # Check articles and critiques
    for subdir in ["articles", "critiques"]:
        path = os.path.join(root_dir, subdir)
        if os.path.exists(path):
            for root, _dirs, files in os.walk(path):
                if "archive" in root:
                    continue
                for file in files:
                    if file.endswith(".qmd") or file.endswith(".md"):
                        files_list.append(os.path.join(root, file))
    return files_list


def check_file(filepath: str) -> None:
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

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
            elif state != STATE_CODE_BLOCK:
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
                                f"Line {start_line}: Encountered '$$' inside inline math starting at line {start_line}"
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
                                    f"Line {start_line}: Inline math has leading space: '${content_str}$'"
                                )

                        if not math_content:
                            errors.append(f"Line {start_line}: Empty inline math '$'")

                        i += 1
                        break

                    math_content.append(curr)
                    i += 1
                else:
                    # Unclosed inline math. Ignore for now as it's likely non-math text.
                    pass

        else:
            i += 1

    if errors:
        print(f"Errors in {filepath}:")
        for e in errors:
            print(f"  {e}")
        print("-" * 20)


if __name__ == "__main__":
    files = find_qmd_md_files(".")
    print(f"Scanning {len(files)} files...")
    for f in files:
        check_file(f)
