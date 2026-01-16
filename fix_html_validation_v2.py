"""Script to fix HTML validation issues (version 2)."""

import re
from pathlib import Path


def fix_file(filepath: Path) -> None:
    """Fix HTML validation issues in the given file (version 2).

    Args:
    ----
        filepath: Path to the HTML file to fix.

    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return

    original_content = content

    # 1. Fix Anchor link missing text (wcag/h30) on logo
    # <a href="../index.html" class="navbar-brand navbar-brand-logo">
    if 'class="navbar-brand navbar-brand-logo"' in content:
        content = re.sub(
            r'(<a [^>]*class="navbar-brand navbar-brand-logo"[^>]*)>',
            r'\1 aria-label="Home">',
            content,
        )
        # Prevent double aria-label if ran multiple times (simple check)
        content = re.sub(
            r'aria-label="Home" aria-label="Home"',
            'aria-label="Home"',
            content,
        )

    # 2. Fix invalid IDs (containing dots)
    # This is tricky because we need to match id="..." and href="#..."
    # Pattern: id="...words.words..." -> id="...words-words..."
    # We will target specific known bad IDs from the log to be safe, or a general pattern.
    # The log showed IDs like "toc-velocity-dependence-vs.-torque-dependence"
    # We can replace dots with dashes inside id="..." values if they look like the ones in the log.

    def replace_dots_in_match(match: re.Match[str]) -> str:
        """Replace dots with dashes in the matched string."""
        return match.group(0).replace(".", "-")

    # Fix id="..."
    content = re.sub(r'id="[^"]*\.[^"]*"', replace_dots_in_match, content)

    # Fix href="#..." (internal links to those IDs)
    content = re.sub(r'href="#[^"]*\.[^"]*"', replace_dots_in_match, content)

    # 3. Fix missing button type
    # <button ...> without type attribute
    # We'll look for <button tags that don't have type=
    # This regex is a bit simplistic but should work for the generated HTML style
    def add_button_type(match: re.Match[str]) -> str:
        """Add type='button' attribute if missing."""
        tag = match.group(0)
        if "type=" not in tag:
            return tag.replace("<button", '<button type="button"')
        return tag

    content = re.sub(r"<button[^>]*>", add_button_type, content)

    # 4. Fix iframe missing title
    def add_iframe_title(match: re.Match[str]) -> str:
        """Add title attribute to iframe if missing."""
        tag = match.group(0)
        if "title=" not in tag:
            return tag.replace("<iframe", '<iframe title="Embedded Content"')
        return tag

    content = re.sub(r"<iframe[^>]*>", add_iframe_title, content)

    # 5. Fix unique landmarks (multiple mains or navs without labels)
    # The log showed errors about unique landmarks.
    # Let's try to add aria-labels to sidebars if they are <aside> or <nav>
    # <nav id="TOC" ...> -> aria-label="Table of Contents"
    if '<nav id="TOC"' in content and "aria-label" not in content:
        content = content.replace(
            '<nav id="TOC"',
            '<nav id="TOC" aria-label="Table of Contents"',
        )

    # <aside class="left-sidebar">
    if '<aside class="left-sidebar"' in content and "aria-label" not in content:
        content = content.replace(
            '<aside class="left-sidebar"',
            '<aside class="left-sidebar" aria-label="Primary Sidebar"',
        )

    if '<aside class="right-sidebar"' in content and "aria-label" not in content:
        content = content.replace(
            '<aside class="right-sidebar"',
            '<aside class="right-sidebar" aria-label="Secondary Sidebar"',
        )

    if content != original_content:
        filepath.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    # Process all HTML files in docs
    files = Path("docs").rglob("*.html")
    for file in files:
        fix_file(file)
