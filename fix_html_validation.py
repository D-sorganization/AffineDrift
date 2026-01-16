"""Script to fix HTML validation issues."""

import re
from pathlib import Path


def fix_file(filepath: Path) -> None:
    """Fix HTML validation issues in the given file.

    Args:
    ----
        filepath: Path to the HTML file to fix.

    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return

    original_content = content

    # 1. Fix crossorigin
    # <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="">
    content = re.sub(r'crossorigin=""', "crossorigin", content)

    # 2. Fix redundant role="link"
    # role="link"
    content = re.sub(r'\s+role="link"', "", content)

    # 3. Fix aria-labelledby on dropdown-menu
    # <ul class="dropdown-menu" aria-labelledby="...">
    content = re.sub(
        r'(\s+class="dropdown-menu")\s+aria-labelledby="[^"]+"',
        r"\1",
        content,
    )

    if content != original_content:
        filepath.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    # Process all HTML files in docs
    files = Path("docs").rglob("*.html")
    for file in files:
        fix_file(file)
